---
name: deep-lit-tick
description: 按 scope 运行深度文献循环, 搜索、精读、扩展直到相关论文饱和.
argument-hint: [--scope topic|idea|experiment] [slug] [--idea idea-slug]
---

<env>
- cwd 是 agon-artifact（`topics/` / `ideas/` / `workspace/` 路径相对 cwd）。wiki 位置完全由 `$ARXIV_WIKI_DIR/` 配置。
- `${CLAUDE_PLUGIN_ROOT}` 由 Claude Code plugin 运行时注入，指向 Agon 根目录（含 `agents/` / `commands/` / `skills_aris/` ...）。
- `${ARXIV_CACHE_DIR}` 是机器上共享的 arxiv 缓存目录（`paper_cache.db` + 下载的 tex）。wiki 不从缓存目录、其他环境变量或默认路径推断；必须使用 `$ARXIV_WIKI_DIR` 指定的位置。
- arxiv_tool 路径由 `agon:arxiv-tools` skill 在开工时给出，下文 `uv run arxiv_tool.py ...` 示例省略绝对路径，实跑时按 skill 输出替换。
- 不做启动时阻塞式环境验证；如果外部依赖实际调用失败，报告具体缺失项和继续所需配置。
</env>

You are a dispatcher. You run the deep literature review cycle for a given scope. Your job: search → select → read → wiki → expand → repeat. You never read papers yourself — that is the `deep-lit-reader` agent's job. All literature operations go through arxiv-tool.

<scope>
本 tick 跑在三种 scope 之一, 由参数决定:
- `--scope topic <topic_slug>`: 围绕整个 topic 方向调研。集成时写 landscape + 所有相关 idea。
- `--scope idea <topic_slug> --idea <idea_slug>`: 围绕单个 idea 的具体 method / claim / baseline / 数据集深挖。集成时只写该 idea 文件; 新论文清单交回上层 dispatcher 并入 landscape (避免多个 per-idea 运行并行写 landscape 冲突)。
- `--scope experiment <workspace_slug>`: 服务正在跑的实验, 目标是给当前急需解决的问题找最新工具 / 方法 / 垫脚石 / 实现细节, 同时核对实验有没有撞上别人做过的东西。搜索种子取自实验当前状态 (当前卡点 / 主攻 claim / 正在实现的 method / baseline)。集成时把搜出的全部新文献写进 workspace 的 idea.md (文献总账), 只把命中当前急需问题的解决方案写进 lit-feed.md (inbox)。
三种 scope 共用 `$ARXIV_WIKI_DIR` 指定的 wiki 池, 不重复读已读论文。下文凡涉及 scope 差异处会标注 [topic] / [idea] / [experiment]。
</scope>

<absolute_red_lines>
1. 所有文献搜索、下载、引文查询必须通过 arxiv-tools skill 提供的 `arxiv_tool.py`。禁止编造论文。开工前先用 Skill 工具加载 `agon:arxiv-tools` 取本机绝对路径。
2. B3 选出的每一篇论文都必须派 agent 读。选了几篇就派几个 agent。不许跳过。
3. 每个 `deep-lit-reader` reader 按 local settings 的 `lit_reader_model` 和 dispatch_manual 派发；Claude Bash tool 本身必须前台运行，不得设置 `run_in_background: true`。如需并行，用同一个前台 Bash 命令内部 `&` 启动多个 reader 并 `wait` 收口。
4. 结果从 `/tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json` 收集。
5. B7 对每篇 wiki_written 必须跑 `references` + `cited` + author-search + title-term-search 四项反向扩展, 不是 advisory。跳过任一项视为 tick 失败。
6. E 段 commit 前必须跑自检脚本验证 wiki 真存在 + 反向扩展调用数达标, 不通过视为 tick 失败。
</absolute_red_lines>

## A. 准备

### A1. 读取配置

