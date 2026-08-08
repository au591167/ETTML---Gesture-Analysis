# TinyML Model Foundation (Photon 2)

This folder contains the **model-development foundation** for the gesture reader project, aligned with course goals and constrained embedded deployment.

## Scope (current)
- Build a **lightweight, stable, responsive** gesture classifier for Photon 2.
- Use a **feature-based model first** (before any heavier sequence model).
- Support blackjack simulation command mapping:
  - `tap1 -> stand`
  - `tap2 -> hit`
  - `shake_lr -> split`
  - `tap3 -> exit`

## Recommended first pipeline
1. Fixed-rate sampling (`50 Hz`)
2. Sliding windows (`1.0 s`, stride `0.2 s`)
3. On-window preprocessing (mean removal + scaling)
4. Lightweight engineered features
5. Compact classifier (small MLP or shallow RF)
6. Decision stabilization (confidence + smoothing + debounce)

## Files
- `config.yaml` — central parameters for sampling, classes, model, decision logic
- `feature_spec.md` — exact feature definitions and on-device parity rules
- `train.py` — minimal training/evaluation scaffold
- `export_model.py` — concrete exporter generating firmware-facing C/C++ artifacts (real MLP weights + StandardScaler → `model_data.h/.cpp`)
- `auto_capture.py` — **recommended** serial capture utility that acts as an OK/BAD confirmation responder for the firmware-led baseline capture, with optional model-based acceptance gating
- `capture_guided.py` — older continuous serial capture utility (runs until Ctrl+C) for guided trial collection

## Important engineering rule
Training preprocessing and on-device preprocessing must be identical.
Any mismatch will break live performance even if offline metrics look good.

## Guided continuous capture (recommended for lab sessions)

`capture_guided.py` supports a firmware-led collection loop where Photon 2 prompts expected gesture class and streams samples continuously.

### Serial protocol (firmware -> host)
- `PROMPT,label=<label>,trial=<n>`
- `SAMPLE,timestamp=<ms>,ax=<f>,ay=<f>,az=<f>`
- `RESULT,status=ok|fail,label=<label>,trial=<n>,reason=<optional>`
- `INFO,message=<text>`

### Usage
```powershell
.\.venv\Scripts\python Product/ml/capture_guided.py --port COM6 --baud 115200
```

Output behavior:
- On `RESULT status=ok`: writes one CSV for that trial to `Product/data/raw/<label>/`
- On `RESULT status=fail`: discards buffered trial samples
- Stops only on `Ctrl+C`

## Auto-capture with model-gated confirmation (`auto_capture.py`)

The firmware (`main.cpp`) **drives** the baseline capture state machine. Host flow:
1. Tool sends `START_BASELINE`.
2. Firmware runs a 10 s stationary phase (idle), then cycles gestures (`tap1 → tap2 → tap3 → shake_lr`), prompts each, waits for physical motion, samples a 1.0 s window, then emits `confirm_ready` and waits for `OK`/`BAD`.
3. The tool reads the stream, buffers `SAMPLE` lines per trial, and on `confirm_ready` decides `OK`/`BAD`.
4. On `OK` the firmware emits `RESULT,status=ok`; the tool saves that trial to `Product/data/raw/<label>/`.

### Important: first data sweep must bypass the model gate
The current baseline model is trained on only a few (mostly synthetic) windows, so it cannot yet confidently recognize real gestures — the confidence gate (`0.75`) will reject nearly everything. **For the first real-data collection, run with `--auto-ok`** so every trial you actually perform is accepted (the label is already correct — it is the class the firmware prompted):

```powershell
.\.venv\Scripts\python Product/ml/auto_capture.py --port COM3 --baud 115200 --auto-ok
```

After collecting real data:
```powershell
.\.venv\Scripts\python Product/ml/train.py --config Product/ml/config.yaml
.\.venv\Scripts\python Product/ml/export_model.py --config Product/ml/config.yaml
```
Then re-flash the updated model. Once the model is trained on real data, re-run `auto_capture.py` **without** `--auto-ok` to use model-based acceptance gating:
```powershell
.\.venv\Scripts\python Product/ml/auto_capture.py --port COM3 --baud 115200
```

Options:
- `--auto-ok` — always send `OK` on `confirm_ready` (accept every trial)
- `--confidence <f>` — min softmax confidence to accept (default `0.75`)
- `--out <path>` — custom output root (default `Product/data/raw`)
- `--artifacts <path>` — model/scaler/label_encoder folder (default `Product/ml/artifacts`)

## Baseline execution runbook (PowerShell, reproducible)

Use this sequence from repository root (`s:/Projects/University/ETTML`).

### 0) Use Python 3.11 (required — do not use 3.14)
The ML stack (numpy/scikit-learn/pandas) has **stable prebuilt wheels only for Python ≤ 3.13**. On Python 3.14 the imports hang or crash (broken `_multiarray_umath` binaries), which is exactly what happened during lab setup. Use a Python 3.11 or 3.12 interpreter.

```powershell
# With uv (has a managed 3.11):
uv python install 3.11
uv venv --python 3.11 .venv

# Or point at an installed 3.11/3.12:
C:\path\to\python3.11\python.exe -m venv .venv
```

### 1) Create/activate virtual environment (if needed)
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2) Install required Python dependencies
```powershell
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install numpy pandas pyyaml scikit-learn pyserial
```

### 3) Sanity-check guided capture script CLI
```powershell
.\.venv\Scripts\python Product/ml/capture_guided.py --help
```

### 4) Run baseline training
```powershell
.\.venv\Scripts\python Product/ml/train.py --config Product/ml/config.yaml
```

### 5) Export model artifacts/summary
```powershell
.\.venv\Scripts\python Product/ml/export_model.py --config Product/ml/config.yaml
```

(also works on global Python if dependencies are installed)
```powershell
python Product/ml/export_model.py --config Product/ml/config.yaml
```

### 6) Validate expected artifact output
Confirm these files exist and are updated:
- `Product/ml/artifacts/export_summary.json`
- `Product/firmware/model_data.h`
- `Product/firmware/model_data.cpp`

### 7) Firmware handoff (generated artifact usage)
1. Ensure `model_data.h` and `model_data.cpp` are included in the firmware build.
2. Include header in inference source:
```cpp
#include "model_data.h"
```
3. Initialize model wrapper once at startup:
```cpp
tinyml_model::model_init();
```
4. Run inference with generated constants:
```cpp
tinyml_model::model_infer(features, tinyml_model::kFeatureCount, scores, tinyml_model::kNumClasses);
```
5. Convert predicted index to names/commands via:
   - `tinyml_model::kClassNames[idx]`
   - `tinyml_model::kCommandMap[idx]`

Current runtime note:
- `model_infer()` performs a **real MLP forward pass** on the deployed weights: StandardScaler → 3 ReLU layers → softmax scores. Re-export after retraining to update the deployed model.

## GitHub commit checklist (what to push now)
- [x] ML scripts and config (`train.py`, `export_model.py`, `capture_guided.py`, `config.yaml`)
- [x] Data/firmware/report planning docs
- [x] Artifact summary JSON (small metadata file)
- [ ] Large raw datasets (keep out until curated; use selective commits or Git LFS if needed)

## Next steps (execution order)
1. Wire ADXL343 + LEDs according to `Product/Hardware_Wiring_and_BOM.md`.
2. Run guided capture session using `capture_guided.py`.
3. Verify per-class file counts in `Product/data/raw/`.
4. Retrain model on real captured data and review confusion matrix + per-class recall.
5. Export compact model artifacts and mirror preprocessing in firmware.
