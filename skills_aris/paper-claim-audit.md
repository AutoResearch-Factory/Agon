# Paper Claim Audit

Zero-context evidence audit — verifies that every number in the paper exactly matches the raw evidence files.

## Why zero-context

The executor writes experiments AND writes the paper, so it "knows" what the results should be. This creates confirmation bias — rounding 84.7% up to 85.3%, reporting best seed instead of average, citing metrics from a different config, claiming "improves by 15%" when delta is 12.8%. A fresh reviewer with zero prior context catches these because it has no expectations — it just compares paper text vs raw files.

This audit answers: does the paper report the data truthfully and precisely? (Distinct from experiment-audit which audits code honesty, and result-to-claim which audits scientific support.)

## Core principle

The auditor receives ONLY paper `.tex` files (the claims) and raw result files (the evidence). It does NOT receive EXPERIMENT_LOG.md, EXPERIMENT_TRACKER.md, AUTO_REVIEW.md, NARRATIVE_REPORT.md, any executor summary or interpretation, any prior audit results, any conversation history. This is stricter than reviewer-independence — it's zero-context evidence audit.

Reviewer instructions: "You are a paper-to-evidence auditor. You have ZERO prior context about this research. You will receive only paper source files and raw result files. Your job is to verify that every number in the paper exactly matches the raw evidence."

For each quantitative claim, trace to evidence: find the raw file containing the number, compare exact values.

## Failure modes to check

- **Number inflation**: paper says 85.3%, raw file says 84.7%. Only standard rounding to displayed precision allowed.
- **Best-seed cherry-pick**: paper says "achieves 90.2%" but that's the best of N seeds; mean is lower. Check if paper specifies "average" / "best" / "median".
- **Config mismatch**: paper compares A vs B, but they used different hyperparameters / datasets / splits. Verify config files show same settings.
- **Aggregation mismatch**: paper says "average over 5 seeds" but result files show only 3 runs. Count actual runs vs claimed count.
- **Delta error**: paper says "improves by 15%" but actual is 16.7%. Verify arithmetic of all relative improvements.
- **Caption-table mismatch**: figure caption describes something different from what the figure / table actually shows. Cross-check every caption against its content.
- **Scope overclaim**: paper says "consistently outperforms" but only tested on 2 datasets. Check if language matches actual evaluation scope.

Rounding rule: only standard rounding to displayed precision. 84.7% → 84.7% or 85% is OK. 84.7% → 85.3% is NOT OK.