阅读 ${CLAUDE_PLUGIN_ROOT}/references/dispatch_manual.md 理解如何用命令行启动 claude/claude-* 和 codex subagent。
读取 local settings: 优先用 `.settings.toml`, 不存在则用 `.settings.example.toml`; 提取 `lit_reader_model` 并告知用户。

### A2. 读取课题上下文

Read（cwd 为 agon-artifact，下同）。

[topic] / [idea] scope 读 topics/ 下的方向文件：
- `topics/<topic_slug>.md`（topic 高层方向）
- `topics/<topic_slug>-landscape.md`（landscape，单一事实源，含已有文献 arxiv_id 清单 + 已确认撞车风险）

[idea] scope 额外读：
- `ideas/<idea_slug>.v<latest>.md`（取版本号最大的那个文件）
- `ideas/<idea_slug>-proposal.v<latest>.md`（如存在）

[experiment] scope 改读 workspace 内的文件（实验阶段的上下文都在 workspace 里），不读 topics/ 与 ideas/：
- `workspace/<workspace_slug>/STATE.md`（**当前急需问题的来源**：`### 卡点` / §A6 已知问题 / 当前主攻 claim / §6 下一步）
- `workspace/<workspace_slug>/idea.md`（含已知文献，作为 already-known；其 frontmatter `topic:` 字段给出 topic_slug，下文 wiki 去重沿用该 topic_slug）
- `workspace/<workspace_slug>/proposal.md`、`workspace/<workspace_slug>/landscape.md`

提取核心 research question、核心 claims、已有参考文献 arxiv_id 清单、已确认的撞车风险，压缩为一段 `<topic_context>`（≤1500 字）。搜索 query 的种子按 scope 取：[idea] 用该 idea 的具体 method / claim / baseline / 数据集；[experiment] 用 STATE.md 里当前急需解决的问题（卡点 / 正在实现的 method / 待对比的 baseline），而非泛 topic 方向。

如果 landscape frontmatter 含 `mandatory_authors:` 列表，单独提取保存供 A4 axis 7 使用。

### A3. 加载已读记录

Bash 检查 wiki 池（`$ARXIV_WIKI_DIR/`）：
```
ls "$ARXIV_WIKI_DIR/"*.md 2>/dev/null
```

对每个 .md，Bash grep 检查是否含 `## Read by: <topic_slug>`。含则将其 arxiv_id 加入 `already_read_ids`。（[experiment] scope 用 A2 从 idea.md frontmatter 取到的 topic_slug 作 key，从而复用 idea 阶段已读的 wiki，不重复读。）

### A4. 生成初始搜索关键词

基于 `<topic_context>`，生成 query，强制覆盖以下 6 个 axes（每 axis ≥ 1 组完整 query，总计 ≥ 6 组）：

| axis | 关键词模板 |
|---|---|
| 方法 | topic 中具体 method / model / 架构词 |
| 应用 | 目标领域 / 任务 / use case |
| 数据 | dataset / benchmark / domain corpus |
| 评估/判断 | judge / soundness / evaluator / pre-execution / first-gate / gatekeeper |
| 失败模式 | failure mode / pitfall / fabrication / optimism bias / hallucination / over-judge |
| 对抗 framing | 对 `<topic_context>` 中每个核心 claim/moat 生成"竞品 attack 这个 claim 会用什么词"的反向 query |

**额外 axis 7（mandatory_authors 扫盘，可选）**：如果 landscape frontmatter 有 `mandatory_authors: [name1, ...]`，每个 name 生成 1 组 `<name> <topic 核心> 2025 2026` query — 防止该 PI/lab 新作品漏掉（典型 case: missed a lab-specific 2025/2026 benchmark，axis 4 + axis 7 双缺失）。

每组 query 加 `--domain cs --max 15 --year 2025,2026`。后续轮次 A4 不重跑，关键词由 B7 喂入，但若任一 axis 在某轮 B7 派生候选 = 0，下轮 B1 必须显式补一个该 axis 的新 query。

## B. 主循环

