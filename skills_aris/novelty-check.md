# Novelty Check

## Quick check (during brainstorm)

For each candidate idea, do 2-3 targeted searches to see if it's already been done. Full deep check comes later for survivors. Keep this stage cheap — the goal is to kill obvious duplicates, not to confirm novelty.

## Deep check (before commit)

### Decompose into claims first

Do not search the whole idea as one block. Identify 3-5 core technical claims that would need to be novel; for each claim, judge:

- What is the method?
- What problem does it solve?
- What is the mechanism?
- What makes it different from obvious baselines?

Searching at the claim level catches partial overlap that whole-idea search misses.

### Multi-source search per claim

For EACH core claim, search across all available sources:

- arXiv, Google Scholar, Semantic Scholar
- Known top-venue databases: ICLR 2025/2026, NeurIPS 2025, ICML 2025/2026
- Recent arXiv preprints (2025-2026)

Per claim:

- Use specific technical terms from the claim, not high-level keywords.
- Try at least 3 different query formulations.
- Include year filters for 2024-2026.

### Read both abstract AND related work

For each potentially overlapping paper, examine both the abstract AND the related work section. Related work is a fast prior-art summary — it tells you whether overlap is real without reading the full paper.

### Cross-model verification

Re-ask the same three questions using an external (different-model) reviewer with all surfaced papers in hand:

- Is this method novel?
- What is the closest prior work?
- What is the delta (between our method and the closest prior)?

A single model misses things; a second model with the same evidence catches them.

## Honesty rules

- Be BRUTALLY honest. False novelty claims waste months of research time.
- "Applying X to Y" is NOT novel unless the application reveals genuinely surprising insights.
- Check both the method AND the experimental setting for novelty. A new dataset, new constraint regime, or new evaluation protocol can sometimes carry the contribution even when the algorithm is reused.
- If the method is not novel but the FINDING would be, say so explicitly — the result is still publishable, but the framing has to change from "new method" to "new empirical insight".
- Always check the most recent 6 months of arXiv. The field moves fast and concurrent work is common; concurrent work that pre-dates our submission is the most common kill.
