# Implementation Execution Log
## TinyML Gesture Reader (Photon 2 + ADXL343)

## 2026-08-10 — Mode Architecture, Idle Class, and Verified Deployment

### Implemented

- Added explicit DEBUG, TRAINING, and LIVE operating modes.
- Kept the TRAINING capture phases as a separate nested state machine.
- Unified each logical capture tick around one physical accelerometer read.
- Framed and persisted exact 50-sample idle trials; collected 15 real trials.
- Implemented 0.2 s overlapping LIVE stride, three consistent-prediction
  smoothing, 300 ms debounce, EVENT output, and deterministic RGB patterns.
- Added inference timing and sensor-read error counters to STATUS.
- Added real CLI config parsing and fail-closed atomic model export.
- Increased MLP max_iter from 40 to 500 after the 40-iteration run failed to
  converge.

### Measured outcome

- Dataset: 75 windows, balanced at 15 for each of five classes.
- Held-out split: 15 windows, random state 42, stratified.
- Accuracy: 80.0%; macro precision 85.3%; macro recall 80.0%; macro F1 78.3%.
- Cloud build: 26,270 B flash and 4,150 B static RAM.
- Short on-device check: mean model inference 0.49 ms, max 3.09 ms,
  zero sensor read errors, and zero LIVE events during 10 stationary seconds.
- Firmware flashed successfully to `TinyML_Node1`.

### Interpretation

The end-to-end five-class path is functional and reaches the project accuracy
target on a small split. Tap2/tap3 remain the weakest classes, and the short
stationary check is not a substitute for the planned five-minute false-trigger
test or controlled live confusion matrix.

This log records **actions, decisions, rationale, outcomes, and next steps** from preparation to execution.  
Goal: keep implementation reproducible, simple, and exam-ready.

---

## 2026-08-01 — Session Start (Foundation + Readiness Pass)

### Objective
Establish a reliable model-development and deployment foundation **before full hardware assembly**.

### Context at Start
- ML scaffold already present:
  - `Product/ml/train.py`
  - `Product/ml/export_model.py`
  - `Product/ml/config.yaml`
  - `Product/ml/capture_guided.py`
- Planning docs present:
  - `Product/data/DATASET_SPEC.md`
  - `Product/firmware/INFERENCE_INTEGRATION_PLAN.md`
  - `Report/TinyML_Gesture_Report.typ`
- Hardware not fully wired yet (ADXL343 pending).

---

## Action 1 — Scope and Delivery Strategy

### Decision
Use a **two-phase path**:
1. **Pre-hardware phase**: validate pipeline, export artifacts, prepare firmware interfaces and logging workflow.
2. **Hardware phase**: wire ADXL343, run guided capture, retrain with real data, redeploy updated model.

### Rationale
This reduces risk and avoids blocking on hardware assembly while still producing meaningful progress for report and exam readiness.

### Outcome
Plan accepted and execution started.

### Next
Add explicit runbook/checklists and architecture/diagram support docs.

---

## Action 2 — Guided Capture Baseline Already Added

### Decision
Keep the guided serial protocol simple and robust:
- `PROMPT,label=<label>,trial=<n>`
- `SAMPLE,timestamp=<ms>,ax=<f>,ay=<f>,az=<f>`
- `RESULT,status=ok|fail,label=<label>,trial=<n>,reason=<optional>`
- `INFO,message=<text>`

### Rationale
A small deterministic protocol is easier to debug on embedded systems and easier to document in report and oral exam.

### Outcome
`Product/ml/capture_guided.py` exists and uses this protocol.

### Next
Validate script readiness during testing pass and keep documentation aligned.

---

## Action 3 — Documentation Quality Requirement

### Decision
All implementation outputs must be:
- simple,
- strongly commented where needed,
- standards-aligned for TinyML + embedded workflow,
- directly runnable with minimal fixes.

### Rationale
Project timeline is tight; reliability and clarity are higher priority than feature breadth.

### Outcome
Set as an explicit project constraint for all further edits and testing.

### Next
Apply to README/runbook, firmware integration checklist, and report implementation section.

---

## Current Status Snapshot
- [x] Model-training scaffold exists.
- [x] Export scaffold exists.
- [x] Guided capture script exists.
- [ ] Hardware wiring complete (ADXL343 + LEDs).
- [ ] Hardware-in-the-loop data collection validated.
- [ ] Final model retrained on real gesture data.
- [ ] On-device inference fully validated with live gestures.

---

## Pending Execution Steps (This Work Package)
1. Add concrete PowerShell runbook in `Product/ml/README.md`.
2. Add hardware diagram scaffold file (Mermaid).
3. Extend firmware integration plan with model-upload and pre-wire checklist.
4. Add implementation action→decision documentation to Typst report.
5. Run critical-path software tests and record outcomes here.

---

## Testing Ledger (to be updated this session)
### Already known from previous session
- `train.py` and `export_model.py` executed successfully in prior iteration.
- `capture_guided.py` initially failed due to missing `pyserial`; dependency was installed into `.venv`.

### To verify now
- [ ] `capture_guided.py --help` runs cleanly.
- [ ] `train.py` executes with current config/data.
- [ ] `export_model.py` writes expected artifact summary.

---

## Risks and Mitigations
### Risk 1: Limited real data quality at first hardware run
- Mitigation: guided LED-assisted collection and immediate trial acceptance/rejection flow.

### Risk 2: Train/inference mismatch
- Mitigation: keep preprocessing parity as first-priority check in firmware integration.

### Risk 3: Time pressure before Sunday
- Mitigation: maintain critical path (working baseline + documented runbook + report updates) and defer non-essential enhancements.

---

## Definition of Done for This Package
- Software pipeline runnable from documented commands.
- Deployment preparation documented clearly.
- Hardware diagram scaffold ready for final schematic conversion.
- Report implementation section updated with actual action/decision process.
- Remaining hardware-dependent tasks explicitly listed for follow-up.
