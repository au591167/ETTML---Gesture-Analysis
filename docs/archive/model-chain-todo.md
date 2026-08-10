# On-Device Model Chain — Implementation TODO

Goal: get a real trained model running on the Photon 2 (not the idle placeholder).

## Critical fixes
- [x] 0. Root-cause analysis complete (full chain gaps identified)
- [x] 1. `export_model.py` — train MLP + fit StandardScaler + serialize weights/scaler as C arrays; generate real `model_infer()`
- [x] 2. `model_data.cpp` — real MLP forward pass (scale → 3 ReLU layers → softmax scores) with `<math.h>`
- [x] 3. `main.cpp` — add ring buffer + stat_v1 feature extraction (28 features) + convert raw→g + feed real features into inference
- [x] 4. `main.cpp` — emit PROMPT/SAMPLE/RESULT guided-capture protocol (START_CAPTURE / STOP_CAPTURE serial commands)
- [x] 5. Regenerate artifacts with real weights (run export) — verified: 12 windows, 28 features, real_inference=true
- [x] 6. Compile & flash firmware — compile succeeded; flashed to TinyML_Node1
- [x] 7. Collect real labeled data (4 classes x 5 trials = 20 windows, 50 samples each), retrain, redeploy; live inference verified on device

## Follow-up (after hardware)
- [x] Wire decision logic (threshold/smoothing/debounce) + LED mapping
- [x] Run test protocol and fill report Section 6.5 — real metrics (40 windows, acc 62.5%, shake_lr 1.00, tap confusion) recorded; PDF compiled

## Dependencies
- `.venv` Python with numpy/pandas/pyyaml/scikit-learn/pyserial
- `typst` (installed) for report PDF
