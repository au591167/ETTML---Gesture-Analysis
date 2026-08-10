# Baseline Dataset v1 Archive

This directory preserves the complete first acquisition experiment before the
v2 capture/feature redesign on 2026-08-10.

## Contents

- 96 CSV windows in total.
- `idle`: 16 windows.
- `tap1`, `tap2`, `tap3`, `shake_lr`: 20 windows each.
- 50 samples per window at a nominal 50 Hz (approximately 1.0 second).

## Why it was archived

The file structure and sampling cadence were valid, but a session-held-out
evaluation exposed poor generalization between the three tap-count classes.
Two early idle trials also contained obvious motion. The `stat_v1` feature set
mostly represented amplitude/distribution and did not encode tap count and
spacing strongly enough.

These files are retained as experimental evidence and must not be mixed into
the v2 training set under `Product/data/raw/`.

## v2 change

Dataset v2 uses 75-sample (1.5-second) windows, a stationary settling period,
a fixed 250-300 ms tap rhythm, and tap-sensitive peak-count/jerk features.
