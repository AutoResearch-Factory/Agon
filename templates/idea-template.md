<!-- 书写报告使用中文 -->
---
topic: topics/mmdd-slug.md
landscape: topics/mmdd-slug-landscape.md
workspace: workspace/slug/
---

- One-sentence summary: [what this idea is, to refiner: 这句话是记载"这个 idea 当前的一句话概括, 不要写成相对于上个版本的更改!"]
- Hypothesis: [what you expect to find and why]
- Expected outcome: [what success/failure looks like; include the cheapest falsifying signal in one clause]
- Contribution type: [from {empirical-finding, method, theory, diagnostic, application, benchmark}; 可同时属于多种, 用 + 连接. 若 topic 声明了 `preferred-contribution-types`, 此处填的类型集合必须是 preference 的子集]
- Risk: LOW / MEDIUM / HIGH
- Estimated effort:
  - Compute: [GPU-hours estimate]
  - Data: available / needs collection / needs annotation
  - Implementation: days / weeks
- Novelty quick-check: [closest 1-2 prior works from First-Pass Filtering searches + one-sentence differentiation. idea-reviewer will run a deep novelty check later.]
- Strongest objection: [the strongest counterargument a reviewer would raise, one sentence]
- Why we should do this: [1-2 sentences]
- Pilot:
  - Setup: [one sentence — data subset / model / epochs / single seed]
  - Metric: [metric definition + success threshold, e.g., "if metric improves by > 1%, signal is positive"]
  - Result: [measured number]
  - Signal: POSITIVE / WEAK / NEGATIVE / SKIPPED

<!-- 注意: 不要将 <added-on-refine> 这个 xml tag 写到报告中, 它只是模板标记, 用于指示 refine 阶段新增的字段 -->
<added-on-refine>
- Claims and Claims matrix: [paper 级 claims + 不同 outcome 下允许的 claim 强度]
- Narrative: [如何讲成 paper 故事, 1-2 sentences]
- Experiments: [扩展实验集, 留到 proposal 阶段细化]
- Assets status: [一句话说明数据/模型是否可得; 路径细节只写 `workspace/{slug}/data/MANIFEST.md`]
</added-on-refine>
