# ETTML machine-learning pipeline

This folder contains the supported host-side workflow for the final 400 Hz
gesture model. Superseded 50 Hz capture clients were removed; historical data
and notes remain under `Product/data/archive/` for provenance.

## Core files

| File | Responsibility |
|---|---|
| `randomized_capture_gui.py` | Automatic randomized 400 Hz capture, validation, retry and CSV/JSON/PNG persistence |
| `train.py` | Schema normalization, four-second windows, 28 `stat_v2` features and held-out evaluation |
| `export_model.py` | Fail-closed training and atomic export of scaler/MLP parameters to firmware C++ |
| `generate_figures.py` | Recreates report signal and confusion-matrix figures from the deployed session |
| `config.yaml` | Single source of truth for labels, sampling, model and decision settings |
| `feature_spec.md` | Exact Python/firmware feature contract |

Generated artifacts live in `artifacts/`; generated firmware parameters live in
`Product/firmware/src/model_data.{h,cpp}`. Do not edit those parameters by hand.

## Reproduce the final baseline

Run from the repository root:

```bash
source .venv/bin/activate
python Product/ml/randomized_capture_gui.py --port /dev/ttyACM1 --series 5
python Product/ml/train.py --config Product/ml/config.yaml
python Product/ml/export_model.py --config Product/ml/config.yaml
python Product/ml/generate_figures.py
particle compile photon2 Product/firmware --saveTo firmware.bin
particle flash TinyML_Node1 firmware.bin
```

The deployed config points explicitly to the accepted files from session
`20260810_141717`: 25 windows, five per class. Rejected and diagnostic files
must not be included in training.

## Contracts and safety

- Capture: synchronized XYZ, 400 Hz, 4.0 seconds, exactly 1,600 samples.
- Classes: `idle`, `tap1`, `tap2`, `tap3`, `shake_lr`.
- Features: 7 statistics × X/Y/Z/magnitude = 28 float32 values.
- Model: StandardScaler + MLP 28–32–16–5.
- Export validates complete class coverage and never replaces deployment files
  with placeholders after a failed training run.
- LIVE uses confidence thresholding, three-window smoothing, four-second
  debounce and an impact-count guard after the learned tap-family decision.

The current 80% held-out result contains only five test cases. It proves the
pipeline runs; it is not evidence of user-independent generalization.
