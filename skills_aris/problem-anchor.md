# Problem Anchor

## Why anchor

A research project drifts. Reviewer feedback, idea brainstorming, and method refinement all push the target around. Without an immutable anchor, the project ends up solving an easier or different problem than the one the user actually cares about. Always carry the same anchor through every round.

## What to anchor

When you receive a research direction, freeze five fields before doing anything else:

- **Bottom-line problem**: What technical problem must be solved?
- **Must-solve bottleneck**: What specific weakness in current methods is unacceptable?
- **Non-goals**: What is explicitly NOT the goal of this project?
- **Constraints**: Compute, data, time, tooling, venue, deployment limits.
- **Success condition**: What evidence would make the user say "yes, this method addresses the actual problem"?

Copy these verbatim into every proposal and every refinement round.

## When the user input is too vague

- The user provides a DIRECTION, not an idea. Your job is to turn it into concrete ideas / methods.
- If the direction is too broad (e.g., "NLP", "computer vision", "reinforcement learning"), STOP and ask the user to narrow it. A good direction is 1-2 sentences specifying the **problem + domain + constraint** (e.g., "factorized gap in discrete diffusion LMs", "sample efficiency of offline RL with image observations"). Without sufficient specificity, downstream ideas / methods will be too vague to run.

## When a research brief exists

If `RESEARCH_BRIEF.md` (or equivalent) exists, extract:

- Problem statement and context
- Constraints (compute, data, timeline, venue)
- What the user already tried / what didn't work
- Domain knowledge and non-goals
- Existing results (if any)

Merge with any one-line prompt: the brief takes priority for details; the prompt sets the direction.

## Drift detection

If at any later stage (reviewer feedback, ablation suggestion, scope expansion request) a change would alter the problem being solved, flag it as **drift** and push back. Adapt the method, not the problem.

## Robotics problem framing

For robotics/embodied AI: default to simulation-first and public benchmark preferred. Frame must specify embodiment, task family, observation/action interface, learning regime, available assets, compute budget, and safety constraints.

Good ideas expose real bottlenecks in perception-action coupling; improve robustness under embodiment shift; reduce operator/reset/demonstration cost; strengthen sim2real transfer with measurable mechanisms. Weak ideas apply foundation models without bottleneck analysis; are demo-driven but not benchmarkable; need inaccessible hardware.

Filtering: no concrete benchmark → reject; no credible baseline → reject; no metric beyond "looks better" → reject; privileged observations that make the claim weak → reject. Each pilot design must specify success metrics AND failure metrics. Infrastructure realism matters — operator time, reset burden, and safety are research constraints.
