#!/usr/bin/env python3
"""PreToolUse hook (matcher: CronCreate), 由 plugin 的 hooks/hooks.json 加载.

启用本 plugin 的会话禁止任何 durable cron: durable:true 的 CronCreate 一律拒绝
(它会写进 .claude/scheduled_tasks.json 并在会话结束后继续存活).
session-only cron (durable:false) 照常放行. 其它任何情况 (别的工具, 输入解析失败) exit 0 不干预.
"""
import json
import os
import sys


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0  # malformed input: fail open
    if not isinstance(d, dict) or d.get("tool_name") != "CronCreate":
        return 0
    if not (d.get("tool_input") or {}).get("durable"):
        return 0  # session-only cron is allowed
    project = os.environ.get("CLAUDE_PROJECT_DIR") or d.get("cwd") or os.getcwd()
    reason = (
        f"Durable cron jobs are banned by the agon plugin ({project}): no persistent cron. "
        f"durable:true would persist to .claude/scheduled_tasks.json and outlive this session. "
        f"Use durable:false (session-only) instead."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
