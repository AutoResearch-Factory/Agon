#!/usr/bin/env python3
"""Offline plugin tests: no provider calls, global CC settings, or shell edits."""

from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "scripts"


def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = load("backend-limit-retry.py", "backend_limit_retry")
# These fixtures cover supported backend limit message formats. Tests
# keep their own fixtures rather than depending on another session's files.
CODEX = ("ERROR: You've hit your usage limit. Visit https://chatgpt.com/codex/settings/usage "
         "to purchase more credits or try again at Sep 28th, 2026 4:46 AM.")
MONTHLY = ("You've hit your monthly spend limit · raise it at "
           "claude.ai/settings/usage?from=cc_cli_limit_message · your session limit "
           "resets 2:30pm (America/New_York)")
SESSION = "You've hit your session limit · resets 7:50am (America/New_York)"


class RewriteTests(unittest.TestCase):
    def success(self, response):
        result = hook.handle({"hook_event_name": "PostToolUse", "tool_response": response})
        return result["hookSpecificOutput"] if result else None

    def test_two_error_lines_in_successful_bash_stdout(self):
        original = {"stdout": CODEX + "\n" + CODEX + "\n[exited with code 1]",
                    "stderr": "", "interrupted": False, "isImage": False,
                    "noOutputExpected": False}
        result = self.success(original)
        self.assertNotIn("additionalContext", result)
        updated = result["updatedToolOutput"]
        self.assertEqual(updated["stdout"].count(hook.RETRY_TEXT), 2)
        self.assertTrue(updated["stdout"].endswith("[exited with code 1]"))
        self.assertEqual(updated.keys(), original.keys())
        self.assertEqual({k: v for k, v in updated.items() if k != "stdout"},
                         {k: v for k, v in original.items() if k != "stdout"})
        self.assertIn("Sep 28th", original["stdout"])

    def test_claude_forms(self):
        for text, expected in [(MONTHLY, MONTHLY.split("your session")[0] + hook.RETRY_TEXT),
                               (SESSION, "You've hit your session limit · " + hook.RETRY_TEXT),
                               ("your session limit resets 2:30pm", hook.RETRY_TEXT)]:
            with self.subTest(text=text):
                result = self.success({"stdout": text})
                self.assertEqual(result["updatedToolOutput"]["stdout"], expected)
                self.assertNotIn("additionalContext", result)

    def test_read_and_mcp_shapes(self):
        for value in [{"type": "text", "file": {"filePath": "/x", "content": CODEX,
                                                  "numLines": 1, "startLine": 1, "totalLines": 1}},
                      [{"type": "text", "text": CODEX}, {"type": "image", "data": "AA=="}],
                      CODEX]:
            with self.subTest(value=value):
                result = self.success(value)
                self.assertNotIn("additionalContext", result)
                self.assertIn(hook.RETRY_TEXT, str(result["updatedToolOutput"]))

    def test_serialized_json_and_repr(self):
        for raw in [json.dumps({"result": MONTHLY, "next": "keep"}, ensure_ascii=False),
                    repr(MONTHLY), repr("prefix 'quote' " + CODEX)]:
            result = self.success(raw)["updatedToolOutput"]
            self.assertIn(hook.RETRY_TEXT, result)
            self.assertEqual(result.count("\\'"), raw.count("\\'"))
            if raw.startswith("{"):
                self.assertEqual(json.loads(result)["next"], "keep")

    def test_boundaries_and_unrelated_reset(self):
        inputs = [
            CODEX + "\nJob resets 8:00am (America/New_York)",
            json.dumps({"error": "You've hit your usage limit", "other": "try again at Sep 28th, 2026 4:46 AM"}),
            "You've hit your usage limit.\ntry again at Sep 28th, 2026 4:46 AM",
            "You've hit your usage limit.\\ntry again at Sep 28th, 2026 4:46 AM",
        ]
        self.assertTrue(self.success(inputs[0])["updatedToolOutput"].endswith("Job resets 8:00am (America/New_York)"))
        for raw in inputs[1:]:
            result = self.success(raw)
            self.assertNotIn("updatedToolOutput", result)
            self.assertEqual(result["additionalContext"], hook.REMINDER)

    def test_trailing_business_text(self):
        raw = CODEX + " Keep this next task unchanged."
        self.assertTrue(self.success(raw)["updatedToolOutput"].endswith(". Keep this next task unchanged."))

    def test_rewritten_results_are_idempotent(self):
        for raw in [CODEX, MONTHLY, SESSION]:
            first = self.success({"stdout": raw})
            self.assertIsNone(self.success(first["updatedToolOutput"]))
        self.assertIsNotNone(self.success({"stdout": "You've hit your usage limit without a date"}))

    def test_unknown_format_reminder_only(self):
        result = self.success("You've hit your usage limit. try again at 2026-09-28T04:46Z")
        self.assertEqual(set(result), {"hookEventName", "additionalContext"})

    def test_case_escaped_apostrophe_multiple_fields(self):
        raw = {"stdout": CODEX.upper(), "stderr": MONTHLY.replace("'", "\\'")}
        result = self.success(raw)
        self.assertNotIn("additionalContext", result)
        self.assertIn(hook.RETRY_TEXT, result["updatedToolOutput"]["stderr"])

    def test_no_match_and_no_input_scanning(self):
        self.assertIsNone(self.success({"stdout": "normal", "stderr": "", "value": 0}))
        self.assertIsNone(hook.handle({"hook_event_name": "PostToolUse", "tool_input": CODEX,
                                       "tool_response": "normal"}))

    def test_failure_only_checks_error(self):
        result = hook.handle({"hook_event_name": "PostToolUseFailure", "error": CODEX})
        self.assertEqual(result, hook.context_output("PostToolUseFailure"))
        self.assertIsNone(hook.handle({"hook_event_name": "PostToolUseFailure", "error": "Other failure",
                                       "tool_response": CODEX}))


class StateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="agon-limit-test-")
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def event(self, name, **values):
        return hook.handle({"session_id": "fixture-session", "hook_event_name": name, **values}, self.root)

    def test_failure_and_single_manual_reminder(self):
        self.assertIsNone(self.event("StopFailure", error="rate_limit", last_assistant_message=MONTHLY))
        self.assertEqual(self.event("UserPromptSubmit", prompt="continue"), hook.context_output("UserPromptSubmit"))
        self.assertIsNone(self.event("UserPromptSubmit", prompt="next"))
        self.assertNotIn(MONTHLY, "".join(path.read_text() for path in self.root.glob("*.json")))

    def test_resume_consumes_once(self):
        self.event("StopFailure", error="rate_limit")
        self.assertIsNotNone(self.event("SessionStart", source="resume"))
        self.assertIsNone(self.event("UserPromptSubmit", prompt="continue"))
        self.assertIsNone(self.event("UserPromptSubmit", prompt=hook.AUTO_PROMPTS[0]))

    def test_auto_resume_without_marker(self):
        for prompt in hook.AUTO_PROMPTS:
            self.assertIsNotNone(self.event("UserPromptSubmit", prompt=prompt))
        self.assertIsNone(self.event("UserPromptSubmit", prompt="ordinary input"))

    def test_new_failure_rearms_once_and_sessions_are_isolated(self):
        self.event("StopFailure", error="rate_limit")
        other = {"session_id": "different-session", "hook_event_name": "UserPromptSubmit", "prompt": "continue"}
        self.assertIsNone(hook.handle(other, self.root))
        self.assertIsNotNone(self.event("UserPromptSubmit", prompt="continue"))
        self.assertIsNone(self.event("UserPromptSubmit", prompt="continue"))
        self.event("StopFailure", error="rate_limit")
        self.assertIsNotNone(self.event("UserPromptSubmit", prompt="continue"))

    def test_ordinary_submission_without_failure_creates_only_lock(self):
        self.assertIsNone(self.event("UserPromptSubmit", prompt="ordinary input"))
        self.assertEqual(list(self.root.glob("*.json")), [])
        self.assertEqual(len(list(self.root.glob("*.lock"))), 1)

    def test_consume_waits_for_first_writer_before_checking_state(self):
        key = hashlib.sha256(b"fixture-session").hexdigest()
        state_path = self.root / (key + ".json")
        lock_path = self.root / (key + ".lock")
        entered_lock = threading.Event()
        real_flock = fcntl.flock

        def observe_lock(fd, operation):
            entered_lock.set()
            return real_flock(fd, operation)

        with ThreadPoolExecutor(max_workers=1) as pool:
            with lock_path.open("a") as writer_lock:
                real_flock(writer_lock, fcntl.LOCK_EX)
                try:
                    with patch.object(hook.fcntl, "flock", side_effect=observe_lock):
                        consumer = pool.submit(self.event, "UserPromptSubmit", prompt="continue")
                        waited_for_writer = entered_lock.wait(1)
                        pending_path = self.root / "first-write.tmp"
                        pending_path.write_text(json.dumps({"pending": True}))
                        os.replace(pending_path, state_path)
                finally:
                    real_flock(writer_lock, fcntl.LOCK_UN)
            result = consumer.result(timeout=3)
        self.assertTrue(waited_for_writer, "consume skipped the in-progress first writer")
        self.assertEqual(result, hook.context_output("UserPromptSubmit"))
        self.assertIsNone(self.event("UserPromptSubmit", prompt="next"))

    def test_only_exact_auto_prompts_trigger_without_a_marker(self):
        for prompt in ["Your claude.ai usage limit has reset.",
                       "Investigate: " + hook.AUTO_PROMPTS[0], "quota_auto_resume_fired"]:
            self.assertIsNone(self.event("UserPromptSubmit", prompt=prompt))

    def test_unrelated_events_and_subagents(self):
        self.event("StopFailure", error="authentication_failed")
        self.assertIsNone(self.event("UserPromptSubmit", prompt="continue"))
        self.event("StopFailure", error="rate_limit", agent_id="child")
        self.assertIsNone(self.event("UserPromptSubmit", prompt="continue"))

    def test_state_not_written_into_plugin_or_global_settings(self):
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": str(self.root)}):
            self.assertEqual(hook.state_directory(), self.root / "limit-retry")
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": ""}):
            path = hook.state_directory()
            self.assertEqual(path.name, "agon-limit-retry-%s" % os.getuid())
            self.assertNotIn(PLUGIN, path.parents)

    def test_shared_or_symlink_state_directory_rejected(self):
        public = self.root / "public"
        public.mkdir()
        public.chmod(0o777)
        payload = {"session_id": "session", "hook_event_name": "StopFailure", "error": "rate_limit"}
        self.assertIsNone(hook.handle(payload, public))
        self.assertEqual(list(public.iterdir()), [])
        private = self.root / "private"
        private.mkdir(mode=0o700)
        link = self.root / "linked"
        link.symlink_to(private, target_is_directory=True)
        self.assertIsNone(hook.handle(payload, link))
        self.assertEqual(list(private.iterdir()), [])


