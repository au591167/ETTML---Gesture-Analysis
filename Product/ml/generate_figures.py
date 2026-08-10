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
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from train import build_dataset, load_config, load_raw_data, train_model, validate_class_coverage

RAW_DIR = Path("Product/data/pilot_v3/20260810_141717/accepted")
OUT_DIR = Path("Report/src/img")

CLASSES = ["idle", "tap1", "tap2", "tap3", "shake_lr"]
AXES = ["ax", "ay", "az"]

def load_trials(label: str) -> list[pd.DataFrame]:
    """Load all CSV trial files for a given gesture class, skipping empty files."""
    trials = []
    for fp in sorted(RAW_DIR.glob(f"{label}_*.csv")):
        if fp.stat().st_size == 0:
            print(f"[WARN] Skipping empty trial file: {fp}")
            continue
        df = pd.read_csv(fp).rename(
            columns={"time_us": "timestamp", "x_g": "ax", "y_g": "ay", "z_g": "az"}
        )
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
                t_ms = (t["timestamp"] - t["timestamp"].iloc[0]) / 1e3
                for a in AXES:
                    ax.plot(t_ms, t[a], color=colors[a], alpha=0.55, linewidth=1.0,
                            label=a if t is trials[0] else None)
        else:
            ax.text(0.5, 0.5, "ingen data", ha="center", va="center",
                    transform=ax.transAxes, style="italic", color="gray")

        ax.set_ylabel(f"{cls}\n(g)", fontsize=9)
        ax.grid(alpha=0.3, linewidth=0.5)

    axes[0].legend(loc="upper right", fontsize=8, ncol=3)
    axes[-1].set_xlabel("Tid (ms)")
    fig.suptitle("Accelerometersignaler pr. gestusklasse (ax/ay/az)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    out = OUT_DIR / "gesture_signals.png"
    fig.savefig(str(out), dpi=150)
    plt.close(fig)
    print(f"[OK] Wrote {out}")


def evaluate_confusion() -> tuple[list[str], np.ndarray]:
    """Reproduce train.py's held-out split instead of embedding stale numbers."""
    cfg = load_config("Product/ml/config.yaml")
    df = load_raw_data(Path(cfg["data"]["raw_dir"]), cfg["data"]["file_glob"])
    X, y = build_dataset(cfg, df)
    validate_class_coverage(cfg, y)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=cfg["evaluation"]["test_size"],
        random_state=cfg["evaluation"]["random_state"],
        stratify=y_encoded,
    )
    scaler = StandardScaler()
    model = train_model(cfg, scaler.fit_transform(X_train), y_train)
    predicted = model.predict(scaler.transform(X_test))
    labels = list(range(len(encoder.classes_)))
    return [str(x) for x in encoder.classes_], confusion_matrix(y_test, predicted, labels=labels)


def plot_confusion_matrix() -> None:
    cm_labels, confusion = evaluate_confusion()
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(confusion, cmap="Blues")

    ax.set_xticks(np.arange(len(cm_labels)), labels=cm_labels, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(cm_labels)), labels=cm_labels)
    ax.set_xlabel("Forudsagt klasse")
    ax.set_ylabel("Faktisk klasse")
    ax.set_title(f"Confusion matrix (held-out test, {int(confusion.sum())} vinduer)", fontsize=12)

    # Annotate each cell.
    for i in range(len(cm_labels)):
        for j in range(len(cm_labels)):
            val = confusion[i, j]
            color = "white" if val > confusion.max() / 2 else "black"
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
