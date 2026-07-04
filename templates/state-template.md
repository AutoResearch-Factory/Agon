---
phase: needs_scientist                # dispatcher 状态机: needs_scientist | coding_and_running | needs_auditor | needs_reviewer | needs_litfeed | done
version: 0                            # 当前送审次数, reviewer 维护
iteration: 0                          # 当前迭代号, scientist 维护
route: ""                             # 当前技术路线 (同 git branch)
git_branch: main                      # main | route/<name>
gpu_dollars_equivalent: 0.00          # 等效美元, coder 维护
latest_audit: ""                      # 最新 auditor 报告路径, auditor 维护
audit_verdict: ""                     # WARN | CRITICAL | BLOCKER, auditor 维护
---

<!--
========================================================================================
STATE.md —— 实验最高级别状态文件
========================================================================================

读者：人类用户（做战略决策）+ agent（写代码跑实验）。

原则：
1. 新人友好：你的默认读者是第一天来的实习生——聪明但什么都不知道。写每一段之前，先对自己说一遍"我们到底在干什么，为什么"。比喻、对比、流程图/示意图、"简单来说"比术语堆砌好 100 倍。
2. 言简意赅：重要信息只在最合适的地方出现一次，不反复讲，不遗漏。
3. 自包含：读完这一个文件 → 能指导下一步实验 + 能直接重写成一篇可投稿的论文。
4. 两层结构：前半部分给人读（战略），后半部分给 agent 读（执行）。没有中间层。

Method 段在 proposal.md，本文档不重复。历史在 experiment-log.md / git。
使用中文书写正文。Thinking 用 English。
-->

---

# 项目名：xxx

> 一句话：研究什么，核心发现是什么。

## 1. 背景

### 1.1 领域常识

<!-- 用最白的话。2-3 段，每段 ≤5 句。新人读完就知道这个领域在干什么。 -->

### 1.2 核心概念

<!-- 只列本项目用到的，每个一句话。 -->

| 概念 | 一句话解释 |
|------|-----------|
| ... | ... |

### 1.3 研究问题

<!-- 研究问题（1 句）→ 直觉预期（1 句）→ 实际发现（1 句）。-->

## 2. 实验全景

### 2.1 实验流程

<!-- mermaid flowchart：输入 → 处理 → 输出。一张图说清整个实验。
     节点粒度：每个语义阶段（数据 / Prompt / 推理 / 后处理 / 指标）一个节点，分支项放进节点内容里用 bullet 列举，不要每个分支拆成独立节点。
     保持简短、可执行、可审计。 -->

### 2.2 核心指标

| 指标 | 含义 | 计算 |
|------|------|------|
| ... | ... | ... |

### 2.3 实验矩阵

<!-- 所有实验一行一个。状态用 ✅⚠️❌。 -->

| 实验 | 研究问题 | 模型 | 数据 | 状态 | 核心结果 |
|------|---------|------|------|------|---------|

## 3. 算法与代码

### 3.1 算法本质

<!-- 每个核心算法一段，≤5 句。输入 → 做了什么 → 输出。 -->

### 3.2 代码地图

<!-- "想知道 X → 打开 Y → 看 Z"。不是文件列表。 -->

| 想知道... | 文件 | 函数/类 |
|----------|------|--------|
| ... | `src/...` | `xxx()` |

### 3.3 计算量

<!-- 瓶颈在哪，一个样本多久，完整实验多久。 -->

## 4. 当前结果

### 4.1 已完成实验

| 实验 | 记录数 | 关键数字 | 结论 |
|------|--------|---------|------|

### 4.2 关键警告

<!-- 什么东西不对劲，需要在论文里处理或加实验。 -->

### 4.3 Claims 速查

<!-- 我们要证明什么、证据是什么、证据够不够。一句话一行。 -->

| 要证明的事 | 证据 | 强度 |
|-----------|------|------|
| ... | ... | 够/还不够 |

## 5. 战略决策（人类决定）

<!--
⚠️ 这一章只有人类用户能决定。§5 只能由 experiment-tick dispatcher 在得到人类明确回复后逐字写入。
dispatcher 只能记录用户原文, 不得总结、翻译、扩写或替用户下结论。
scientist/auditor/coder/reviewer 以及其他 agent 不得新增、删除、改写、重排、总结或代写 §5。
这是人类用户的最高指令区。写在这里的任何实验方向、技术判断、优先级排序, agent 必须无条件执行。

Agent 规则：
- auditor：每次审计第一项检查——§5 里的指令被执行了吗？没执行 → BLOCKER。
- scientist：每轮读 §5 → 逐条确认状态 → 在 plan 里体现。
- coder：读 §5 → 确认自己要实现的东西和人类指令一致。
- dispatcher：除记录人类明确回复到 §5 外, 不解释、不改写 §5。平时只按 phase 路由。
-->

<!-- 示例：
- 最高优先：把 T2（弱模型 vs π0.5）的 6 个指标全部做到 LB>0。per_suite_loo joint 是泛化能力的 gold standard, 不能牺牲。
- 扫表先扫完。模型×任务全矩阵 4-seed strict success 不做完不准训 router。
- 优先用 Transformer encoder over candidates, 不用 MLP pointwise。
- 不准用 BCa bootstrap。不准 cherry-pick seed。不准做 cross-route ensemble。
- 加入 qwen-vla 和 lingbot-vla。找不到 ckpt 就诚实标记 missing。
- Claim 永远不许降级!
- 光证明 idea work 不够, 要用这个 pipeline 在一个真实的、以前 FEX 高维搞不定的 PDE 上 lift 成功，解一个能令人震惊的、以前解决不了的问题。外部 baseline 必须够强，不许挑软柿子对比。
-->

- ...

## 6. 下一步行动

