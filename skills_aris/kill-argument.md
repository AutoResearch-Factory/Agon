# Kill Argument

Adversarial review that tests **headline-level survival** — whether the paper as a whole answers the worst rejection paragraph a senior area chair would write.

## Core insight

Standard score-based reviews (peer-review / research-review / auto-paper-improvement-loop) produce balanced weakness lists — each weakness gets ~equal attention. Empirically misses one failure mode: the **single most damaging argument** a reviewer would write in a rejection paragraph — the one sentence that, if a senior area chair reads it, kills the paper.

Balanced reviewer might list "scope-overclaim risk" as MAJOR alongside several other MAJORs, never quite committing. Adversarial reviewer **must commit**: entire job is to convince area chair to reject in ~200 words.

Asking one model to "write the rejection memo" produces qualitatively different feedback than asking it to "review and grade" — the former forces commitment, the latter encourages hedging.

Why kill-argument: improvement loop optimizes for score; claim audit verifies numbers; citation audit verifies cites — none catches the case where every local component is correct but the paper still oversells what it actually proves. Per-component audits verify local correctness; kill-argument catches headline-level overselling.

Most valuable for theory papers with several theorem-class environments (so headline depends on real proof obligations). Empirical papers without theorems → use peer-review instead.

## Attack phase

Simulate hostile reviewer (NeurIPS / ICLR / ICML). NOT a balanced review — construct the **single strongest argument for rejecting**. Read source carefully. Do NOT consult prior reviews / fix lists / summaries; fresh zero-context adversarial pass.

Attack target axes (pick most damaging combination, do NOT list all):
- **Theorem validity** — are central theorems actually proved as stated?
- **Assumption-vs-claim mismatch** — does body silently retreat to a narrower object than title/abstract advertise?
- **Missing proof obligations** — fundamental lemma invoked but not proved (concentration, generic position, prefactor envelope) that headline depends on?
- **Limit-order ambiguity** — limits in K/n/d/eps composed in a way the paper does not commit to?
- **Claim-vs-evidence gap** — empirical/numerical evidence too narrow to support breadth of stated theorem or take-away?
- **Scope overclaim** — title or abstract sells a result substantially broader than what body proves?

Attack constraints: approximately 200 words total (do NOT exceed 250); single argument, NOT a list — pick most damaging line and develop it; cite specific file:line / equation numbers when accusing; tone dispassionate but uncompromising, do NOT hedge, do NOT acknowledge mitigations the paper might have made elsewhere; do NOT reference prior review rounds or any context outside current files.

Attack must commit. Single argument, ~200 words. No "consider also" hedge.

## Adjudication phase

Independent area-chair adjudicator examining whether current paper text answers the rejection memo. NOT the paper's defender — read attack point-by-point, rule from current source alone whether each point stands or falls. Fresh, zero-context; do NOT reference prior reviews / fix lists.

Paste the verbatim attack memo. Decompose into atomic rejection points (a handful — neither one nor very many). Each point classified:
- **`answered_by_current_text`** — current paper source already mitigates this point (cite specific file:line evidence).
- **`partially_answered`** — paper has some response but not enough to refute the attack as written.
- **`still_unresolved`** — paper has no effective response.

Label `answered_by_current_text` is intentional — "fixed" implies history of patching and biases toward optimism. Adjudicator reads paper as a reviewer would, with no knowledge of prior round drafts.

Adjudicator constraints: do NOT consult prior round reviews or fix lists, strictly current paper files; if paper cannot refute a point, do NOT minimize, keep severity honest; author-chosen positions (deliberate title scope, deliberate omission of qualifier) marked `partially_answered` with note that position is intentional AND say whether sustainable under attack — do NOT auto-grade as `answered_by_current_text` just because intentional; be specific, no flattery, no hedging, no rationalizing on paper's behalf.

Adjudicator must classify, not minimize. `still_unresolved` is honest if paper has no effective response. Don't downgrade to `partially_answered` unless evidence is real.

## Constraints

Detect-only by direct invocation. Output is informational; human decides whether to act. This skill itself never edits paper files.
