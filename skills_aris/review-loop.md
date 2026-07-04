# Review Loop

Iteratively review → fix → re-review until the external reviewer gives a positive assessment or max rounds reached.

## Layered adversarial mechanisms

Each layer strengthens reviewer independence; can be stacked.

- **Baseline**: MCP-based review; author controls what context the reviewer sees.
- **Reviewer Memory**: reviewer tracks own suspicions across rounds; becomes skeptical of convenient omissions in later rounds.
- **Debate Protocol**: author rebuts each weakness, reviewer rules SUSTAINED / OVERRULED / PARTIALLY SUSTAINED.
- **Adversarial Verification**: reviewer reads repo directly (code, results, logs), verifies independently — author cannot filter context.

## Each round

Each round starts by identifying current weaknesses + open TODOs from prior reviews (continuity discipline).

In compact mode (when summary files exist), read findings.md + EXPERIMENT_LOG.md instead of the full review log to save context window.

## Baseline review prompt

Reviewer acts as senior ML reviewer (NeurIPS / ICML level) and:

- Scores 1-10 for a top venue.
- Lists remaining critical weaknesses (ranked by severity).
- For each weakness, specifies the MINIMUM fix (experiment / analysis / reframing).
- States clearly: READY for submission? Yes / No / Almost.
- Is brutally honest; says so clearly when work is ready.

## With Reviewer Memory

Prepend prior-round memory to the prompt and add:

> "You have memory from prior rounds. Check whether previous suspicions were genuinely addressed or merely sidestepped. The author controls what context you see — be skeptical of convenient omissions."

Additional output: memory update (new suspicions, unresolved concerns, patterns to track).

Reviewer Memory per-round entry: Suspicion / Unresolved / Patterns; round 2+ also "Previous suspicions addressed?" + New suspicions. Append each round, never delete (audit trail). Copy reviewer's "Memory update" verbatim. This file is the reviewer's persistent brain across rounds.

## With Adversarial Verification

Reviewer accesses repo autonomously. Author does NOT control what reviewer sees. Reviewer:

- Reads experiment code, results files (JSON / CSV), logs themselves.
- Verifies reported numbers match output files.
- Checks if evaluation metrics are computed correctly (ground truth, not model output).
- Looks for cherry-picked results, missing ablations, suspicious hyperparameter choices.
- Output: score, verdict, verified claims, unverified / false claims, weaknesses (ranked + minimum fix), memory update.

> "Be adversarial. Trust nothing the author tells you — verify everything yourself."

## Parse the response

Save the FULL raw reviewer response verbatim. Do NOT discard or summarize — raw text is the primary record.

Extract structured fields: Score (1-10), Verdict (ready / almost / not ready), Action items (ranked list of fixes).

Stop condition: positive verdict ("ready" / "almost") + acceptable score → stop loop, document final state.

## Debate Protocol

Author rebuts each weakness with: Accept / Partially Accept / Reject + Argument (why invalid / addressed / misunderstood) + Evidence (point to code / results / prior fixes).

Rebuttal rules:

- Must be honest (no fabricated evidence).
- Can point out factual errors in review (reviewer misread code, wrong metric, etc.).
- Can argue out-of-scope or unreasonable effort.
- Only a few rebuttals per round (pick most impactful).

Reviewer rules each rebuttal: SUSTAINED (withdraw weakness) / OVERRULED (criticism stands, explain) / PARTIALLY SUSTAINED (revise to narrower scope).

With Adversarial Verification: reviewer verifies author's evidence claims independently (reads files referenced, doesn't take author's word).

Update score and action items based on ruling. Append debate to review log.

## Human checkpoint (when enabled)

Present results after the review parse, wait for user input. Options: Approval / Custom instructions / Skip specific / Stop.

## Implement fixes

Implement fixes in priority order (highest priority first). Action items typically span:

- Code changes (scripts / model / analysis).
- Run experiments (deploy to GPU).
- Analysis (eval, results, figures, tables).
- Documentation (project notes + review document).

