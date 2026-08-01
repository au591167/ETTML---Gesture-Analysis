# TinyML Gesture Interface for Provisio  
**Course:** ETTML-01 Tiny Machine Learning  
**Student:** [Your Name]  
**Date:** [Submission Date]  
**Platform:** Particle Photon 2 + ADXL343  
**Project Type:** Embedded TinyML Classification System  

---

## Abstract
This project presents a TinyML-based gesture recognition interface implemented on a Particle Photon 2 microcontroller using an ADXL343 three-axis accelerometer. The system recognizes predefined hand gestures in real time and maps them to control commands for the Provisio prediction interface. In addition to serial command output, the project includes visual feedback via LEDs/RGB LED to demonstrate low-latency embedded action execution.

The implementation follows a full TinyML pipeline: sensor data acquisition, labeling, preprocessing, feature/window preparation, model training and evaluation, model optimization (quantization), and on-device inference. The project is designed to satisfy both functional and non-functional exam requirements, including self-collected labeled data, reproducible processing, and embedded deployment on Photon 2.

Expected outcomes include robust live gesture recognition performance, low-latency inference, and a compact model that fits microcontroller memory constraints. The report documents requirements, architecture, implementation details, test and verification strategy, and conclusions with future improvements.

---

## 1. Introduction
Tiny Machine Learning (TinyML) enables machine learning inference on resource-constrained embedded devices such as microcontrollers. Compared to cloud-based processing, on-device inference offers low latency, reduced bandwidth use, improved privacy, and low power operation. These properties make TinyML suitable for real-time human-machine interaction systems.

This project investigates whether hand gestures can function as a practical interaction modality for an embedded system. Instead of traditional buttons, the user performs defined movements captured by an accelerometer. A lightweight classification model running on Photon 2 predicts gesture classes and triggers interface outputs (serial command + LED feedback).

The work contributes a complete embedded ML artifact aligned with course objectives:
- Data acquisition from local sensor hardware.
- Labeled dataset generation by the student.
- TinyML model training and deployment.
- Real-time classification and output integration.

---

## 2. Project Description
### 2.1 Problem Context
Embedded systems often rely on mechanical interfaces (buttons, toggles). These are simple but less flexible and can reduce usability in dynamic interaction scenarios. Gesture-based control offers intuitive, contact-light interaction but introduces classification challenges due to user variability, orientation differences, and sensor noise.

### 2.2 Project Goal
Develop a Photon 2-based TinyML gesture classifier using ADXL343 acceleration data, with live output mapping to:
1. **Provisio command protocol** over serial.
2. **LED/RGB LED visual response** for immediate local feedback.

### 2.3 Gesture Vocabulary
Target gestures (final set may be adjusted for separability):
- Idle / No gesture
- Swipe Left
- Swipe Right
- Push Forward
- Pull Back
- Shake
- Double Tap
- Circle (optional if separability allows)

### 2.4 Deliverable Summary
- Embedded hardware prototype (Photon 2 + ADXL343 + LED/RGB LED).
- Labeled gesture dataset (CSV format with metadata).
- Trained and optimized model for embedded inference.
- Firmware implementing real-time pipeline.
- Documentation and exam report.

---

## 3. Requirements Analysis
This section maps course exam requirements to the project solution.

### 3.1 Functional Requirements
1. **Read data from connected local sensor**  
   - ADXL343 (I2C) sampled on Photon 2.

2. **Predict a class outcome**  
   - Gesture classification using TinyML model on-device.

3. **Implement ML/AI algorithm**  
   - Lightweight classifier (e.g., compact MLP/CNN or embedded-compatible model) trained on self-collected data.

4. **Collect and label own dataset**
   - Student-collected gesture recordings.
   - Label per recording/window.
   - Metadata included: sample rate, format, axis units, class label.

5. **Output and communication**
   - Serial protocol to host/Provisio test harness.
   - LED mapping for immediate status/gesture feedback.

### 3.2 Non-Functional Requirements
1. **Required platform**
   - Particle Photon 2 used as deployment target.

2. **Data and software sharing**
   - Source code, dataset, and hardware documentation organized for repository publication.

3. **Performance quality targets**
   - Live recognition accuracy target: ≥80%.
   - Inference latency target: <50 ms/window.
   - Model size and memory footprint suitable for MCU constraints.

