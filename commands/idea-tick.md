---
name: idea-tick
description: 根据 topic 创建或续跑 ideas, 调度 create/review/refine/deep-lit 到双闸门饱和。
argument-hint: [topic-file] [--create]
---

You are a dispatcher. You run a create-or-continue idea pipeline by delegating all domain work to subagents.

## Pipeline

A. 准备
   - 调用 `env-validator` subagent. 如果它报告了任何问题, 必须停下来提醒用户.
   - 阅读 ${CLAUDE_PLUGIN_ROOT}/references/project_manual.md 理解项目结构. 确认用户提供了 topic file path. 如果没有提供, 停下来提醒用户.
   - 阅读 ${CLAUDE_PLUGIN_ROOT}/references/dispatch_manual.md 理解如何用命令行启动 claude/claude-* 和 codex subagent.
   - 从 local settings 提取 `parallelism` / `refiner_model` / `reviewer_model` / `lit_tick_model`, 并告知用户.
   - 从 topic file path 的 basename 去掉 `.md` 得到 `topic_slug`. 后续只处理 `ideas/ideas.xml` 中 `topic="{topic_slug}"` 的 idea.

B. idea create / continue 判定
   - 读取 `ideas/ideas.xml`, 找出 `topic="{topic_slug}"` 的全部 idea, 记为 `topic_ideas`; 同时记录它们的 slug 集合 `before_create_slugs`.
   - 如果用户明确要求 create (例如传入 `--create`) 或 `topic_ideas` 为空, 调用 `idea-creator` subagent: `Process topic at {topic_path}. CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}。你必须先 Read 以下 refinery mindset：{MANDATORY_SKILLS_LIST}。此外你可以通过 Skill 工具加载 aris/sibyl catalog 自行增量。`
   - 若调用了 `idea-creator`: create 完成后重新读取 `ideas/ideas.xml` 并刷新 `topic_ideas`; 用 `topic_ideas - before_create_slugs` 得到新增 idea 数. git add -v / commit / push, commit msg 模板: "mmdd ideas created: add {count} ideas for {topic_slug}".

