# Common Conventions

## Model Selection & Time Budget

Small models for experiments: GPT-2, BERT-base, Qwen-0.5B. Single-GPU, random seeds. Time budget: ≤60 min per experiment, ≤15 min for pilots. Scale to fit budget.

## Remote Servers

Project-restricted files, shared registry for datasets and weights. Symlink when available, download and register if not. Environment activation from config, never hardcoded. No cross-project file access.

## Self-Evolution Safety

Every system modification: write tests, pass all tests, git commit, git push immediately. No destructive changes without verified safety. Git history is the audit trail — all system evolution must be reversible and traceable.

## Quality Standards

Outputs specific and actionable. Every claim evidence-backed. Flag suspicious results (>30% improvement over simple baselines). Save sample outputs, not just statistics. Honestly report negative results.
