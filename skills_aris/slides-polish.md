# Slides Polish

Post-generation visual polish for presentation decks — layout and typography only, never content.

## Hard Scope

Polishes layout and typography only:
- Does NOT rewrite content, claims, numbers, citations, URLs, author names, affiliations, experiment results
- Does NOT add, remove, or reorder slides unless explicit user flag
- Does NOT generate outlines, speaker scripts, or new decks from paper source
- Does NOT change figures or equations content

## Hard Invariants

1. **Reference is required.** Never polishes without explicit visual anchor.
2. **Original is never overwritten.** All edits target versioned copy; original snapshot preserved.
3. **Speaker notes are preserved verbatim.** Byte-for-byte verified against snapshot.
4. **No content edits.** Only style/typography/box edits. If a proposed change touches content, stop and report.
5. **No slide reordering** unless explicit flags.
6. **Cross-model independence.** Per-page review calls are fresh threads, never sharing context.
7. **Anonymity placeholders fail closed.** If a proposal fills in real title/count/URL where a placeholder was, reject and surface for human review.
8. **Page numbers stay ≤ 16pt.**
9. **`reasoning_effort: xhigh`** invariant.
10. **Robust shape selection.** Edits use unique-prefix text matching; if duplicate matches found, abort and request disambiguation.

## Fix Patterns

**Beamer**:
- Frame title underline: use `beamercolorbox` with `\hrule` AFTER title text, not bare `\rule{}` outside
- Section labels: small caps, wide-tracked, accent color — avoid `\MakeUppercase` with inline color (uppercases color name → error)
- `array` package needed for ragged-right p-columns in cards (without it, tabular cells justify and create rivers)
- Banner = real `tcolorbox`, not `\begin{center}\color{...}`
- Em-dash spacing: prefer `\textemdash{}` or `\,---\,` over bare `—`
- CJK + math: set East Asian fonts explicitly; mixed Chinese-English titles need EA font hint or characters fall back to Latin

**PPTX**:
- Image aspect ratio: bumping width without height stretches PNGs; compute height from aspect ratio
- Banner = real filled rectangle behind text frame, not just colored text
- Italic style leak: wrap italic scope in `{...}` to prevent inheritance across runs
- Chinese rendering: needs East Asian font hint (macOS: PingFang SC, Windows: Microsoft YaHei); without it, characters render as tofu boxes
- Em-dash spacing: bare `—` in titles renders with collapsed spaces; insert spaces or use figure-space
- Label positioning: ensure bbox stays inside slide bounds (left > 0.4in, top > 0.4in) — content is silently clipped otherwise
- Anonymity placeholders: use generic phrasing ("Withheld for anonymous review", "[anonymized]"); never infer or fill in real titles, counts, or URLs

## Font Scaling Heuristic (Beamer → PPTX)

| Beamer pt | PPTX target | Role |
|---|---|---|
| 8 | 14-18 small caps | section labels |
| 10 italic | 14 italic | gray italic cue |
| 11 body | 22-24 | bullets, paragraphs |
| 12 page number | 16 (cap) | bottom-right gray |
| 14 emphasis | 22-24 | bigger sub-headers |
| 16 callout | 24-28 | box content |
| 17-22 big number | 28-36 | hero stats |
| 22 frame title | 40-44 | every page title |
| 28 emphasis hero | 36-44 | hero text |
| 42 cover wordmark | 80-100 plain BLACK | cover |

Page-number rule: never bump page numbers above 16pt. After font bump, always re-check text-frame overflow.

## Per-Page Review Philosophy

Per-page review converges in 1-2 rounds where single-pass batch review never converges. Each review is a fresh thread comparing the slide against a reference page, returning specific fixes identified by shape text content (never by index — index drifts). If a fix would change content, stop and report instead of applying.
