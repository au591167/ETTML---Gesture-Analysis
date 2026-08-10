# Firmware architecture

The final firmware is a cooperative, non-blocking Particle Device OS
application. Its implementation is in `Product/firmware/src/main.cpp`; model
parameters are generated into `model_data.h/.cpp`.

## Runtime layers

1. **Sensor** — initializes ADXL343 over I2C, reads synchronized XYZ at 400 Hz,
   and records read errors.
2. **Window** — stores 1,600 samples (4 seconds) and advances by 100 samples
   (0.25 seconds) after the initial fill.
3. **Features** — mean removal and seven `stat_v2` features over X/Y/Z and
   magnitude, producing 28 values.
4. **Classifier** — embedded StandardScaler and MLP 28–32–16–5 with ReLU and
   softmax.
5. **Decision** — confidence threshold, three-window consistency, four-second
   debounce, and a calibrated impact-count guard for tap multiplicity.
6. **Presentation** — stable serial `EVENT` records and non-blocking onboard
   RGB patterns.

## Ownership rules

- `OperatingMode` owns top-level purpose: DEBUG, TRAINING, or LIVE.
- The training capture state machine is nested inside TRAINING.
- The LED sequencer is the only runtime owner of RGB animation.
- Model weights are generated; source code must never hand-edit them.
- DEBUG and LIVE share the same acquisition and inference path.

## Resource result

The final Particle cloud build used 27,950 B flash and 46,686 B RAM. Recorded
LIVE inference was 345 µs mean and 364 µs maximum with zero sensor read errors.

See the [code walkthrough](code-walkthrough.md) for source-level details.

