## How to start a claude-*/codex subagent?

本文档教你如何用命令行启动 claude (包括 claude-grok, claude-codex 等变种, 接口一致) 和 codex 作为 subagents.

首先你需要准备:
- AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/agents/${AGENT_NAME}.md" 会进入 subagent 的 system message
- TASK_PROMPT="本次具体任务指令" 会进入 subagent 的 user message
- OUT="/tmp/$USER/${problem-slug}-${AGENT_NAME}-${time:hhmmss}.txt"

调用返回后先读取 `$OUT` 作为 response, 再 `rm "$OUT"` 防止之后混淆.

codex 的 session id 打印在 stderr banner 里. 加 `2>&1` 后从合并输出读取, Resume 时传入该 id.

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
  --append-system-prompt-file "$AGENT_PROMPT" \
  --resume "<session_id>" \
  -p "$TASK_PROMPT" > "$OUT"
```

claude-* 是由各个不同公司 api 驱动的 claude code, 其接口与 claude 完全一致, 目前可用的有: claude-grok (xAI 公司), claude-codex (gpt 驱动)

## 注意

- 不要在 CLI subagent 命令内部再加 `nohup` 或者 `&`. Claude Code 的 Bash background 已经是一层后台机制; 启动 subagent 时, 不要再用 `nohup` 或 `&`.
- 一个 Bash background task 只能启动一个 subagent; 禁止在 task 内用 `&` / `wait` 并发启动多个 subagent.
- 禁止在 CLI subagent 命令后接任何 pipe (`tail`, `head`, `grep` 等); 需要 grep 时先将输出写入文件.
- 是否仍在运行以本次 Bash background task 的状态为准; codex 打印 session id 不能证明进程存活, 禁止用 `pgrep -f <role>` 猜测. 根据 task 状态, 退出码和 `$OUT` 判定:
  - 在跑 + `$OUT` 空: 继续等.
  - 在跑 + `$OUT` 非空: 仍等 task 正常结束.
  - 已结束 + exit 0 + `$OUT` 非空 + `$OUT` 内容正常: 成功.
  - 已结束 + exit 非 0 或 `$OUT` 空 或 `$OUT` 内容为报错: 失败. 特别地, exit 0 + `$OUT` 空也是失败 (例如 codex 用量耗尽).
- 所有 subagent 都必须且只能通过本手册规定的 shell/CLI 命令调用; 严格禁止使用 Agent tool 或任何其他内置 subagent 机制, 即使 CLI 调用失败也不得切换到 Agent tool.
- Codex 和 Claude Code 在 Resume 时的行为不同, Codex 会保留之前注入的 `AGENT_PROMPT`, 不需要再次传入, 但是 claude-* 的 append system prompt 只对当前 invocation 生效, 所以需要再次指定.
