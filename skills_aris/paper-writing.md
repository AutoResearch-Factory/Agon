# Paper Writing

## Style reference rules

- Style reference (when used) is structural only — section count, ordering tendency, theorem density, caption-length distribution, sentence cadence, math display ratio, citation style. Never copy prose, claims, examples, or terminology from the source.
- Never pass style-ref or cache contents to reviewer / auditor sub-agents. Cross-model review independence.
- Forward style-ref only to writer-side sub-skills (planning, writing, illustration). Do NOT forward to reviewer / auditor.

## Section drafting

- Backup before overwriting `paper/` — never silently destroy existing work.
- Clean stale section files when changing section structure (e.g., 5 → 7 sections, old `5_conclusion.tex` left behind after restructure causes confusion).
- Section files flexible — match PAPER_PLAN, don't force into rigid 5 sections.
- Before drafting front matter, re-read one-sentence contribution from PAPER_PLAN. Abstract + Introduction should make that takeaway obvious before the reader reaches the full method.
- Section drafting produces complete LaTeX (not placeholders).
- Write complete sections, not outlines.
- One file per section — modular for easy editing.

## Abstract

- 5-part flow: what / why hard / how / evidence / strongest result.
- Self-contained — readable without the paper.
- Start with paper's specific contribution, NOT generic field-level background.
- Include one concrete quantitative result.
- 150-250 words.
- No citations, no undefined acronyms.

## Introduction

- Open with a compelling hook (1-2 sentences, problem motivation).
- State the gap clearly ("However, ...").
- Give brief approach overview before reader gets lost in details.
- List 2-4 specific, falsifiable contributions as numbered / bulleted list.
- Preview the strongest result early instead of saving for experiments.
- End with brief roadmap.
- Include main result figure if space allows.
- Methods should begin by page 2-3 at the latest.

## Related Work

- Minimum 1 full page (3-4 substantive paragraphs). Short related work is a common reviewer complaint.
- Organize by category using paragraph headers.
- Organize methodologically, by assumption class, or research question — NOT paper-by-paper mini-summaries.
- Each category: 1 paragraph summarizing the line of work + 1-2 sentences positioning this paper.
- Do NOT just list papers — synthesize and compare.
- End each paragraph with how this paper relates / differs.

## Method / Preliminaries

- Define notation early (reference math macros).
- Use formal environments (`\begin{definition}`, `\begin{theorem}`) for formal statements.
- Theory papers: include proof sketches of key results in main body, full proofs in appendix.
- Theory papers: include a comparison table of prior bounds vs this paper.
- Include algorithm pseudocode if applicable.

## Experiments

- Start with experimental setup (datasets, baselines, metrics, implementation).
- Main results table / figure first.
- Then ablations and analysis.
- Every claim from intro must have supporting evidence.
- For each major experiment, make explicit what claim it supports and what the reader should notice.

## Conclusion

- Summarize contributions (rephrase — NOT copy-paste from intro).
- Limitations — honest, reviewers appreciate.
- Future work (1-2 concrete directions).
- Ethics + reproducibility statements (if venue requires).

## Appendix

- Proof details (full proofs of main-body theorems), additional experiments / ablations, implementation details + hyperparameter tables, additional visualizations.

## Theory paper consistency

- Do NOT leave placeholders like "see supplementary proof document" or "proof omitted for brevity". Main body proof sketches stay short, but appendix never sketch-only when a full proof source exists. Use main-body theorem statement as canonical public statement; appendix copy must match.
- Restatement audit: compare every theorem / lemma / proposition statement restated in appendix against main-body version. Audit only statements, hypotheses, case splits, quantifiers, domains, notation, variable names, terminology — do NOT diff proof bodies. Mismatches like `stationary` vs `terminal`, changed assumption names, or missing case splits must be resolved or explicitly documented. If appendix needs different wording, add an explicit notation bridge instead of silently renaming.

## Bibliography

- Only include entries actually cited.
- NEVER fabricate BibTeX from memory.
- LLM-generated BibTeX frequently hallucinates venue names, page numbers, co-authors. Verify against DBLP or CrossRef, which return publisher-verified metadata.
- Every BibTeX entry must have author + title + year + venue/journal. Prefer published venue versions over arXiv preprints.
- Consistent key format: `{firstauthor}{year}{keyword}`. Remove duplicates (same paper, different keys).
- Entry is dead if its key doesn't appear in any `\cite` command — dead entries cause bib bloat and metadata drift.
- Enforced bib hygiene validation: verify each cited entry — year disagreement, venue/journal disagreement, first-two-author list differs, both DBLP and CrossRef unreachable.
- Clean bib — `references.bib` must only contain `\cite`d entries.