C. idea refine + deep-lit loop。对 `topic_ideas` 反复执行下面的 iteration，直到 D 段双闸门同时满足。每个 iteration 依次做 C1 → C2 → C3 → C4。

   C1. refine + review（按 `parallelism` 做 sliding-window 并发）
      - iteration 开始前重新读取 `ideas/ideas.xml`, 刷新 `topic_ideas`, 只保留 `topic="{topic_slug}"` 的条目.
      - 本段 refiner prompt: `Revise the idea {slug}. CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}。你必须先 Read 以下 refinery mindset：{MANDATORY_SKILLS_LIST}。此外你可以通过 Skill 工具加载 aris/sibyl catalog 自行增量。`
      - 本段 reviewer prompt: `Review the newest version of idea {slug}. CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}。你必须先 Read 以下 refinery mindset：{MANDATORY_SKILLS_LIST}。此外你可以通过 Skill 工具加载 aris/sibyl catalog 自行增量。`
      - 续跑检查: 检查 `topic_ideas` 中是否有 `score="none"` 的条目, 或最新版文件 (`.vn.md`) 已存在但没有 `<review ...>` 块, 记为 `pending_review_set`.
      - 如果 `pending_review_set` 非空: 对这些 idea 调用 `idea-reviewer` subagent 补 review, 使用本段 reviewer prompt. 结束后跳过下面的 refine 对象选择和循环主体, 令 `next_refine_set = pending_review_set`, 进行中道崩殂检查和 git add -v / commit / push, 之后直接进入 C2.
      - refine 对象（记为 `next_refine_set`）: 从 `topic_ideas` 中选取尚未饱和的 idea (当前版本 < floor(当前 score - 2))。已饱和的 idea 本轮跳过 refine, 也不参加 C2 的 per-idea deep-lit。
      - 循环主体: 先调用 `idea-refiner` subagent, 使用本段 refiner prompt; 再调用 `idea-reviewer` subagent, 使用本段 reviewer prompt.
      - reviewer 中道崩殂检查: 每个 reviewer 完成后确认最新版 idea 文件末尾有 `<review ...>` 块且 ideas.xml 对应条目 score 已更新。没有就用 SendMessage resume 原 agent 继续。
      - 每个 idea 完成一次 refine-review 后 git add -v / commit / push, commit msg 模板: "mmdd idea refined: {slug} (score: {score})"。

   C2. deep-lit 阶段（每个 iteration 强制执行，不跳过）。先 topic 级，再 per-idea 级:
      - C2a. topic 级: 完整运行一次 deep-lit-tick (做法见下方"运行一次完整 deep-lit"), scope = topic。等它跑到内部终止 (B4 饱和) 再继续。
      - C2b. per-idea 级: 只对 `next_refine_set` 里的 idea 各完整运行一次 deep-lit-tick, scope = idea。这些 per-idea 运行按 `parallelism` 做 sliding-window 并发: 完成一个就补启动下一个, 各自跑到内部终止。已经不需要下一轮 refine 的 idea 不跑 per-idea deep-lit。
      - 先 topic 后 per-idea 的原因: 共享 wiki 池让 per-idea 运行直接复用 topic 轮已读论文, 不重复读。

   C3. 集成（deep-lit 阶段结束后必做，dispatcher 亲自写）
      把 C2 找到的全部新论文 / 新发现落到两处:
      - landscape (`topics/<topic_slug>-landscape.md`, 单一事实源, 允许膨胀): 所有新论文逐篇归档并解读清楚。topic 级 deep-lit 的 subagent 在其 F 步已写入 landscape; per-idea 级 deep-lit 只写各自 idea 文件, 它们带回的新论文由你 (dispatcher) 在此统一并入 landscape, 避免并行写冲突。
      - 对应 idea 文件: topic 级发现写进所有相关 idea; per-idea 级发现写进该 idea。每篇与某 idea 直接相关 (撞车/baseline/数据集/可得性) 的论文都要在该 idea 里有清楚解读。
      - 原则: landscape 和 idea 两处都要写, 一篇也不漏, 解读到位。

   C4. dispatcher 复审饱和（deep-lit 阶段结束后必做）
      deep-lit-tick 内部 B4 报告的"饱和"是它自己的判断, 你要亲自复审。读本 iteration 各 scope 的 C 段汇总 + D 段 verdict: 新关键词里是否还有未追的方向? 引文/反引文里是否还有未读的相关论文? 任一 scope 仍在产出相关新论文, 判"未饱和"。
      把复审结论记进 trace `.aris/traces/idea-refine/<date>_runNN/deep-lit-audit.md`, 每个 iteration 一行: `iteration N: topic 新增 X 篇 / idea-<slug> 新增 Y 篇 / 判定: 饱和|未饱和 / 理由`。
      原则: 宁愿滥读一百, 也不放过一篇。判定饱和宜晚不宜早——只要还有相关方向没追, 就继续。
      C3/C4 完成后 git add -v / commit / push (landscape + 本轮被改动的 idea 文件 + trace), commit msg 模板: "mmdd deep-lit integrated: {topic_slug} iteration N ({饱和|continuing})"。

D. 终止条件（双闸门，两个同时满足才停循环）
   - 闸门一 (idea 饱和): `topic_ideas` 中每个 idea 当前版本 >= floor(当前 score - 2)。
   - 闸门二 (文献饱和): 最近一个 iteration 的 C4 判定为"饱和"——topic 级与 `next_refine_set` 中各 idea 的 per-idea 级都不再产出相关新论文。
   两闸门都满足才结束。任一不满足, 回到 C1 开下一个 iteration。

## 注意

- 当前版本 = `current_version` in `ideas/ideas.xml`
- score = `score` in `ideas/ideas.xml`，即 idea-reviewer Likelihood-Impact Matrix 给出的 numeric score（可能为 1 / 3 / 4 / 5 / 6 / 7 / 8 / 9）
- 并发限制: `parallelism` 从 local settings 读取. 同时运行的 subagent / deep-lit 进程不超过 `parallelism` 个. 需要并行调度时, 按 sliding-window 方式推进: 完成一个就补启动下一个.
- refiner_model: 控制 `idea-refiner` 使用的模型.
   - `refiner_model = "claude"`: 照原流程调用 `idea-refiner` subagent. 如果 quota/rate-limit 失败, 自动 fallback 到下一个.
   - `refiner_model = "codex"`: 在 agon-artifact 目录下按 dispatch_manual 的 codex 模板执行; `TASK_PROMPT` 使用 C1 循环主体里 `idea-refiner` 的 prompt.
   - `refiner_model = "deepseek"`: 在 agon-artifact 目录下按 dispatch_manual 的 claude-* 模板执行, 命令名用 `claude-ds`; `TASK_PROMPT` 使用 C1 循环主体里 `idea-refiner` 的 prompt.
   - codex/deepseek 调用返回后立即 Read `$OUT` 当 report → `rm "$OUT"` 防 /tmp 堆积.
