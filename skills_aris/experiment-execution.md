# Experiment Execution

Bridge from a stable experiment plan to running experiments and initial results.

## Detect environment

Detect environment from project's CLAUDE.md: local / remote SSH / Vast.ai / Modal. Modal handles its own code sync + GPU allocation — delegate.

## Pre-flight

Before deploying anything:

- Verify GPU availability (free GPU = `memory.used < 500 MiB`).
- Check SSH connection works (remote).
- Check conda env / cwd exist on remote.
- Check all preconditions (checkpoints, input files).
- Check enough free GPUs for the parallel target.

If any precondition fails, show which jobs are blocked and why.

## Code sync (remote)

- rsync only necessary files (python / yaml / json / sh), exclude data / checkpoints / large files.
- If `code_sync: git`, use git push + remote pull instead (version-tracked, multi-server sync with one push).
- For Vast.ai, always rsync to `/workspace/project/`.

## W&B integration (when configured)

Ensure scripts have `wandb.init` + `wandb.log` for training loss, lr, eval metrics, GPU memory, throughput. Verify wandb login on target.

## Implement experiment code

- Check existing code first; reuse as much as possible.
- Implement missing pieces: training script with argparse (all hyperparameters configurable), eval scripts, data loading, baseline impls, fixed seeds for reproducibility, JSON / CSV result format, proper logging.
- Follow plan's run order: sanity → baseline → main → ablation → polish.
- Self-review before deploy: hyperparameters reflected in argparse? Seed fixed and controllable? Results in parseable format? Code matches proposal's method description?

## Cross-model code review (before deploy)

Send experiment code to a different-model reviewer with these checks:

1. Does the code correctly implement the method described in the proposal?
2. Are all hyperparameters reflected in the code?
3. Are there logic bugs (wrong loss function, incorrect data split, missing eval)?
4. Is the evaluation metric computed correctly?
5. **CRITICAL: Does evaluation use the dataset's actual ground truth labels — NOT another model's output as ground truth?**
6. Any potential issues (OOM risk, numerical instability, missing seeds)?

For each issue: classify CRITICAL / MAJOR / MINOR + exact fix.

On results: no CRITICAL → proceed; CRITICAL → fix + re-submit (max 2 rounds); reviewer unavailable → skip silently (graceful degradation).

## Sanity first

Before deploying the full suite, run the sanity-stage experiment. Verify training loop runs without errors, metrics computed and saved correctly, GPU memory within bounds, output format matches expectations.

Never deploy a full suite without verifying sanity passes.

## Auto-debug failed sanity (max 3 attempts)

Never give up on the first failure. Most crashes are fixable without human intervention.

1. **Read the error**: traceback, stderr, log files.
2. **Diagnose**:
   - OOM → reduce batch size or enable gradient checkpointing
   - ImportError → install package
   - FileNotFoundError → fix path or download data
   - CUDA error → check GPU / reduce model size
   - NaN / divergence → reduce lr / check preprocessing
3. **Fix and re-run**.
4. **Attempt 2+ still failing** → cross-model rescue: an independent model often catches issues the first missed (wrong tensor shapes, subtle import shadowing, config mismatches).
5. **Still failing after 3 attempts** → stop. Report failure with all attempted fixes + error logs. Do not proceed with broken code.

## Route deployment by job count

- **Small batch** (≤5 jobs per milestone) → single-shot launcher. Each experiment gets its own screen session + GPU binding (remote) or background process (local). Use `tee` for logs.
- **Large batch** (≥10 jobs, multi-seed sweeps, or phase dependencies) → queue-based orchestration with OOM-aware retry, stale-screen cleanup, wave-transition race prevention, phase dependency enforcement, crash-safe state persistence.

Auto-routing: a milestone with ≥10 jobs (seeds × configs) or teacher → student phase dependencies → queue; otherwise single-shot.

## Queue orchestration (high level)

When using queue, scheduler responsibilities:

- For each pending job, assign to free GPU, launch via screen.
- Poll job status (every 60s).
- Detect stale screens (python exited but screen detached → kill).
- Detect OOM (CUDA OOM in log → mark `failed_oom` → retry after delay).
- Detect completion (expected output file exists → mark `completed`).
- Launch next wave only when current wave settles (all python exited, no stale screens, GPU memory dropped below threshold, preconditions for next wave met).
- Write state to JSON continuously; idempotent on restart.

Job state machine: `pending → running → completed`. Side branches: `failed_oom → pending` (after delay, retry up to N); `failed_other → stuck` (manual inspection); `stale_screen_detected → cleaned → pending`.

OOM handling: mark `failed_oom`, kill screen, wait delay, try another free GPU (or same when free), requeue as `pending`. Max N retries before `stuck`.

## After main experiments

If main results are positive → route into ablation planning (see ablation section in experiment-planning). If negative or inconclusive, skip ablation and note in summary.

## Auto-destroy cloud instances

When using vast.ai with `auto_destroy: true`: after experiment completes, download results + logs, destroy instance, report cost. Users never billed for idle instances.

## Always

- ALWAYS check GPU availability first — never blindly assign GPUs (Modal manages automatically).
- Each experiment its own screen session + GPU (remote) or background process (local).
- Use `tee` to save logs.
- Run deployment commands with `run_in_background: true` to keep conversation responsive.
- Multiple experiments → launch in parallel on different GPUs.
- **CRITICAL — Evaluation must use dataset ground truth.** ALWAYS compare model predictions against the dataset's actual ground truth labels / targets — NEVER another model's output. Double-check: (1) ground truth comes from the dataset split (not from a baseline / backbone), (2) metrics computed against the same ground truth for all methods, (3) use official eval scripts when available.
- **Follow the plan.** Do not invent experiments not in the plan. If something is missing, note but don't add.
- **Sanity first.** Never deploy a full suite without sanity passing.
- **Reuse existing code.** Scan project before writing new scripts. Extend, don't duplicate.
- **Save everything as JSON / CSV.** Downstream review needs parseable results.
- **Update the tracker** after each run completes.
- **Don't wait forever.** If an experiment exceeds 2× its estimated time, flag and move on.
- **Budget awareness.** Track GPU-hours against the plan's budget. Warn approaching limit.
- **Vast.ai cost awareness**: report running cost; if `auto_destroy: true`, destroy as soon as all experiments on it complete.
- **Modal cost awareness**: estimate and display cost before running. Auto-scales to zero — no idle billing.
- **Never overlap screens on same GPU** — always wait for `memory.used < 500 MiB`.
- **State to disk** — every state change flushed to state JSON (for queue orchestration).
- **Idempotent scheduler** — safe to restart; picks up from state file.
- **Expected-output-based completion** — verify output file exists; don't trust screen state alone.
- **Bounded retry** — max N OOM retries, then `stuck` and alert.
- **Dependencies enforced at launch** — never launch student before teacher checkpoint exists.
