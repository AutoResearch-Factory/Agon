# Experiment Log: [slug]

<!--
experiment-log.md: 跨 branch 持久的完整项目日志
新条目 **prepend** (时间倒序, 最新在顶部).
-->

## [Version V+1 Start] YYYY-MM-DD HH:MM — 一句话概述 (route: <route-name>)

- route: route/<name>
- Claim 主攻: [本 version 主要 push 什么]
- Plan 简述: [本 version 要跑哪几个 runs, 期望看到什么]

## [Audit] YYYY-MM-DD HH:MM — verdict=PASS/WARN/CRITICAL/BLOCKER (iter N)

- Report: audits/audit_iterN_YYYYMMDD_HHMM.md
- Load-bearing issues: [一句话列最重要的 1-3 个问题]
- Required scientist response: [下一轮 scientist 必须回应什么]


## [Review of Version V] YYYY-MM-DD HH:MM — score=Y/10

- Verdict: ready / almost / not ready
- Primary concern: [同 STATE.md `<review>` 块的 Primary concern]


## [Version V Finished] YYYY-MM-DD HH:MM — 一句话结论 (route: <route-name>)

- Changes: [本 version 累积的主要变化]
- Result: [关键指标]


## [Iter N Start] YYYY-MM-DD HH:MM — 一句话概述 (route: <route-name>)

- Claim 主攻: [本 iter 主要 push 哪条 claim]
- Plan 简述: [本 iter 要跑哪几个 runs, 期望看到什么]


## [Run Crash] YYYY-MM-DD HH:MM — run <run-name> (iter N)

- 错误类型: [Python traceback / CUDA OOM / NaN / shape mismatch / assertion / import]
- 所在文件行号: [file:line]
- 根本原因分析: [一句话]
- 对应日志路径:


## [Run Sync] YYYY-MM-DD HH:MM — run <run-name> on <server> (iter N)

- Manifest: results/<run-name>/manifest.json
- Synced local paths:
- Remote-only assets:
- Missing / suspect files:


## [Run Done] YYYY-MM-DD HH:MM — run <run-name> on <server> (iter N)

- Wall time: <M hours>
- GPU $: <amount>
- Manifest: results/<run-name>/manifest.json
- Key metrics:


## [Init] YYYY-MM-DD HH:MM — workspace 接手 (slug: <slug>)

- Topic: topics/<mmdd-slug>.md
- Landscape: topics/<mmdd-slug>-landscape.md
- Idea: ideas/<slug>.vN.md
- Proposal: ideas/<slug>-proposal.vN.md
- Cleanup commit: <hash> on main
- First route: route/<name>
- Claim 主攻: [本 version 主要 push 哪条 sub-claim]
- Plan 简述: [本 version 要跑哪几个 runs, 期望看到什么]
