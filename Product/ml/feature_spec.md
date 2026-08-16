# Feature Specification (stat_v2)

This document defines the first lightweight feature set for embedded TinyML gesture classification.

## Window definition
- Sampling rate: 400 Hz
- Window length: 4.0 s (1,600 samples)
- Stride: 0.25 s (100 nye samples per step, 1,500 samples overlap)
- Channels: `ax, ay, az` + optional magnitude `mag = sqrt(ax^2 + ay^2 + az^2)`

## Preprocessing order
1. Slice window.
2. If enabled, compute `mag`.
3. Remove per-window mean for each channel.
4. Compute the seven statistical features for each channel.
5. Apply `StandardScaler` to the resulting **feature vector**, using means and
   scales fitted only on the training set.

> On-device preprocessing must match this order exactly.

The scaler does **not** standardize the 75 raw samples before feature
calculation. It standardizes the final 28-element feature vector immediately
before the MLP forward pass. This distinction matters because reversing the
order produces different min/max/range/energy values and invalidates the
deployed model.

## Per-channel features
For each selected channel (`ax, ay, az, mag`), compute:

1. **std**
   \[
   \sigma = \sqrt{\frac{1}{N}\sum (x_i-\mu)^2}
   \]

2. **min**
   \[
   \min(x)
   \]

3. **max**
   \[
   \max(x)
   \]

4. **range**
   \[
   \max(x) - \min(x)
   \]

5. **energy**
   \[
   \frac{1}{N}\sum x_i^2
   \]

6. **peak_count**
   On the mean-centered channel, let `a[i] = abs(x[i])` and
   `threshold = 0.05 g`. A sample is a candidate when
   `a[i] >= threshold`, `a[i] >= a[i-1]`, and `a[i] > a[i+1]`. Accept a
   candidate only when it is at least 8 samples (20 ms at 400 Hz) after the
   previous accepted peak. Endpoints are not candidates. The fixed physical
   threshold prevents an unusually strong first tap from hiding later taps;
   the refractory interval suppresses accelerometer ringing from one impulse.

7. **max_abs_diff**
   Maximum absolute difference between adjacent mean-centered samples:
   \[
   \max_{i=1\ldots N-1}|x_i-x_{i-1}|
   \]
   This is a lightweight jerk proxy; at a fixed sample rate, the omitted time
   division is a constant factor.

## Expected feature count
- 4 channels × 7 features = 28 features (if magnitude enabled)
- 3 channels × 7 features = 21 features (if magnitude disabled)

## Notes for stability
- Keep feature definitions simple and deterministic.
- Feature order is exactly `std, min, max, range, energy, peak_count,
  max_abs_diff` for each of `ax, ay, az, mag`.
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
