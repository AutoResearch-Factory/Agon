# Pipeline Meta

## Pipeline order

The default research idea-discovery pipeline goes:

```
literature survey → idea generation → novelty check → external review → method refinement → experiment planning
```

Each phase builds on the previous one's output. Skip a phase and downstream work gets worse, not faster.

## Don't skip phases

Each phase exists because it filters and validates. Skipping the filter doesn't save time — it just relocates the cost to later, when fixes are more expensive. Better to kill 10 bad ideas at novelty-check than to implement one and find out.

## Checkpoint between phases

After every phase, briefly summarize what was found before moving on. The summary is for the user to redirect, and for future-you to reconstruct why the project went the way it did.

Typical checkpoint branches:

- **User approves (or no response under AUTO_PROCEED)** → proceed with current best.
- **User requests scope adjustment** → re-run the current phase with the adjusted scope, present again, repeat.
- **User unhappy with output** → collect feedback ("what's missing?", "what direction do you prefer?"), update the prompt with constraints, re-run.
- **User wants to back up** → return to an earlier phase with refined inputs.

## Triage when resuming

When picking up mid-pipeline:

- Extract problem / approach / constraints / resources / target venue from current state.
- Check if downstream outputs (proposal, experiment plan, etc.) still match the current request.
- If existing outputs are stale or materially diverged, re-run the upstream phase rather than patching a misaligned downstream.
- In doubt: prefer re-running an upstream phase over forcing a downstream phase onto a wrong upstream.

## Don't run downstream on unstable upstream

Don't plan a large experiment suite on top of an unstable method. First stabilize the thesis; then turn the stable thesis into experiments. Same applies one level up: don't refine a method on an unstable problem anchor.

## Lite mode for degraded inputs

If an upstream phase produced weak output (reviewer score below threshold, pilot signal weak or absent), run downstream in **lite mode**: skip the most ambitious downstream phase, run only the essential one, and note the remaining risks in the report. Don't pretend the input is healthier than it is.

## Document everything

Save every raw reviewer response, every anchor check, every simplicity check, every major method or scope change. Dead ends are just as valuable as successes for future reference — if you didn't write down why you killed an idea, you'll re-investigate it in 3 months.

## Use staged skills when only one stage is needed

If only one stage is needed (just refine a method, just plan experiments), use the staged skill directly. The end-to-end pipeline skill is for integrated flow, not a heavier-handed default.

## Gate before expensive compute

Before committing expensive GPU time and multiple review rounds, evaluate which idea to pursue. The gate prevents running expensive compute on the wrong idea.

## Budget awareness

Track resource budget across the pipeline. Flag if approaching limits.

## Stage handoff

Every stage updates its own output file; full history should be self-contained. If any stage fails (no good ideas, experiments crash, review loop stuck), report clearly and suggest alternatives rather than forcing forward. If review loop ends at max rounds without positive assessment, stop and report remaining issues — do not loop forever.

## Knowledge accumulation

Failed ideas are the most valuable memory — never prune them. One source of truth for relationships; derived views are auto-generated. Canonical IDs everywhere — never raw titles or inconsistent shorthands. Deterministic knowledge compression, not open-ended summarization. Append to log for every mutation — the audit trail is load-bearing.

## Harness optimization

Improving the harness itself from usage data. Every proposed change must cite specific data from event logs. Analysis dimensions: frequency (which skills used most? parameter overrides most common?), failure (which tools fail most? error patterns?), convergence (rounds to threshold, score trajectory), intervention (where do manual corrections occur?). Rules: log-driven, not speculative; minimal patches; reviewer-gated; reversible; honest about uncertainty.

## Grant proposals

Grant proposals argue for future work (feasibility + potential), not completed work (results + claims). Agency-mandated section order always takes precedence over any style reference or generic structure. Never copy proposal prose, claims, or budget items from references. Never pass style-ref to reviewer — proposal must be judged on its own merits.
