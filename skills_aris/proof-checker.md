# Proof Checker

Formal mathematical proof verification — catches logical gaps, unjustified interchanges, missing domination conditions, and hidden assumptions that traditional review misses.

## Acceptance gate

Objective standard (replaces subjective scoring): proof passes iff zero open FATAL or CRITICAL; every theorem / lemma has explicit hypotheses + proof with all interchanges justified + every application discharges hypotheses in ledger; all big-O / Θ / o statements have declared parameter dependence and uniformity scope; counterexample pass executed on all key lemmas (log candidates even if none found).

## Issue taxonomy (4 groups, 20 categories)

- **Group A — Logic & Proof Structure**: UNJUSTIFIED_ASSERTION / UNPROVEN_SUBCLAIM ("clearly" hides nontrivial) / QUANTIFIER_ERROR / IMPLICATION_REVERSAL / CASE_INCOMPLETE / CIRCULAR_DEPENDENCY / LOGICAL_GAP.
- **Group B — Analysis & Measure Theory**: ILLEGAL_INTERCHANGE / NONUNIFORM_CONVERGENCE / MISSING_DOMINATION / INTEGRABILITY_GAP / REGULARITY_GAP / STOCHASTIC_MODE_CONFUSION.
- **Group C — Model & Parameter Tracking**: MISSING_DERIVATION / HIDDEN_ASSUMPTION / INSUFFICIENT_ASSUMPTION / DIMENSION_TRACKING / NORMALIZATION_MISMATCH / CONSTANT_DEPENDENCE_HIDDEN.
- **Group D — Scope & Claims**: SCOPE_OVERCLAIM / REFERENCE_MISMATCH.

## Two-axis severity

- Axis A (proof status / what is wrong): INVALID (counterexample exists) / UNJUSTIFIED (could be true, proof inadequate) / UNDERSTATED (true after strengthening) / OVERSTATED (true after weakening) / UNCLEAR (ambiguous notation).
- Axis B (impact / how much breaks): GLOBAL (breaks main theorem) / LOCAL (side result) / COSMETIC (exposition).
- Severity labels (derived): FATAL = INVALID+GLOBAL; CRITICAL = (INVALID+LOCAL) or (UNJUSTIFIED+GLOBAL); MAJOR = (UNJUSTIFIED+LOCAL) or (UNDERSTATED/OVERSTATED+GLOBAL); MINOR = clarity / notation / dimension bookkeeping that doesn't change claims.

## Side-condition checklists

When invoking common theorems, explicitly verify ALL listed conditions:
- DCT: pointwise a.e. convergence + integrable dominating function.
- MCT: monotone increasing + non-negative.
- Fubini / Tonelli: product measurability + integrability (Fubini) or non-negative (Tonelli).
- Leibniz integral rule: continuity of integrand + dominating function for derivative.
- Implicit Function Theorem: continuous differentiability + non-singular Jacobian.
- Taylor with remainder: sufficient differentiability + remainder form.
- Jensen's inequality: convexity + integrability.
- Cauchy-Schwarz: correct inner product space + integrability of both factors.
- Weyl / Davis-Kahan: symmetry / Hermiticity + perturbation bound conditions.
- Analytic continuation: domain connectivity + identity theorem conditions.
- WLOG reduction: invariance under claimed symmetry + reduction is reversible.

## Proof-obligation ledger

