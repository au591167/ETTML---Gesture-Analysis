# Dataset Specification (Gesture Reader)

This document defines how gesture data should be recorded and organized for model training.

## Scope classes
- `idle`
- `tap1`
- `tap2`
- `tap3`
- `shake_lr`

## Blackjack demo command mapping
- `tap1 -> stand`
- `tap2 -> hit`
- `shake_lr -> split`
- `tap3 -> exit`

## Sampling requirements
- Target sampling rate: **50 Hz**
- Sensor channels: `ax, ay, az`
- Optional derived channel in training: `mag`

## File format
CSV columns (required):
- `timestamp` (ms or monotonic ticks)
- `ax`
- `ay`
- `az`
- `label`

Optional columns:
- `trial_id`
- `user_id`
- `notes`

## Folder layout
```text
Product/data/
  raw/
    idle/
    tap1/
    tap2/
    tap3/
    shake_lr/
  processed/
```

## Guided continuous collection protocol (recommended)
Use firmware-led prompts + host serial logger (`Product/ml/capture_guided.py`) for repeatable trial capture.

Expected serial protocol from firmware:
- `PROMPT,label=<label>,trial=<n>`
- `SAMPLE,timestamp=<ms>,ax=<f>,ay=<f>,az=<f>`
- `RESULT,status=ok|fail,label=<label>,trial=<n>,reason=<optional>`
- `INFO,message=<text>`

Capture behavior:
1. Firmware announces expected label/trial via `PROMPT`.
2. Firmware streams `SAMPLE` lines continuously for active trial.
3. Firmware validates trial quality and sends `RESULT`.
4. Host writes trial CSV only on `status=ok`; failed trials are discarded.

Suggested host command:
```powershell
.\.venv\Scripts\python Product/ml/capture_guided.py --port COM6 --baud 115200
```

Suggested filename pattern:
- `gesture_<label>_<trial>.csv`
- Example: `gesture_tap2_014.csv`

## Collection guidance
- Minimum baseline: **30–50 trials per class**
- Include variation:
  - fast / normal / slow execution
  - slight orientation changes
  - realistic idle periods between gestures
- Keep class balance as even as possible.

## Labeling rules
1. One dominant label per recorded trial.
2. No mixed-gesture labels in a single trial file.
3. If uncertain recording quality, discard or mark in notes.
4. Re-record ambiguous trials to reduce label noise.

## Quality checks before training
- Confirm required columns exist in all files.
- Confirm no corrupted numeric values.
- Confirm sampling cadence is close to target.
- Confirm class counts are reasonably balanced.
- Spot-check random files visually (signal sanity).

## Split policy (recommended)
- Use train/validation/test split with stratification.
- Keep trials independent across splits (avoid leakage by duplicating near-identical samples).

## Why this matters
Reliable TinyML behavior depends primarily on:
1) representative labeled data,
2) consistent preprocessing,
3) class separability in the collected signal space.
