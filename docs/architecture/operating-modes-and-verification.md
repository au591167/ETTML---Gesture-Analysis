# Operating modes and verification

## Modes

| Mode | Purpose | Gesture actions |
|---|---|---|
| DEBUG | Sensor/model diagnostics and high-rate scope capture | Suppressed |
| TRAINING | Firmware-guided labelled acquisition state machine | Capture cues only |
| LIVE | Continuous model inference and application feedback | Enabled |

Select modes with `MODE DEBUG`, `MODE TRAINING`, and `MODE LIVE`. `STATUS`
reports the current mode, sensor health, window fill, inference timing, and read
errors.

## LIVE event contract

```text
EVENT,class=<label>,command=<mapping>,score=<probability>
```

Idle and low-confidence predictions emit no application event. Accepted
gestures use these patterns:

| Class | Pattern |
|---|---|
| tap1 | blue for 1 second |
| tap2 | blue ×2 at 0.5-second cadence |
| tap3 | red ×3 at approximately 0.33-second cadence |
| shake_lr | red-blue-red-blue at 1-second cadence |

## Verified release state

- Balanced deploy dataset: 25 accepted windows, five per class
- CSV integrity: 1,600 rows each, monotonic timestamps, no NaN or clipping
- Held-out accuracy: 80% on five cases; small-sample limitation applies
- Firmware: cloud compile and flash succeeded
- Runtime: sensor OK, zero read errors, 345/364 µs mean/max inference
- Physical LIVE feedback: confirmed working

Unfinished robustness tests are session-held-out evaluation, a timed idle
false-trigger run, multi-user testing, and an endurance/power test.

