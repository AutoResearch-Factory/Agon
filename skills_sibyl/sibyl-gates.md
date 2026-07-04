# Quality Gates & Decisions

## Research Contribution Review

Four dimensions weighted: Novelty (genuinely new? one-sentence contribution? changes how people think?), Technical Soundness (claims backed by evidence? method precise enough to reimplement? logical gaps?), Experimental Rigor (baselines fair and tuned? ablations isolating contribution? statistically meaningful? cross-validate against raw data), Reproducibility (result reproducible from paper alone?).

### NeurIPS-Calibrated Scoring

10: Award-quality. 9: Strong Accept. 8: Accept. 7.5: Borderline Accept. 7: Weak Accept. 6: Borderline Reject. 5: Reject. 4: Clear Reject. 3: Strong Reject. 1-2: Desk Reject. Do NOT inflate scores. Score work as-is, not potential. Be consistent across iterations. Cross-validate with raw data.

## Experiment Decision (PROCEED/PIVOT)

PROCEED: results outperform baselines or close with clear improvement path, core hypotheses validated, improvement effort manageable. PIVOT: core hypotheses refuted, results far below with no clear path, continued optimization not justified. Analyze: method feasibility, performance vs baselines, improvement headroom, time-cost tradeoff, critical objections fatal or addressable?

## Idea Validation (ADVANCE/REFINE/PIVOT)

Weighted decision matrix: Pilot signal (0.30) + Hypothesis survival (0.25) + Path to full result (0.20) + Novelty (0.15) + Resource efficiency (0.10). Score 1-5 per criterion.

ADVANCE: weighted ≥3.5, main hypothesis NOT falsified. REFINE: 2.5-3.5, or promise but methodology issues — state exactly what to change. PIVOT: all <2.5, or hypothesis falsified — state which evidence triggered pivot.

Sanity checks: compared ALL candidates? Penalized candidates failing their own falsification criteria? Not swayed by sunk cost? If inconclusive, defaulting to REFINE?

## Third-Party Review

Independent perspective from a different model ecosystem catches blind spots, ignored risks, and assumption gaps that internal reviewers miss. Review the research output, not re-litigate internal consensus. Do not block the pipeline if unavailable.

## Reviewer Simulation

Stay in character: evaluate from the specific reviewer's perspective, maintain their standards and expertise. Harsh original? Remain skeptical. Constructive? Be open. Per concern: addressed (fully/partially/not), convincing (strong/adequate/weak), evidence quality, score delta. Watch for: new problems introduced by rebuttal, inconsistencies with original paper, evasive responses.
