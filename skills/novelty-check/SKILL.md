---
name: novelty-check
description: Use when checking novelty of a research idea or proposal. Extract core claims, do multi-source arxiv / Scholar / S2 search, grade each claim HIGH/MEDIUM/LOW. 基本就是 ARIS novelty-check skill, 但去掉了 cross-model verification 和 report schema.
---

<novelty-check>

这是一个挑剔的research reviewer系统性检查一个工作的核心贡献是否新颖的流程.

## 流程

### 1. Extract Core Claims

Identify 3-5 core technical claims that would need to be novel:

- What is the method?
- What problem does it solve?
- What is the mechanism?
- What makes it different from obvious baselines?

### 2. Multi-Source Literature Search

For each core claim, search broadly:

- sources: arXiv / Google Scholar / Semantic Scholar
- Use specific technical terms from the claim
- Try at least 3 different query formulations per claim
- Always check the most recent 6 months of arXiv — the field moves fast
- 顶会近期核查: 明确看最近的 ICLR, NeurIPS, ICML 等会议的相关子领域的 proceedings 和 accepted papers

### 3. 判断 novelty

对每个 claim 打一个 novelty 等级:

- HIGH: 没查到实质重叠的工作, claim 是原创机制
- MEDIUM: 存在相关工作, 但 application / scope / mechanism 有明显区别
- LOW: 已有高度相似工作, 或本质上是 "Apply X to Y" 且 application 没揭示意外洞见

## Key Rules

- Be brutally honest — false novelty claims waste months of research time.
- "Applying X to Y" is NOT novel unless the application reveals surprising insights.
- Check both the method AND the experimental setting for novelty.
- If the method is not novel but the FINDING would be, say so explicitly.
- web search / metadata 摘要只是线索, 不是证据. 所有进入报告的论文引用必须用 arxiv tool / arxiv skill 下载并阅读 tex/full text 核验.
- 最终报告 novelty check 部分的字数在 200-300 words 左右.

## 不要在此停下

novelty check 只是某个 reviewer workflow 的第 1 步. 产出 200-300 字 novelty 报告后, **必须返回父 agent 继续做**: Quality Review → codex second opinion → 写 `<review>` 块 → 更新 `ideas.xml` / `proposals.xml`. 不要把 novelty check 的报告当成最终交付物而 end_turn.

</novelty-check>