4. **Robustness**
   - Reasonable tolerance to speed and orientation variation.

### 3.3 Constraints
- Tight timeline (9 days remaining).
- Limited hardware channels and embedded memory.
- Manual data collection variability.
- Need for simple, reliable demo for oral exam.

---

## 4. System Design
### 4.1 High-Level Architecture
1. **Sensor Layer**: ADXL343 provides x/y/z acceleration samples.
2. **Preprocessing Layer**: normalization + windowing (and optional feature extraction).
3. **Inference Layer**: embedded model predicts gesture class.
4. **Output Layer**:  
   - serial command (`G:<id>`) to Provisio interface  
   - LED/RGB feedback (class-dependent color/pattern)

### 4.2 Dataflow
1. Read accelerometer at fixed sample rate (e.g., 50 Hz).
2. Maintain rolling buffer (e.g., 100 samples = 2 s window).
3. Preprocess window identically to training pipeline.
4. Run model inference.
5. Apply smoothing (majority vote over last N windows).
6. Emit command + LED action on stable class detection.

### 4.3 Hardware Design
- **Particle Photon 2**
- **ADXL343** over I2C (SDA/SCL, 3.3V, GND)
- **LED or RGB LED** via GPIO (with current-limiting resistors)

Optional:
- Battery operation
- BLE communication (deferred unless required)

### 4.4 Communication Protocol
Minimal serial protocol for robust integration:
- ASCII line mode: `G:<gesture_id>\n`
- Optional confidence field: `G:<gesture_id>,P:<confidence>\n`

### 4.5 Design Choices and Rationale
- Accelerometer-only interface minimizes hardware complexity.
- On-device classification ensures low latency and no cloud dependency.
- LED output improves usability and demo clarity.
- Compact model prioritized over maximal complexity to satisfy MCU constraints.

---

## 5. Implementation
### 5.1 Data Acquisition Implementation
- Firmware streams timestamped acceleration data:  
  `timestamp_ms,ax,ay,az,label`
- Labeling mode controlled manually per trial session.
- Each recording saved as CSV file in gesture-specific naming scheme:
  `gesture_<label>_<trial>.csv`

### 5.2 Dataset and Labeling Strategy
- Balanced class distribution target.
- At least 20–30 recordings per gesture.
- Variation introduced intentionally:
  - speed (slow/normal/fast),
  - start orientation,
  - user execution style (if possible multiple users).

### 5.3 Preprocessing
- Sensor axis normalization.
- Segmentation into fixed windows.
- Two feasible approaches:
  1. Raw window input (time-series model).
  2. Statistical feature vector input (mean, std, min, max, magnitude metrics).
- Training and embedded preprocessing must be identical.

### 5.4 Model Training
Candidate compact models:
- **MLP baseline** for feature vectors.
- **1D CNN** for raw sequences.

Training setup:
- train/validation/test split
- class-balanced evaluation
- metric monitoring (accuracy, confusion matrix, per-class recall)

### 5.5 Model Optimization & Deployment
- Convert trained model to deployable format (e.g., TFLite / C array depending on chosen runtime).
- Post-training quantization to reduce memory and improve speed.
- Validate accuracy drop after quantization (target minimal degradation).

### 5.6 Embedded Firmware Integration
Firmware modules:
- Sensor driver wrapper
- Buffer/window manager
- Preprocessing
- Inference wrapper
- Decision smoothing
- Output mapper (serial + LED)

### 5.7 LED Output Mapping Example
- Idle: LED off / dim white
- Swipe Left: blue blink
- Swipe Right: green blink
- Push: yellow pulse
- Pull: purple pulse
- Shake: red rapid blink
- Double Tap: white double blink

---

## 6. Test and Verification
### 6.1 Test Objectives
- Verify functional correctness of data capture, inference, and output.
- Measure classification quality and system responsiveness.
- Confirm embedded resource feasibility.

### 6.2 Test Categories
1. **Unit-level checks**
   - Sensor readout integrity
   - Buffer length correctness
   - Protocol formatting

2. **Offline model validation**
   - Validation/test accuracy
   - Confusion matrix analysis
   - Class imbalance checks

