# Paper Resubmit

Resubmitting a polished paper to a different venue under hard constraints — text-only microedits, no new experiments, no new theorems, no new citations, no framework changes.

## Hard Invariants

1. **Never overwrite prior submission directories.** The new venue's submission lives as a sibling of all prior venues. Physical copy, never symlink, never cross-directory input from shared pool.
2. **Bib is frozen.** All citation findings translate to text-rewrite proposals, not bib edits.
3. **Edit whitelist is binding.** Every edit round respects path and operation constraints; rejections logged, never silently dropped.
4. **Per-round diff gate is mandatory.** Multi-round drift is the highest-risk failure mode — small softenings across rounds can compound into meaningful framing change. Each round's diff must be inspected before the next round.
5. **Convergence criteria are fixed.** Default 2 rounds. Loop does not auto-extend.
6. **Anonymity scan is 5-layer.** Surface identifiers, self-citation phrasing, acknowledgments, cross-rebuttal references, internal codenames — not just author surname grep.
7. **Kill-argument is residual-risk reporting, not auto-rewrite.** Adjudicator's unresolved critical points must be surfaced, not blindly trigger extra rounds.
8. **Resubmit is a fundamentally different scope.** Paper is already polished; only text-only microedits allowed. No new experiments, no new theorems, no new citations, no framework changes.

## Page-Shrink Heuristic

When page overflow detected, apply in order (least risky to most risky):
1. Compress conclusion (cut future-work prose)
2. Tighten abstract/intro hedging
3. Move marginal figures to appendix
4. Move proof sketches/extended remarks to appendix
5. Compress related-work prose

Forbidden: removing experiments, removing theorems from main, removing citations (bib frozen). Stop as early as page limit is met.

## Composition Rules

- New main file written fresh for target venue's style; only title, author, abstract, and section input lines are ported
- Section files physically copied (not symlinked, not cross-directory included) — symlinks break export
- Figures copied in, not symlinked; watch for path traps
- Bibliography written directly in new main; never input an existing ref file that contains its own bibliography command

## Key Rules

- Never overwrite prior submission directories — single hardest invariant
- Bib is frozen — citation audit must use text-rewrite mode only
- Edit whitelist binding — rejections logged, per-round summary shown
- Per-round diff gate mandatory — compound drift is the highest-risk failure mode
- Convergence criteria are fixed — default 2 rounds, loop does not auto-extend
- Anonymity scan is 5-layer, not just author surname grep
- Kill-argument result surfaces unresolved issues for review; it is not an auto-rewrite directive
- Page-shrink heuristic ordered "least to most risky"; stop as early as page limit met
