# 9-Day Completion Plan
## TinyML Gesture Project – Report + Product + Oral Exam Readiness

This plan is optimized for your current state:
- You have hardware parts (Photon 2 + ADXL343).
- Physical build is not yet assembled.
- You need report quality + working demo + oral readiness.

---

## Global Strategy
- **Day 1–2:** Build + data pipeline baseline (highest risk first).
- **Day 3–5:** Dataset + model training + embedded integration.
- **Day 6–7:** Live validation + metric collection + report finalization.
- **Day 8–9:** Presentation prep + buffer for issues.

---

## Daily Plan

## Day 1 — Hardware Bring-Up + Firmware Skeleton
### Deliverables
- Breadboard assembled (Photon 2 + ADXL343 + RGB LED).
- ADXL sensor read test working.
- LED test working.
- Firmware project skeleton created.

### Tasks
1. Wire hardware using `Product/Hardware_Wiring_and_BOM.md`.
2. Flash I2C sensor test.
3. Confirm acceleration values update with movement.
4. Flash RGB LED test and verify all channels.
5. Create firmware module placeholders (or equivalent files) per `Product/Firmware_Architecture.md`.

### Exit Criteria
- Sensor and LED both verified on actual hardware.
- No unresolved wiring uncertainty.

---

## Day 2 — Data Acquisition Pipeline
### Deliverables
- Reliable sampling stream from Photon 2.
- CSV logging script (or serial log method) running.
- Labeling workflow defined.

### Tasks
1. Implement fixed-rate sampling (target 50 Hz).
2. Print samples as `timestamp,ax,ay,az`.
3. Build PC-side logging script (Python serial) or save terminal logs.
4. Define labeling convention and file naming:
   - `gesture_<name>_<trial>.csv`
5. Capture small pilot dataset (3–5 trials/gesture) to validate pipeline.

### Exit Criteria
- You can record labeled files repeatedly without manual chaos.
- Metadata fields are present and consistent.

---

## Day 3 — Main Data Collection
### Deliverables
- Core dataset collected for all selected gestures.
- Initial class balance achieved.

### Tasks
1. Finalize gesture set (reduce if needed for reliability).
2. Record at least 20 trials/gesture (minimum baseline).
3. Include idle/no-gesture class.
4. Ensure movement variation:
   - slow / normal / fast
   - slight orientation differences
5. Spot-check files for corruption and mislabeling.

### Exit Criteria
- Dataset is complete enough for first real training cycle.
- No class is severely underrepresented.

---

## Day 4 — Preprocessing + Baseline Model Training
### Deliverables
- Reproducible preprocessing script.
- Baseline trained model with first validation metrics.

### Tasks
1. Build preprocessing script:
   - windowing
   - normalization/scaling
   - optional feature extraction
2. Split data train/validation/test.
3. Train baseline model (lightweight MLP or 1D model).
4. Generate:
   - overall accuracy
   - per-class metrics
   - confusion matrix
5. Identify top confusion pairs.

### Exit Criteria
- You have a baseline model and measurable results.
- You know which gestures are hardest.

---

## Day 5 — Model Improvement + Export
### Deliverables
- Improved model selected for deployment.
- Deployable model artifact generated.
- Quantized variant tested (if pipeline supports).

### Tasks
1. Improve model based on Day 4 errors:
   - class rebalancing
   - feature/preprocess tweaks
   - class pruning/merge if necessary
2. Retrain and compare metrics.
3. Export embedded-ready model format.
4. If possible, quantize and compare performance drop.

### Exit Criteria
- One model is chosen for embedded integration.
- You have “before vs after” metric story for report discussion.

---

## Day 6 — Embedded Inference Integration
### Deliverables
- Model running on Photon 2.
- Live gesture predictions visible on serial.
- LED mapped to class output.

### Tasks
1. Integrate model inference into firmware.
2. Mirror preprocessing on-device exactly.
3. Add decision smoothing (majority vote / confidence threshold).
4. Connect gesture ID to:
   - serial protocol command
   - LED/RGB pattern mapping
5. Perform quick end-to-end sanity tests.

### Exit Criteria
- Device performs real-time classification and output action.
- Pipeline works without manual intervention in loop.

---

## Day 7 — Verification and Metric Capture
### Deliverables
- Test protocol executed.
- Final metric tables filled.
- Evidence material for report and oral demo prepared.

### Tasks
1. Run tests from `Product/Test_Protocol_and_Metrics.md`.
2. Capture:
   - live accuracy
   - confusion matrix
   - latency stats
   - false trigger/idle behavior
3. Record memory/resource numbers from build output.
4. Save logs/screenshots/tables for report appendices.

### Exit Criteria
- You have hard numbers (not placeholders) for report.
- Demo behavior is stable enough for exam.

---

## Day 8 — Report Finalization + Slide Draft
### Deliverables
- Report near-final (PDF-ready content in markdown/doc workflow).
- Slide deck draft completed.

### Tasks
1. Fill `[TBD]` placeholders in `Report/TinyML_Gesture_Report_Draft.md`.
2. Add measured result tables and short interpretation.
3. Tighten references using:
   - `Report/Reference_Notes_Project_Relevant.md`
4. Build short presentation:
   - problem, architecture, pipeline, results, limitations.
5. Rehearse 5-minute demo sequence.

### Exit Criteria
- Report content is complete and coherent.
- Slides exist and follow time limit.

---

## Day 9 — Buffer + Rehearsal + Final Packaging
### Deliverables
- Final report and repository package.
- Oral defense confidence.

### Tasks
1. Resolve any final technical issues.
2. Final proofread report (structure, grammar, references).
3. Verify repository has required artifacts:
   - source code
   - data (or representative subset + description)
   - hardware docs
4. Rehearse Q&A using `Report/Oral_Exam_Quick_Study_Guide.md`.
5. Prepare fallback demo plan (video/log proof) in case live demo glitches.

### Exit Criteria
- Submission-ready package complete.
- You can explain design decisions and results calmly.

---

## Daily Minimum Checklist (Use Every Day)
- [ ] One concrete deliverable completed.
- [ ] Changes committed/saved in structured folders.
- [ ] A short note written: what worked, what blocked, next action.
- [ ] Tomorrow’s first task decided before stopping.

---

## Priority Rules (If Time Collapses)
1. **Must keep:** working hardware + basic model + evidence metrics + complete report structure.
2. **Can reduce:** gesture vocabulary size (quality over quantity).
3. **Can defer:** advanced features (BLE, OLED, multi-user adaptation).

---

## Suggested Folder Use (Final Structure Alignment)
- `Report/`
  - report draft, study guide, reference notes, schedule
- `Product/`
  - hardware wiring/BOM, firmware architecture, test protocol
  - actual firmware source and scripts (recommended subfolders)
- `Project Planning/`
  - source planning docs and course/project context (already present)

This keeps navigation clean and submission-friendly.
