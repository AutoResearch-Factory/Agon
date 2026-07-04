# Method Refinement

## Four governing principles

1. **Do not lose the original problem.** Carry the Problem Anchor verbatim into every round.
2. **The smallest adequate mechanism wins.** Prefer the minimal intervention that directly fixes the bottleneck. Bigger is not automatically better.
3. **One paper, one dominant contribution.** Prefer one sharp thesis plus at most one supporting contribution. A long module list is not novelty.
4. **Modern leverage is a prior, not a decoration.** Use LLM / VLM / Diffusion / RL / distillation / inference-time scaling concretely when they naturally fit the bottleneck. Do not bolt them on as buzzwords.

## Goal

Turn a vague direction into a **problem → focused method → minimal validation** document — concrete enough to implement, elegant enough to feel paper-worthy, current enough to resonate in the foundation-model era.

## Pipeline shape

Freeze Anchor → scan grounding papers → identify the technical gap → choose the sharpest route → write the focused proposal → external method review (7-dim scoring) → revise with anchor + simplicity check → re-evaluate in the same review thread → repeat the review-revise loop until the score crosses threshold or max rounds reached.

## Scan grounding before designing

Read existing literature focused on **method sections, training setup, and failure modes** — not just abstracts. Answer:

- What mechanism do current methods use?
- Where exactly do they fail for this problem?
- Which recent foundation-model-era techniques are actually relevant here?
- What training objectives, representations, or interfaces are reusable?
- What details distinguish a real method from a renamed high-level idea?

## Identify the gap operationally

Don't stop at generic research questions. Make the gap concrete:

- **Current pipeline failure point**: where does the baseline break?
- **Why naive fixes are insufficient** (larger context, more data, prompting, memory bank, stacking modules).
- **Smallest adequate intervention**: least additional mechanism that could plausibly fix the bottleneck.
- **Frontier-native alternative**: a more current route using foundation-model-era primitives, if it matches the bottleneck better.
- **Core technical claim** that could survive top-venue scrutiny.
- **Required evidence**: minimum proof needed to defend the claim.

## Compare two candidate routes

If both are plausible:

- **Route A: Elegant minimal route** — smallest mechanism that directly targets the bottleneck.
- **Route B: Frontier-native route** — modern primitive (LLM / VLM / Diffusion / RL / distillation / inference-time scaling) ONLY IF it gives a cleaner or stronger story.

Decide by asking:

- Which is more likely to become a strong paper under the stated constraints?
- Which has the cleaner novelty story relative to the closest work?
- Which avoids contribution sprawl?

If both are weak, rethink the framing instead of combining into a larger system.

## Concretize the method (11 dimensions)

The proposal must answer "how would we actually build this?" Prefer reuse over invention. Cover:

1. **One-sentence method thesis** — single strongest mechanism claim.
2. **Contribution focus** — one dominant + at most one supporting.
3. **Complexity budget** — what's frozen / reused, what's new, what tempting additions are intentionally excluded.
4. **System graph** — modules, data flow, I/O.
5. **Representation design** — what latent / embedding / plan token / reward signal / memory state / alignment space is used?
6. **Training recipe** — data source, supervision, pseudo-labeling, negatives, curriculum, losses, weighting, stagewise vs joint.
7. **Inference path** — how trained components are used at test time, signal flow.
8. **Why the mechanism stays small** — why a larger stack is unnecessary.
9. **Exact role of any frontier primitive** — planner / teacher / critic / reward model / generator prior / search controller / distillation source.
10. **Failure handling** — what could go wrong, fallback or diagnostic.
11. **Novelty and elegance argument** — why more than naming a module, why the paper still looks focused.

If the method is still only described as "add a module" or "use a planner", it is not concrete enough.

## Anchor check + Simplicity check (before each revision)

When a reviewer round comes back, before changing anything:

1. Copy the **Problem Anchor verbatim**.
2. **Anchor Check**:
   - What is the original bottleneck?
   - Does the current method still solve it?
   - Which reviewer suggestions would cause drift if followed blindly?
3. **Simplicity Check**:
   - What is the dominant contribution now?
   - What components can be removed / merged / kept frozen?
   - Which reviewer suggestions add unnecessary complexity?
   - If a frontier primitive is central, is its role still crisp and justified?

## Process reviewer feedback by validity

- **Valid** → sharpen mechanism, simplify if possible, modernize if the paper truly improves.
- **Debatable** → revise with reasoning + evidence.
- **Wrong / drifting / over-complicating** → push back with evidence from local papers and the Problem Anchor.

## Bias revisions toward

- Sharper central contribution
- Fewer moving parts
- Cleaner reuse of strong existing backbones
- More natural foundation-model-era leverage when it improves the paper
- Leaner, claim-driven experiments

**Do NOT** add multiple parallel contributions to chase score. If the reviewer requests another module, first ask whether the same gain can come from a better interface, distillation signal, reward model, or inference policy on top of an existing backbone.

## Exit criteria (toward experiment planning)

Exit method refinement only when these are explicit:

- The final method thesis.
- The dominant contribution.
- The complexity intentionally rejected.
- The key claims and must-run ablations.
- The remaining risks, if any.

If the verdict is still REVISE, continue into experiment planning only when the remaining weaknesses are clearly documented.

## Formula derivation

Building a coherent theory line from scattered notes. Before deriving: identify the invariant object — the single organizing quantity (objective, total cost, conserved quantity, expected metric). Do not let a convenient proxy silently replace the actual conceptual object.

Classify every step honestly: identity (exact algebra) / proposition (requires conditions) / approximation (model simplification) / interpretation (prose meaning). Never merge these categories without signaling.

Strategies: definition→substitution→simplification / primitive law→intermediate variable→target / global quantity→perturbation→decomposition / exact→approximation→interpretable closed form.

Rules: do not hide gaps with "clearly" or "similarly"; define every symbol before use; mark approximations explicitly; if the true object is dynamic but a simpler slice is analyzed, say so; if a formula is only heuristic, label it honestly; never fabricate a coherent derivation if the object/assumptions/scope don't support one; coherence matters more than elegance.

## Always

- Be specific about compute and data assumptions. "We'll train a model" is not enough.
- Do not fabricate results — describe expected evidence and planned experiments only.
- Review the mechanism, not the parts count. A long module list is not novelty.
- Minimal experiments inside this skill — only what's needed to prove the core claims. Default to 1-3 core blocks; leave the full execution roadmap to the experiment-planning stage.
