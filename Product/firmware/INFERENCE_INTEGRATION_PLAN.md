# Firmware Inference Integration Plan (Photon 2)

This document bridges ML pipeline outputs with embedded firmware integration.

## Objectives
- Run gesture inference on Photon 2 with low latency.
- Keep behavior stable (few false triggers).
- Maintain strict preprocessing parity with offline training.

## Runtime pipeline (target)
1. Fixed-rate sample acquisition (50 Hz)
2. Ring buffer update
3. Window extraction (1.0 s, stride 0.2 s)
4. Preprocessing (same as training)
5. Feature extraction (`stat_v1`)
6. Model inference
7. Decision stabilization (confidence + smoothing + debounce)
8. Command emit + feedback output

## Gesture classes and command mapping
- `tap1 -> stand`
- `tap2 -> hit`
- `shake_lr -> split`
- `tap3 -> exit`
- `idle -> no action`

## Guided capture protocol (firmware <-> host)

To support continuous, guided data collection before/alongside model training, firmware should emit a simple line protocol consumed by `Product/ml/capture_guided.py`.

### Protocol messages (firmware -> host)
- `PROMPT,label=<label>,trial=<n>`
- `SAMPLE,timestamp=<ms>,ax=<f>,ay=<f>,az=<f>`
- `RESULT,status=ok|fail,label=<label>,trial=<n>,reason=<optional>`
- `INFO,message=<text>`

### LED guidance states
- Cue LEDs (4 dedicated indicators):
  - LED1: expected `tap1`
  - LED2: expected `tap2`
  - LED3: expected `tap3`
  - LED4: expected `shake_lr`
- RGB status:
  - Blue: ready for next input
  - Green flash: trial accepted (`RESULT status=ok`)
  - Red flash: trial rejected (`RESULT status=fail`)

### Host-side behavior
- Host runs continuously until Ctrl+C.
- Samples are buffered between `PROMPT` and `RESULT`.
- Trial CSV is persisted only on `status=ok`.
- Failed trials are discarded automatically.

## Model upload and deployment readiness checklist

This checklist is intended to make model-to-firmware handoff predictable and quick.

### A. Artifact readiness (host side)
- [ ] `Product/ml/train.py` completed successfully on current dataset.
- [ ] `Product/ml/export_model.py` completed successfully.
- [ ] `Product/ml/artifacts/export_summary.json` updated for current run.
- [ ] Label ordering and class mapping verified:
  - `tap1 -> stand`
  - `tap2 -> hit`
  - `shake_lr -> split`
  - `tap3 -> exit`
  - `idle -> no action`

### B. Firmware preload readiness
- [ ] Preprocessing parity confirmed against training config:
  - sample rate
  - window size/stride
  - mean removal/scaling
  - feature set
- [ ] Model wrapper accepts expected input vector length.
- [ ] Score output dimension equals number of classes.
- [ ] Decision thresholds set to conservative defaults for first live trials.
- [ ] Build compiles with model artifact integrated (or placeholder adapter).

### C. Pre-wire smoke path (before ADXL connected)
- [ ] Firmware boots and emits startup diagnostics.
- [ ] Protocol channel responds over serial at configured baud.
- [ ] Guided prompt/state loop can be simulated from firmware stubs.
- [ ] LED outputs can be toggled and observed (cue + RGB state patterns).

### D. First wire-up execution path (after ADXL connected)
- [ ] Sensor detected over I2C (address and read sanity pass).
- [ ] Sample stream stability checked near target frequency.
- [ ] Guided capture loop generates accepted/rejected trials correctly.
- [ ] New real-data files appear under class folders in `Product/data/raw/`.
- [ ] Retrain + export run completed on newly captured data.

## Integration checkpoints

### A. Sensor + timing
- Validate ADXL343 read reliability.
- Validate sample timing stability around 50 Hz.
- Log dropped sample count.

### B. Feature parity
- Implement exact `stat_v1` feature set from `Product/ml/feature_spec.md`.
- Compare a known test window against Python-computed feature values.
- Accept only small numerical differences.

### C. Model wrapper
- Add model artifact loading interface.
- Expose a single inference call returning class scores.
- Validate score vector length and finite values.

### D. Decision logic
- Confidence threshold (start: 0.75)
- Smoothing window (start: 3)
- Debounce (start: 300 ms)
- Reject low-confidence outputs as `idle`.

### E. Output mapping
- Map stable class result to command string and LED/RGB response.
- Keep mapping table centralized and documented.

## Suggested firmware constants
- `SAMPLE_RATE_HZ = 50`
- `WINDOW_SIZE = 50`
- `WINDOW_STRIDE = 10`
- `CONF_THRESHOLD = 0.75`
- `SMOOTH_HISTORY = 3`
- `DEBOUNCE_MS = 300`

## Validation sequence
1. Sensor bring-up and timing checks
2. Buffer/window correctness checks
3. Feature parity checks (offline vs firmware)
4. Inference sanity checks
5. Live gesture trials
6. Idle false-trigger test
7. Latency measurement
8. Endurance run

## Metrics to collect
- Live accuracy and confusion matrix
- Per-class recall (especially tap classes vs shake)
- Inference latency (mean/max)
- False triggers per minute (idle)
- Flash/RAM usage

## Notes
- Start with feature-based model before considering heavier sequence models.
- Keep firmware loop non-blocking.
- Any preprocessing mismatch is a first-priority bug.
