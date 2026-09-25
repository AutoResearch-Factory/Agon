#!/usr/bin/env python3
"""Plugin hooks: normalize retry hints without modifying source logs or quotas."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time

REMINDER = (
    "User reminder: If the backend is unavailable now, retry in about 30 minutes. "
    "The reset time shown above is your hallucination; do not wait for days!"
)
RETRY_TEXT = "try again in 30 minutes"
H = r"[^\S\r\n]"
YOU = rf"You(?:\\?['’])ve{H}+hit{H}+your{H}+"
TRIGGER = re.compile(
    rf"{YOU}(?:(?:[A-Za-z]+(?:['’][A-Za-z]+)?{H}+){{0,3}}spend{H}+limit"
    rf"|usage{H}+limit|session{H}+limit)"
    rf"|your{H}+session{H}+limit{H}+resets", re.IGNORECASE,
)
# Do not cross newlines, escaped newlines, or quoted-string boundaries in
# serialized JSON/repr results. Never parse and reserialize an embedded log.
BOUNDARY = re.compile(r'''[\r\n"'`]|\\[rn]''')
CLOCK = rf"(?:0?[1-9]|1[0-2]):[0-5][0-9]{H}*[ap]m\b"
ZONE = rf"(?:{H}*\([A-Za-z0-9_+.-]+(?:/[A-Za-z0-9_+.-]+)+\))?"
MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
         r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?"
         r"|Nov(?:ember)?|Dec(?:ember)?)")
RETRY_AT = re.compile(
    rf"\btry{H}+again{H}+at{H}+{MONTH}{H}+\d{{1,2}}(?:st|nd|rd|th)?"
    rf",{H}+\d{{4}}{H}+{CLOCK}{ZONE}", re.IGNORECASE,
)
SESSION_RESET = re.compile(
    rf"\byour{H}+session{H}+limit"
    rf"(?:(?P<separator>{H}*[·:—-]{H}*)|{H}+)"
    rf"(?P<reset>resets{H}+{CLOCK}{ZONE})", re.IGNORECASE,
)
NORMALIZED_RETRY = re.compile(rf"\btry{H}+again{H}+in{H}+30{H}+minutes\b", re.IGNORECASE)
MAX_INPUT = 16 * 1024 * 1024
AUTO_PROMPTS = (
    "Your claude.ai usage limit has reset. Continue the task you were working on when the limit was reached; do not repeat work that is already complete.",
    "Your claude.ai usage is available again before the usage-limit reset. Continue the task you were working on when the limit was reached; do not repeat work that is already complete.",
)


def state_directory():
    """Runtime data is separate from plugin code and global CC configuration."""
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data:
        return Path(plugin_data) / "limit-retry"
    # Older hosts may not export CLAUDE_PLUGIN_DATA. Keep their state in a
    # private, user-specific temporary directory, never in the plugin checkout.
    return Path(tempfile.gettempdir()) / ("agon-limit-retry-%s" % os.getuid())


def rewrite_text(text):
    """Return (text, matched, changed); change only recognized time spans."""
    spans = set()
    matched = False
    for hit in TRIGGER.finditer(text):
        boundary = BOUNDARY.search(text, hit.end())
        end = boundary.start() if boundary else len(text)
        fragment = text[hit.start():end]
        local_spans = set()
        for pattern in (RETRY_AT, SESSION_RESET):
            for timestamp in pattern.finditer(fragment):
                start = timestamp.start()
                if pattern is SESSION_RESET and timestamp.group("separator"):
                    start = timestamp.start("reset")
                local_spans.add((hit.start() + start, hit.start() + timestamp.end()))
        if local_spans:
            spans.update(local_spans)
            matched = True
        elif not NORMALIZED_RETRY.search(fragment):
            matched = True
    if not spans:
        return text, matched, False
    # The spend-limit and session-limit triggers can find the same reset span.
    nonoverlapping = []
    for start, end in sorted(spans):
        if nonoverlapping and start < nonoverlapping[-1][1]:
            continue
        nonoverlapping.append((start, end))
    for start, end in reversed(nonoverlapping):
        text = text[:start] + RETRY_TEXT + text[end:]
    return text, matched, True


def rewrite_value(value):
    if isinstance(value, str):
        return rewrite_text(value)
    if isinstance(value, (dict, list)):
        matched = changed = False
        result = {} if isinstance(value, dict) else []
        items = value.items() if isinstance(value, dict) else enumerate(value)
        for key, original in items:
            updated, found, rewritten = rewrite_value(original)
            matched |= found
            changed |= rewritten
            if isinstance(value, dict):
                result[key] = updated
            else:
                result.append(updated)
        return result, matched, changed
    return value, False, False


def has_trigger(value):
    if isinstance(value, str):
        return TRIGGER.search(value) is not None
    if isinstance(value, dict):
        return any(has_trigger(item) for item in value.values())
    if isinstance(value, list):
        return any(has_trigger(item) for item in value)
    return False


def context_output(event):
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": REMINDER}}


def session_state(payload, operation, root=None):
    """One reminder per main-session failure; never store prompt/error text."""
    session = payload.get("session_id")
    if not isinstance(session, str) or not session or payload.get("agent_id"):
        return False
    root = state_directory() if root is None else Path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Reject another user's pre-created directory/symlink in shared /tmp.
    if root.is_symlink() or root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o022:
        return False
    key = hashlib.sha256(session.encode()).hexdigest()
    state_path = root / (key + ".json")
    lock_path = root / (key + ".lock")
    with lock_path.open("a") as lock:
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        # A first writer may hold the lock before its atomic rename creates
        # the state file. Never check for absence outside this lock.
        if operation == "consume" and not state_path.exists():
            return False
        try:
            state = json.loads(state_path.read_text())
            if not isinstance(state, dict):
                state = {}
        except (OSError, ValueError):
            state = {}
        now = time.time()
        result = False
        if operation == "mark":
            state["pending"] = True
            state["failure_at"] = now
        elif operation in ("consume", "auto"):
            pending = state.get("pending") is True
            if operation == "auto":
                delivered_at = state.get("delivered_at", 0)
                recent_resume = (state.get("delivered_by") == "SessionStart"
                                 and isinstance(delivered_at, (int, float))
                                 and 0 <= now - delivered_at < 60)
                result = pending or not recent_resume
            else:
                result = pending
            if result:
                state["pending"] = False
                state["delivered_at"] = now
                state["delivered_by"] = payload.get("hook_event_name")
        if operation == "mark" or result:
            descriptor, tmp = tempfile.mkstemp(prefix=key + ".", dir=root)
            try:
                with os.fdopen(descriptor, "w") as target:
                    json.dump(state, target)
                    target.write("\n")
                os.replace(tmp, state_path)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        return result


def handle(payload, state_root=None):
    if not isinstance(payload, dict):
        return None
    event = payload.get("hook_event_name")
    if event == "PostToolUse":
        output, matched, changed = rewrite_value(payload.get("tool_response"))
        if changed:
            return {"hookSpecificOutput": {"hookEventName": event, "updatedToolOutput": output}}
        if matched:
            return context_output(event)
    elif event == "PostToolUseFailure":
        if has_trigger(payload.get("error")):
            return context_output(event)
    elif event == "StopFailure":
        if payload.get("error") == "rate_limit":
            session_state(payload, "mark", state_root)
    elif event == "UserPromptSubmit":
        prompt = payload.get("prompt")
        automatic = isinstance(prompt, str) and prompt.strip() in AUTO_PROMPTS
        if session_state(payload, "auto" if automatic else "consume", state_root):
            return context_output(event)
        if automatic and not payload.get("agent_id") and not payload.get("session_id"):
            return context_output(event)
    elif event == "SessionStart" and payload.get("source") == "resume":
        if session_state(payload, "consume", state_root):
            return context_output(event)
    return None


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            return
        result = handle(json.loads(raw))
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (ValueError, TypeError, OSError, RecursionError):
        # Fail open: a reminder must never disrupt the underlying user tool.
        return


if __name__ == "__main__":
    main()
