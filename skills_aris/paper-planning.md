# Paper Planning

## Style reference rules

- Style reference (when used) is structural only — guidance on section list, subsection counts, theorem density, figure budget. Never copy prose, claims, examples, section names verbatim, or terminology from the source. User's narrative is the only source of substance.
- Never pass style-ref (or cache contents) to reviewer / auditor sub-agents. Cross-model review independence requires reviewers see only the artifact and the user's prompt.

## Claims and structure

- Claim extraction: first check for upstream validated claims (from result validation). If exists, use as starting point — already mapped to evidence. Otherwise extract from narrative: core claims (3-5 main contributions), one-sentence contribution (single sentence that best states what the paper contributes), evidence per claim, known weaknesses, suggested framing.
- Build a **Claims-Evidence Matrix**: each row maps a claim → evidence → status (Supported / Partially supported) → target section. This is the backbone — every claim must map to evidence; every experiment must support a claim.
- Claims-Evidence Matrix is the backbone — every claim must map to evidence; every experiment must support a claim.

## Narrative principles

- Paper should tell one coherent technical story.
- By end of Introduction, the outline should make **What / Why / So What** explicit.
- Front-load: title, abstract, introduction, hero figure. Reviewers often judge before reading the full method.
- Front-load the story — outline should make the contribution clear in title + abstract + introduction + hero figure before the reader reaches the full method.

## Section structure

- Section count is flexible (5-8). Choose what fits the content best. Don't force content into a rigid 5-section template.
- Paper type shapes:
  - Empirical / Diagnostic: Intro / Related / Method / Experiments / Analysis / Conclusion.
  - Theory + Experiments: Intro / Related / Preliminaries / Experiments / Theory A / Theory B / Conclusion. Often 7 sections (split theory into estimation + optimization, or setup + analysis). Total budget must sum to page limit.
  - Method: Intro / Related / Method / Experiments / Ablation / Conclusion.
- Theory papers should include: proof sketch locations (not just theorem statements); comparison table of prior bounds vs this paper's; explicit appendix vs main-body proof split.

## Section-by-section

- **Abstract**: what we achieve / why hard / how / evidence / most remarkable result. Self-contained — readable without the paper. Length: 150-250 words.
- **Introduction**: opening hook, gap / challenge, one-sentence contribution, approach overview, key questions, 2-4 numbered specific falsifiable contributions, results preview, hero figure description (clear comparison if applicable), key citations. Length: 1.5 pages. Front-loading check: would a skim reader know the main claim before reaching the method?
- **Related Work**: 2-4 subtopic categories, positioning per category. Minimum 1 full page (3-4 substantive paragraphs). Organize methodologically / by assumption / by question — not paper-by-paper. Must synthesize, compare, position — not just list.
- **Method / Setup / Preliminaries**: notation, problem formulation, method description, formal statements (theorems, propositions), proof sketch locations.
- **Experiments / Main Results**: each figure with type (bar / line / table / architecture) + what comparison it shows; data source per figure.
- **Conclusion**: restatement (rephrased, not copy-pasted from intro), honest limitations, 1-2 future work directions.

## Figures

- Figure plan: every figure / table needs ID, type, description, data source, priority.
- Hero figure description must include: which methods being compared, what the visual difference should demonstrate, caption draft that clearly states the comparison, why the figure helps a skim reader understand the paper before reading the full method.
- Figures need detailed descriptions — especially the hero figure, which must clearly specify comparisons and visual expectations.

## Citation rules

- NEVER generate BibTeX from memory — verify via search or existing `.bib` files.
- Every citation must be verified: correct authors, year, venue.
- Flag any uncertain citation with `[VERIFY]`.
- Prefer published venue versions over arXiv preprints.
- Venue-specific citation: ML conferences use `natbib` (`\citep` / `\citet`); IEEE venues use `cite` package (`\cite{}`, numeric style).

## Review and constraints

- Cross-review the outline for: logical flow (story builds naturally?), claim-evidence alignment (every claim backed?), missing experiments or analysis, positioning relative to prior work, page budget feasibility, front-matter strength (title + abstract + intro + hero figure strong enough for skim-reading reviewers?).
- For each weakness, the reviewer should suggest the MINIMUM fix. Specific and actionable — "add X" not "consider more experiments".
- Do NOT generate author information — leave author block as placeholder or anonymous.
- Be honest about evidence gaps — mark claims as "needs experiment" rather than overclaiming.
- Page budget is hard — if content exceeds the limit, suggest what to move to appendix.
- Page counting differs by venue: ML conferences (ICLR / NeurIPS / ICML) count main body to Conclusion end, references / appendix NOT counted. IEEE venues: references ARE counted toward the page limit.
