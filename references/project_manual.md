# 大规模并行科研系统说明书

这是一个多人协作, 大规模并行科研系统. 请仔细阅读本文件, 了解各种文件的位置和自己的读取权限, 防止与其他人撞车.

## 项目结构

```
workspace/<slug>/
├── proposal.md       # 用户提供的唯一上游研究定义
├── landscape.md      # 可选的已有文献背景
├── STATE.md
├── LESSONS.md
├── experiment-log.md
├── audits/
├── data/MANIFEST.md
└── results/<run-name>/manifest.json
```


## Workspace XML

```xml
<workspace slug="example-slug" date="YYYY-MM-DD" gpu_dollars_equivalent="0.00">
  <one-line>One-sentence description of the current experiment status.</one-line>
</workspace>
```

## API 预算

- API 预算上限 (跨所有 API_KEY): 每个项目总计 $50, 超过前须先征得用户同意; 其他计算资源的限制以用户配置和资源提供方规则为准.
