# Dataset and Acquisition Protocol v2

## Status

This document defines the next acquisition cycle. It is a protocol and release
gate, not evidence that v2 collection, training, deployment, or verification
has already completed.

The v2 change is intentionally breaking: recordings made with the earlier
50-sample/1.0-second protocol must not be silently mixed with v2 recordings.

## Fixed v2 parameters

| Parameter | v2 contract |
|---|---|
| Sample rate | 50 Hz target |
| Active-gesture window | 1.5 seconds |
| Samples per active trial | Exactly 75 |
| Idle settle period | 2.0 seconds before idle capture begins |
| Tap spacing | 250–300 ms between consecutive taps |
| Classes | `idle`, `tap1`, `tap2`, `tap3`, `shake_lr` |
| Pilot size | 5 accepted trials per class |
| Pilot total | 25 accepted trials |

The 75 samples are the saved classification window. Cue time, the idle settle
period, operator reaction time, and confirmation time are outside that window.

## Why v2 is separate

The earlier recordings used a shorter window and were collected while the
capture/model contract was changing. Mixing them with v2 would make window
length, gesture timing, preprocessing, and evaluation provenance ambiguous.
The v2 dataset therefore starts from a clean namespace and receives its own
model/export identity.

The old files are not deleted. They remain useful as engineering history and
for explaining why the protocol changed, but they are not eligible v2 training
examples unless they are explicitly transformed and documented as derived
data. Repeating collection is preferred over transforming one-second trials.

## Archive-v1 and provenance procedure

Before the first v2 pilot:

1. Freeze the current raw-data inventory as `archive-v1` without modifying the
   original CSV contents.
2. Record a manifest containing every relative path, file size, checksum,
   label, row count, capture timestamp/session, and known protocol version.
3. Record the firmware commit or binary identifier, host capture-tool version,
   sensor configuration, sample-rate target, units, and operator/user ID when
   known.
4. Mark unknown metadata as `unknown`; do not reconstruct it as fact.
5. Store v2 recordings separately from archive-v1 so recursive training cannot
   ingest both generations accidentally.

Recommended conceptual layout:

```text
Product/data/
  archive-v1/
    manifest.csv
    raw/...
  v2/
    DATASET_MANIFEST.md
    pilot/
      idle/
      tap1/
      tap2/
      tap3/
      shake_lr/
    scale/
```

The exact move/copy operation is a separate data-management task. This
document does not authorize deleting, relocating, or rewriting current data.

## Per-session provenance

Each v2 session must record:

- protocol version: `v2`;
- date/time and session identifier;
- participant/operator identifier;
- Photon 2 device identifier and firmware version/commit;
- model/export version present on the device during capture;
- ADXL343 mode, range, resolution, units, and nominal scale;
- sample-rate target and measured cadence where available;
- window length: `1.5 s / 75 samples`;
- idle settle: `2.0 s`;
- tap rhythm: `250–300 ms`;
- orientation/grip and intentional variation notes;
- host tool version and command used;
- accepted, rejected, and retried trial counts per class.

Every saved CSV must be traceable to this session record through a session ID
or unambiguous filename. A label alone is not sufficient provenance.

## Gesture execution contract

### Idle

1. Show the idle cue.
2. The operator places the device in the documented neutral position.
3. Wait exactly 2.0 seconds for handling motion to settle.
4. Capture 75 stationary samples over 1.5 seconds.
5. Reject the trial if the device is touched, moved, or visibly unstable during
   the saved window.

The settle samples are not part of the saved idle window. This prevents the
act of putting the device down from being labeled as idle.

### Tap1

Perform one deliberate tap within the 1.5-second window. Keep tap force and
location representative of intended LIVE use. Do not add a second corrective
tap.

### Tap2

Perform exactly two deliberate taps. The onset-to-onset spacing between taps
must be 250–300 ms. Use an audible or visual pacing cue during the pilot if
needed; record whether a cue was used.

### Tap3

Perform exactly three deliberate taps. Each consecutive onset-to-onset spacing
must be 250–300 ms. Avoid accelerating the final pair or allowing taps to merge
into one long vibration burst.

