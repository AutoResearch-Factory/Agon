# Paper Poster

Conference poster design system — from paper to print-ready A0 poster. Posters are visual-first: one page, bullet points only, figures dominant. A good poster tells the story in 60 seconds.

## Venue Color Schemes

Use deep, saturated colors for primary — pastel/light colors wash out on large posters viewed from distance. Each venue uses 3-color system: primary (dark, title bar), secondary (medium, section headers), accent (contrast, highlights).

| Venue | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| NeurIPS | `#4C1D95` deep purple | `#6D28D9` purple | `#2563EB` blue |
| ICML | `#7F1D1D` deep maroon | `#B91C1C` red | `#1E40AF` blue |
| ICLR | `#065F46` deep green | `#059669` green | `#0284C7` blue |
| CVPR | `#1E3A8A` deep blue | `#2563EB` blue | `#7C3AED` purple |
| GENERIC | `#1E293B` deep slate | `#334155` slate | `#2563EB` blue |

Never use light/pastel colors as primary — they look washed out on A0 posters. Always use the darkest shade as primary for the title bar.

## Layout Rules

**#1 cause of failure: content overflow.** The fixed grid silently clips content exceeding box bounds — no compilation error.

**#2 cause: large whitespace gaps.** Use fine-grained rows (e.g., rows=20 for A0 landscape, ~42mm per row) for precise control. Use `between=rowN and rowM` syntax (not `below=name`) — `below=` auto-places and leaves unwanted gaps.

### Row Count by Format

| Poster Size | Orientation | Rows | Columns | Row height |
|-------------|-------------|:---:|:---:|:---:|
| A0 | landscape | 20 | 4 | ~42mm |
| A0 | portrait | 20 | **3** | ~59mm |
| A1 | landscape | 16 | 3 | ~37mm |
| A1 | portrait | 20 | 2 | ~30mm |

### Portrait A0: 3 columns, NEVER 4
At 841mm width, 4 columns = ~195mm per column — too narrow for readable text at poster-session distance. 3 columns (~260mm) is the recommended default for content-rich papers.

### Cross-column alignment
All columns in a row band share identical row boundaries. Never mix row ranges across columns — creates visual misalignment. Card separation via left accent stripe + drop shadow, not grid spacing.

## Modern Card Design (Left Accent Stripe)

Instead of rounded boxes with colored headers, use **left accent stripe** design — cleaner, more modern, avoids "PowerPoint box" look.

4 card styles using venue's 3-color system:
- **redcard** (secondary stripe): Background, Key Idea, Ablation, References, Setup
- **bluecard** (accent stripe): Result figures, Benchmarks, Analysis
- **darkcard** (primary stripe): Contributions, Method
- **highlightcard** (primary fill): Key Takeaways / Conclusion

Card backgrounds must NOT be pure white (#FFFFFF). Use subtle tints matching each card's color family — barely visible but adds cohesion. Colorbox intensity: 18-25%, not 8-12% (faint is invisible on print).

## Font Size Rules (A0)

A poster viewed from 1.5m needs much larger fonts. Body text at 20pt on A0 is unreadable from more than 0.5m. 34pt is the minimum.

| Element | Font size |
|---------|:---------:|
| Title | 90pt |
| Author line | 42pt |
| Section headers | 42pt |
| Body text | 34pt |
| Stat callout numbers | 72pt |
| Equations | 32pt |
| Table cells | 30pt |
| Figure captions | 28pt |

## Content Budget

Total target: 300-500 words (excluding figure captions and stat callouts). A poster is NOT a paper summary — it's a visual guide. Each bullet: 5-8 words max, not full sentences. Target ~70% fill per card (breathing room), NOT 100%.

Numbers > words: "**42% less memory**" not "reduces memory usage by 42 percent". Max 8 words per bullet. No abstract paragraph — replace with stat banner: 3-4 large-number callout boxes showing headline results. Figures should occupy 40-50% of poster area.

## 4-Column IMRAD Layout
- Col 1: Background & Motivation + Contributions + References & QR
- Col 2: Dataset & Paradigms (fig) + Computational Models (equations)
- Col 3: Architecture (fig) + Result 1 (fig + stat table)
- Col 4: Result 2 (fig + stat table) + Ablation + Conclusion

## Key Rules

- Less text is more — 300-500 words total, 5-8 words per bullet
- Do NOT fabricate data — all numbers must come from paper sections
- No abstract paragraph — replace with stat banner
- Figures 40-50% of poster area
- Card backgrounds must NOT be pure white — use subtle tints
- Left accent stripe card design
- 4 card styles create visual rhythm across the poster
- Use inline math `$\displaystyle ...$` inside colorboxes, NOT display math `\[...\]` (adds margins causing overflow)
- Reduce equation font to 26-28pt inside narrow colorboxes