Build all six components before reviewing:
- Dependency DAG (nodes = defs / assumptions / lemmas / theorems; edges = "uses"; detect cycles including semantic circularity).
- Assumption ledger (per theorem / lemma: every hypothesis + WHERE verified or UNVERIFIED; track usage-minimal sets — actually used vs merely stated).
- Typed symbol table (per symbol: type signature; flag any whose meaning changes or type is inconsistent across uses).
- Canonical quantified statements (rewrite each with explicit quantifiers, domains, limit order; if you can't restate precisely, mark UNCLEAR).
- Micro-claim inventory (every nontrivial step in sequent form: Context ⊢ Goal; Rule; Side-conditions + where proven).
- Limit-order map (every asymptotic statement's limit order + uniformity scope; flag ambiguous / unclear ones).

## Eight review axes

- **Definitions**: list any ambiguous / changing symbols.
- **Hypothesis discharge**: for each lemma APPLICATION, list each hypothesis + whether verified + location.
- **Inequality audit**: verify direction, missing absolute values, missing conditions (convexity / PSD / integrability).
- **Interchange audit**: flag every limit / derivative / expectation / integral interchange + which theorem justifies + which conditions verified / missing.
- **Probability mode**: track a.s. / in prob. / in expectation / w.h.p. + justify transitions.
- **Uniformity & constants**: every O / o / Θ declare what parameters uniform over; list hidden parameter dependence.
- **Edge / degenerate cases**: attempt to break each key lemma with a 1D, low-rank, or extreme-parameter construction.
- **Dependency consistency**: detect cycles or forward references to unproven results.

## Counterexample red-team

For each CRITICAL / MAJOR issue + every key lemma that introduces a new inequality bound / identifiability or uniqueness claim / curvature or PSD / strong convexity assertion / uniform-in-parameter claim / convergence mode upgrade (pointwise → uniform, in prob → w.h.p.). Strategies:
- Dimensional collapse (d=1 or 2, K=2, n small).
- Degeneracy (singular covariance, tiny weight, overlapping means, identical components).
- Extremal distributions (two-point ±a, bounded non-subGaussian, heavy tails).
- Adversarial parameter scaling (pick parameters making neglected terms dominate).
- Numeric falsification (translate to a function, brute-force optimize over small domain).

Label "counterexample found" ONLY if algebraically verified. Otherwise log as "candidate counterexample — needs verification". Record all attempts (successful or not).

## Global closure checks

After all fixes:
- Statement-conclusion match: proof ends with EXACTLY what the theorem claims (quantifiers, constants, uniformity).
- All obligations discharged: every node in obligation DAG proven or explicitly assumed (and theorem statement includes it).
- Case analysis coverage: cases partition the domain AND include boundary / degenerate cases.
- Induction correctness (if applicable): base case, inductive step, correct IH use, induction measure strictly decreases.
- WLOG reductions: each "without loss of generality" spawns a micro-claim proving the reduction is lossless.
- No silent assumption strengthening: any fix that strengthened assumptions must propagate to the main theorem statement.

## Restatement regression

Catches drift between the canonical theorem statement and its restatements elsewhere (summary tables, abstract, discussion, captions). Drift patterns: main theorem makes a partly-conditional claim but a summary cites it as fully unconditional; κ exponent differs from constants table; regime condition is squared envelope but a remark shows first-order envelope; restatement quietly drops a quantifier that the proof relied on.

## Deep-fix opt-in philosophy

Default `minimal_fix` is intentionally short — suits the common case where executor wants high-level pointers and will derive patch separately. Forcing `deep_fix_plan` on every run would inflate every reviewer call, trigger re-review thrash, change the shape of issues for every existing caller.

Deep-fix opt-in is appropriate when: executor intends to apply the fix in the same session; a previous run identified a CRITICAL or MAJOR issue whose `minimal_fix` was too vague; algebra-heavy proofs with Schur / quadratic-form / operator-norm steps where reviewer's first pass produced under-specified fixes.

If producing a fix plan, be precise — vague prose ("strengthen the bound", "redo the Schur step") is not acceptable. If you cannot produce a precise plan, say so rather than emitting a vague one.

## Core principles

- Never accept a proof step on faith. "Clearly" / "it follows" / "by standard arguments" are red flags — each must spawn a micro-claim.
- Hypothesis discharge: every time a lemma is APPLIED, verify EACH of its hypotheses at that point.
- Interchange discipline: every swap of limit / expectation / derivative / integral must cite a theorem (DCT / MCT / Fubini / Leibniz) and verify its conditions with explicit dominating function or integrability proof.
- Uniformity discipline: every O / Θ must declare what parameters it is uniform over. "O(1)" secretly depending on d, n, K is a CONSTANT_DEPENDENCE_HIDDEN issue.
- Quantifier discipline: check ∀/∃ order. "For sufficiently small κ" must specify whether κ₀ depends on K, π, d.
- Counterexample-first: before trying to fix a gap, first try to break it.
- WLOG prohibition: every "without loss of generality" must have an explicit micro-claim proving the reduction. No free WLOGs.
- No silent assumption strengthening: any fix that adds conditions must propagate to the theorem statement.
- Reviewer reasoning always at maximum — never downgrade.
- Send full content — don't summarize, send actual math for line-by-line checking.
- Minimal fixes — fix exactly what's broken, nothing more.
- Full derivation — every fix includes complete mathematical argument.
- Don't overclaim — if a fix makes a result conditional, say so.
- Separate "proven" from "assumed" in the audit report.
- Log open problems — issues requiring future work are listed, not hidden.

## Proof writing (complement: writer writes, checker verifies)

Feasibility triage before writing: does the conclusion follow from listed assumptions? Is any cited theorem used outside its conditions? Is there an obvious counterexample, boundary case, or quantifier failure? If not provable as stated, do NOT fabricate. Do NOT silently strengthen assumptions.

Proof strategies: direct / contradiction / induction / construction / reduction to known result / coupling.

Mathematical rigor: never use "clearly", "obviously", "it can be shown", "by standard arguments" to hide a gap; define every constant before use; check quantifier order; handle degenerate cases explicitly; if invoking a standard fact, state its name and why its assumptions are satisfied.

Proof package: Claim → Assumptions → Notation → Strategy → Dependency Map (claim→lemmas→cited theorems→assumptions per step→boundary cases) → Proof (numbered steps, every nontrivial implication justified) → Corrections → Open Risks.

Key rules: never fabricate a missing proof step; prefer weakening over overclaiming; separate assumptions, derived facts, heuristics, and conjectures; preserve original theorem statement unless explicitly marking corrected claim; if false as written, say so with counterexample; if uncertain, mark in Open Risks.
