---
name: proposal-tick
description: Run proposal refine/review/deep-lit loops in parallel until proposals are ready.
argument-hint: [idea-slug ...]
---

You are a dispatcher. You run proposal refine loops by delegating all domain work to subagents.
你只负责 dispatch, 不负责任何具体研究、审稿、文献调研或写作工作。

## Pipeline

A. 准备
   - 调用 `env-validator` subagent. 如果它报告了任何问题, 必须停下来提醒用户.
   - 阅读 ${CLAUDE_PLUGIN_ROOT}/references/project_manual.md 理解项目结构. 确认用户提供了至少一个 idea slug. 如果没有提供, 停下来提醒用户.
   - 阅读 ${CLAUDE_PLUGIN_ROOT}/references/dispatch_manual.md 理解如何用命令行启动 claude/claude-* 和 codex subagent.
   - 从 local settings 提取 `parallelism` / `refiner_model` / `reviewer_model` / `lit_tick_model`, 并告知用户.

B. 续跑检查: 对每个 slug, 若最新版 proposal 已存在但没有 `<review ...>` 块, 先派一次 `proposal-reviewer` 补 review (同样受 `{parallelism}` 限制). review 补完后若尚未满足终止条件, 跑一次 proposal deep-lit (见下方"运行一次 proposal deep-lit"), 让下一轮 refiner 能读到新文献上下文.

C. proposal refine loop, 对所有 slug 并行执行 proposal-refiner -> proposal-reviewer -> deep-lit 循环:
   - 循环主体: 先调用 `proposal-refiner` subagent, 再调用 `proposal-reviewer` subagent. 若尚未满足终止条件, 跑一次 proposal deep-lit, 然后进入下一轮 refiner.
   - 每个 slug 的终止条件: `current_version >= 3` 或最新版 proposal 的 `<review>` 块 `## Verdict` 字段 == `READY`
   - 每个 slug 执行完一次 refine-review(+deep-lit) loop 都要 git add -v / commit / push, 注意不要把不属于自己的更改带进去 (ideas/proposals.xml 是例外, 因为是共享文件, 所以你可以为了 commit 自己的带入别人的更改), commit msg 模板: "mmdd proposal refine: {slug} (v{N}, verdict: {verdict})"
   - reviewer 有时候会中道崩殂, 每个 reviewer 完成后你要检查最新版 proposal 文件最后有 `<review ...>` 块并且 proposals.xml 对应条目的 score 已更新. 如果没有完成, 就 resume 原 agent 让它继续干.

循环结束后, 向用户汇总 subagents 抱怨的各种问题.

## Refinery Skills

每次 dispatch 前，根据子代理角色从 `skills_aris/` 中选 3-5 个最相关的 refinery mindset，将完整路径列表拼入 dispatch message 的 `{MANDATORY_SKILLS_LIST}`。

## 派发 subagent 时的提示词

- `proposal-refiner`: 如果 proposal 完全不存在用 `"Write proposal for idea {slug}. CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}。你必须先 Read 以下 refinery mindset：{MANDATORY_SKILLS_LIST}。此外你可以通过 Skill 工具加载 aris catalog 自行增量。"`, 否则用 `"Revise the latest proposal for idea {slug}. CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}。你必须先 Read 以下 refinery mindset：{MANDATORY_SKILLS_LIST}。此外你可以通过 Skill 工具加载 aris catalog 自行增量。"`
- `proposal-reviewer`: `"Review the latest proposal for idea {slug}. CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}。你必须先 Read 以下 refinery mindset：{MANDATORY_SKILLS_LIST}。此外你可以通过 Skill 工具加载 aris catalog 自行增量。"`

## 运行一次 proposal deep-lit

proposal deep-lit 用 deep-lit-tick 的 idea scope。对 slug `{slug}`:
- 读取最新版 `ideas/{slug}.v*.md` 的 frontmatter `topic:` 字段, 取 basename 并去掉 `.md` 得到 topic slug.
- 在 agon-artifact 目录下按 `lit_tick_model` 和 dispatch_manual 启动完整 tick。这里 `AGENT_PROMPT` 指向 command 文件而不是 agents 文件；paper reader 的模型由 `deep-lit-tick` 自己读取和控制。

```bash
AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/commands/deep-lit-tick.md"
TASK_PROMPT="完整执行 deep-lit-tick: --scope idea <topic_slug> --idea {slug}。跑到内部 B4 饱和为止。CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}"
```

- 读 `$OUT` 拿 C 段汇总 + D 段 verdict + 本次新增论文清单, 然后 `rm "$OUT"`.
- 进程异常退出或 `$OUT` 不完整: 直接重跑同一条命令 (deep-lit 内部用 wiki / JSON 缓存做 resume, 已读论文不会重读).
- idea scope 的 deep-lit 会写对应 idea 文件; 不直接写 proposal. 下一轮 `proposal-refiner` 通过读取最新版 idea 和最新版 proposal 消费这些文献发现.

注意:
- 当前版本 = `current_version` in `ideas/proposals.xml`
- verdict = 最新版 proposal `<review>` 块里 `## Verdict` 字段的取值 (常见: `READY` / `REVISE` / 等)
- 并发限制: 同时运行的 subagent / deep-lit 进程不超过 {parallelism} 个. 需要并行调度时, 完成一个再补一个, 用 sliding window 的方式推进.
- refiner_model: 如果 refiner_model 是 `claude` 则照原流程调用 `proposal-refiner` subagent. 如果 refiner_model 是 `codex`, 则遵从如下流程使用 codex 完成 refiner 工作:
   - 在 agon-artifact 目录下按 dispatch_manual 的 codex 模板执行; `TASK_PROMPT` 使用当前调用点里 `proposal-refiner` 的 prompt.
   - 调用返回后读 `$OUT` 当 report, 然后 `rm "$OUT"` 避免 /tmp 堆积.
- reviewer_model: 控制 `proposal-reviewer` 使用的模型.
   - `reviewer_model = "claude"` (默认): 照原流程调用 `proposal-reviewer` subagent. 如果 Claude quota/rate-limit 失败, 自动 fallback 到下一个.
   - `reviewer_model = "deepseek"`: 在 agon-artifact 目录下按 dispatch_manual 的 claude-* 模板执行, 命令名用 `claude-ds`; `TASK_PROMPT` 使用当前调用点里 `proposal-reviewer` 的 prompt.
- lit_tick_model: 控制 `deep-lit-tick` dispatcher 使用的模型.
   - `lit_tick_model = "deepseek"` (默认): 按 dispatch_manual 的 claude-* 模板执行, 命令名用 `claude-ds`.
   - `lit_tick_model = "claude"`: 按 dispatch_manual 的 claude 模板执行.
   - `lit_tick_model = "codex"`: 按 dispatch_manual 的 codex 模板执行.
- 如果 subagent 中途退出, 用 SendMessage resume 原 agent 继续.

## Rules

- Do NOT reason about research content, novelty, or idea quality.
- Pass only the specified context strings to each agent, nothing else.
- 如果 subagent 失败, 通过日志调查原因之后重试; 如果连续失败 3 次以上, 询问用户怎么办. 严格禁止你接手 subagent 的工作: 你没有足够上下文, 不能取代 subagent.
- 如果有任何 agent/codex 抱怨"看不到 CLAUDE_PLUGIN_ROOT 是啥", 立即停下来报告给我
