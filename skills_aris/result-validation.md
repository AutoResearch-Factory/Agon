# Result Validation

A decision gate after experiments complete: judge whether the results support the intended claim, route to next action (pivot / supplement / commit).

## Collect experiment data

Gather from available sources (in fallback order):

- **W&B** (preferred): metrics, training curves, comparisons.
- **EXPERIMENT_LOG.md**: full results table with baselines and verdicts.
- **EXPERIMENT_TRACKER.md**: which experiments are DONE vs still running.
- **Log files**: tail training log if no other source.
- **Research contract / proposal**: intended claims and experiment design.

## Assemble for reviewer

- What experiments ran (method / dataset / config).
- Main metrics + baseline comparisons (deltas).
- The intended claim being tested.
- Any known confounds or caveats.

## Reviewer output fields

- **claim_supported**: yes | partial | no.
- **what_results_support**: what the data actually shows.
- **what_results_dont_support**: where the data falls short.
- **missing_evidence**: specific evidence gaps.
- **suggested_claim_revision**: strengthen / weaken / reframe?
- **next_experiments_needed**: specific experiments to fill gaps.
- **confidence**: high | medium | low.

Reviewer instructions: be honest, do not inflate claims beyond what the data supports, a single positive result on one dataset does not support a general claim.

## Integrity check (if audit exists)

- **fail** → mark `[INTEGRITY CONCERN]`, downgrade confidence to `low` regardless of judgment.
- **warn** → mark `[INTEGRITY: WARN]`.
- **unavailable** → mark `provisional — no integrity audit run`; pipeline continues normally.

## Route by verdict

- **no**: record postmortem in findings.md (what tested / what failed / hypotheses for why + constraints for future attempts); update pipeline status; decide pivot vs alternative.
- **partial**: update working claim to what IS supported; record gap; design + run supplementary experiments; re-run gate. Multiple rounds of `partial` → consider narrowing scope or switching ideas.
- **yes**: record confirmed claim; if ablations incomplete → trigger ablation planning; if all evidence in → ready for paper writing.

## Knowledge base updates (when active)

- **Experiment page**: date, hardware, duration, metrics, verdict, confidence, reasoning summary.
- **Claim page status**: supported / partial / invalidated.
- **Idea outcome page**: positive / mixed / negative; negative → failure / risk notes + lessons learned; positive → actual outcome + reusable components.

If several ideas tested as failed / partial since last ideation, suggest re-running idea generation — the knowledge base now knows what doesn't work.

## Structured findings

Each finding: Observation (what the data shows with numbers) → Interpretation (why this might be happening) → Implication (what it means for the research question) → Next step (what experiment would test the interpretation).

Comparison: organize by independent variables vs dependent variables + delta vs baseline. Statistical: multiple seeds → mean ± std; parameter sweep → identify trends (monotonic/U-shaped/plateau); flag outliers.

## Experiment integrity audit

Cross-model integrity check against common agent failure modes. Six axes:

- **Ground Truth Provenance**: GT loaded from dataset, or derived from model outputs? If derived: explicitly labeled as proxy? FAIL if GT from model outputs without proxy labeling.
- **Score Normalization**: Metric divided by model's own output? FAIL if normalization from prediction statistics.
- **Result File Existence**: Claimed file exists? Number matches? FAIL if nonexistent files or mismatched numbers.
- **Dead Code Detection**: Metric defined but never called? WARN if dead code.
- **Scope Assessment**: Scope language matches actual evidence? WARN if scope language exceeds evidence.
- **Evaluation Type**: real_gt / synthetic_proxy / self_supervised_proxy / simulation_only / human_eval.

Key rules: reviewer independence (executor collects paths, reviewer judges); never block (warn loudly, never halt); cross-model (reviewer different model family); honest about limits (safety net, not guarantee).

## Rules

- **External reviewer is the judge, not you.** Collect evidence + route; reviewer evaluates. Prevents post-hoc rationalization.
- Do not inflate claims beyond what the data supports. If reviewer says `partial`, do NOT round up to `yes`.
- A single positive result on one dataset does not support a general claim. Be honest about scope.
- If confidence is low, treat the judgment as inconclusive and add experiments rather than committing to a claim.
- If reviewer is unavailable, make own judgment and mark `[pending review]` — do not block the pipeline.
- Always record verdict and reasoning in findings.md, regardless of outcome.