### Prioritization rules

- Skip fixes requiring excessive compute (flag for manual follow-up).
- Skip fixes requiring external data / models not available.
- Prefer reframing / analysis over new experiments when both address the concern.
- Always implement metric additions (cheap, high impact).

## During pending experiments

Run training quality check via W&B to catch NaN / divergence / plateau early — don't wait for the full run to find out it was unhealthy.

## Per-round documentation

Per round, record: assessment summary (score + verdict + key criticisms), reviewer raw response verbatim, debate transcript (when using Debate Protocol), actions taken + results, status (continuing / stopping).

Make the loop resumable across context-window restarts (state persistence) — long loops shouldn't lose progress on auto-compaction. In compact mode, append a one-line finding per round.

## Termination

Termination hand-off: write a method / pipeline description (1-2 paragraphs of architecture + data flow) for downstream paper writing; generate validated claims from results (via result validation) so downstream paper-plan uses them directly instead of re-extracting.

If stopped at max rounds without positive verdict: list remaining blockers, estimate effort needed for each, suggest continue-manually vs pivot.

## Reviewer Independence Protocol

The reviewer must be context-naive on every round. Prior-round summaries, fix lists, and executor explanations are not evidence; they are a source of confirmation bias. If the reviewer is told what changed, scores tend to drift upward even when the manuscript itself has not materially improved.

- Every round starts fresh, never with prior thread context.
- Never include "since last round", "we fixed", "after applying", or any fix summary in the reviewer prompt.
- The only acceptable evidence of improvement is the current source and output.
- If a fix cannot be observed in the output, the reviewer should not be told it happened.

## Paper Fix Patterns

Common fixes during paper improvement rounds:

| Issue | Fix Pattern |
|-------|-------------|
| Assumption-model mismatch | Rewrite assumption to match the model, add formal proposition bridging the gap |
| Overclaims | Soften language: "validate" → "demonstrate practical relevance" |
| Missing metrics | Add quantitative table with honest parameter counts and caveats |
| Theorem not self-contained | Add interpretation paragraph listing all dependencies |
| Notation confusion | Rename conflicting symbols globally, add Notation paragraph |
| Theory-practice gap | Explicitly frame theory as idealized; add synthetic validation subsection |
| Keyword inconsistency | The "Banana Rule": if Methods uses one term, Results must not switch to a synonym. Extract key terms, verify consistency across all sections |

## Restatement Regression

After every recompilation, verify theorem-statement consistency so fix rounds cannot reintroduce drift. Compare only theorem/lemma/proposition/corollary statements (not proof bodies). Flag any change in hypotheses, case splits, quantifier order, or terminology as regression drift.

## Format Check Philosophy

Location-aware thresholds: main-body issues block completion regardless of size; appendix issues block only if visibly clipping; bibliography issues block only if excessive. Underfull warnings remain warnings unless they create obvious layout damage. Duplicate labels hard block.

## Typical Score Progression

A well-structured but rough first draft typically gains several points across rounds: round 0 (baseline, assumption-model mismatch and overclaims) → round 1 (fixed core issues) → round 2 (added synthetic validation and formal propositions) → final round (format pass: compressed, fixed overfull boxes).

## Always

- Be honest — include negative results and failed experiments.
- Do NOT hide weaknesses to game a positive score.
- Implement fixes BEFORE re-reviewing (don't just promise to fix).
- **Exhaust before surrendering** — before marking any reviewer concern as "cannot address": (1) try at least 2 different solution paths, (2) for experiment issues, adjust hyperparameters or try an alternative baseline, (3) for theory issues, provide a weaker version of the result or an alternative argument, (4) only then concede narrowly and bound the damage. Never give up on the first attempt.
- If an experiment is long-running, launch it and continue with other fixes while waiting.
- Document EVERYTHING — review log should be self-contained.
- Update project notes after each round, not just at the end.
