# Experiment Execution

Discipline for running ML experiments reliably on remote GPUs.

## Code Quality

Scripts self-contained, no hardcoded paths or server addresses. Auto-detect environment from config. Every script writes structured results with metadata (git commit, GPU info, hyperparameters, metrics). Use completion markers, not epoch counts in filenames.

## Pilot First

Before full evaluation: pilot with a single seed and timeout budget. Qualitatively inspect output samples. Report GO/NO-GO with confidence per candidate. At least one candidate must beat the shared baseline for GO. GO/NO-GO bar: GO = task completed, results plausible, at least one candidate above baseline. NO-GO = fatal errors or impossible results (all zeros, NaNs, nonsensical output).

## Error Patterns

OOM → reduce batch size, not hidden dimension. NaN loss → check learning rate, gradient clipping, data preprocessing. Slow training → check data loading bottleneck. GPU memory unused despite OOM → suspect memory fragmentation.

## Drift Detection

Compare actual vs planned: runtime exceeding timeout? Loss plateau unexpected? GPU utilization low sustained? Output rate far from expected? Diagnose before run ends — early intervention is cheaper than waiting for a dead run to finish.

## Intervention

Runtime > 1.5× plan: investigate bottleneck (CPU-GPU transfer, I/O, memory fragmentation). Loss plateau > expected: reduce learning rate 2× then 10×. GPU util < 90% sustained: check data loading or CPU-bound pre-processing. NaN/Inf: reduce learning rate or clip gradients.

## Resilience

SSH drops, processes die, filesystems slow down — all normal. Retry with backoff, never fail permanently. A single dead task must not block the queue: skip it, continue others, surface for investigation.

## Resource Sharing

Check shared resource registry before downloading: symlink if available, download and register if not. Never touch other projects' directories. Environment activation from config, never hardcoded.

## File Isolation

Every experiment fully isolated: project-specific directories, no cross-project access. Shared resources through central registry with symlink reuse. All experiment files (code, logs, results) under project root.

## Remote Execution

Code writing and debugging server-local to avoid SSH command-by-command interaction. Result analysis and visualization on main system where rich context is available. Environment setup is one-time, server-local.

## Checkpointing

Every task saves intermediate progress. Long-running tasks checkpoint at natural boundaries (epoch end, validation phase). Crash recovery reads latest checkpoint and resumes — never restart from zero if a checkpoint exists.

## Completion

Write completion marker for each finished task. Check for existing marker before starting — completed tasks are final and must not be re-run. Final results as structured JSON with metadata.
