r"""
Auto-capture + model-validated confirmation for Photon 2 gesture data.

The firmware (main.cpp) DRIVES the guided baseline capture state machine:
- Host sends "START_BASELINE" to begin.
- Firmware runs a 10 s stationary phase (idle) -> emits RESULT,status=ok,label=idle.
- Firmware then cycles gestures internally (tap1, tap2, tap3, shake_lr), emitting
  PROMPT lines, waiting for PHYSICAL MOTION to auto-trigger a 1.0 s sampling
  window, then emits "INFO,message=confirm_ready" and waits for an OK/BAD
  confirmation over serial. On OK it emits RESULT,status=ok; on BAD it emits
  RESULT,status=fail and retries the same gesture.

This tool is a CONFIRMATION RESPONDER that:
- Sends "START_BASELINE" to begin.
- Reads the serial stream, buffering SAMPLE lines per trial.
- When the model is available, on each "confirm_ready" it evaluates the buffered
  window with the deployed model and sends "OK" only if the model's prediction
  matches the PROMPTED (expected) class at or above a confidence threshold;
  otherwise it sends "BAD" (auto-reject/retry).
- When no model is available, it sends "BAD" (so the operator can confirm
  manually) — or, with --auto-ok, always sends "OK".
- Saves each trial's samples to Product/data/raw/<label>/ on RESULT,status=ok.

Why this is safe (label-aware gating):
- The ground-truth label is the CLASS THE FIRMWARE PROMPTED, not the model output.
- The model is used only as a capture-quality gate: if the model agrees with the
  expected class at high confidence, the trial is consistent with what was asked
  and is appended to the dataset. If not, the trial is auto-retried.
- Retraining on the accepted dataset then improves accuracy, and the loop repeats
  for iterative self-improvement.

Serial protocol consumed (firmware -> host):
- PROMPT,label=<label>,trial=<n>
- SAMPLE,timestamp=<ms>,ax=<f>,ay=<f>,az=<f>
- RESULT,status=ok|fail,label=<label>,trial=<n>,reason=<optional>
- INFO,message=<text>   (including "confirm_ready" cue)

Host -> firmware: START_BASELINE, STOP_BASELINE, OK, BAD, ECHO_ON, ECHO_OFF

Usage (PowerShell, from repo root):
    .\.venv\Scripts\python Product/ml/auto_capture.py --port COM3 --baud 115200

Options:
    --port             Serial port (required), e.g. COM3
    --baud             Baud rate (default 115200)
    --out              Output raw root (default Product/data/raw)
    --confidence       Min softmax confidence to accept (default 0.75)
    --artifacts        Folder with model.pkl / scaler.json / label_encoder.pkl
    --auto-ok          Always send OK on confirm_ready (skip model gating)
    --timeout-ms       Max ms without any line before printing a progress note

The tool stops on Ctrl+C (sends STOP_BASELINE) or when the firmware reports
"baseline complete".
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import serial

try:
    from sklearn.preprocessing import StandardScaler  # noqa: F401 (used for parity)
    HAS_SKLEARN = True
except Exception:  # pragma: no cover
    HAS_SKLEARN = False


@dataclass
class SampleRow:
    timestamp: str
    ax: float
    ay: float
    az: float
    label: str
    trial_id: str


def parse_kv_message(line: str) -> tuple[str, Dict[str, str]]:
    parts = [p.strip() for p in line.strip().split(",") if p.strip()]
    if not parts:
        return "", {}
    kind = parts[0].upper()
    payload: Dict[str, str] = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            payload[k.strip().lower()] = v.strip()
    return kind, payload


def ensure_dirs(base_raw: Path, label: str) -> Path:
    out_dir = base_raw / label
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def write_trial_csv(out_file: Path, rows: List[SampleRow]) -> None:
    with out_file.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "ax", "ay", "az", "label", "trial_id"])
        for r in rows:
            w.writerow([
                r.timestamp,
                f"{r.ax:.6f}",
                f"{r.ay:.6f}",
                f"{r.az:.6f}",
                r.label,
                r.trial_id,
            ])


def zero_crossings(x: np.ndarray, eps: float = 1e-6) -> int:
    """Mirror train.py: zero out near-zero values, then count sign flips."""
    x2 = x.copy()
    x2[np.abs(x2) < eps] = 0.0
    s = np.sign(x2)
    return int(np.sum((s[:-1] * s[1:]) < 0))


def channel_features(x: np.ndarray) -> list:
    """Mirror train.py exactly: mean, std, min, max, range, energy, zero-cr."""
    mean = float(np.mean(x))
    std = float(np.std(x))
    mn = float(np.min(x))
    mx = float(np.max(x))
    rng = mx - mn
    energy = float(np.mean(x ** 2))  # NOTE: train.py uses MEAN of squares
    zc = float(zero_crossings(x))
    return [mean, std, mn, mx, rng, energy, zc]


def compute_stat_features(window: np.ndarray) -> np.ndarray:
    """Compute stat_v1 features for a window of shape (N, 3) as [ax, ay, az].

    Mirrors train.py exactly: adds magnitude channel, per-window mean removal
    per channel, then the 7 stat_v1 features per channel. Must match
    build_dataset() for validation parity.
    """
    arr = np.asarray(window, dtype=np.float64)  # (N, 3): ax, ay, az
    mag = np.sqrt(arr[:, 0] ** 2 + arr[:, 1] ** 2 + arr[:, 2] ** 2)
    cols = np.column_stack([arr, mag])  # (N, 4): ax, ay, az, mag

    feats: list = []
    for c in range(cols.shape[1]):
        x = cols[:, c].copy()
        x = x - np.mean(x)
        feats.extend(channel_features(x))
    return np.asarray(feats, dtype=np.float64)


def load_validator(artifacts: Path):
    """Load model, scaler mean/scale, and label encoder from artifacts."""
    if not HAS_SKLEARN:
        print("[validator] sklearn unavailable; validation disabled.")
        return None, None, None

    model_path = artifacts / "model.pkl"
    scaler_path = artifacts / "scaler.json"
    le_path = artifacts / "label_encoder.pkl"

    if not (model_path.exists() and scaler_path.exists() and le_path.exists()):
        print(f"[validator] Missing artifacts in {artifacts}. Run export_model.py first.")
        return None, None, None

    with model_path.open("rb") as f:
        model = pickle.load(f)
    scaler_cfg = json.loads(scaler_path.read_text(encoding="utf-8"))
    with le_path.open("rb") as f:
        le = pickle.load(f)

    mean = np.asarray(scaler_cfg["mean"], dtype=np.float64)
    scale = np.asarray(scaler_cfg["scale"], dtype=np.float64)
    return model, (mean, scale), le


def predict_window(model, mean, scale, le, window: np.ndarray) -> tuple[Optional[str], float]:
    """Return (predicted_label, confidence) for a window, or (None, 0.0)."""
    if model is None:
        return None, 0.0
    feats = compute_stat_features(window)
    denom = np.where(scale > 1e-9, scale, 1.0)
    feats_s = ((feats - mean) / denom).reshape(1, -1)
    probs = model.predict_proba(feats_s)[0]
    idx = int(np.argmax(probs))
    conf = float(probs[idx])
    label = le.inverse_transform([idx])[0]
    return label, conf


def run_session(args) -> None:
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    model, scaler, le = load_validator(Path(args.artifacts))
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    accepted = defaultdict(int)
    rejected = defaultdict(int)

    # Current trial state (buffered samples keyed by prompted label).
    current_label: Optional[str] = None
    current_trial: Optional[str] = None
    rows: List[SampleRow] = []
    last_activity = time.time() * 1000

    print(f"[auto] session={session_id} port={args.port} baud={args.baud}")
    print(f"[auto] confidence threshold={args.confidence} auto_ok={args.auto_ok}")
    print("[auto] sending START_BASELINE ...")
    print("[auto] press Ctrl+C to stop early.")

    with serial.Serial(args.port, args.baud, timeout=0.2) as ser:
        # Give the firmware a moment to drain any startup chatter, then begin.
        time.sleep(1.0)
        ser.reset_input_buffer()
        ser.write(b"START_BASELINE\n")
        ser.flush()

        try:
            while True:
                raw = ser.readline()
                now_ms = time.time() * 1000

                if not raw:
                    # Idle line: report inactivity to show the loop is alive.
                    if now_ms - last_activity >= args.timeout_ms:
                        print(f"[auto] (no serial activity for {args.timeout_ms} ms; "
                              f"accepted={dict(accepted)} rejected={dict(rejected)})")
                        last_activity = now_ms
                    continue

                line_raw = raw.decode("utf-8", errors="ignore").strip()
                if not line_raw:
                    continue
                last_activity = now_ms
                kind, msg = parse_kv_message(line_raw)

                if kind == "PROMPT":
                    # Firmware is about to expect a gesture. Reset trial buffer.
                    current_label = msg.get("label")
                    current_trial = msg.get("trial")
                    rows = []
                    print(f"[auto] PROMPT label={current_label} trial={current_trial}")

                elif kind == "SAMPLE":
                    if current_label is None or current_trial is None:
                        continue
                    try:
                        rows.append(SampleRow(
                            timestamp=msg.get("timestamp", ""),
                            ax=float(msg.get("ax", "nan")),
                            ay=float(msg.get("ay", "nan")),
                            az=float(msg.get("az", "nan")),
                            label=current_label,
                            trial_id=current_trial,
                        ))
                    except ValueError:
                        continue

                elif kind == "INFO":
                    text = msg.get("message", "")
                    if "confirm_ready" in text:
                        # Firmware finished sampling a window and awaits OK/BAD.
                        print(f"[auto] confirm_ready for {current_label} trial={current_trial} "
                              f"({len(rows)} samples)")
                        decision = "BAD"
                        reason = "no_model"
                        if args.auto_ok:
                            decision = "OK"
                            reason = "auto_ok"
                        elif model is not None and len(rows) >= 20:
                            window = np.asarray(
                                [[r.ax, r.ay, r.az] for r in rows], dtype=np.float64
                            )
                            pred, conf = predict_window(model, scaler[0], scaler[1], le, window)
                            if pred == current_label and conf >= args.confidence:
                                decision = "OK"
                                reason = f"pred={pred} conf={conf:.2f}"
                            else:
                                reason = f"pred={pred} conf={conf:.2f} (expected {current_label})"
                        elif len(rows) < 20:
                            reason = f"too_few_samples={len(rows)}"
                        print(f"[auto] decide {decision} ({reason})")
                        ser.write(f"{decision}\n".encode("utf-8"))
                        ser.flush()
                    elif "baseline complete" in text:
                        print("[auto] firmware reports baseline complete.")
                        break
                    else:
                        print(f"[auto] INFO: {line_raw}")

                elif kind == "RESULT":
                    status = msg.get("status")
                    label = msg.get("label")
                    trial = msg.get("trial")
                    if status == "ok":
                        accepted[label] += 1
                        if label and label != "idle":
                            out_dir = ensure_dirs(out_root, label)
                            out_file = out_dir / f"gesture_{label}_{trial}_{session_id}.csv"
                            write_trial_csv(out_file, rows)
                            print(f"[auto] ACCEPT {label} trial={trial} rows={len(rows)} -> {out_file.name}")
                        else:
                            print(f"[auto] ACCEPT {label} trial={trial} (idle baseline, {len(rows)} samples)")
                        rows = []
                    elif status == "fail":
                        rejected[label] += 1
                        print(f"[auto] REJECT {label} trial={trial} reason={msg.get('reason', '?')}")
                        rows = []
                else:
                    # Unknown line (e.g. startup diagnostics); ignore.
                    pass

        except KeyboardInterrupt:
            print("\n[auto] stopped by user; sending STOP_BASELINE ...")
            try:
                ser.write(b"STOP_BASELINE\n")
                ser.flush()
            except Exception:
                pass

    print(f"\n[auto] Summary: accepted={dict(accepted)} rejected={dict(rejected)}")
    print("[auto] Files written under " + str(out_root))


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Auto-capture confirmation responder for the Photon 2 baseline capture (model-gated)."
    )
    ap.add_argument("--port", required=True, help="Serial port, e.g. COM3")
    ap.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    ap.add_argument("--out", default="Product/data/raw", help="Output raw data root folder")
    ap.add_argument("--confidence", type=float, default=0.75, help="Min softmax confidence to accept trial")
    ap.add_argument("--artifacts", default="Product/ml/artifacts", help="Folder with model/scaler/label_encoder")
    ap.add_argument("--auto-ok", action="store_true", help="Always send OK (skip model gating)")
    ap.add_argument("--timeout-ms", type=int, default=15000, help="Idle timeout before a progress note (ms)")
    args = ap.parse_args()
    run_session(args)


if __name__ == "__main__":
    main()
