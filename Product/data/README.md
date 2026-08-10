# Dataset organization

## Deployed baseline

The final model is trained only from:

```text
pilot_v3/20260810_141717/accepted/
```

It contains 25 balanced CSV trials: five each for `idle`, `tap1`, `tap2`,
`tap3`, and `shake_lr`. Each trial has 1,600 synchronized XYZ samples at a
nominal 400 Hz. JSON and PNG sidecars preserve quality metrics and visual
evidence.

## Folder roles

| Folder | Purpose | Used for deployment training? |
|---|---|---|
| `pilot_v3/<session>/accepted/` | Automatically validated high-rate captures | Only the session named in `config.yaml` |
| `pilot_v3/<session>/rejected/` | Failed attempts retained for audit | No |
| `diagnostics/` | Axis and tap-scope experiments | No |
| `raw/` | Superseded 50 Hz acquisition generations | No |
| `archive/` | Historical baselines and timing-bug sessions | No |
| `processed/` | Optional derived-data workspace | No |

## Active CSV contract

Core fields are `time_us`, `x_g`, `y_g`, `z_g`, `label`, requested pace and
force, session ID, and acceptance status. Derived delta/magnitude fields are
included for audit. An accepted capture must contain exactly 1,600 rows,
monotonic timestamps, no missing values, no clipping, and class-appropriate
motion.

The authoritative deployed path is set explicitly in
[`Product/ml/config.yaml`](../ml/config.yaml), preventing archived data from
being mixed into training accidentally.
