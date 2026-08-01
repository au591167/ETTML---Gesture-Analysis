# Firmware Architecture
## TinyML Gesture Interface – Photon 2 + ADXL343 + LED/Serial Output

This document defines firmware structure for implementation and reporting.

---

## 1. Firmware Objectives
- Read ADXL343 acceleration continuously.
- Build inference windows at fixed sample rate.
- Apply preprocessing compatible with training.
- Run gesture inference on-device.
- Stabilize output using smoothing logic.
- Trigger:
  - Serial command for Provisio integration
  - LED/RGB gesture feedback

---

## 2. Suggested Project Structure (inside Product code project)

```text
Product/
  firmware/
    src/
      main.cpp
      config.h
      sensor_adxl343.h/.cpp
      sampler.h/.cpp
      preprocess.h/.cpp
      model_inference.h/.cpp
      decision_logic.h/.cpp
      output_map.h/.cpp
      protocol.h/.cpp
```

If your existing Particle project structure differs, keep module boundaries conceptually the same.

---

## 3. Runtime Pipeline (Loop-Level)

1. **Sample acquisition**
   - Read `ax, ay, az` at configured `SAMPLE_RATE_HZ`.

2. **Buffer update**
   - Push sample into circular/ring buffer.
   - Once enough samples exist (`WINDOW_SIZE`), mark window ready.

3. **Preprocess**
   - Normalize/scale data exactly as in training.
   - Optional: compute feature vector.

4. **Inference**
   - Run model on current window/features.
   - Obtain class probabilities/scores.

5. **Decision logic**
   - Pick top class.
   - Apply confidence threshold.
   - Apply smoothing (majority vote over recent windows).
   - Optional debounce/cooldown.

6. **Output**
   - Serial protocol message to Provisio endpoint.
   - LED pattern update.

---

## 4. Core Configuration (config.h)

Example constants:
- `SAMPLE_RATE_HZ = 50`
- `WINDOW_SIZE = 100` (2 s window at 50 Hz)
- `WINDOW_STRIDE = 25` (for overlap, optional)
- `NUM_CLASSES = N`
- `CONF_THRESHOLD = 0.70f`
- `SMOOTH_HISTORY = 3`
- `DETECTION_COOLDOWN_MS = 300`

Other recommended compile-time params:
- axis scale/offset constants
- gesture enum mapping
- serial baud rate

---

## 5. Module Responsibilities

## 5.1 sensor_adxl343
- Initialize ADXL343 (I2C setup, range/data rate config).
- Read raw acceleration values.
- Handle sensor availability/errors.
- Optional calibration offsets.

Public interface example:
- `bool begin();`
- `bool read(float& ax, float& ay, float& az);`

## 5.2 sampler
- Timing control for stable sample rate.
- Convert loop timing into deterministic sampling ticks.

Public interface:
- `bool sampleDue(uint32_t nowMs);`

## 5.3 preprocess
- Input: window of raw samples.
- Output: model-ready tensor/features.
- Must mirror training pipeline exactly.

Typical operations:
- scale/normalize axes
- axis clipping
- optional derived magnitude channel
- optional statistical features

## 5.4 model_inference
- Own model data and interpreter/runtime wrappers.
- Accept preprocessed input and return class score array.

Public interface:
- `bool begin();`
- `bool infer(const float* input, float* scoresOut);`

## 5.5 decision_logic
- Convert raw scores into robust class events.

Includes:
- argmax class selection
- confidence gating
- rolling majority vote
- idle suppression
- event cooldown

Public interface:
- `GestureID update(const float* scores, uint32_t nowMs);`

## 5.6 output_map
- Map `GestureID` to:
  - LED color/pattern
  - protocol command ID

Public interface:
- `void applyLedPattern(GestureID g);`
- `const char* toProtocolCommand(GestureID g);`

## 5.7 protocol
- Format and send serial messages.

Example message:
- `G:<id>\n`
or
- `G:<id>,P:<confidence>\n`

---

## 6. Gesture and Output Mapping

Example enum:
- `GESTURE_IDLE = 0`
- `GESTURE_SWIPE_LEFT = 1`
- `GESTURE_SWIPE_RIGHT = 2`
- `GESTURE_PUSH = 3`
- `GESTURE_PULL = 4`
- `GESTURE_SHAKE = 5`
- `GESTURE_DOUBLE_TAP = 6`
- `GESTURE_CIRCLE = 7` (optional)

LED mapping should remain deterministic and documented for demo clarity.

---

## 7. State Model (Conceptual)

States:
1. **INIT**
   - Initialize sensor, model, outputs.

2. **COLLECT**
   - Gather samples until full window.

3. **INFER**
   - Preprocess + inference.

4. **DECIDE**
   - Smoothing + threshold + cooldown logic.

5. **ACT**
   - Emit serial + LED output.

Then repeat COLLECT→INFER→DECIDE→ACT continuously.

---

## 8. Timing and Performance Notes
- Keep loop non-blocking (avoid long delays).
- Prefer fixed-rate sampling rather than free-running reads.
- Measure inference timing (`micros()` before/after invoke).
- Track min/max/mean latency for report table.

---

## 9. Reliability and Error Handling
- If sensor read fails: skip sample, increment error counter.
- If model invoke fails: emit diagnostic message.
- If confidence below threshold: output IDLE/no action.
- Add startup self-test prints:
  - sensor OK
  - model OK
  - config summary

---

## 10. Logging Strategy
Recommended serial diagnostics (toggle via compile flag):
- Sampling rate check
- Inference scores per class
- Selected class + confidence
- Output action emitted
- Timing metrics every N windows

Use compact logs during normal demo mode.

---

## 11. Minimal Pseudocode

```cpp
setup() {
  initSerial();
  initLedPins();
  sensor.begin();
  model.begin();
  decision.init();
}

loop() {
  now = millis();
  if (sampler.sampleDue(now)) {
    if (sensor.read(ax, ay, az)) {
      ringBuffer.push(ax, ay, az);
    }
  }

  if (ringBuffer.windowReady()) {
    preprocess(window, modelInput);
    infer(modelInput, scores);
    gesture = decision.update(scores, now);

    if (gesture != GESTURE_IDLE) {
      protocol.send(gesture, scores[gesture]);
      output.applyLedPattern(gesture);
    } else {
      output.applyLedPattern(GESTURE_IDLE);
    }
  }
}
```

---

## 12. Implementation Notes for Report
In the final report:
- Include this module-level decomposition in “Implementation.”
- Include timing and memory observations in “Test/Verification.”
- Explain why decision smoothing was required for robust live behavior.
