# Paper Compile

## Post-compilation quality signals

- No "??" in PDF (undefined references).
- No "[?]" in PDF (undefined citations).
- Figures rendered (not missing-image placeholders).
- No overfull content visibly extending past margins.

## Page count by venue

- **ML conferences**: main body = first page through end of Conclusion. References + appendix NOT counted.
- **IEEE venues**: TOTAL page count including references must fit the limit.

## Stale file detection

- `.tex` files under `sections/` not `\input`ed by `main.tex` cause confusion when section structure changes.

## Submission readiness

- Anonymous: no author names, affiliations, or self-citations revealing identity.
- Appendix clearly separated after `\newpage\appendix`.
- No `[VERIFY]` markers remaining.
- Font embedding is critical — some venues reject PDFs with non-embedded fonts.

## Constraints

- Never delete the user's source files — only modify to fix errors.
- Don't suppress warnings — report them, let the user decide.