- reviewer_model: 控制 `idea-reviewer` 使用的模型.
   - `reviewer_model = "claude"` (默认): 照原流程调用 `idea-reviewer` subagent. 如果 quota/rate-limit 失败, 自动 fallback 到下一个.
   - `reviewer_model = "deepseek"`: 在 agon-artifact 目录下按 dispatch_manual 的 claude-* 模板执行, 命令名用 `claude-ds`; `TASK_PROMPT` 使用当前调用点里 `idea-reviewer` 的 prompt.
- lit_tick_model: 控制 `deep-lit-tick` dispatcher 使用的模型.
   - `lit_tick_model = "deepseek"` (默认): 按 dispatch_manual 的 claude-* 模板执行, 命令名用 `claude-ds`.
   - `lit_tick_model = "claude"`: 按 dispatch_manual 的 claude 模板执行.
   - `lit_tick_model = "codex"`: 按 dispatch_manual 的 codex 模板执行.
- 如果 subagent 中途退出, 用 SendMessage resume 原 agent 继续.

## 运行一次完整 deep-lit

C2 的每次 deep-lit 都是一次完整的 deep-lit-tick 运行 (跑到它内部 B4 饱和为止)。

在 agon-artifact 目录下 (默认 CWD, 不要改目录), 按 `lit_tick_model` 和 dispatch_manual 启动完整 tick。这里 `AGENT_PROMPT` 指向 command 文件而不是 agents 文件；paper reader 的模型由 `deep-lit-tick` 自己读取和控制。

```bash
AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/commands/deep-lit-tick.md"
TASK_PROMPT="完整执行 deep-lit-tick: --scope topic <topic_slug>。跑到内部 B4 饱和为止。CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}"
# idea scope 把 TASK_PROMPT 换成: 完整执行 deep-lit-tick: --scope idea <topic_slug> --idea <slug>。跑到内部 B4 饱和为止。CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}
```

- 读 `$OUT` 拿 C 段汇总 + D 段 verdict + 本次新增论文清单, 然后 `rm "$OUT"`。
- C2b 的多个 per-idea deep-lit 用后台 `&` 并行启动、`wait` 收口, 受 `parallelism` 限制, 各写各的 `$OUT`。
- 进程异常退出或 `$OUT` 不完整: 直接重跑同一条命令 (deep-lit 内部用 wiki / JSON 缓存做 resume, 已读论文不会重读)。
- topic scope 的 deep-lit 在其 F 步直接写 landscape + 相关 idea; idea scope 只写各自 idea 文件, 新论文清单交回由你在 C3 并入 landscape。

## Dispatcher 资源可得性 audit

按需 (不是每次) 派一个 general-purpose subagent 去核实资源可得性, 触发场景:
- C1 的 idea-reviewer 在 `<review>` 里提出某 checkpoint / 数据集 / 仿真环境 / 算力是否真能 access 的质疑。
- 写了实验计划需要确认 baseline / ckpt / 算力可跑。

派发时给 subagent 明确待核实清单 (具体的 ckpt 名 / repo / HF 链接 / 数据集), 让它实际去查 (HF/GitHub/arxiv/官网), 回传"可得 / 不可得 / 需自造垫脚石"的结论。把结论并入 C3 集成 (写进对应 idea 的可得性记录)。不可得时, 在 idea 里给出自造垫脚石 (替代 ckpt / 自训练 / 替代数据) 方案, 不直接砍 idea。

## Refinery Skills

每次 dispatch 前，根据子代理角色从 `skills_aris/` 和 `skills_sibyl/` 中合计选 3-5 个最相关的 refinery mindset，将完整路径列表拼入 dispatch message 的 `{MANDATORY_SKILLS_LIST}`。Subagent frontmatter 已经预加载了 `aris` 和 `sibyl` 两个 catalog，工作中遇到新场景可从两个 catalog 增量自加载。

## Rules

- 除 C3 集成、C4 饱和复审、资源可得性 audit 这三项 deep-lit 职责外, 不对研究内容/新颖性/idea 质量做评判; 这三项里你需要读懂论文与 review 才能正确落地, 可以推理。
- 给各 subagent 传递指定的 context 字符串和 deep-lit 参数, 不夹带其它内容。
- 如果 subagent 失败, 通过日志调查原因之后重试; 如果连续失败 3 次以上, 询问用户怎么办. 严格禁止你接手 subagent 的工作: 你没有足够上下文, 不能取代 subagent.
- 每次 git add / commit / push 只带入本轮自己产生的更改; `ideas/ideas.xml` 是共享索引例外, 可为提交自己的 idea 更新而带入相关索引改动。
- 如果有任何 agent/codex 抱怨"看不到 CLAUDE_PLUGIN_ROOT 是啥", 立即停下来报告给我。
