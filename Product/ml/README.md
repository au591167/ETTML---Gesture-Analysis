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
- `export_model.py` — concrete exporter generating firmware-facing C/C++ artifacts for integration
- `capture_guided.py` — continuous serial capture utility (runs until Ctrl+C) for guided trial collection

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

## Baseline execution runbook (PowerShell, reproducible)

Use this sequence from repository root (`s:/Projects/University/ETTML`).

### 1) Create/activate virtual environment (if needed)
```powershell
python -m venv .venv
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
- `model_infer()` is intentionally a deterministic placeholder (idle fallback) until trained-weight runtime serialization is integrated.

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
