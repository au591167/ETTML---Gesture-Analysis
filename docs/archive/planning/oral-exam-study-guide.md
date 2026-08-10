# Oral Exam Quick Study Guide  
## TinyML Gesture Interface (Photon 2 + ADXL343)

This is a fast revision guide for oral exam preparation.

---

## 1) 60-second Project Pitch
I built an embedded TinyML gesture-recognition interface on a Particle Photon 2 using an ADXL343 accelerometer.  
The device classifies hand gestures in real time and outputs both:
1. Serial commands for Provisio integration, and
2. LED/RGB feedback for immediate local confirmation.

The project demonstrates the full TinyML pipeline:
- self-collected labeled data,
- preprocessing and model training,
- model optimization,
- deployment on microcontroller,
- live on-device inference and verification.

---

## 2) Core TinyML Concepts You Must Explain Clearly

### What is TinyML?
Machine learning inference on resource-constrained hardware (microcontrollers), focused on low latency, low power, and local decision-making.

### Why TinyML here?
Gesture recognition must feel immediate. On-device inference avoids cloud delay and supports offline operation.

### Classification vs regression vs anomaly detection
- **Classification**: predict class labels (used in this project).
- **Regression**: predict continuous values.
- **Anomaly detection**: detect outliers from normal behavior.

### Why this is not rule-based only
Hand gestures vary in speed/orientation/user style. Pure threshold/rule systems become brittle. ML generalizes better to variation when trained correctly.

---

## 3) Hardware Talking Points

### Components
- Particle Photon 2 (required platform)
- ADXL343 (3-axis accelerometer)
- LED or RGB LED + resistors

### Signal path
Gesture motion → acceleration samples (x,y,z) → preprocessing/windowing → model inference → command + LED action.

### Why ADXL343?
Simple, available, suitable for motion-based gesture classification in a constrained setup.

---

## 4) Data Pipeline Talking Points

### Data collection
- Collected own dataset (course requirement).
- Multiple trials per gesture.
- Saved in CSV with labels + metadata.

### Metadata examples
- sample rate (Hz)
- columns/format (`timestamp, ax, ay, az, label`)
- unit/axis meaning

### Why balancing classes matters
Imbalanced classes can bias model toward frequent gestures and reduce practical usability.

---

## 5) Model & Training Talking Points

### Candidate models
- Lightweight MLP on engineered features
- Small 1D-CNN on raw windows

### Why lightweight model?
MCU constraints (RAM/Flash) and real-time inference goals.

### Overfitting explanation
Model may perform very well on training data but poorly on unseen live gestures.  
Mitigation: validation split, regularization, more varied training data, class balancing.

### Quantization (if used)
Converts model weights/activations to lower precision (e.g., int8), reducing memory and improving inference speed with minor accuracy trade-off.

---

## 6) Embedded Inference Talking Points

### Runtime steps
1. Sample sensor at fixed rate.
2. Build fixed-size window.
3. Apply same preprocessing as training.
4. Run inference.
5. Smooth outputs (majority vote).
6. Trigger serial command + LED pattern.

### Why smoothing?
Reduces jitter and false rapid class switching in real-time use.

### Latency goal
Keep inference and decision delay low enough for responsive interaction (target <50 ms inference per window).

---

## 7) Verification Talking Points

### What to report
- Overall accuracy
- Per-class confusion matrix
- Latency
- Memory footprint
- False positives during idle

### Why confusion matrix matters
Shows which specific gestures are confused, guiding data recollection and class redesign.

### Typical failure cases
- Similar directional motions (left/right confusion)
- Variable amplitude/speed
- Idle-transition false triggers

---

## 8) Likely Oral Questions + Strong Answer Frames

### Q1: Why choose gesture recognition?
**Answer frame:** Strong TinyML fit, self-collectable data, real-time embedded classification, practical demo value.

### Q2: Why Photon 2?
**Answer frame:** Course-mandated embedded platform; sufficient I/O and compute for compact on-device inference.

### Q3: Why not cloud inference?
**Answer frame:** Latency, reliability, privacy, and independence from network; TinyML objective is local inference.

### Q4: How did you ensure data quality?
**Answer frame:** Structured labeling, metadata, balanced classes, repeated trials with variation, outlier cleanup.

### Q5: How did you prevent overfitting?
**Answer frame:** train/validation/test discipline, small model capacity, regularization (if used), data variation.

### Q6: What did quantization change?
**Answer frame:** Reduced model size and likely faster inference; monitored post-quantization accuracy impact.

### Q7: Biggest engineering trade-off?
**Answer frame:** Accuracy vs memory/latency. Chose a compact model that fits MCU while maintaining acceptable live performance.

### Q8: What would you improve next?
**Answer frame:** personalized calibration, sensor fusion, stronger confidence gating, BLE protocol.

---

## 9) 3-Minute Technical Presentation Skeleton

1. **Problem and motivation (30s)**
   - Buttons vs gesture interface, TinyML fit.

2. **System architecture (45s)**
   - Photon 2 + ADXL343 + LED + serial output.

3. **Data and model pipeline (60s)**
   - Collection, labeling, preprocessing, training, quantization, deployment.

4. **Results and metrics (30s)**
   - Accuracy, latency, confusion matrix highlights.

5. **Limitations + future work (15s)**
   - hardest gesture confusions + extension plan.

---

## 10) Quick Revision Checklist (Night Before Exam)
- [ ] Can explain TinyML in one sentence.
- [ ] Can justify model and feature choices.
- [ ] Can explain training/validation/test split.
- [ ] Can explain confusion matrix interpretation.
- [ ] Can explain one failure mode and mitigation.
- [ ] Can explain why this satisfies course functional and non-functional requirements.
- [ ] Can deliver a clean live demo flow in under 5 minutes.
