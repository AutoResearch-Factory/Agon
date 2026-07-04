# LaTeX Typesetting

## Template Discipline

Use official venue template as skeleton — never invent new structures. The template's preamble, title block, and bibliography structure are authoritative.

## Table Rules

Booktabs package (`\toprule`, `\midrule`, `\bottomrule`). Bold best values, align decimals. Use `\pm` for standard deviations. Never use vertical rules.

## Figure Rules

Architecture diagrams to TikZ. Descriptive captions — self-contained, 1-2 sentences. Label every figure. Process all visual elements before compilation. Copy figures into the LaTeX directory; don't symlink.

## Compilation

Compile only after all sections, figures, tables, and bibliography are in place. Check for undefined references and citations. Fix errors before accepting the PDF.