3. **On-device live verification**
   - Gesture-by-gesture success rate
   - Latency measurement using timestamp/micros
   - Stability under repeated runs

4. **Integration test**
   - Command reception by host/Provisio harness
   - Correct LED pattern per detected class

### 6.3 Metrics
- Overall accuracy (%)
- Per-class precision/recall/F1
- Confusion matrix
- Inference latency (ms)
- Flash/RAM estimate
- False trigger rate during Idle windows

### 6.4 Acceptance Criteria
- Live accuracy ≥80% across selected gestures.
- Inference latency <50 ms/window.
- Stable command output and LED response.
- Model fits Photon 2 memory constraints.

### 6.5 Result Tables (to fill after testing)
| Metric | Result | Target | Status |
|---|---:|---:|---|
| Validation accuracy | [TBD]% | ≥80% | [TBD] |
| Live test accuracy | [TBD]% | ≥80% | [TBD] |
| Inference latency | [TBD] ms | <50 ms | [TBD] |
| Model size | [TBD] KB | MCU-fit | [TBD] |
| RAM usage | [TBD] KB | MCU-fit | [TBD] |

---

## 7. Discussion
### 7.1 Technical Reflection
Expected trade-offs:
- More gesture classes increase usability but reduce separability.
- Raw time-series models may improve accuracy but can cost more memory.
- Statistical features can be lightweight and robust but may lose temporal nuance.

### 7.2 Failure Modes
- Confusion between directional gestures.
- Variable execution amplitude causing class overlap.
- False positives during transition from idle to active gesture.

### 7.3 Mitigation
- Improve class definitions and recording consistency.
- Add smoothing / debounce logic.
- Merge problematic classes if confusion remains high.
- Collect targeted additional data for weak classes.

---

## 8. Conclusion
This project demonstrates a complete TinyML workflow on embedded hardware by building a gesture recognition interface on Particle Photon 2 with ADXL343. The implementation addresses course goals by combining local sensor acquisition, student-generated labeled data, model training and optimization, and real-time on-device inference.

By coupling classification output to both serial protocol commands and LED feedback, the artifact provides a practical and demonstrable interaction interface for Provisio integration. With successful validation of accuracy, latency, and memory constraints, the project establishes a solid baseline TinyML embedded system and a platform for future extensions such as personalization, BLE communication, and sensor fusion.

---

## 9. Future Work
- Personalized calibration profiles per user.
- Sensor fusion with gyroscope for improved rotational gesture separation.
- Confidence-aware command gating.
- BLE integration for cable-free interface.
- Adaptive thresholding / online update strategy.

---

## 10. Literature and Theory Basis
This report is grounded in:
1. **Course material (ETTML-01 TinyML)**:
   - Photon 2 hardware workflow
   - Data acquisition and feature engineering
   - Embedded ML deployment and optimization topics (quantization/pruning)
   - Semester project requirements and reporting structure

2. **Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (3rd ed.)**
   - Practical ML pipeline design
   - Model evaluation discipline and reproducible workflow
   - Training/validation methodology

3. **Machine Learning with PyTorch and Scikit-Learn**
   - Foundational concepts in supervised classification
   - Preprocessing, scaling, and model evaluation
   - Overfitting and regularization fundamentals

---

## 11. References
- ETTML-01 Tiny Machine Learning course pages (Welcome, Hardware, Software, Literature, Semester/Exam Project).
- Project Description: *Tiny Machine Learning Gesture Interface for Provisio*.
- Géron, A. *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (3rd ed.).
- Raschka, S., Liu, Y., Mirjalili, V. *Machine Learning with PyTorch and Scikit-Learn*.

---

## Appendix A – Practical Build Checklist
- [ ] Wire ADXL343 to Photon 2 (I2C)
- [ ] Wire LED/RGB LED with resistors
- [ ] Verify raw sensor stream
- [ ] Record balanced dataset
- [ ] Train and select model
- [ ] Deploy model to Photon 2
- [ ] Validate live inference
- [ ] Record metrics for report tables

## Appendix B – Oral Demo Script (Short)
1. Show hardware and explain sensor + MCU + output chain.  
2. Perform 2–3 gestures and show LED + serial output.  
3. Summarize model type, dataset size, and key metrics.  
4. Explain one limitation and one improvement path.
