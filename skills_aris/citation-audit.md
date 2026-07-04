# Citation Audit

Citation verification before submission — checks every cited reference across three axes against canonical sources via live web lookup.

## Dangerous citation problems

The dangerous citation problems are NOT wildly fake citations (easy to spot). Dangerous ones:
- **Wrong-context**: real paper, but the cited claim is not what that paper establishes (e.g., citing Self-Refine to support "self-feedback produces correlated errors" — Self-Refine argues the opposite).
- **Author hallucinations**: anonymous placeholders slipped through, missing co-authors, wrong order.
- **Title drift**: arXiv v1 vs v3 with different titles silently merged.
- **Venue confusion**: arXiv preprint cited but official venue is now CVPR/ICML/NeurIPS — using wrong record.
- **Year mismatch**: arXiv preprint with later conference acceptance, year inconsistent.
- **Phantom DOIs**: DOI looks real but does not resolve.
- **Self-citation drift**: your own prior work cited with year off by one.

Why citation audit is the most diagnostic: wildly fake citations are easy to spot. The dangerous failure mode is a real paper cited in a context it doesn't actually support — slips past metadata-only checks and damages submission credibility.

## Three audit layers

1. **Existence** — paper actually exists at claimed arXiv ID / DOI / venue.
2. **Metadata correctness** — author names, year, venue, title match canonical sources (DBLP, arXiv, ACL Anthology, Nature, OpenReview).
3. **Context appropriateness** — cited paper actually supports the claim it is being used to support.

## Verification axes

Reviewer examines each citation across: EXISTENCE (YES/NO/UNCERTAIN + verifying URL), METADATA per field (correct / wrong: should be ... / typo), CONTEXT per use (SUPPORTS / WEAK / WRONG + one-sentence reasoning). Final VERDICT: KEEP / FIX / REPLACE / REMOVE. Be honest; if cannot verify online, say UNCERTAIN.

Web access required. Reviewer must do real lookups, not memory pattern-match.

## Per-entry verdict semantics

- **KEEP**: entry clean, all uses appropriate.
- **FIX**: metadata needs correction; uses appropriate.
- **REPLACE**: cite is wrong-context — find a different paper that actually supports the claim.
- **REMOVE**: entry is hallucinated or unsupportable.

Wrong-context > metadata. A real paper used to support a wrong claim is more dangerous than a typo in author name.

## Uncited entry detection (opt-in)

- Uncited entries are detect-only; never sent to reviewer.
- Opt-in by default disabled. Why: surfacing uncited by default would change output for every existing run AND noise up the verdict for users who intentionally maintain a superset bib file.
- Suggestion: `prune` default; `check` only when concrete local evidence exists (e.g., `% TODO: cite X` comment, recently removed `\cite` visible in diff). Do not infer intent from the bib key string alone.
- Fallback: if bib enumeration fails, the cited-entry audit must still proceed. Mark uncited as unavailable.
- Uncited detection is opt-in only. Never auto-enable; never block on uncited; existing callers must observe identical output if they do not opt-in.

## Soft-only mode

For callers operating under hard "freeze the bib" constraint. If a citation is wrong-context, soften the surrounding sentence; do NOT change, add, or remove the cite itself.

Soft-only invariant: audit semantics UNCHANGED — existence + metadata + context-appropriateness all run, reviewer still invoked once per cited entry, per-entry verdicts still emitted exactly as default. Only the action layer changes.

Soft-only verdict translation:
- `KEEP` → `keep_unchanged` (no action).
- `FIX` (metadata wrong) → `keep_metadata_drift_acknowledged` (bib stays; flag for human review).
- `REPLACE` (wrong-context) → `soften_citing_sentence` (per-occurrence sentence-rewrite proposal that does not claim what the cited paper actually establishes).
- `REMOVE` (hallucinated paper) → `drop_cite_in_body_only` (bib entry untouched; inline `\cite{X}` MUST be removed and sentence rewritten). Never leave a `\cite{X}` to a hallucinated paper — reviewers will check the reference and find nothing.

Soft-only hard guarantees: no bib mutations under any circumstance; only `*.tex` rewrite proposals (still require human approval); downstream caller proposing bib edit under soft-only is refused; wrong-context still FAIL; soft-only composes with uncited.

Under soft-only, never mutate the bib regardless of finding severity. Text-rewrite proposals only.

## Constraints

- REPLACE/REMOVE require human approval. Never auto-modify content claims.
- Audit is wall-clock expensive (web lookup per entry); not for every save.
