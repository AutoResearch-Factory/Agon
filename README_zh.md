# Agon

### 面向自主 AI 科研的 Claude Code 插件 —— 从一句课题描述到跑起来的实验, 全程无人编写实验代码

[![Project page](https://img.shields.io/badge/project-page-1f6feb.svg)](https://haizhaoyang.github.io/research/autoresearch.html)
[![arXiv](https://img.shields.io/badge/arXiv-2606.24177-b31b1b.svg)](https://arxiv.org/abs/2606.24177)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2.svg)](https://claude.com/claude-code)

[English](README.md) | 中文

**Agon** ([论文](https://arxiv.org/abs/2606.24177)) 把一个科研项目从一句话的课题一路推到跑起来的实验. 各个 agent 在闭环里互相规划, 实现, 审计和评审, 每一次交接都经由磁盘上的文件 —— 一次运行因此可恢复, 可审计, 也可跨项目复用. 流程保持最小且显式: `topic → idea → proposal → experiment`.

Agon 构建于 [**Prompt Economy**](https://arxiv.org/abs/2606.08878) 之上: 把 prompt engineering 当作工程问题, 并最小化它对人的工程投入. 跨十余个研究领域的部署细节见[论文](https://arxiv.org/abs/2606.24177).

## 快速开始

Clone [Agon](https://github.com/AutoResearch-Factory/Agon) 和 [agon-artifacts](https://github.com/AutoResearch-Factory/agon-artifacts):

```
git clone https://github.com/AutoResearch-Factory/Agon.git
git clone https://github.com/AutoResearch-Factory/agon-artifacts.git
```

两个目录并排放置:

```
.
├── Agon/
└── agon-artifacts/
```

然后在 artifacts 仓库里启动 Claude Code:

```
cd agon-artifacts
claude --plugin-dir ../Agon --dangerously-skip-permissions --effort medium --model claude-sonnet-5[1m]
```

`--dangerously-skip-permissions` 是必需的, 因为这些循环本来就是无人值守跑的: 子 agent 会连续几小时写文件、起实验、调工具, 没有人守在键盘前, 一个权限确认框就会把整轮跑卡死. 介意的话, 给 Agon 单独一台机器, 一个容器, 或一个独立账号.

进入 Claude Code 后, 用这些命令推进科研流程:

- `/idea-tick`: 围绕 topic 创建、评审、修改 idea, 并做文献检查.
- `/proposal-tick`: 把选中的 idea 变成 proposal.
- `/experiment-tick`: 为一个 workspace 调度 scientist、coder、auditor、reviewer.
- `/deep-lit-tick`: 其他阶段共用的深度文献循环.

## 示例 Prompt

```
/deep-lit-tick 穷尽 <topic> 相关文献, 结果写到 topics/mmdd-<slug>-landscape.md
/idea-tick <topic-slug> <topic> 最近很火, 帮我 brainstorm 几个 idea
/idea-tick <idea-slug> 我有一个关于 <topic> 的 vague idea. 帮我创建 topic file、idea file, 并 refine idea
/proposal-tick <idea-1> <idea-2> <idea-3> 为这几个 idea 生成 proposal
/experiment-tick <slug> 开干!
/experiment-tick <slug> 这是一次调试过程. 先解释完整流程, 每调用完一个 agent 都停下来等我确认
```

## 结构

Agon 本身是一个 Claude Code plugin. 运行时建议使用独立的数据 workspace, 通常命名为 `agon-artifacts`, 这样 prompts/code 和 research data 可以分开管理.

预期的数据 workspace 结构:

```
agon-artifacts/
├── topics/
├── ideas/
└── workspace/
```

本地设置可以写在 `.settings.toml` (从复制 `.settings.example.toml` 开始).

## claude-ds 的安装

`claude-ds` 是 deepseek 驱动的 claude code

1. 首次启动前建空 `~/.claude-ds/`，只处理 symlink（其余由 claude 首次启动自动生成）:
   - 设置侧 (symlink): `CLAUDE.md` `mcp-needs-auth-cache.json` `memory/` `plugins/` `settings.json` `settings.local.json` `skills/`
   - 会话侧 (隔离): `backups/` `cache/` `downloads/` `ide/` `stats-cache.json` `projects/` `sessions/` `session-env/` `file-history/` `history.jsonl` `paste-cache/` `shell-snapshots/` `.claude.json`
   - symlink 是为了在 `claude` 和 `claude-ds` 之间共享 skills, MCP, plugins

2. 在 `~/.bashrc` 中写入 `claude-ds()` 函数
```
claude-ds() {
  CLAUDE_CONFIG_DIR="$HOME/.claude-ds" \
  ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic" \
  ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY" \
  ANTHROPIC_MODEL="deepseek-v4-pro[1m]" \
  ANTHROPIC_SMALL_FAST_MODEL="deepseek-v4-flash" \
  claude --effort max "$@"
}
```
注意:
- 写到 `# If not running interactively` 守卫之前，确保非交互式 shell 如 Claude Code 的 Bash 工具也能看到
- 模型 ID 加 `[1m]` 后缀解锁 1M context
3. 运行 `claude-ds`

## Claude Code 必要设置

| 项 | 作用 |
|------|------|
| `DISABLE_TELEMETRY` | 关闭 Statsig 遥测（用量统计，不含代码/文件路径） |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | 允许主 agent 向后台/异步子 agent 发消息 resume, 以及子 agent 之间互发消息协作 |
| `cleanupPeriodDays: 3650` | 保留 `~/.claude/projects/` 下的 session 历史（默认 30 天会被自动清掉），写在 `~/.claude/settings.json` 顶层 |

**配置 statusline**

直接和 `claude` 或者 `claude-ds` 说: "把 statusline-setup 叫出来, 我要 `[5h:6% 7d:69%(2d17h)] Ctx:7% Opus 4.6 (1M context)`"

## 引用

```bibtex
@misc{sun2026agonautonomouslargescaleomnidisciplinary,
      title={Agon: An Autonomous Large-Scale Omnidisciplinary Research System Built on Prompt Economy},
      author={Youran Sun and Xingyu Ren and Chugang Yi and Jiaxuan Guo and Kejia Zhang and Jianda Du and Haizhao Yang},
      year={2026},
      eprint={2606.24177},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2606.24177},
}
```

## 致谢

- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
- [AutoResearch-SibylSystem](https://github.com/Sibyl-Research-Team/AutoResearch-SibylSystem)
- [Telegram MCP Communicator](https://github.com/WhymustIhaveaname/mcp-communicator-telegram)
- [Claude Memory Manager](https://github.com/WhymustIhaveaname/claude-memory-manager)
- [humanizer](https://github.com/blader/humanizer)
