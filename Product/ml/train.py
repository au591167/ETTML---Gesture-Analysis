"""
TinyML Gesture Model Training Scaffold (feature-based baseline)

This is a foundation script, intentionally lightweight:
- Loads config
- Loads CSV data
- Builds sliding windows
- Extracts stat_v1 features
- Trains a compact baseline model (MLP by default)
- Prints core metrics and confusion matrix

Adjust paths and data format in config.yaml as needed.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import yaml

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
)
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier


def load_config(path: str = "Product/ml/config.yaml") -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_raw_data(raw_dir: Path, file_glob: str) -> pd.DataFrame:
    # Data is organized per-class in subdirectories (e.g. raw/tap1/*.csv),
    # so search recursively to collect all trial files.
    files = sorted(raw_dir.rglob(file_glob))
    if not files:
        raise FileNotFoundError(f"No CSV files found in: {raw_dir}")

    chunks = []
    for fp in files:
        df = pd.read_csv(fp)
        df["__source_file"] = fp.name
        chunks.append(df)
    return pd.concat(chunks, ignore_index=True)


def compute_magnitude(df: pd.DataFrame) -> pd.Series:
    # Coerce to numeric explicitly; concatenated CSVs can yield object dtype.
    ax = pd.to_numeric(df["ax"], errors="coerce").fillna(0.0)
    ay = pd.to_numeric(df["ay"], errors="coerce").fillna(0.0)
    az = pd.to_numeric(df["az"], errors="coerce").fillna(0.0)
    return np.sqrt(ax ** 2 + ay ** 2 + az ** 2)


def sliding_windows(
    df: pd.DataFrame,
    sample_rate_hz: int,
    window_seconds: float,
    stride_seconds: float,
) -> List[pd.DataFrame]:
    win = int(sample_rate_hz * window_seconds)
    stride = int(sample_rate_hz * stride_seconds)

    if win <= 0 or stride <= 0:
        raise ValueError("Window and stride must be positive.")

    windows = []
    start = 0
    n = len(df)
    while start + win <= n:
        windows.append(df.iloc[start : start + win].copy())
        start += stride
    return windows


def zero_crossings(x: np.ndarray, eps: float = 1e-6) -> int:
    x2 = x.copy()
    x2[np.abs(x2) < eps] = 0.0
    s = np.sign(x2)
    return int(np.sum((s[:-1] * s[1:]) < 0))


def channel_features(x: np.ndarray) -> List[float]:
    mean = float(np.mean(x))
    std = float(np.std(x))
    mn = float(np.min(x))
    mx = float(np.max(x))
    rng = mx - mn
    energy = float(np.mean(x ** 2))
    zc = float(zero_crossings(x))
    return [mean, std, mn, mx, rng, energy, zc]


def extract_features_for_window(window_df: pd.DataFrame, use_mag: bool) -> List[float]:
    channels = ["ax", "ay", "az"]
    if use_mag:
        channels = channels + ["mag"]

    feats: List[float] = []
    for c in channels:
        x = window_df[c].to_numpy(dtype=np.float32)
        # remove per-window mean (configured behavior for baseline)
        x = x - np.mean(x)
        feats.extend(channel_features(x))
    return feats


def majority_label(window_df: pd.DataFrame) -> str:
    return str(window_df["label"].mode().iloc[0])


def build_dataset(cfg: Dict, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    sr = cfg["sampling"]["sample_rate_hz"]
    ws = cfg["sampling"]["window_seconds"]
    ss = cfg["sampling"]["stride_seconds"]
    use_mag = bool(cfg["preprocessing"]["use_magnitude_channel"])

    if use_mag and "mag" not in df.columns:
        df = df.copy()
        df["mag"] = compute_magnitude(df)

    X_list: List[List[float]] = []
    y_list: List[str] = []

    # build windows per source file to avoid crossing trial boundaries
    for _, g in df.groupby("__source_file"):
        wins = sliding_windows(g, sr, ws, ss)
        for w in wins:
            X_list.append(extract_features_for_window(w, use_mag))
            y_list.append(majority_label(w))

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=object)
    return X, y


def train_model(cfg: Dict, X_train: np.ndarray, y_train: np.ndarray):
    fam = cfg["model"]["family"].lower()
    if fam == "rf":
        rf = cfg["model"]["rf"]
        model = RandomForestClassifier(
            n_estimators=rf["n_estimators"],
            max_depth=rf["max_depth"],
            random_state=rf["random_state"],
        )
    else:
        mlp = cfg["model"]["mlp"]
        model = MLPClassifier(
            hidden_layer_sizes=tuple(mlp["hidden_layers"]),
            activation=mlp["activation"],
            max_iter=mlp["epochs"],
            batch_size=mlp["batch_size"],
            learning_rate_init=mlp["learning_rate"],
            random_state=cfg["evaluation"]["random_state"],
        )
    model.fit(X_train, y_train)
    return model


def main():
    cfg = load_config()

    raw_dir = Path(cfg["data"]["raw_dir"])
    file_glob = cfg["data"]["file_glob"]

    df = load_raw_data(raw_dir, file_glob)

    required = set(cfg["data"]["expected_columns"])
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    X, y = build_dataset(cfg, df)

    if len(X) == 0:
        sr = cfg["sampling"]["sample_rate_hz"]
        ws = cfg["sampling"]["window_seconds"]
        required_samples = int(sr * ws)
        raise ValueError(
            "No training windows were produced from the available CSV files. "
            f"Current window config requires at least {required_samples} samples per trial "
            f"({ws}s at {sr}Hz). Add longer recordings or reduce window_seconds/adjust sample_rate_hz."
        )

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    class_counts = np.bincount(y_enc)
    min_class_count = int(class_counts.min()) if len(class_counts) > 0 else 0
    stratify_arg = y_enc if min_class_count >= 2 else None
    if stratify_arg is None:
        print(
            "WARNING: At least one class has fewer than 2 samples/windows. "
            "Falling back to non-stratified train/test split for this run."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_enc,
        test_size=cfg["evaluation"]["test_size"],
        random_state=cfg["evaluation"]["random_state"],
        stratify=stratify_arg,
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = train_model(cfg, X_train_s, y_train)

    y_pred = model.predict(X_test_s)

    acc = accuracy_score(y_test, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("=== Baseline Results ===")
    print(f"Samples: {len(X)} | Features: {X.shape[1]}")
    print(f"Accuracy:        {acc:.4f}")
    print(f"PrecisionMacro:  {p:.4f}")
    print(f"RecallMacro:     {r:.4f}")
    print(f"F1Macro:         {f1:.4f}")
    print("\nLabel map:")
    for i, name in enumerate(le.classes_):
        print(f"  {i}: {name}")

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    all_labels = list(range(len(le.classes_)))
    print(
        classification_report(
            y_test,
            y_pred,
            labels=all_labels,
            target_names=[str(x) for x in le.classes_],
            zero_division=0,
        )
    )


if __name__ == "__main__":
    main()
