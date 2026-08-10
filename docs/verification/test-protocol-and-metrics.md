# Test protocol and metrics

This file separates completed evidence from recommended follow-up tests.

## Completed release checks

| Check | Result |
|---|---|
| Accepted class balance | 5 each: idle, tap1, tap2, tap3, shake_lr |
| Samples per trial | 1,600 |
| Median sample interval | 2,498–2,501 µs |
| Missing values / clipping | none |
| Held-out accuracy | 80% (4/5) |
| Macro precision / recall / F1 | 70.0% / 80.0% / 73.3% |
| Firmware flash / RAM | 27,950 B / 46,686 B |
| Inference mean / maximum | 345 µs / 364 µs |
| Sensor read errors in status check | 0 |
| Physical LIVE LED test | pass |

## Required interpretation

The test split contains one case per class and comes from the same operator and
session as training. It verifies the software/deployment chain but cannot
establish user-independent accuracy.

## Recommended next protocol

1. Capture at least three sessions on different days.
2. Hold out a complete session before any tuning.
3. Run a randomized sequence with at least 20 attempts per active class.
4. Leave the device untouched for 10 minutes and count false events.
5. Record decision latency from first impact to `EVENT`, not only MLP runtime.
6. Run a 15-minute soak test and record read errors and memory stability.

