# Figure Styling

CVPR/ICLR/NeurIPS academic figure style standards and review discipline — applies to AI-generated illustrations, architecture diagrams, and data plots alike.

## Visual Standards

- Clean white background — no decorative patterns or gradients (unless extremely subtle)
- Sans-serif fonts — Arial, Helvetica, or Computer Modern; minimum 14pt
- Subtle color palette — use 3-5 coordinated colors, not rainbow
- Print-friendly — must be readable and distinguishable in grayscale
- Professional borders — thin (2-3px), solid colors, not flashy

## Layout Standards

- Horizontal flow — left-to-right is the standard for pipelines
- Clear grouping — use subtle background boxes or spacing to group related modules
- Consistent sizing — similar components should have similar sizes
- Balanced whitespace — not cramped, not sparse

## Arrow Standards

- Thick strokes — 4-6px minimum (thin arrows disappear when printed)
- Clear arrowheads — large, filled triangular heads
- Dark colors — black or dark gray (#333333); avoid colored arrows
- Labeled — every arrow should indicate what data flows through it
- No crossings — reorganize layout to avoid arrow crossings
- CORRECT DIRECTION — arrows must point to the RIGHT target

## Color Palette (Academic Professional)

- Inputs: green (#10B981 / #34D399)
- Encoders: blue (#2563EB / #3B82F6)
- Fusion: purple (#7C3AED / #8B5CF6)
- Outputs: orange (#EA580C / #F97316)
- Arrows: black or dark gray (#333333 / #1F2937)
- Background: pure white (#FFFFFF)

## Visual Appeal

Should have:
- Subtle gradient fills — same-color-family, not rainbow
- Rounded corners — 6-10px radius, modern but restrained
- Clear visual hierarchy — size and color depth to distinguish layers
- Consistent color coding — 3-4 main colors with stable semantics
- Internal structure — major modules show sub-components inside
- Professional typography — clean labels, readable size hierarchy

Avoid:
- Rainbow color schemes
- Heavy drop shadows or glowing effects
- 3D perspective effects
- Excessive decorative icons or clip art
- Slide-deck / PPT-template styling that feels flashy
- Flat, boring box soup with no hierarchy

Ideal effect: professional, clear at a glance; moderate visual appeal without being decorative; appropriate for top-tier conference paper figure; survives PDF scaling and grayscale printing.

## Style Reference Rules

- Style reference (when used) is structural only — align caption length, figure density, and visual cadence with reference paper. CVPR/ICLR/NeurIPS visual standards above still take precedence.
- Never copy figure content, color palettes, or specific design elements from the reference. Visual design comes from user's prompt.
- Never pass style-ref (or cache contents) to reviewer sub-agents when scoring — image must be judged on its own merits.

## Review Discipline

Arrow correctness is non-negotiable — any wrong arrow direction = reject. Block content must be verified — wrong content = reject. Be specific in feedback: "Arrow from A to B points to wrong target C" not "arrow is wrong". Accept only excellence, not "good enough". Visual appeal matters — plain boring figures need improvement. Save all iterations for comparison. Never accept a figure that is logically wrong just because it looks attractive. Accept only figures that look paper-ready, not slide-ready. Prefer 1-3 strong refinement rounds over many shallow ones.

Every review must check: arrow correctness (wrong direction = automatic fail), block content correctness, arrow visibility (thick, clear arrowheads, dark colors), arrow labels (every arrow labeled, readable), visual appeal (balanced — neither too plain nor too flashy), layout and flow (left-to-right, no crossings, traceable in 5 seconds), style compliance (venue standards, font readable, print-friendly).