```
LOOP:
  B0. Web search 辅助发现（增量补充，非主导）
  B1. arxiv-tool 并行搜索（主导）
  B2. 合并 B0 候选 + B1 结果 → 去重，除 already_read_ids
  B3. 选 6-8 篇最相关（宁多勿漏）
  B4. 选不出 → 终止
  B5. 并行派 agent 读全部选中论文（有几篇派几个 agent）
  B6. 等全部完成，读 /tmp/$USER/*-deep-lit-reader-*-result.json 收集结果
  B7. 从 wiki 中提新关键词
  B8. 加引文/反引文搜索 → 下一轮
```

### B0. Web search 辅助发现（增量）

**定位**：arxiv-tool 是唯一权威文献来源。WebSearch 仅用于发现 arxiv-tool 可能漏掉的候选 arxiv_id（标题变更、社区别名、不在 arXiv/S2/OpenAlex 索引中的情况）。WebSearch 产出的每一条候选都必须过 arxiv-tool `info` 验证，验证不通过的直接丢弃。

**时机**：每轮循环 B1 之前跑一次。首轮必跑，后续轮次如果上轮 web 发现产出少（<2 条有效候选）可以跳过。

用当前活跃关键词拼一组面向 web 的 query（更口语化、更社区导向，与 B1 的学术 query 互补）：
```
"<topic 核心概念> <替代名称/社区叫法> arxiv 2024 2025 2026"
"<topic 核心概念> dataset benchmark survey github"
"<topic 核心概念> <可能漏掉的关键作者/组名>"
```

非 arxiv 索引的 corner-case 来源也必须扫一遍（arxiv 不索引但本领域常发新工作处）：
```
site:github.com trending "<topic 核心概念>" stars:>50 (近 30 天)
site:huggingface.co/datasets OR site:huggingface.co/spaces "<topic 核心概念>" bench
site:openreview.net "<topic 核心概念>"
"awesome-<topic 核心概念>" curated list github
"<topic 核心概念>" workshop NeurIPS OR ICLR OR ICML 2025 2026
```

每组 query → `WebSearch`。从返回结果中提取：
- 直接出现的 arxiv ID（如 `arXiv:2411.17335` 或 `/abs/2411.17335`）
- 论文标题中包含的技术名词，可追问 `WebSearch "<paper title> arxiv"` 确认 ID

收集到候选 arxiv_id 列表后，逐条过筛子：
```bash
uv run arxiv_tool.py info <id>
```
- `info` 成功返回且标题/摘要与 topic 相关 → 保留，记入 `web_candidates`
- `info` 失败或无关 → 丢弃
- 已经在 `already_read_ids` 中 → 丢弃

**重要**：B0 是纯增量。B1 的 arxiv-tool 搜索完全不受影响，独立并行运行。B0 产出为 0 也不阻塞流程。

### B1. arxiv-tool 并行搜索（主导）

每个活跃关键词一个 Bash，全部并行：
```
uv run arxiv_tool.py search "<query>" --domain cs --max 15 --year 2025,2026
```

各搜索间 sleep 3 秒防 rate limit。某搜索返回空或超时 → 跳过继续。

### B2. 汇总 + 去重

合并 B1 的 arxiv-tool 搜索结果 + B0 的 `web_candidates`（已验证过的）。按 arxiv_id 去重。排除 `already_read_ids`。每个结果记：arxiv_id, title, year, abstract（前 300 字）、来源（arxiv-tool / web）。B0 候选与 B1 结果重复时优先保留 B1 的完整 metadata。

### B3. 选择最相关的一批

选择标准（按优先级）：
1. 标题/摘要与 topic 核心 claims 有直接交集
2. 标题含 "survey" / "review" / "benchmark" → **最高优先级**
3. 2026 年新工作
4. S2 citation ≥ 20
5. 在 topic 已知引用列表中出现过

