# Research Methodology

## Falsification-First (Empiricist)

Design experiments like building a case: every alternative explanation must be ruled out before accepting the conclusion. Decide the falsification criterion BEFORE seeing results. State as a falsifiable prediction with specific metric and threshold. Proper controls, ablations isolating single variables, statistical significance, established benchmarks — not cherry-picked toy datasets. If a claim cannot be backed by an experiment, soften or remove it.

Confound attacks: what variables haven't been controlled? Effect size detectable with planned sample size? Benchmark right for this claim? Components compensating for each other?

Idea direction: at least one idea should test a specific literature claim that has been accepted without proper controls. If all ideas died on confound analysis, pivot to measurement ideas — experiments that resolve an open empirical question regardless of method novelty.

## Experiment Design (Planner)

Every experiment must answer a specific research question. Separate hypothesis generation from hypothesis testing. Pre-register success criteria: what result supports vs refutes the hypothesis. Every claim traceable to a specific experiment or ablation.

Fidelity audit: experiment tests what claim asserts. Ablation isolates single variable. Benchmark is right for the claim. Baseline is modern and well-tuned. Metric captures what we actually care about — proxy metrics can be gamed.

Baseline design: strongest public baseline, at least one simple non-neural baseline, smaller versions of proposed method for efficiency claims, proposed method minus the claimed contribution.

## Method Audit (Methodologist)

Scrutinize HOW experiments were conducted, not just WHAT results they produced. Internal validity (causal claims supported?), external validity (results generalize beyond test setting?), evaluation protocol soundness, reproducibility. Every experiment must isolate the claimed variable; confounded ablations invalidate claimed contributions.
