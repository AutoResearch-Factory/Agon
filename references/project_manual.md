# 大规模并行科研系统说明书

这是一个多人协作, 大规模并行科研系统. 请仔细阅读本文件, 了解各种文件的位置和自己的读取权限, 防止与其他人撞车.

## 项目结构

一个研究项目会经历 topic --> landscape summary --> idea --> proposal --> experiment 的阶段.
对应这些步骤, 项目分为 **idea factory** 和 **experiment factory**, 其中
- idea factory 负责 landscape summary, idea, proposal 的生成和优化
- experiment factory 输入是成熟的 proposal, 负责实验和评估目前的结果(包括 baseline 和 ablation)是否能达到顶会标准, 如果达不到, 如何改进并继续

项目的文件结构是

```
/
├── topics/
│   ├── mmdd-slug.md                # mmdd 是日期, 方便追踪时间
│   ├── mmdd-slug-landscape.md      # slug 对应的 landscape summary 报告
│   └── ...
├── ideas/
│   ├── ideas.xml                   # idea metadata 的数据库
│   ├── proposals.xml               # proposal metadata 的数据库
│   ├── slug.v1.md                  # 某个 idea 的第 1 版 (由 idea-creator 创建)
│   ├── slug.vn.md                  # 某个 idea 的第 n 版 (由 idea-refiner 创建)
│   ├── slug-proposal.v1.md         # 某个 idea 的第 1 版 proposal
│   ├── slug-proposal.vn.md         # 某个 idea 的第 n 版 proposal
│   └── ...
└── workspace/                      # 每个文件夹对应一个 proposal 的 experiment 阶段
    ├── workspaces.xml              # workspace metadata 的数据库
    ├── slug/
    │   ├── src/slug/{models,data,training,utils,...}/
    │   ├── conf/                   # hydra config
    │   ├── scripts/{train.py,eval.py,sweep.sh,...}
    │   ├── data/
    │   │   ├── MANIFEST.md         # 每条数据的 metadata
    │   │   └── ...
    │   ├── checkpoints/
    │   ├── results/
    │   ├── tests/
    │   └── README.md
    └── another-slug/
```

## XML Schema

`ideas.xml`:

```xml
<idea slug="example-slug" topic="mmdd-topic-slug" date="YYYY-MM-DD" current_version="1" score="none">
  <one-line>One-sentence summary of the idea.</one-line>
</idea>
```

`proposals.xml`:

```xml
<proposal slug="example-slug" date="YYYY-MM-DD" current_version="1" score="none">
  <one-line>One-sentence summary of the proposal.</one-line>
</proposal>
```

`workspaces.xml`:

```xml
<workspace slug="example-slug">
  <one-line>One-sentence description of the current exp status.</one-line>
</workspace>
```

## 可用外部 skills

<!--为什么要写这个? 因为 subagents 的 context 默认没有任何 skill-->

- agon:arxiv-tools: This skill should be used when the user asks to "search for papers", "get paper info", "download LaTeX source", "generate BibTeX citation", "find citing papers", or provides an arXiv ID or arXiv URL. **注意: web search 返回的论文信息不可靠 — 摘要可能残缺, 作者/年份可能错配, arxiv ID 本身甚至可能是幻觉. 任何要写入 idea / review / proposal 的论文引用, 都必须用 arxiv-tools 拉取原文核验, 不能仅凭 web search 结果落笔.**
- humanizer: Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Based on Wikipedia's comprehensive "Signs of AI writing" guide. Detects and fixes patterns including: inflated symbolism, promotional language, superficial -ing analyses, vague attributions, em dash overuse, rule of three, AI vocabulary words, negative parallelisms, and excessive conjunctive phrases.
- server-health: Use when you need server load history (CPU util, GPU busy count, mem GB) to pick a server, or to confirm your running task is still alive. Configure it with project-specific server snapshots and `references/servers_manual.md`; do not assume private defaults.
- superpowers:write-plan execute-plan brainstorm writing-plans dispatching-parallel-agents subagent-driven-development systematic-debugging verification-before-completion brainstorming using-superpowers executing-plans finishing-a-development-branch receiving-code-review writing-skills using-git-worktrees requesting-code-review test-driven-development
- huggingface-skills:huggingface-community-evals huggingface-papers huggingface-datasets transformers-js huggingface-trackio huggingface-paper-publisher huggingface-vision-trainer huggingface-llm-trainer huggingface-gradio hf-cli huggingface-tool-builder
- code-review:code-review

## Codex 调用

全部走本地 CLI `codex exec`。调用模式：

```bash
codex exec --dangerously-bypass-approvals-and-sandbox -m gpt-5.6-sol -c model_reasoning_effort=max \
  --output-last-message "$OUT" \
  - < "$PROMPT" 2>&1
```

关键坑位:

- sandbox 必须 bypass (触发 `bwrap: loopback: Failed RTM_NEWADDR`)
- 不要 pipe `codex ... | tail -N`, tail 会 block 到 stdin EOF
- prompt 走 stdin, 不塞 argv
- 异步任务 poll 输出文件大小, 不 poll `pgrep`
- 必须加 `--output-last-message` 否则 output 会非常非常大
- 结束后记得清理自己留在 `/tmp` 的文件

## 可用环境变量

- OPENAI_API_KEY: 可以调用 OpenAI 平台. 优先用 Batch API (半价, 实测不慢).
- DEEPSEEK_API_KEY: 可以调用 DeepSeek 平台. 无 Batch API, 但有: (1) off-peak 50-75% off 在 UTC 16:30-00:30 (= EDT 12:30-20:30); (2) 相同 prefix 自动 prompt cache, cache hit ~90% off; (3) V4 Pro 75% off promo (到 2026-05-31).
- MOONSHOT_API_KEY: 可以调用 Moonshot 官方 Kimi 平台 (https://api.moonshot.cn/v1). 无 Batch API, 仅有 cache hit 83% off.
- NVIDIA_API_KEY: 可以调用 NVIDIA NIM 托管平台 (https://integrate.api.nvidia.com/v1), 覆盖 Kimi / GLM / MiniMax / Qwen / Meta 等 140 个模型. 只要能用就是免费, 但是有限流: 40 RPM, per-model 独立计数.
- 预算上限 (跨所有 API_KEY): 每个项目总计 $50, 超过前须先征得用户同意.
- HF_TOKEN: 可以使用 Hugging Face; 不要把 token 写进共享 `HF_HOME`
- HF_HOME: 可选。若使用 Hugging Face 资产, 用户应指向自己的缓存目录。
- ARXIV_CACHE_DIR: deep-lit 使用的 arXiv 缓存目录, 由用户环境提供。

中国主流模型 output token 标价 (不打折时):

| Provider | Model | Output $/M |
|----------|-------|-----------|
| DeepSeek | deepseek-chat | $0.28 |
| DeepSeek | deepseek-reasoner | $0.42 |
| Moonshot | Kimi K2.6 | $4.00 |
| Zhipu | GLM-5 | $3.20 |