| 优先级 | 行动 | deadline | 完成标志 |
|--------|------|---------|---------|
| P0 | ... | ... | ... |

### 6.1 论文框架速览

<!-- 论文打算分几节，每节写什么。3-5 行，人话。 -->

---

## 自检清单（提交前必做，7/7 通过才能 commit）

1. 闭眼 30 秒，一句话说出项目在研究什么、核心发现是什么。说不出来 → §1 没写好
2. 搜任一术语在 §1 首次出现处，有没有用一句话解释它是什么。没有 → 补
3. §1.1 超过 15 行？→ 你在写综述，删
4. 遮住核心概念表，任选一词能用大白话解释给外行吗？不能 → 删掉这个词或补解释
5. 任选 §2-§6 连续 3 句话，实习生读到会问"这跟我有什么关系"？会 → 重写
6. 任选一段删掉，实习生仍能理解项目？能 → 删掉
7. `wc -l STATE.md` > 450？→ 删到 ≤450，不许挪到 A 段绕过

# Agent 执行层

<!--
以下给 agent 读。人不需要逐行看但应能看懂。
coder worker pool 按 A1 写代码 → 部署 → 维护 A3 Runs 表 → crash 时写 ad-hoc 诊断段。
-->

## A0. Audit Response

<!--
scientist 维护。每轮 scientist 必须逐条回应 latest_audit 中的 BLOCKER / CRITICAL / MAJOR。
不要改 auditor report；只在这里写 response / action / evidence。
下一轮 auditor 会检查这些回应是否充分，以及 coder 是否真的落实。
-->

| audit issue | scientist response | action/evidence | status |
|-------------|--------------------|-----------------|--------|

## A1. Experiments-to-do

<!-- scientist 维护。以 Task Group 组织——dispatcher 读 group + server health 后决定每个 group 拆几个 coder。
     can_split: true  → group 内 run 互相独立，dispatcher 可视情况拆给多个 coder
     can_split: false → group 内 run 有依赖/共享资源，必须同一个 coder 顺序跑
     depends_on:      → 这个 group 必须等另一个 group 跑完
     不想操心细节时，每个 run 放一个单 run group 就是退化情况，dispatcher 自己处理。 -->

### Task Group A: [一句话描述]

- runs: [run-a1, run-a2]
- can_split: true
- depends_on: none
- priority: P0

### Run: [run-name]

<!-- scientist 写 Plan，coder 执行。每个 run 必须写明所属 Task Group——不然 dispatcher 无法关联。-->

- Task Group: A/B/C/...（必填）
- Advances: 回答什么问题，对应 §4 的哪个 claim
- Config: 命令行参数
- Input assets: data/checkpoint ids or exact paths from `data/MANIFEST.md`
- Expected outputs: `results/<run-name>/manifest.json`, key result files/logs, remote-only assets if any
- Priority: MUST-RUN / NICE-TO-HAVE
- Compute cost: GPU-hours 估算
- Server: primary + fallback
- remote_dir:
- Success criterion: 硬判据（事后不改）
- Failure interpretation: 如果失败/空，说明什么
- Risk: OOM / 数据 / 兼容性

### 代码改动

<!-- 跨所有 Task Group 的代码改动写在这里。per-run 的改动写在对应 Run 的 Config/Input assets 字段里。-->

## A2. 实验详细规格

<!-- 每个实验的完整技术规格。agent 写代码时的参考。-->

### E?: [Name]

- 模型 / 数据 / 超参 / seeds
- 对比系统（baseline / ablation / variant）
- 输入资产、输出文件与 source 路径
- 结果（关键数字，带 source）

## A3. Runs

<!-- scientist 初始化 run 行，coder worker pool 维护其余字段。collected 表示证据链已同步/登记完整, 整合进 §4 后删行。-->

| run | server | remote_dir | launched_at | session_id | crash_count | phase |
|-----|--------|------------|-------------|------------|-------------|-------|

字段责任：

| 字段 | scientist 初始化 | coder worker pool 维护 |
|------|------------------|------------|
| `run` | ✓ | — |
| `server` | ✓ | 切 server 时改 |
| `remote_dir` | ✓ | 切 server 时改 |
| `launched_at` | 空 | ✓ |
| `session_id` | 空 | ✓ |
| `crash_count` | `0` | ✓ crash +=1 |

Per-run phase: `needs_impl` → `queued` → `running` → `needs_sync` → `collected`（或 `needs_fix` → `queued`）

## A4. 环境

| 服务器 | GPU | 显存 | 远程路径 | HF_HOME | 注意 |
|--------|-----|------|---------|---------|------|

```bash
# 本地 dry-run
uv run python scripts/xxx.py --config conf/xxx.yaml --dry-run

# lint + test
uv run ruff check . && uv run pytest
```

## A5. 运行历史

| 时间 | 实验 | 事件 | 备注 |
|------|------|------|------|

## A6. 已知问题与修复

| 问题 | 根因 | 修复 | 状态 |
|------|------|------|------|

<!--
ad-hoc 诊断段（coder 按需临时 insert，scientist 分析后删除）：

| 段名 | 谁写 | 触发 |
|------|------|------|
| `### 卡点` | coder | crash 判代码问题或无法推进。root-cause-first：已确认事实 / 已排除假设 / 最可能根因 / 最小下一步 / 禁用的替代 |
| `### Coder 旁注` | coder | 每次完成代码或扫描后：做了什么 / 困难 / 疑惑 / 对 plan 的建议 |
| `### 疑似调度问题` | 任一 agent | 怀疑 dispatcher 状态机 bug 而非实验 bug |
-->

<review score="X.X" date="YYYY-MM-DD">

由 reviewer 填写。最近一轮评审，旧 review 整体替换不堆叠。

</review>
