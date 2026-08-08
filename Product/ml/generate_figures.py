"""
Generate report figures from real captured data.

Produces (saved to Report/src/img/):
  - gesture_signals.png     : time-series plot of ax/ay/az for each gesture class
  - confusion_matrix.png    : heatmap of the held-out test confusion matrix

Run from repo root:
    .venv\\Scripts\\python Product/ml/generate_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless backend (no display needed)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAW_DIR = Path("Product/data/raw")
OUT_DIR = Path("Report/src/img")

CLASSES = ["idle", "tap1", "tap2", "tap3", "shake_lr"]
AXES = ["ax", "ay", "az"]

# Held-out test confusion matrix from the baseline training run.
# Rows = true class, Cols = predicted class (order: shake_lr, tap1, tap2, tap3).
CM_LABELS = ["shake_lr", "tap1", "tap2", "tap3"]
CONFUSION = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0],
], dtype=int)


def load_trials(label: str) -> list[pd.DataFrame]:
    """Load all CSV trial files for a given gesture class, skipping empty files."""
    trials = []
    for fp in sorted((RAW_DIR / label).glob("*.csv")):
        if fp.stat().st_size == 0:
            print(f"[WARN] Skipping empty trial file: {fp}")
            continue
        df = pd.read_csv(fp)
        if len(df) > 0:
            trials.append(df)
        else:
            print(f"[WARN] Skipping empty trial file: {fp}")
    return trials


def plot_gesture_signals() -> None:
    fig, axes = plt.subplots(len(CLASSES), 1, figsize=(10, 2.4 * len(CLASSES)),
                             sharex=True)
    colors = {"ax": "#d62728", "ay": "#1f77b4", "az": "#2ca02c"}

    for ax_idx, cls in enumerate(CLASSES):
        ax = axes[ax_idx]
        trials = load_trials(cls)

        if trials:
            # Overlay all trials for the class, semi-transparent.
            for t in trials:
                t_ms = (t["timestamp"] - t["timestamp"].iloc[0]) / 1e3 if "timestamp" in t else np.arange(len(t)) / 50.0
                for a in AXES:
                    ax.plot(t_ms, t[a], color=colors[a], alpha=0.55, linewidth=1.0,
                            label=a if t is trials[0] else None)
        else:
            ax.text(0.5, 0.5, "ingen data", ha="center", va="center",
                    transform=ax.transAxes, style="italic", color="gray")

        ax.set_ylabel(f"{cls}\n(g)", fontsize=9)
        ax.grid(alpha=0.3, linewidth=0.5)

    axes[0].legend(loc="upper right", fontsize=8, ncol=3)
    axes[-1].set_xlabel("Tid (s)")
    fig.suptitle("Accelerometersignaler pr. gestusklasse (ax/ay/az)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    out = OUT_DIR / "gesture_signals.png"
    fig.savefig(str(out), dpi=150)
    plt.close(fig)
    print(f"[OK] Wrote {out}")


def plot_confusion_matrix() -> None:
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(CONFUSION, cmap="Blues")

    ax.set_xticks(np.arange(len(CM_LABELS)), labels=CM_LABELS, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(CM_LABELS)), labels=CM_LABELS)
    ax.set_xlabel("Forudsagt klasse")
    ax.set_ylabel("Faktisk klasse")
    ax.set_title("Confusion matrix (holdt-out test, 4 vinduer)", fontsize=12)

    # Annotate each cell.
    for i in range(len(CM_LABELS)):
        for j in range(len(CM_LABELS)):
            val = CONFUSION[i, j]
            color = "white" if val > CONFUSION.max() / 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=12)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    out = OUT_DIR / "confusion_matrix.png"
    fig.savefig(str(out), dpi=150)
    plt.close(fig)
    print(f"[OK] Wrote {out}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plot_gesture_signals()
    plot_confusion_matrix()
    print(f"\nDone. Figures written to: {OUT_DIR}")


if __name__ == "__main__":
    main()
