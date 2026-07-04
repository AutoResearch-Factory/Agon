# Experiment Monitor

Monitor running experiments — both process status (是否还在跑) and training quality (loss / metric trends).

## Status check sources

- SSH server: screen list.
- Vast.ai: screen list + `vastai show instances` (cost tracking).
- Modal: `app list`; apps auto-terminate so missing = finished.

## Output collection

Hardcopy / log file / `tee` output, capture last N lines per session.

## Result file pull

List recent JSONs in `results_dir`; fetch and parse the latest.

## W&B metrics (when enabled)

Pull training curves and metrics via Python API. Per run extract:

- **Training loss curve** — converging? diverging? plateauing?
- **Eval metrics** — loss, PPL, accuracy at latest checkpoint.
- **Learning rate** — schedule behaving as expected?
- **GPU memory** — OOM risk?
- **Run status** — running / finished / crashed?

W&B gives richer signal than just screen output — training dynamics, loss curves, metric trends over time.

## Training quality check (separate from process health)

Process health (session alive, GPU active) is a watchdog's job. Training quality is this skill's job: NaN / divergence / plateaus / wrong-direction metrics.

When training is confirmed running (session alive, loss decreasing for first few steps), set up periodic checks (cron / scheduled job).

If W&B is unreachable, fall back to tailing log file directly via SSH.

### Signals

- Loss trend: decreasing over last N steps?
- Eval metrics: improving or at least not degrading?
- NaN / Inf in loss or gradients?
- Spikes: sudden large jumps (>10× normal variance)?
- Learning rate schedule behaving as expected?
- Gradient norm exploding or vanishing?

### Judgment

| Signal | Judgment | Action |
|--------|----------|--------|
| NaN / Inf in loss | Clearly bad | Stop |
| Loss diverging (increasing for >N steps) | Clearly bad | Stop |
| Eval significantly worse than baseline | Clearly bad | Stop |
| Loss decreasing, metrics improving | Clearly fine | Continue, increase interval |
| Loss flat but not diverging | Unsure | Escalate to external reviewer |
| Metrics noisy, can't tell trend | Unsure | Escalate to external reviewer |
| Slightly worse than baseline but still early | Unsure | Escalate to external reviewer |

### External reviewer (only when unsure)

Only escalate when signal is ambiguous. For clearly good or clearly bad, act directly.

Provide reviewer: run id, current step (X of Y), last 10 training loss checkpoints, last 3 eval metrics, baseline reference, specific concern. Ask for STOP / CONTINUE / WAIT.

### Act

- STOP → kill session; save run URL, key metrics, reason in project notes.
- CONTINUE → do nothing; invoke again at next interval (increase if consistently healthy).
- WAIT → keep current short interval (don't increase).

## Interpret results

- Compare against the correct baseline (same config).
- Flag unexpected results (negative delta, NaN, divergence).
- Suggest next steps based on findings.
- If results look wrong, check training logs for errors before concluding.

## Always

- Always show raw numbers before interpretation.
- Note if experiments are still running (check progress bars, iteration counts).
- Do not stop training on first sign of noise — some loss spikes are normal. Look at trends over multiple checkpoints.
- When stopping, always save run URL and key metrics as evidence.
- If both W&B and log files unreachable, report connectivity issue and try again next interval. Do not assume training is broken.
- Gradually increase check interval when healthy (e.g., 10 → 20 → 30 → 60 min). Reset to short interval after any anomaly.
- **Vast.ai cost awareness**: report running cost (hours × $/hr). If all experiments on an instance are done, remind to destroy.
- **Modal cost awareness**: auto-scales to zero — no idle billing. Report actual execution time + estimated cost.