class PluginIntegrationTests(unittest.TestCase):
    def test_hooks_are_plugin_relative_and_existing_hook_is_preserved(self):
        manifest = json.loads((PLUGIN / 'hooks/hooks.json').read_text())
        target = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backend-limit-retry.py"'
        for event in ['PostToolUse', 'PostToolUseFailure', 'StopFailure', 'UserPromptSubmit', 'SessionStart']:
            commands = [entry for rule in manifest['hooks'][event] for entry in rule['hooks']]
            matching = [item for item in commands if item.get('command') == target]
            self.assertEqual(len(matching), 1, event)
            self.assertFalse(matching[0].get('async', False))
        existing = [entry['command'] for rule in manifest['hooks']['PostToolUse'] for entry in rule['hooks']]
        self.assertTrue(any('settings-change-notify.py' in item for item in existing))
        self.assertIn('SessionEnd', manifest['hooks'])

    def test_plugin_configured_command_with_space_in_plugin_path(self):
        manifest = json.loads((PLUGIN / 'hooks/hooks.json').read_text())
        command = next(item['command'] for rule in manifest['hooks']['PostToolUse']
                       for item in rule['hooks'] if 'backend-limit-retry.py' in item['command'])
        with tempfile.TemporaryDirectory(prefix='plugin-path-test-') as temp:
            plugin = Path(temp) / 'plugin with spaces'
            plugin.mkdir()
            (plugin / 'scripts').symlink_to(SCRIPTS, target_is_directory=True)
            env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(plugin), CLAUDE_PLUGIN_DATA=str(Path(temp) / 'data'))
            payload = {'hook_event_name': 'PostToolUse', 'tool_name': 'Bash',
                       'tool_response': {'stdout': CODEX, 'stderr': '', 'interrupted': False, 'isImage': False}}
            result = subprocess.run(['bash', '--noprofile', '--norc', '-c', command],
                                    input=json.dumps(payload).encode(), capture_output=True, env=env, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)['hookSpecificOutput']
            self.assertNotIn('additionalContext', output)
            self.assertIn(hook.RETRY_TEXT, output['updatedToolOutput']['stdout'])

    def test_registered_state_event_commands_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix='plugin-state-test-') as temp:
            env = dict(os.environ, CLAUDE_PLUGIN_DATA=temp)
            for event, fields, expect_context in [
                ('StopFailure', {'error': 'rate_limit'}, False),
                ('UserPromptSubmit', {'prompt': 'continue'}, True),
                ('UserPromptSubmit', {'prompt': 'next'}, False),
                ('UserPromptSubmit', {'prompt': hook.AUTO_PROMPTS[1]}, True),
            ]:
                payload = {'session_id': 'integration-fixture', 'hook_event_name': event, **fields}
                result = subprocess.run([sys.executable, str(SCRIPTS / 'backend-limit-retry.py')],
                                        input=json.dumps(payload).encode(), capture_output=True, env=env, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                if expect_context:
                    self.assertEqual(json.loads(result.stdout), hook.context_output(event))
                else:
                    self.assertEqual(result.stdout, b'')

    def test_malformed_input_fails_open(self):
        for data in [b'{bad', b'[]', b'null', b'', b'{}']:
            result = subprocess.run([sys.executable, str(SCRIPTS / 'backend-limit-retry.py')],
                                    input=data, capture_output=True, timeout=5)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b'', b''))


if __name__ == '__main__':
    unittest.main(verbosity=2)
