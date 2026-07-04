# DSE Loop

Autonomous design space exploration: run → analyze → tune → repeat until objective met or timeout.

## Parameter Inference

When ranges are not provided, infer from type: powers of 2 for memory/sizes; small integers for widths; geometric for bounds/timeouts; enumerate for booleans/enums; log-scale sweep for continuous. Start conservative (3-5 values), expand if best is at boundary.

## Search Strategies

**Initial**: diverse sampling to identify which parameters matter most. **Directed**: adaptive — grid for few params, coordinate descent for many, binary/golden section for continuous, Pareto frontier for multi-objective. Each iteration: select next point based on trend, avoid re-runs, balance exploration vs exploitation.

## Stopping Conditions

Timeout / max iterations / patience exhausted / success criteria met / constraint violation pattern. Respect the timeout — if next run likely exceeds budget, stop.

## Key Rules

- Every run must be logged — even failures. The log is ground truth.
- Never re-run identical configuration
- Parse metrics programmatically — don't eyeball logs
- Constraint violations are not improvements — a point violating constraints is never "best"
- Same crash 3 times with different configs → stop and report
