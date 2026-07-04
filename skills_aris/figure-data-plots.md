# Figure Data Plots

Publication-quality data-driven plots (matplotlib) — covers ~60% of a typical ML paper's figures. Remaining ~40% (hero figure, architecture diagram, qualitative results) need manual creation.

## Figure Type Selection

| Data Pattern | Recommended Type | Size |
|-------------|-----------------|------|
| X=time/steps, Y=metric | Line plot | 0.48\textwidth |
| Methods × 1 metric | Bar chart | 0.48\textwidth |
| Methods × multiple metrics | Grouped bar / radar | 0.95\textwidth |
| Two continuous variables | Scatter plot | 0.48\textwidth |
| Matrix / grid values | Heatmap | 0.48\textwidth |
| Distribution comparison | Box/violin plot | 0.48\textwidth |
| Multi-dataset results | Multi-panel (subfigure) | 0.95\textwidth |
| Prior work comparison | LaTeX table | — |

## Quality Checklist

- Font size readable at printed paper size (not too small)
- Colors distinguishable in grayscale (print-friendly)
- **No title inside figures** — titles go only in LaTeX `\caption{}`
- Legend does not overlap data
- Axis labels have units where applicable
- Axis labels are publication-quality (not variable names like `emp_rate`)
- Figure width fits single column (0.48\textwidth) or full width (0.95\textwidth)
- PDF output is vector (not rasterized text)
- No matplotlib default title (remove `plt.title` for publications)
- Serif font matches paper body text (Times / Computer Modern)
- Colorblind-accessible

## Key Rules

- Every figure must be reproducible — save the generation script alongside the output
- Do NOT hardcode data — always read from JSON/CSV files
- Use vector format (PDF) for all plots — PNG only as fallback
- No decorative elements — no background colors, no 3D effects, no chart junk
- Consistent style across all figures — same fonts, colors, line widths
- One script per figure — easy to re-run individual figures when data changes
- No titles inside figures — captions are in LaTeX only
- Comparison tables count as figures — generate them as standalone .tex files
