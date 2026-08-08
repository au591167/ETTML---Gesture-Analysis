"""Lightweight impulse-count analysis of raw gesture CSVs (no pandas)."""
import csv
import glob
import os
from collections import defaultdict
import numpy as np


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                rows.append((float(row["ax"]), float(row["ay"]), float(row["az"])))
            except (ValueError, KeyError):
                continue
    arr = np.asarray(rows, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 3)
    return arr


def detect_impulses(arr, mag_thresh=0.5, min_gap=3):
    """Count distinct impulses = magnitude excursions above thresh, separated by min_gap samples."""
    if arr.shape[0] == 0:
        return 0, 0.0, 0.0
    mag = np.sqrt(arr[:, 0] ** 2 + arr[:, 1] ** 2 + arr[:, 2] ** 2)
    active = mag > mag_thresh
    count = 0
    in_impulse = False
    since_last = 0
    for a in active:
        if a:
            if not in_impulse:
                # new impulse only if enough gap since last one
                if since_last >= min_gap or count == 0:
                    count += 1
                in_impulse = True
            since_last = 0
        else:
            in_impulse = False
            since_last += 1
    return count, float(mag.max()), float(mag.mean())


results = defaultdict(list)
files = glob.glob("Product/data/raw/*/*.csv")
for f in sorted(files):
    label = f.split(os.sep)[-2]
    arr = load_csv(f)
    n, mx, mean = detect_impulses(arr)
    results[label].append((n, mx, mean, len(arr)))

print(f"{'class':<10} {'n_files':<8} {'impulse_counts':<40} {'max_mag_range':<20} {'len_range'}")
for label in sorted(results):
    data = results[label]
    counts = [d[0] for d in data]
    maxes = [d[1] for d in data]
    lens = [d[3] for d in data]
    cnt_str = str(sorted(counts))
    mx_str = f"{min(maxes):.2f}-{max(maxes):.2f}"
    ln_str = f"{min(lens)}-{max(lens)}"
    print(f"{label:<10} {len(data):<8} {cnt_str:<40} {mx_str:<20} {ln_str}")

# Per-file detail for tap3
print("\n--- tap3 detail (impulse_count, max_mag, n_samples) ---")
for f in sorted(glob.glob("Product/data/raw/tap3/*.csv")):
    arr = load_csv(f)
    n, mx, mean = detect_impulses(arr)
    print(f"  {os.path.basename(f)}: impulses={n} max_mag={mx:.2f} samples={len(arr)}")
