# Agon

English | [中文](README_zh.md)

Agon ([paper](https://arxiv.org/abs/2606.24177)) is an automated research system. It keeps the workflow minimal and explicit: `topic -> idea -> proposal -> experiment`.

## Quick start

Clone [Agon](https://github.com/AutoResearch-Factory/Agon) and [agon-artifacts](https://github.com/AutoResearch-Factory/agon-artifacts):

```
git clone https://github.com/AutoResearch-Factory/Agon.git
git clone https://github.com/AutoResearch-Factory/agon-artifacts.git
```

Put the two directories side by side:

```
.
├── Agon/
└── agon-artifacts/
```

Then run Claude Code from the artifacts repository:

```
cd agon-artifacts
claude --plugin-dir ../Agon --dangerously-skip-permissions
```

In Claude Code, use these commands to move the research forward:

- `/idea-tick`: create, review, refine, and literature-check ideas for a topic.
- `/proposal-tick`: turn selected ideas into reviewed proposals.
- `/experiment-tick`: coordinate scientist, coder, auditor, and reviewer roles for one workspace.
- `/deep-lit-tick`: run the shared deep literature loop used by the other stages.

## Example Prompts

```
/deep-lit-tick Exhaustively survey the literature on <topic>, and write the result to topics/mmdd-<slug>-landscape.md.
/idea-tick <topic-slug> <topic> is becoming important. Brainstorm several research ideas.
/idea-tick <idea-slug> I have a vague idea about <topic>. Create the topic file, create the idea file, and refine the idea.
/proposal-tick <idea-1> <idea-2> <idea-3> Generate proposals for these ideas.
/experiment-tick <slug> Start the experiment.
/experiment-tick <slug> This is a debugging run. First explain the full procedure, then pause for my approval after each agent call.
```

## Layout

Agon itself is a Claude Code plugin. Run it from a separate data workspace, commonly named `agon-artifacts`, so prompts/code and research data can evolve independently.

Expected data workspace layout:

```
agon-artifacts/
├── topics/
├── ideas/
└── workspace/
```

Optional local settings live at `.settings.toml`. Start from `.settings.example.toml` when you need to customize model routing or parallelism.

## claude-ds installation

`claude-ds` is DeepSeek-backed Claude Code.

1. Before first launch, create an empty `~/.claude-ds/` and only handle symlinks. Claude will generate the rest on first launch:
   - Settings side (symlink): `CLAUDE.md` `mcp-needs-auth-cache.json` `memory/` `plugins/` `settings.json` `settings.local.json` `skills/`
   - Session side (isolated): `backups/` `cache/` `downloads/` `ide/` `stats-cache.json` `projects/` `sessions/` `session-env/` `file-history/` `history.jsonl` `paste-cache/` `shell-snapshots/` `.claude.json`
   - The symlinks let `claude` and `claude-ds` share skills, MCP, and plugins

2. Add the `claude-ds()` function to `~/.bashrc`:
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
Notes:
- Put it before the `# If not running interactively` guard, so non-interactive shells such as Claude Code's Bash tool can see it
- Add the `[1m]` suffix to the model ID to unlock 1M context
3. Run `claude-ds`

## Required Claude Code settings

| Item | Purpose |
|------|------|
| `DISABLE_TELEMETRY` | Disable Statsig telemetry (usage stats, no code or file paths) |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Let the main agent resume background/asynchronous subagents, and let subagents message each other |
| `cleanupPeriodDays: 3650` | Keep session history under `~/.claude/projects/` (default cleanup is after 30 days); set this at the top level of `~/.claude/settings.json` |

**Configure statusline**

Tell `claude` or `claude-ds`: "call statusline-setup, I want `[5h:6% 7d:69%(2d17h)] Ctx:7% Opus 4.6 (1M context)`"

## References

- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
- [AutoResearch-SibylSystem](https://github.com/Sibyl-Research-Team/AutoResearch-SibylSystem)
- [Telegram MCP Communicator](https://github.com/WhymustIhaveaname/mcp-communicator-telegram)
- [Claude Memory Manager](https://github.com/WhymustIhaveaname/claude-memory-manager)
- [humanizer](https://github.com/blader/humanizer)
