# Writing Craft

Structural discipline for writing cohesive academic papers.

## Visual Communication

Every major claim supported by a figure, table, or diagram. Minimum: 1 architecture diagram (Method), 1 results table (Experiments), 1 analysis figure (Experiments/Discussion). Each figure self-explanatory with descriptive caption — reader should understand key point from caption alone. Unified visual style: consistent color palette (proposed vs baseline vs ablation), font ≥10pt, line width ≥1.5, grayscale-readable. Tables: bold best values, align decimals, include ± std. Prefer figures over text for trends, comparisons, distributions. Reference every figure in text before placement.

## Notation + Glossary

Unify all mathematical symbols and terminology before any section begins. Define every symbol by category with dimensionality. Specify preferred phrasing and abbreviations. No section may introduce novel notation or alternate terminology independently. If gaps are found while writing, update incrementally — never contradict existing definitions.

## Sequential Discipline

Write sections in strict order — each completed section constrains the next. Introduction defines the problem that Method solves, Method defines the approach that Experiments validates, Experiments produces data that Discussion interprets, Discussion raises questions that Conclusion answers. Forward-declare claims, notation, and references for later sections. Back-reference exactly, never paraphrase.

## Per-Section Requirements

Introduction: problem+motive, 3-4 contributions, preview method and key results, optional teaser figure, methods should begin by page 2-3. Related Work: organized by theme (not paper-by-paper), clearly indicate how this work differs from existing. Method: notation consistent, reproducible algorithm description, 1 architecture diagram minimum, pseudocode recommended. Experiments: setup consistent with Method, datasets/baselines/metrics clearly stated, main results table with bold best+std, 1 visualization minimum (trend/comparison/distribution), ablation study recommended. Discussion: based on actual data from Experiments, error analysis/case study figures recommended, propose future work. Conclusion: summarize contributions, echo questions raised in Introduction, no new content.

## Integration

After sections drafted: check narrative coherence (sections flow naturally?), notation consistency, terminology consistency, visual communication (figures near first reference?), claim-evidence alignment (every claim backed?). Cross-section verification: introduction claims supported in experiments, method matches what was implemented, related work accurate and fair, conclusion rephrased (not copy-pasted).