**选 6-8 篇。** 符合标准的不足 6 篇 → 有几篇选几篇。一篇都没有 → 终止。**不确定是否相关 → 选上。宁多勿漏。**

### B4. 终止判断

B3 选出论文数 = 0 → 终止循环。跳到 C。

### B5. 并行派 agent 读全文

对 B3 选出的**每一篇**论文，先检查是否已有结果 JSON（resume）：
```bash
cat /tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json 2>/dev/null | grep -c '"status"' || echo 0
```

如果 JSON 已存在且 status 有效 → 跳过 dispatch（已成功完成过）。

否则按 `lit_reader_model` 和 dispatch_manual 调用 `deep-lit-reader` reader：

```bash
AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/agents/deep-lit-reader.md"
TASK_PROMPT="arxiv_id: <arxiv_id> topic_slug: <topic_slug> CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}"
OUT="/tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>.txt"
```

- `lit_reader_model = "deepseek"` (默认): 用 claude-* 模板，命令名 `claude-ds`.
- `lit_reader_model = "claude"`: 用 claude 模板.
- `lit_reader_model = "codex"`: 用 codex 模板.

B5 派发 reader 后必须等待所有 subagents 返回，并确认每篇论文的 result JSON 存在且非空；缺失、空文件或失败的 reader 必须重试/恢复，全部产物有效后才能继续 B7 或退出 deep-lit-tick。禁止在 reader 仍是 Claude Bash 后台任务时输出完成或退出。

### B6. 收集结果

逐个检查 `/tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json`：

```bash
cat /tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json 2>/dev/null || echo '{"status":"no_result_file"}'
```

对每个结果：
- `wiki_written` → 读 `summary` 字段，加入 `already_read_ids`，收集 `top_related_keywords_for_next_search`
- `already_read` → 加入 `already_read_ids`
- `tex_download_failed` → 记入 errors
- `no_result_file` 或缺少 `summary` → 读 `/tmp/$USER/<topic_slug>-deep-lit-reader-<id>.txt` 尾部 50 行，记入 errors

### B7. 反向扩展（mandatory，违反即 tick 失败）

对 B6 **每篇** wiki_written 论文必须跑四项反向扩展：

```bash
uv run arxiv_tool.py references <id>           # 正引：该 paper 引了谁
uv run arxiv_tool.py cited <id> --source s2    # 反引：谁引了该 paper
```

```
# Author chase: 通讯/一作 在 2024..2026 的全部 autoresearch 相关 paper
uv run arxiv_tool.py search "<author last name> <topic 核心> 2025 2026" --max 10

# Title-term chase: paper 标题里的独特术语直接 search 同名/衍生
uv run arxiv_tool.py search "<unique term from title>" --max 10
```

从全部输出提新 arxiv_id，加入下一轮候选池。再加 B6 收集到的 `top_related_keywords_for_next_search`（去重）。

四项调用数必须 ≥ wiki_written 数 × 4, 不到的在 errors 标 `B7_DISCIPLINE_VIOLATED`, E 段自检会查。

### B8. 继续循环

跳回 B1。

## C. 汇总

循环终止后生成报告。读所有 wiki 文件中 `## Read by: <topic_slug>` 的内容，汇总撞车评估。

```
# Deep Literature Review — <topic_slug> — YYYY-MM-DD

## 循环统计
| 轮次 | 搜索数 | 新论文 | 选中读全文 | Wiki 写入 | 新关键词 |
|------|--------|--------|-----------|----------|---------|
| ...

## 已读论文清单
[每个 wiki 一行：arxiv_id, title, year, 撞车风险, 关键发现]

## 本次新增论文（供上层并入 landscape）
[本次 tick 新读、之前不在 landscape 的每篇一行：arxiv_id | title | year | 一句话解读 | 与哪个 claim/baseline 相关]

## 撞车风险评估
[每个核心 claim 一行：是否被覆盖、最接近的已有工作]

## 可用新工具/方法

## Errors
```

## D. 终止条件判断

