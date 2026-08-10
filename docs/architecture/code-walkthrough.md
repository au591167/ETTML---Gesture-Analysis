# Current code walkthrough

This document describes only the final, supported 400 Hz implementation. The
report contains the architectural rationale, measurements and citations; this
file is the source-oriented companion used when preparing the oral exam.

## End-to-end path

```text
ADXL343 (XYZ at 400 Hz)
  -> 1,600-sample / 4-second firmware window
  -> mean removal + magnitude
  -> 7 statistics on each of four channels (28 features)
  -> embedded StandardScaler
  -> MLP 28 -> 32 -> 16 -> 5
  -> confidence + three-window stability
  -> impact-count guard for tap multiplicity
  -> EVENT record + non-blocking RGB sequence
```

## Firmware

`Product/firmware/src/main.cpp` owns orchestration and is organized by labelled
sections:

1. Hardware/model constants and `OperatingMode`.
2. Sensor and inference buffers.
3. RGB sequencer and decision history.
4. Feature extraction and model invocation.
5. ADXL343 register access and initialization.
6. High-rate capture and TRAINING state machine.
7. Serial command dispatcher.
8. `setup()` and the cooperative `loop()`.

The three modes answer different operational questions:

- `DEBUG`: inspect sensor/model status; gesture actions are suppressed.
- `TRAINING`: firmware-guided acquisition state machine.
- `LIVE`: quiet inference, stable `EVENT` output and LED feedback.

The LED controller never calls `delay()`. `flashStart()` records a pattern and
`flashStep()` advances it from `loop()`, allowing serial and sampling to
continue. Alternating patterns store a primary and secondary color.

The model output is not an application event by itself. `updateDecision()`
first applies the 0.75 confidence threshold, then requires three equal
predictions and enforces a four-second duplicate lockout. `countImpactEvents()`
uses the calibrated 0.35 g envelope and 150 ms separation to resolve one/two/
three impacts only after the learned model has selected the tap family.

`model_data.h/.cpp` are generated. They contain the scaler and dense-layer
weights as constant arrays plus a float32 ReLU/softmax forward pass. Edit the
generator or config, never the generated numbers.

## Host pipeline

- `randomized_capture_gui.py` sends `TAP_SCOPE`, displays the randomized
  instruction, parses buffered XYZ samples, validates the attempt, and writes
  CSV/JSON/PNG sidecars. Rejected trials are preserved and requeued.
- `train.py` accepts both unit-bearing v3 names (`x_g`) and the stable internal
  names (`ax`) at ingestion. It groups by source file so windows never cross
  trial boundaries.
- `export_model.py` repeats training, validates all configured classes, stages
  every output, fsyncs it and atomically replaces deployment artifacts.
- `generate_figures.py` uses the configured deploy session and exact held-out
  split, preventing hand-written report metrics from drifting.

## LIVE feedback contract

| Gesture | Serial command | LED |
|---|---|---|
| idle | none | off |
| tap1 | stand | blue 1.0 s |
| tap2 | hit | blue ×2, 0.50 s cadence |
| tap3 | exit | red ×3, ~0.33 s cadence |
| shake_lr | split | red-blue-red-blue, 1.0 s cadence |

## Reproduction

See `Product/ml/README.md` and report Appendix A for the canonical capture,
train, export, compile and flash commands.