### Shake left-right

Perform a deliberate lateral left-right shake within the saved window. Define
the starting orientation and expected number or duration of oscillations in
the session notes, then keep that definition stable within the pilot.

## Trial acceptance rules

Accept a v2 trial only when all of the following are true:

- exactly 75 samples were saved;
- required numeric columns and label are present;
- label, session ID, trial ID, and protocol version are traceable;
- timestamps are monotonic and cadence is plausible for 50 Hz;
- the requested gesture and tap count were actually performed;
- multi-tap spacing followed the 250–300 ms contract;
- no unrelated handling motion contaminated the window; and
- operator/automated acceptance is recorded.

Reject and repeat ambiguous trials. Do not relabel a failed prompted gesture as
another class merely because the current model predicted that class.

## Pilot-first gate

Collect only five accepted trials per class first:

| Class | Pilot target |
|---|---:|
| `idle` | 5 |
| `tap1` | 5 |
| `tap2` | 5 |
| `tap3` | 5 |
| `shake_lr` | 5 |

Do not scale collection until the 25-trial pilot passes these checks:

1. all files contain exactly 75 samples and valid provenance;
2. sample timing and units are consistent;
3. plots contain the intended gesture inside the saved window;
4. idle windows exclude placement/settling motion;
5. tap2/tap3 peaks reflect the fixed rhythm often enough to be separable;
6. preprocessing produces the expected feature dimension with no NaN/Inf;
7. a pilot training run completes without consuming archive-v1; and
8. firmware and host preprocessing agree for at least one known v2 window.

If the pilot fails, fix the protocol or implementation and recollect the
pilot. Do not compensate for a systematic acquisition defect by collecting
more defective trials.

## Scale-up after pilot approval

After pilot approval, collect additional v2 sessions with balanced classes and
controlled variation in speed, force, grip, and orientation. Keep sessions
separable so final evaluation can hold out a complete session rather than
randomly mixing near-neighbor recordings across train and test.

The scale-up target must be chosen after pilot signal review. Record the target
and rationale in the v2 manifest instead of inheriting an undocumented number
from v1.

## Train, deploy, and LIVE release gate

Acquisition does not update the model running on Photon 2. The required chain
after an approved v2 dataset is:

```text
v2 CSV data
  -> v2-only preprocessing and training
  -> held-out evaluation
  -> export new scaler and MLP parameters
  -> compile firmware containing those artifacts
  -> flash the identified Photon 2
  -> verify on-device feature/inference behavior
  -> enable and evaluate LIVE
```

**LIVE is invalid after the v2 protocol change until the model has been
retrained on v2 data, exported, recompiled, and reflashed.** A firmware build
that expects 75-sample windows but contains weights trained from v1 50-sample
windows is not a valid classifier, even if it compiles or produces plausible
scores.

Before LIVE is called valid, retain evidence of:

- approved v2 pilot and scaled dataset manifests;
- exact training input inventory and archive-v1 exclusion;
- evaluation metrics and split method;
- exported-artifact timestamp/hash and model version;
- firmware build identifier and successful flash target;
- Python/firmware preprocessing parity;
- controlled on-device trials for all five classes;
- idle false-trigger measurement;
- inference latency and window-cadence measurement; and
- correct serial/LED event mapping.

Until those gates pass, use DEBUG for inspection and TRAINING for acquisition.
Any LIVE output must be labeled experimental and must not be reported as
performance evidence for the v2 system.

## v2 completion record

Fill this table as work is completed; do not mark a row from memory alone.

| Gate | Evidence location | Date/version | Status |
|---|---|---|---|
| archive-v1 frozen and manifested |  |  | Pending |
| v2 pilot: 5 accepted trials/class |  |  | Pending |
| pilot signal/schema review |  |  | Pending |
| pilot preprocessing parity |  |  | Pending |
| scale-up dataset approved |  |  | Pending |
| v2 model trained and evaluated |  |  | Pending |
| v2 artifacts exported |  |  | Pending |
| firmware compiled and reflashed |  |  | Pending |
| on-device verification completed |  |  | Pending |
| LIVE released |  |  | Blocked by preceding gates |

