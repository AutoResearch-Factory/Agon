#!/usr/bin/env python3
"""Notify Agon dispatchers when .settings.toml changes during a run.

The hook is scoped to conversations that invoked one of Agon's top-level tick
commands. Worker processes load the same plugin, but should not receive config
change notifications. A per-session marker caches the dispatcher check, and a
per-session snapshot stores the previous settings text so every dispatcher can
receive an independent unified diff.

Errors are deliberately swallowed by the entry point: a config reminder must
never disrupt the research workflow.
"""

import difflib
import getpass
import json
import os
import re
import sys
import tempfile


# A real slash-command invocation is recorded in the session transcript as a
# command-name tag. Explicitly list the user-facing dispatcher commands so
# deep-lit workers and plain-text mentions do not produce false positives.
TICK_RE = re.compile(r"command-name>[^<]*(?:experiment-tick|idea-tick|proposal-tick)")


def _atomic_write(path, text):
    """Write text atomically using a temporary file in the same directory."""
    directory = os.path.dirname(path)
    fd, temporary_path = tempfile.mkstemp(dir=directory, prefix=".snap-tmp-")
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
        os.replace(temporary_path, path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except OSError:
            pass
        raise


def _paths(session_id):
    """Return the snapshot directory and safe per-session paths."""
    safe_id = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in session_id
    )
    user = os.environ.get("USER") or getpass.getuser()
    snapshot_directory = os.path.join(tempfile.gettempdir(), user)
    snapshot_path = os.path.join(
        snapshot_directory, "agon-settings-%s.snap" % safe_id
    )
    marker_path = os.path.join(snapshot_directory, "agon-tick-%s.marker" % safe_id)
    return snapshot_directory, snapshot_path, marker_path


def _payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def _is_tick_session(marker_path, transcript_path):
    """Return whether this conversation invoked an Agon dispatcher command."""
    if os.path.exists(marker_path):
        return True
    if not transcript_path or not os.path.isfile(transcript_path):
        return False
    try:
        with open(transcript_path, errors="ignore") as transcript:
            for line in transcript:
                if TICK_RE.search(line):
                    open(marker_path, "w").close()
                    return True
    except OSError:
        return False
    return False


def cleanup(payload):
    """Remove this session's settings snapshot and dispatcher marker."""
    session_id = str(payload.get("session_id") or "nosession")
    _, snapshot_path, marker_path = _paths(session_id)
    for path in (snapshot_path, marker_path):
        try:
            os.unlink(path)
        except OSError:
            pass


def main():
    if len(sys.argv) < 2:
        return

    payload = _payload()
    if sys.argv[1] == "--cleanup":
        cleanup(payload)
        return

    settings_path = sys.argv[1]
    if not os.path.isfile(settings_path):
        return

    session_id = str(payload.get("session_id") or "nosession")
    event = str(payload.get("hook_event_name") or "PostToolUse")
    transcript_path = payload.get("transcript_path")

    snapshot_directory, snapshot_path, marker_path = _paths(session_id)
    os.makedirs(snapshot_directory, exist_ok=True)

    if not _is_tick_session(marker_path, transcript_path):
        return

    with open(settings_path) as settings_file:
        current = settings_file.read()

    if not os.path.exists(snapshot_path):
        _atomic_write(snapshot_path, current)
        return

    with open(snapshot_path) as snapshot_file:
        previous = snapshot_file.read()

    if previous == current:
        return

    diff = "".join(
        difflib.unified_diff(
            previous.splitlines(keepends=True),
            current.splitlines(keepends=True),
            fromfile=".settings.toml (previous)",
            tofile=".settings.toml (current)",
        )
    )
    _atomic_write(snapshot_path, current)

    context = "Settings changed:\n```diff\n" + diff + "\n```"
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": context,
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
