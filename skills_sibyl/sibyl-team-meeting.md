# Research Team Meeting

A chair-led, multi-role meeting protocol for hard research decisions. Use it when a decision needs structured disagreement, convergence, and an executable next step rather than a quick list of lenses.

## When to Use

Use this protocol for:
- Choosing among research directions, experimental routes, or paper strategies.
- Turning a vague decision into explicit options, risks, and evidence needs.
- Resolving disagreement between scientific promise, methodological rigor, implementation cost, and reviewer risk.
- Preparing a plan that must survive later audit or review.

Do not use it for:
- Simple code edits, formatting, bookkeeping, or already-decided implementation tasks.
- Routine review loops that already have a dedicated reviewer/auditor protocol.
- Topics where concrete operational detail would be unsafe or outside scope. In safety-sensitive domains, keep the meeting at high-level research planning and do not provide actionable procedures, optimization details, recipes, or execution parameters.

## Input Contract

Before starting, write a short meeting brief:

```markdown
Problem:
Context:
Decision to make:
Candidate options:
Constraints:
Desired output:
Optional roles:
Safety / scope restrictions:
```

If candidate options are missing, the Chair should first propose a small set of options. If constraints are missing, state the assumptions explicitly and mark them as assumptions, not facts.

## Default Roles

Always include one Chair and one Critic. Other roles may be replaced if the task calls for different expertise.

1. **Chair / PI** — owns the agenda, keeps roles on task, summarizes each round, identifies disagreements, asks follow-up questions, and writes the final synthesis.
2. **Domain Scientist** — focuses on the core scientific question, hypothesis quality, falsifiability, and what would change the field's belief.
3. **Methodologist / ML Specialist** — focuses on method design, baselines, metrics, ablations, statistical rigor, and whether the test actually measures the claim.
4. **Systems / Implementation Specialist** — focuses on data availability, engineering cost, reproducibility, run logistics, failure modes, and whether the plan can be executed reliably.
5. **Scientific Critic / Reviewer** — tries to refute the proposal, names the strongest rejection argument, flags missing controls, and asks what evidence would be required before making a claim.

## Per-Role Output Contract

Every role contribution must include:

```markdown
Recommendation:
Rationale:
Main risk:
Evidence needed:
Concrete next step:
```

Avoid generic encouragement. Each role must say what should be done, why, what could go wrong, what evidence would change its mind, and what to do next.

## Full Protocol: 3 Rounds

### Round 0 — Chair Opens

The Chair writes:
- The agenda as 2-5 decision questions.
- The candidate options under consideration.
- The criteria for a good decision.
- Any known constraints and scope restrictions.

### Round 1 — Initial Positions

Each non-chair role gives its first assessment using the per-role output contract.

The Chair then writes:
- Consensus so far.
- Disagreements.
- Missing information.
- Targeted questions for Round 2.

### Round 2 — Challenge and Refinement

Each role must respond to at least one disagreement or missing-information point from the Chair. Roles should revise their recommendation if another role exposed a real issue.

The Chair then writes:
- Updated consensus.
- Remaining disagreements.
- Which uncertainties are decision-blocking vs. acceptable risk.
- Targeted final questions for Round 3.

### Round 3 — Final Recommendation

Each role gives a final recommendation, including the strongest remaining risk and the minimum evidence needed to proceed.

The Chair produces the final synthesis using the output template below.

## Quick Protocol: 2 Rounds

Use this when the decision is important but not worth a full meeting.

1. Chair opens with agenda and options.
2. Roles give initial positions.
3. Chair summarizes consensus and asks one round of targeted challenges.
4. Roles answer the challenges.
5. Chair writes the final synthesis.

Do not use quick mode if the decision changes the main claim, expensive compute allocation, submission strategy, or safety posture.

## Chair Synthesis Rules

The Chair is not a vote counter. The Chair should:
- Prefer consensus when the reasoning is strong, but override consensus if the Critic identifies a fatal flaw.
- Separate decision-blocking risks from risks that can be managed with a follow-up check.
- Convert disagreement into experiments, checks, or explicit assumptions.
- Preserve minority objections when they affect claim ceiling or reviewer risk.
- End with executable next steps, not a vague recommendation.

## Final Output Template

```markdown
## Agenda
- Q1:
- Q2:

## Role Inputs
### Domain Scientist
- Recommendation:
- Key reason:
- Key risk:

### Methodologist / ML Specialist
...

### Systems / Implementation Specialist
...

### Scientific Critic / Reviewer
...

## Consensus
- ...

## Disagreements
- ...

## Decision / Recommendation
- Decision:
- Why this option wins:
- Claim ceiling:

## Risks and Failure Modes
- Risk:
  - Mitigation / check:

## Answers to Key Questions
- Q1: ...
- Q2: ...

## Next Steps
1. ...
2. ...
3. ...

## Open Questions
- ...
```

## Relation to `sibyl-debate`

Use `sibyl-debate` when you only need quick independent lenses on a claim or result. Use this meeting protocol when you need a chaired, multi-round convergence process with an agenda, role-by-role commitments, explicit disagreements, and a final decision.
