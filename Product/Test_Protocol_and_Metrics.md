# Test Protocol and Metrics
## TinyML Gesture Interface – Verification Plan

This document defines repeatable verification for report evidence and exam demo confidence.

---

## 1. Test Goals
- Validate functional requirements end-to-end:
  - Sensor acquisition
  - On-device classification
  - Serial command output
  - LED/RGB feedback
- Quantify performance:
  - Classification quality
  - Real-time latency
  - Stability and false triggers
  - Resource feasibility

---

## 2. Test Environment

## 2.1 Hardware
- Particle Photon 2
- ADXL343 accelerometer
- LED/RGB LED output
- USB serial connection to host PC

## 2.2 Software
- Particle Workbench / firmware toolchain
- Python (optional) serial logger script
- Model training environment (Python + ML libs used)

## 2.3 Data Conditions
- Gesture vocabulary fixed for final test run.
- Same preprocessing assumptions as deployment.
- Class labels and command mapping frozen before final validation.

---

## 3. Acceptance Criteria (Target)
- Live multiclass accuracy: **≥80%**
- Inference latency per window: **<50 ms**
- Stable output (low flicker/jitter) with smoothing enabled
- Model fits microcontroller flash/RAM constraints
- Serial protocol emits correct gesture commands consistently

---

## 4. Test Matrix Overview

| Test ID | Category | Purpose | Pass Condition |
|---|---|---|---|
| T1 | Sensor bring-up | Verify ADXL343 reads valid changing data | Non-zero changing x/y/z under movement |
| T2 | Sampling timing | Verify sample rate stability | Within acceptable tolerance of configured Hz |
| T3 | Buffer/windowing | Verify window size/stride logic | Correct frame length and update interval |
| T4 | Preprocess parity | Ensure on-device preprocessing matches training | Numerical sanity checks pass |
| T5 | Inference sanity | Verify model produces valid class scores | Scores finite, class index valid |
| T6 | Gesture unit tests | Per-gesture recognition under controlled trials | Each class reaches minimum per-class success |
| T7 | Full live sequence | Mixed gestures in random order | Overall target accuracy met |
| T8 | Idle robustness | Measure false positives during idle | False trigger rate below threshold |
| T9 | Latency | Measure inference + decision time | Mean and worst-case below target |
| T10 | Output mapping | Verify command + LED mapping correctness | Correct output for each detected class |
| T11 | Endurance | 10–15 min run stability | No crash, no degraded behavior |
| T12 | Resource check | Confirm MCU memory feasibility | Build + runtime stable on target |

---

## 5. Detailed Procedures

## T1 – Sensor Bring-Up
1. Flash sensor test firmware.
2. Stream `ax, ay, az` at low rate (e.g., 10–20 Hz).
3. Move board in each axis.
4. Confirm values change and are plausible.

Record:
- Address detected
- Mean/std of idle values
- Any dropped reads

---

## T2 – Sampling Timing
1. Enable timestamp logging per sample.
2. Run 30–60 seconds.
3. Compute observed sample interval statistics.

Pass example:
- Target 50 Hz (20 ms interval)
- Mean interval ~20 ms with acceptable jitter band

---

## T3 – Buffer/Window Verification
1. Enable debug print when window becomes ready.
2. Confirm each window has exact configured sample count.
3. Confirm stride behavior (overlap/no overlap) matches config.

---

## T4 – Preprocess Parity
1. Feed known sample vector/window.
2. Compare preprocessing output from training script vs firmware.
3. Check close numerical match (within tolerance).

---

## T5 – Inference Sanity Check
1. Run inference on known static test window.
2. Confirm:
   - scores are finite
   - score count equals number of classes
   - argmax index in valid range

---

## T6 – Controlled Per-Gesture Trials
For each gesture class:
1. Perform N trials (recommend N=20).
2. Log predicted class and confidence.
3. Compute class-level accuracy/recall.

Template:
- Class: Swipe Left
- Trials: 20
- Correct: X
- Accuracy: X/20

---

## T7 – Mixed Live Sequence
1. Prepare randomized test script of gestures (e.g., 80–120 events total).
2. Execute sequence while logging true label and prediction.
3. Build confusion matrix and aggregate metrics.

---

## T8 – Idle Robustness
1. Keep device stationary and in normal operation for fixed interval (e.g., 5 min).
2. Count non-idle detections.
3. Compute false trigger rate:
   - false triggers per minute
   - false triggers per window

---

## T9 – Latency Measurement
Measure:
- preprocessing time
- model invoke time
- total decision loop time

Method:
- Timestamp before preprocess and after final decision.
- Log min/mean/max across many windows.

---

## T10 – Output Mapping Verification
For each gesture class:
1. Force/perform known gesture.
2. Validate expected:
   - serial command (`G:<id>`)
   - LED pattern/color

Document mapping consistency in table.

---

## T11 – Endurance/Soak Test
1. Run integrated firmware continuously for 10–15 minutes.
2. Periodically perform gestures + idle.
3. Observe for lockups, sensor failures, or timing drift.

---

## T12 – Resource Feasibility
1. Collect build memory output (flash/RAM summary).
2. Confirm runtime remains stable without memory exhaustion.
3. Record model binary size.

---

## 6. Metrics to Report

## 6.1 Classification Metrics
- Overall accuracy
- Per-class precision/recall/F1
- Confusion matrix
- Macro-average F1 (if class balance concern)

## 6.2 Runtime Metrics
- Mean/max inference latency
- End-to-end decision latency
- Sampling interval stability

## 6.3 Robustness Metrics
- Idle false positive rate
- Misclassification hotspots (from confusion matrix)
- Stability over repeated trials

## 6.4 Resource Metrics
- Model size (KB)
- Flash usage
- RAM usage

---

## 7. Results Templates

## 7.1 Per-Class Performance
| Class | Trials | Correct | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Idle | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Swipe Left | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Swipe Right | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Push | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Pull | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Shake | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Double Tap | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

## 7.2 Latency and Resources
| Metric | Measured | Target | Status |
|---|---:|---:|---|
| Inference mean (ms) | [ ] | <50 | [ ] |
| Inference max (ms) | [ ] | <50 (preferred) | [ ] |
| Decision loop mean (ms) | [ ] | low | [ ] |
| Model size (KB) | [ ] | MCU-fit | [ ] |
| Flash use (%) | [ ] | safe margin | [ ] |
| RAM use (%) | [ ] | safe margin | [ ] |

## 7.3 Idle False Trigger
| Duration | False Triggers | Rate (per min) | Status |
|---|---:|---:|---|
| [ ] min | [ ] | [ ] | [ ] |

---

## 8. Reporting Guidance
In final report “Test/Verification”:
- Include confusion matrix image/table.
- Include latency table and measurement method.
- Include one short error analysis subsection:
  - where the model fails,
  - why likely,
  - mitigation applied (e.g., smoothing, extra data, class merge).

---

## 9. Oral Demo Verification Script (Fast)
1. Show idle stability for 10–15 seconds.
2. Perform 4–5 distinct gestures.
3. Narrate predicted class + LED response.
4. Show serial log snippets.
5. Conclude with key measured metrics.
