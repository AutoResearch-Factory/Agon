# Paper Slides

Conference presentation slide design and talk pipeline constraints. Slides tell a temporal story — each slide builds on the previous one.

## Talk Type → Slide Count

| Talk Type | Duration | Slides | Content Depth |
|-----------|----------|:------:|---------------|
| poster-talk | 3-5 min | 5-8 | Problem + 1 method + 1 result + conclusion |
| spotlight | 5-8 min | 8-12 | Problem + 2 method + 2 results + conclusion |
| oral | 15-20 min | 15-22 | Full story with motivation, method detail, experiments, analysis |
| invited | 30-45 min | 25-40 | Comprehensive: background, related work, deep method, extensive results |

## Presentation Rules

| Rule | Rationale |
|------|-----------|
| One message per slide | If a slide has two ideas, split it |
| Max 6 lines per slide | More than 6 lines = wall of text |
| Max 8 words per line | Audience reads, not listens, if text is long |
| Sentence fragments, not sentences | "Improves F1 by 3.2%" not full sentence |
| Figure slides: figure ≥60% area | The figure IS the content; bullets are annotations |
| Bold key numbers | "Achieves **94.3%** accuracy" |
| Progressive disclosure | Reveal complex slides gradually |
| No Related Work slide | Unless invited talk (30+ min) |
| Opening hook matters | Never start with "In this paper, we..." — start with problem or provocative question |

## Slide Templates

**Oral** (15-22 slides): Title → Outline → Motivation & Problem (2-3) → Key Insight → Method with hero fig (4) → Results per slide (5) → Analysis/Ablations (2) → Limitations → Conclusion → Thank You + QR

**Spotlight** (8-12 slides): Title → Problem (2) → Key Insight → Method condensed (2) → Key Results (3) → Takeaway → Thank You + QR

**Poster-talk** (5-8 slides): Title → Problem → Method with fig → Key Result (2) → Takeaway + QR

## Speaker Notes

For each slide: what to say (2-3 sentences, conversational tone), timing hint, transition phrase to next slide. Also generate full talk script — word-for-word manuscript with time budget, anticipated Q&A, and transition cues.

## Font Size Minimums
- Title: ≥28pt, Body: ≥20pt, Footnotes: ≥14pt
- No navigation symbols; frame numbers in bottom-right; clean white background

## Hard Invariants

1. **Original paper is read-only.** Never modifies paper artifacts.
2. **Original deck is preserved.** Baseline → polished versioned copy; original never overwritten.
3. **Speaker notes are byte-stable.** Polish must not change speaker note content.
4. **No new content anywhere.** All slide text, speaker notes, claims, numbers, citations, URLs, author names must be paper-grounded or explicitly user-provided.
5. **No slide reordering** unless explicit user flags.
6. **Cross-model independence.** Per-page review calls use fresh threads.
7. **Anonymity fail-closed.** If any step would replace a placeholder with real content, halt and surface for human review.
8. **Style references are guidance, not text source.** Reference informs visual weight; never copy prose, examples, slide titles, or speaker-note text.
9. **Final output cannot be conference-ready unless required audits pass.**
10. **`reasoning_effort: xhigh`** invariant across all effort levels.

## Key Rules

- One message per slide — split multi-idea slides
- Do NOT fabricate data — all numbers from paper sections
- Bullet points only — never full sentences on slides, sentence fragments are fine
- Figure slides: figure ≥60% of slide area
- Progressive disclosure for complex method slides
- Opening hook matters: never "In this paper, we..."
- Font size minimums: title ≥28pt, body ≥20pt, footnotes ≥14pt
