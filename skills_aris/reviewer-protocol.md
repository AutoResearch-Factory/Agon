# Reviewer Protocol

## Brief the reviewer first

Before calling an external reviewer (model or human), compile a comprehensive briefing. The reviewer cannot read your files:

- Read project narrative documents (e.g., STORY.md, README.md, paper drafts).
- Read memory / notes files for key findings and experiment history.
- Identify: core claims, methodology, key results, known weaknesses.

Send comprehensive context in Round 1. Holding back loses you actionable feedback.

## How to ask for review

Ask the reviewer to act as a **senior ML reviewer (NeurIPS / ICML level)** and identify:

- Logical gaps or unjustified claims
- Missing experiments that would strengthen the story
- Narrative weaknesses
- Whether the contribution is sufficient for a top venue

Ask the reviewer to be **brutally honest**. Be honest yourself about weaknesses — hiding them leads to worse feedback. Include negative results and failed pilots in the review prompt.

## Scoring rubric (when refining a method)

When the review is specifically a **method refinement** review, ask the reviewer to score 7 dimensions (1-10 each):

| Dimension | Weight | What it checks |
|-----------|--------|----------------|
| Problem Fidelity | 15% | Does the method still attack the original bottleneck, or has it drifted? |
| Method Specificity | 25% | Are interfaces / representations / losses / training stages / inference path concrete enough to start implementing? |
| Contribution Quality | 25% | One dominant mechanism-level contribution with novelty + parsimony + no sprawl? |
| Frontier Leverage | 15% | Foundation-model-era primitives used appropriately, not old-school stacking? |
| Feasibility | 10% | Trainable + integrable with stated resources and data assumptions? |
| Validation Focus | 5% | Experiments minimal but sufficient for core claims, no bloat? |
| Venue Readiness | 5% | Would the contribution feel sharp and timely for a top venue? |

For each dimension scoring < 7, demand: specific weakness + concrete method-level fix (interface / loss / training recipe / integration point / deletion) + priority (CRITICAL / IMPORTANT / MINOR).

Plus per-review:

- **Simplification Opportunities** — 1-3 ways to delete / merge / reuse while preserving the main claim (or NONE).
- **Modernization Opportunities** — 1-3 ways to replace old-school with foundation-era primitives if genuinely better (or NONE).
- **Drift Warning** — NONE, or explain drift.
- **Verdict** — READY / REVISE / RETHINK.

Verdict rule:

- **READY**: overall ≥ 9, no meaningful drift, one focused dominant contribution, no complexity bloat.
- **REVISE**: direction promising but not at READY bar.
- **RETHINK**: core mechanism or framing fundamentally off.

## Iterative dialogue patterns

For each round:

1. **Respond** to criticisms with evidence / counterarguments.
2. **Ask targeted follow-ups** on the most actionable points.
3. **Request specific deliverables**: experiment designs, paper outlines, claims matrices.

Useful follow-up patterns:

- "If we reframe X as Y, does that change your assessment?"
- "What's the minimum experiment to satisfy concern Z?"
- "Please design the minimal additional experiment package (highest acceptance lift per GPU week)"
- "Please write a mock NeurIPS / ICML review with scores"
- "Give me a results-to-claims matrix for possible experimental outcomes"

## Re-evaluation focus

When sending a revised proposal back, additionally ask the reviewer to check:

- Whether the Problem Anchor is preserved or drifted.
- Whether the dominant contribution is now sharper or still too broad.
- Whether the method is simpler or still overbuilt.
- Whether the frontier leverage is now appropriate or still forced.

Focus new critique on: **missing mechanism, weak training signal, weak integration point, pseudo-novelty, unnecessary complexity**.

## Reviewer principles to apply

When you (or your reviewer prompt) are the reviewer:

- Prefer the smallest adequate mechanism over a larger system.
- Penalize parallel contributions that make the paper feel unfocused.
- If a modern primitive would clearly produce a better paper, say so concretely.
- If the proposal is already modern enough, do NOT force trendy components.
- Do not ask for extra experiments unless they prove core claims.
- Read the Problem Anchor first; flag drift explicitly instead of treating it as a normal revision.

## Stopping criteria

Stop iterating when:

- Both sides agree on core claims and their evidence requirements.
- A concrete experiment plan is established.
- The narrative structure is settled.

## Hygiene

- Push back on criticisms you disagree with, but accept valid ones. Pushback is encouraged.
- Focus on **ACTIONABLE** feedback — "what experiment would fix this?".
- The review document should be self-contained (readable without the conversation).

## Rebuttal safety model

Three hard gates for responding to external reviewer comments — if any fails, do NOT finalize:

1. **Provenance gate**: every factual statement maps to paper, review, confirmed result, or future work. No source = blocked.
2. **Commitment gate**: every promise maps to already_done, approved, or future_work_only. Not approved = blocked.
3. **Coverage gate**: every reviewer concern ends in answered, deferred_intentionally, or needs_input. No issue disappears.

Response modes per issue: direct_clarification / grounded_evidence / nearest_work_delta / assumption_hierarchy / narrow_concession / future_work_boundary / structural_distinction.

Drafting rules: direct answer → grounded evidence → implication. Evidence > assertion. Concrete numbers for counter-intuitive points. Name closest prior work + exact delta. Concede narrowly when reviewer is right. NEVER invent experiments, numbers, derivations, citations, or links. NEVER promise what hasn't been approved. If no strong evidence exists, say less not more. Don't waste space on unwinnable arguments.

## Prompt templates

- **Initial review**: "I'm going to present a complete ML research project for your critical review. Please act as a senior ML reviewer (NeurIPS/ICML level)..."
- **Experiment design**: "Please design the minimal additional experiment package that gives the highest acceptance lift per GPU week. Our compute: [describe]. Be very specific about configurations."
- **Paper structure**: "Please turn this into a concrete paper outline with section-by-section claims and figure plan."
- **Claims matrix**: "Please give me a results-to-claims matrix: what claim is allowed under each possible outcome of experiments X and Y?"
- **Mock review**: "Please write a mock NeurIPS review with: Summary, Strengths, Weaknesses, Questions for Authors, Score, Confidence, and What Would Move Toward Accept."