```
<verdict>
核心 claims 逐一评估：
- Claim 1: [被覆盖/未被覆盖] [证据]
...
总体：≥1 个 claim 被覆盖 → 建议暂停实验。全未覆盖 → 文献调研通过。
</verdict>
```

## E. Commit + 自检（强制）

自检不通过禁止 commit：

```bash
# 1. 每篇 wiki_written 必须真存在且 ≥ 50 行（wiki 池）
for id in $WIKI_WRITTEN_IDS; do
  test -f "$ARXIV_WIKI_DIR/$id.md" && [ "$(wc -l < "$ARXIV_WIKI_DIR/$id.md")" -ge 50 ] \
    || { echo "FAIL: $ARXIV_WIKI_DIR/$id.md 缺失或 < 50 行"; exit 1; }
done

# 2. B7 反向扩展调用数 ≥ wiki_written × 4 (references + cited + author + title)
[ "$B7_CALLS" -ge $((${#WIKI_WRITTEN_IDS[@]} * 4)) ] \
  || { echo "FAIL: B7 调用 $B7_CALLS < $((${#WIKI_WRITTEN_IDS[@]} * 4)), 违反 red_line #5"; exit 1; }
```

```bash
# wiki 已写入 `$ARXIV_WIKI_DIR` 指定的位置，不提交 wiki 池本身，除非该目录也属于本次明确要提交的产物。
# 只提交 cwd 内的变更（topics/ / ideas/ / workspace/ 等）。
git add -v . && git commit -m "deep-lit <topic_slug>: +N wiki entries across K rounds"
```

## F. 集成（写进 landscape 和 idea）

把本次新读论文逐篇落到位，一篇也不漏，解读到位。

[topic] scope：
- 写 `topics/<topic_slug>-landscape.md`：每篇新论文归档 + 解读（arxiv_id、关键发现、与本 topic claims 的关系、撞车风险）。landscape 允许膨胀，相关论文宁多勿漏。
- 写所有相关 idea 文件（`ideas/<slug>.v<latest>.md`）：把与某 idea 直接相关（撞车 / baseline / 数据集 / 可得性）的发现写进该 idea，每篇解读清楚。

[idea] scope：
- 只写本 scope 的 idea 文件（`ideas/<idea_slug>.v<latest>.md`）：把新发现写进去，解读清楚。
- 不直接写 landscape——本次"新增论文"清单已在 C 段报告里，交回上层 dispatcher 统一并入 landscape，避免多个 per-idea 运行并行写同一文件冲突。

[experiment] scope：写两处，职责不重叠。
- **文献总账** `workspace/<workspace_slug>/idea.md`：本次搜出的**全部**新文献逐篇追加并解读（arxiv_id、关键发现、与本实验哪个 claim/baseline 相关），确保事后能追溯"搜过些什么"，一篇不漏。允许膨胀。
- **inbox** `workspace/<workspace_slug>/lit-feed.md`：只写命中 STATE.md 当前急需问题的条目——每条 = 它解决哪个急需问题 + 搜到的解决方案/工具/垫脚石 + 来源（arxiv_id 与 wiki 路径）。不命中急需问题的论文不进 inbox（它们已在总账里）。写完把 frontmatter `unprocessed` 设为本次新增的 inbox 条目数。inbox 是流动收件箱，由下游 scientist 消费后清空，本步骤不做沉淀。

写完自检：C 段报告里列出的每一篇"新增论文"都已落到对应目标文件（landscape / idea / 总账 idea.md），无遗漏；[experiment] scope 额外确认 inbox 条目都对应 STATE.md 里某个真实的当前急需问题。

## Rules

- 你不读论文。论文阅读是 deep-lit-reader agent 的事。
- 所有搜索走 arxiv-tool，绝对不编造论文。
- B3 选出的论文全部要派 agent，不许跳过任何一篇。
- 搜索间 sleep 3 秒防 rate limit。
- 单个失败不中断整个循环。
