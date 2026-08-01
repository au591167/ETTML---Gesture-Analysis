# Feature Specification (stat_v1)

This document defines the first lightweight feature set for embedded TinyML gesture classification.

## Window definition
- Sampling rate: 50 Hz
- Window length: 1.0 s (50 samples)
- Stride: 0.2 s (10 samples overlap step)
- Channels: `ax, ay, az` + optional magnitude `mag = sqrt(ax^2 + ay^2 + az^2)`

## Preprocessing order
1. Slice window.
2. If enabled, compute `mag`.
3. Remove per-window mean for each channel.
4. Apply scaling (standardization) using **training-set fitted** scaler.
5. Compute features.

> On-device preprocessing must match this order exactly.

## Per-channel features
For each selected channel (`ax, ay, az, mag`), compute:

1. **mean**  
   \[
   \mu = \frac{1}{N}\sum x_i
   \]

2. **std**  
   \[
   \sigma = \sqrt{\frac{1}{N}\sum (x_i-\mu)^2}
   \]

3. **min**  
   \[
   \min(x)
   \]

4. **max**  
   \[
   \max(x)
   \]

5. **range**  
   \[
   \max(x) - \min(x)
   \]

6. **energy**  
   \[
   \frac{1}{N}\sum x_i^2
   \]

7. **zero_crossings**  
   Count sign changes between consecutive samples (optionally with small epsilon deadband).

## Expected feature count
- 4 channels × 7 features = 28 features (if magnitude enabled)
- 3 channels × 7 features = 21 features (if magnitude disabled)

## Notes for stability
- Keep feature definitions simple and deterministic.
- Avoid expensive transforms in first model version.
- Add extra features only if confusion matrix indicates clear need.

## Label set (current)
- `idle`
- `tap1`
- `tap2`
- `tap3`
- `shake_lr`

## Command mapping (demo layer)
- `tap1 -> stand`
- `tap2 -> hit`
- `shake_lr -> split`
- `tap3 -> exit`
