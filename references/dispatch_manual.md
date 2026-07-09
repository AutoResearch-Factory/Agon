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
  -m gpt-5.6-sol -c model_reasoning_effort=max \
  --output-last-message "$OUT" \
  "$TASK_PROMPT" \
  < "$AGENT_PROMPT" 2>&1
```

Resume 已有 session:

```
codex exec resume --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.6-sol -c model_reasoning_effort=max \
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

claude-* 是由各个不同公司 api 驱动的 claude code, 其接口与 claude 完全一致, 目前可用的有: claude-ds (deepseek v4 pro 驱动), claude-codex (gpt 驱动)

## 注意

- 不要在 CLI subagent 命令内部再加 `nohup` 或者 `&`。Claude Code 的 Bash background 已经是一层后台机制；启动 subagent 时，不要再用 `nohup` 或 `&`。
- `$OUT` 缺失/0 字节在这种情况下表示 report 还没交接，不是 subagent 失败。必须等待真正的 codex/claude-* 进程结束；禁止立即 retry。之前的教训: subagent 刚跑 30s 就去检查 `$OUT`，结果自然为空，以为是失败又重试，导致数个重复 subagent 打架。