## Writing quality (5 audit passes)

**Pass 1: Clutter Extraction.** Replace cluttered phrases:
- "Due to the fact that" → "Because"
- "In order to" → "To"
- "A number of" → "Several"
- "It is worth noting that" / "It is important to note that" → delete
- "On the basis of" → "Based on"
- "Have an effect on" → "Affect"
- "Give rise to" → "Cause"

Remove redundancies ("completely eliminate" → "eliminate"; "future plans" → "plans").

Remove AI-isms: delve, pivotal, landscape, tapestry, underscore, noteworthy, intriguingly.

**Pass 2: Active Voice and Verb Vitality.** Spot passive ("to-be" verb + past participle), convert to active. Resurrect smothered verbs (nominalizations): "We made an investigation" → "We investigated"; "Provides a description of" → "Describes". Passive IS acceptable for established facts, methods where agent is irrelevant, or when required by venue style.

**Pass 3: Sentence Architecture.** Flag sentences > 40 words for splitting. Subject and verb close together (no long parenthetical insertions). Familiar context first, new information later. Most important point near end of sentence. Each paragraph does one job. Don't start consecutive sentences with "This" or "We". Each paragraph's first sentence connects to the previous.

**Pass 4: Keyword Consistency — Banana Rule.** Do not call a "banana" an "elongated yellow fruit" to avoid repetition. If Methods say "obese group," Results must NOT switch to "heavier group." Synonym variation forces reader to wonder if a new category exists. Extract all key terms from Method; verify same terms appear in Results / Discussion / Tables / Figure captions. Flag every synonym substitution for a defined term. Acronym austerity: flag non-standard acronyms created only for convenience; verify every acronym defined at first use.

**Pass 5: Numerical and Citation Integrity.** Sample size (N) in Abstract matches Table 1? Percentages in Results match raw numbers in Tables? Significant figures consistent? Figure graphics match Table values? Flag statistics cited only through secondary sources (reviews, textbooks) — recommend verifying primary source.

## Review and quality standards

- Cross-review the draft for: claim-evidence coverage; clear, concise writing free of AI-isms; logical gaps; page limit fit; related work ≥ 1 page; proof sketches adequate (theory); figure / table descriptions and references; skim-reader can grasp contribution from title + abstract + intro + Figure 1.
- Reverse outline test: extract topic sentences (first sentence of every paragraph), read them in sequence — should form a coherent narrative on their own. Every claim from Claims-Evidence Matrix must appear. Every experiment / figure must support a stated claim. If a topic sentence doesn't advance the story, rewrite the paragraph.
- Quality standards: no undefined references or citations; no TODO / FIXME / XXX / `[VERIFY]` markers; abstract self-contained; title specific and informative; related work ≥ 1 full page; `references.bib` contains ONLY cited entries; skim reader can recover the main claim from title + abstract + intro + Figure 1.

## Systems papers

For systems venues (OSDI/SOSP/ASPLOS/NSDI/EuroSys), page budget: Abstract (~0.25p) → Introduction (1.5-2p) → Background (1-1.5p) → Design (3-4p, diagram first) → Implementation (0.5-1p) → Evaluation (3-4p) → Related Work (1p, by methodology) → Conclusion (0.5p). Key principles: define-before-use; every design choice must discuss alternatives; abstract cannot use terms introduced in the paper; every evaluation conclusion stated three times (hypothesis, conclusion, caption); related work grouped by methodology, not paper-by-paper.

## Constraints

- Do NOT generate author names, emails, or affiliations — anonymous or placeholder.
- Every claim must cite evidence — cross-reference Claims-Evidence Matrix.
- No over-claiming — use hedging language ("suggests", "indicates") for weak evidence.
- Venue style matters — ML conferences use `natbib` (`\citep` / `\citet`); IEEE venues use `cite` (numeric). Never mix.
- Page limit rules differ by venue — ML: main body to Conclusion, refs / appendix NOT counted. IEEE: refs ARE counted.
- Front-load the contribution — do not hide the payoff until experiments or appendix.
