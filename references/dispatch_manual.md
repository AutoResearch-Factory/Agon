## How to start a claude-*/codex subagent?

本文档教你如何用命令行启动 claude (包括 claude-ds, claude-kimi, claude-codex 等变种, 接口一致) 和 codex 作为 subagents.

首先你需要准备:
- AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/agents/${AGENT_NAME}.md" 会进入 subagent 的 system message
- TASK_PROMPT="本次具体任务指令" 会进入 subagent 的 user message
- OUT="/tmp/$USER/${problem-slug}-${AGENT_NAME}-${time:hhmmss}.txt"

调用返回后先读取 `$OUT` 作为 response, 再 `rm "$OUT"` 防止之后混淆.

codex 的 session id 打印在 stderr banner 里. 加 `2>&1` 合并到 stdout, 用 `grep 'session id:' | awk '{print $NF}'` 提取. Resume 时传入该 id.

### codex

```
codex exec --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.5 -c model_reasoning_effort=xhigh \
  --output-last-message "$OUT" \
  "$TASK_PROMPT" \
  < "$AGENT_PROMPT" 2>&1
```

Resume 已有 session:

```
codex exec resume --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.5 -c model_reasoning_effort=xhigh \
  --output-last-message "$OUT" \
  "<session_id>" \
  "$TASK_PROMPT" \
  2>&1
```

## claude & claude-*

```
claude --dangerously-skip-permissions \
  --plugin-dir "${CLAUDE_PLUGIN_ROOT}" \
  --output-format json \
  --effort max \
  --append-system-prompt-file "$AGENT_PROMPT" \
  -p "$TASK_PROMPT" > "$OUT"
```

Resume 已有 session:

```
claude --dangerously-skip-permissions \
  --plugin-dir "${CLAUDE_PLUGIN_ROOT}" \
  --output-format json \
  --effort max \
  --resume "<session_id>" \
  -p "$TASK_PROMPT" > "$OUT"
```

claude-* 是由各个不同公司 api 驱动的 claude code, 其接口与 claude 完全一致, 目前可用的有: claude-ds (deepseek v4 pro 驱动), claude-codex (gpt5.5 驱动)
