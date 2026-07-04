# Cloud GPU

Renting GPUs on demand (e.g., vast.ai). The skill **analyzes the task** to determine GPU requirements, presents cost-optimized options, and handles the full lifecycle: rent → setup → run → destroy.

## Task-driven selection

Users do NOT specify GPU models or hardware. They describe the task — the skill figures out what to rent.

Analyze task requirements from:

- **Experiment plan**: compute budget (total GPU-hours), hardware hints, model architecture + dataset size, run order + per-milestone cost.
- **Experiment scripts**: model size (param count, config), batch size + sequence length (estimate VRAM), dataset (training time from size + epochs), multi-GPU markers (DataParallel / DDP / accelerate / deepspeed).
- **User description**: model name / size, dataset scale, estimated duration.

## GPU requirement estimation

| Factor | How to estimate |
|--------|----------------|
| **Min VRAM** | Model params × 4B (fp32) or × 2B (fp16 / bf16) + optimizer states + activations. Rules: 7B ≈ 16GB (fp16), 13B ≈ 28GB, 70B ≈ 140GB (multi-GPU). ResNet / ViT ≈ 4-8GB. Add 20% headroom. |
| **Num GPUs** | 1 unless model doesn't fit, scripts use DDP / FSDP / DeepSpeed, or plan specifies multi-GPU |
| **Est. hours** | From plan's cost column, or `(dataset × epochs) / (throughput × batch)`. Default to user estimate. Add 30% buffer |
| **Min disk** | 20GB + checkpoint + dataset. Default 50GB |
| **CUDA version** | Match PyTorch (2.x → ≥11.8). Default 12.1 |

## Offer search

Always search broadly — do NOT limit to one GPU model. Budget GPUs first, then high-VRAM cards specifically if VRAM > 24GB.

## Presenting options

Present 3 options ranked by **estimated total cost** (not $/hr alone). Show: GPU + VRAM, $/hr, estimated hours (scaled by relative speed), estimated total cost = $/hr × est. hours, reliability %, offer ID.

Faster GPUs have shorter estimated hours. Flag cheap options with reliability < 0.97 ("budget pick — 3% chance of interruption"). For tasks <1 hour, recommend interruptible / bid pricing.

A $0.90/hr GPU finishing in 2h ($1.80) beats a $0.30/hr GPU taking 8h ($2.40). Show total, not unit cost.

### Relative speed scaling (FP16, for hour-estimate across tiers)

| GPU | Relative |
|-----|---------:|
| RTX 3060 | 0.5× |
| RTX 3090 | 1.0× |
| RTX 4090 | 1.6× |
| A5000 | 0.9× |
| A6000 | 1.1× |
| L40S | 1.5× |
| A100 SXM | 2.0× |
| H100 SXM | 3.3× |

## Rent

- Default Docker image `pytorch/pytorch:2.x-cudaY-devel`, with `--ssh --direct`.
- Poll until status `running` (30-60s typically, max ~5 min).
- Always use `vastai ssh-url <ID>` for the direct endpoint — host / port from `show instances` may be a proxy.
- "Permission denied (publickey)" → SSH key was NOT uploaded before instance creation. Destroy, upload key, re-create.

SSH public key **must be uploaded BEFORE creating any instance**. Keys are baked into instances at creation time.

## Setup

- Install dependencies on instance, or `pip install -r requirements.txt` if it exists.
- Sync code via rsync (only py / yaml / yml / json / txt / sh; exclude pt / pth / ckpt / __pycache__ / .git / data / wandb / outputs).
- Verify setup with `torch.cuda.is_available()` + `torch.cuda.device_count()`.

## Destroy

- Download results + logs FIRST (irreversible delete).
- `vastai destroy instance <ID>`.
- Update state file (remove or mark `destroyed`).
- Report actual cost: duration × $/hr, vs estimated.

## Always

- **Task-driven selection** — NEVER ask users to pick GPU models. Analyze, estimate, present options.
- **ALWAYS destroy instances when experiments done** — billed per second.
- **Download results before destroying** — data lost permanently.
- **Prefer on-demand pricing** for short experiments (<2 hours). Suggest interruptible / bid pricing for long runs (>4 hours) with checkpointing.
- **Check reliability > 0.95** — unreliable hosts may crash mid-training.
- **Use `--direct` SSH** when creating instances — faster than proxy SSH.
- **Always use `vastai ssh-url <ID>`** to get connection details.
- **SSH keys uploaded BEFORE creating** — keys baked in at creation.
- **State file must stay up to date** — other skills depend on it.
- **Show estimated total cost, not just $/hr**.
