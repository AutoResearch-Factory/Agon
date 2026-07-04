# Agon

English | [中文](README_zh.md)

Agon is an automated research system. It keeps the workflow minimal and explicit: `topic -> idea -> proposal -> experiment`.

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

## References

- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
- [AutoResearch-SibylSystem](https://github.com/Sibyl-Research-Team/AutoResearch-SibylSystem)
