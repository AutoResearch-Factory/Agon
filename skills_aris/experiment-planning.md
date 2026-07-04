# Experiment Planning

## Goal

Turn a proposal into a **claim → evidence → run order** roadmap that supports four things:

1. The method actually solves the anchored problem.
2. The dominant contribution is real and focused.
3. The method is elegant enough that extra complexity is unnecessary.
4. Any frontier-model-era component is genuinely useful, not decorative.

Not a benchmark wishlist.

## Don't plan experiments on an unstable method

First stabilize the method thesis. Then turn the stable thesis into experiments. Don't widen the paper story after method refinement unless a missing validation block is truly necessary.

## Load upstream context first

Before designing anything, extract from the upstream proposal / refinement docs:

- **Problem Anchor**
- **Dominant contribution**
- **Optional supporting contribution**
- **Critical reviewer concerns**
- **Data / compute / timeline constraints**
- **Which frontier primitive is central, if any**

If these can't be extracted cleanly, the upstream isn't stable enough — go back to method refinement.

## Planning gate

Before the experiment stage, write a short gate check:

- What is the final method thesis?
- What is the dominant contribution?
- What complexity was intentionally rejected?
- Which reviewer concerns still matter for validation?
- Is a frontier primitive central, optional, or absent?

If these answers aren't crisp, tighten the final proposal first rather than designing experiments around fuzzy answers.

## Freeze the claims first

Before designing experiments, write down what must be defended:

- **Primary claim**: the main mechanism-level contribution.
- **Supporting claim**: optional, only if it directly strengthens the main paper story.
- **Anti-claim to rule out**: e.g. "the gain only comes from more parameters", "from a larger search space", "the modern component is just decoration".
- **Minimum convincing evidence**: what would make each claim believable to a strong reviewer?

Prefer one dominant claim plus at most one supporting claim.

## Default experiment block menu

Design the paper around a compact set of experiment blocks. Default menu — delete any that aren't needed:

1. **Main anchor result** — does the method solve the actual bottleneck?
2. **Novelty isolation** — does the dominant contribution itself matter?
3. **Simplicity / elegance check** — can a bigger or more fragmented version be avoided?
4. **Frontier necessity check** — if an LLM / VLM / Diffusion / RL-era component is central, is it actually the right tool?
5. **Failure analysis or qualitative diagnosis** — what does the method still miss?

For each block, decide placement: **Main paper** (essential), **Appendix** (useful but non-blocking), or **Cut** (not worth the paper budget).

## Specifying each block

For every kept block, fully specify:

- **Claim tested**
- **Why this block exists**
- **Dataset / split / task**
- **Compared systems** — strongest baselines, ablations, and variants only
- **Metrics** — decisive first, secondary second
- **Setup details** — backbone, frozen vs trainable, hyperparameters, training budget, seeds
- **Success criterion** — what outcome would count as convincing evidence?
- **Failure interpretation** — if the result is negative, what does it mean?
- **Table / figure target** — where this result should appear in the paper

## Special rules

- A **simplicity check** should compare the final method against either an overbuilt variant or a tempting extra component that the paper intentionally rejects.
- A **frontier necessity check** should compare the chosen modern primitive against the strongest plausible simpler or older alternative.
- If the proposal is intentionally non-frontier, say so explicitly and skip the frontier block instead of forcing one.

## Baselines

Prefer one strong baseline family over many weak baselines. If a stronger modern baseline exists, use it instead of padding the list.

## Execution order (milestones)

Build a realistic run order so the user knows what to do first:

1. **Sanity stage** — data pipeline, metric correctness, one quick overfit or toy split.
2. **Baseline stage** — reproduce the strongest baseline(s).
3. **Main method stage** — run the final method on the primary setting.
4. **Decision stage** — run the decisive ablations for novelty, simplicity, frontier necessity.
5. **Polish stage** — robustness, qualitative figures, appendix extras.

For each milestone, estimate: compute cost, expected turnaround time, stop / go decision gate, risk + mitigation.

Separate **must-run** from **nice-to-have** experiments. Don't let appendix ideas delay the core paper evidence.

## Always

- Every experiment must defend a claim. If it does not change a reviewer belief, cut it.
- Prefer a compact paper story. Design the main table first, then add only the ablations that defend it.
- Defend simplicity explicitly. If complexity is a concern, include a deletion study or a stronger-but-bloated variant comparison.
- Defend frontier choices explicitly. If a modern primitive is central, prove why it is better than the strongest simpler alternative.
- Reuse proposal constraints. Do not invent unrealistic budgets or data assumptions.
- Do not fabricate results. Plan evidence; do not claim evidence.
- Reuse the same claims across final proposal, experiment plan, and pipeline summary.
- Do not let the experiment plan override the Problem Anchor. Adapt the plan, not the problem.

## Ablation planning (special case)

When main results are confirmed (claim supported = yes or partial), plan ablation studies. An external reviewer leads the ablation design — you handle feasibility and execution.

### Cross-model reviewer designs ablations

A different-model reviewer plans ablations that:

1. Isolate the contribution of each novel component.
2. Answer questions reviewers will definitely ask.
3. Test sensitivity to key hyperparameters.
4. Compare against natural alternative design choices.

### Per-ablation fields

- **name**: what to change (e.g., "remove module X", "replace Y with Z").
- **what_it_tests**: the specific question this answers.
- **expected_if_component_matters**: what we predict if the component is important.
- **priority**: 1 (must-run) to 5 (nice-to-have).

### Per-plan also

- **coverage_assessment**: what reviewer questions these ablations answer.
- **unnecessary_ablations**: experiments that seem useful but won't add insight — skip these.
- **suggested_order**: run order optimized for maximum early information.
- **estimated_compute**: total GPU-hours.

### Feasibility review and execution

- Compute budget, code changes (config-only vs code mods), parallel dependencies.
- If budget is tight, propose cuts and ask the reviewer to re-prioritize — don't silently drop ablations.
- Run order: config-only ablations first (faster, less error-prone); smoke test each before full run.

### Ablation rules

- Reviewer leads the design. Do not pre-filter or bias the ablation list before the reviewer sees it.
- Every ablation must have a clear `what_it_tests` and `expected_if_component_matters`. No "just try it" experiments.
- Component ablations (remove / replace) take priority over hyperparameter sweeps.
- Do not generate ablations for components identical to the baseline (no-op ablations).
- Record all ablation results, including negative — component removal having no effect is itself an important finding.
