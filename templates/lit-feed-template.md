---
unprocessed: 0                        # 未消费条目数, deep-lit 写入后 +N, scientist 清空后置 0
---

# Lit Feed: [slug]

<!--
lit-feed.md: 文献 inbox (收件箱), 不是知识库。
reviewer 后的 experiment-scope deep-lit 往这里投递"针对当前急需问题、刚搜来的解决方案/工具/垫脚石"。
scientist 开工第一步消费: 逐条 promote 进 STATE (§5/§6/A1) 或 LESSONS, 用不上的写一句丢弃理由, 处理完删条目 + 置 unprocessed=0。

与同目录文档的分工:
- wiki (`$ARXIV_WIKI_DIR/`): 每篇论文全文精读笔记, 长期沉淀。wiki 池位置由 `$ARXIV_WIKI_DIR` 配置。
- workspace 内 idea.md: deep-lit 搜出的全部新文献总账 (一篇不漏, 可追溯), 长期归档, 允许膨胀。
- 本文件 (inbox): 只装命中当前急需问题的那几条, 流动, 处理完即清空, 不沉淀。

inbox 永远是空或近空。膨胀的东西在 idea.md 总账和 wiki, 不在这里。
不要删除本注释, 一直保留作为本文件的填写指引。
-->

## Inbox

<!-- deep-lit 每条按下面格式追加。scientist 消费后整条删除。

### [arxiv_id] 一句话标题
- 解决哪个急需问题: [对应 STATE.md 的卡点 / 待对比 baseline / 正在实现的 method]
- 解决方案/工具/垫脚石: [它提供了什么可直接用的东西]
- 来源: arxiv_id + wiki 路径 (`$ARXIV_WIKI_DIR/<id>.md`, 可打开看全文细节)
-->
