"""
Guided continuous capture utility for Photon 2 gesture data collection.

Protocol (line-based over serial, UTF-8):
- PROMPT,label=<label>,trial=<n>              -> firmware indicates expected gesture
- SAMPLE,timestamp=<ms>,ax=<f>,ay=<f>,az=<f>  -> firmware streams sample rows
- RESULT,status=ok|fail,label=<label>,trial=<n>,reason=<text-optional>
- INFO,message=<text>

Behavior:
- Runs continuously until Ctrl+C.
- Buffers SAMPLE rows per trial.
- On RESULT status=ok: writes one CSV file for that accepted trial.
- On RESULT status=fail: discards buffered trial rows.
- Also relays operator commands typed on STDIN (START_BASELINE, OK, BAD, ...)
  to the device over the same serial port, so a single terminal can both log
  data and confirm trials (only one process can hold the serial port).
"""

from __future__ import annotations

import argparse
import csv
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import serial


@dataclass
class SampleRow:
    timestamp: str
    ax: float
    ay: float
    az: float
    label: str
    trial_id: str
    session_id: str


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
        w.writerow(["timestamp", "ax", "ay", "az", "label", "trial_id", "session_id"])
        for r in rows:
            w.writerow([r.timestamp, f"{r.ax:.6f}", f"{r.ay:.6f}", f"{r.az:.6f}", r.label, r.trial_id, r.session_id])


def relay_stdin_to_serial(ser: serial.Serial, stop: threading.Event) -> None:
    """Forward lines typed by the operator to the device over the same serial port.

    Because only one process can open the serial port at a time, the logger owns
    COMx and relays operator commands (START_BASELINE, OK, BAD, ECHO_ON, ...) so
    the user does not need a separate serial monitor.
    """
    while not stop.is_set():
        try:
            line = sys.stdin.readline()
        except Exception:
            break
        if not line:
            # EOF (e.g. input closed)
            break
        line = line.strip()
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            print("[capture] 'exit' received; stopping.")
            break
        try:
            ser.write((line + "\n").encode("utf-8"))
            ser.flush()
            print(f"[tx] {line}")
        except Exception as e:
            print(f"[tx] error writing: {e}")
            break
    stop.set()


def main() -> None:
    ap = argparse.ArgumentParser(description="Guided continuous gesture capture over serial.")
    ap.add_argument("--port", required=True, help="Serial port, e.g. COM6")
    ap.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    ap.add_argument("--out", default="Product/data/raw", help="Output raw data root folder")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[capture] session={session_id} port={args.port} baud={args.baud}")

    current_label: Optional[str] = None
    current_trial: Optional[str] = None
    buffer_rows: List[SampleRow] = []

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        stop = threading.Event()
        tx_thread = threading.Thread(
            target=relay_stdin_to_serial, args=(ser, stop), daemon=True
        )
        tx_thread.start()

        print("[capture] running; type commands (START_BASELINE/OK/BAD/...) to send.");
        print("[capture] press Ctrl+C to stop.");
        try:
            while True:
                raw = ser.readline()
                if not raw:
                    continue

                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                except Exception:
                    continue
                if not line:
                    continue

                kind, msg = parse_kv_message(line)

                if kind == "PROMPT":
                    current_label = msg.get("label")
                    current_trial = msg.get("trial")
                    buffer_rows = []
                    print(f"[prompt] label={current_label} trial={current_trial}")

                elif kind == "SAMPLE":
                    if not current_label or not current_trial:
                        continue
                    try:
                        row = SampleRow(
                            timestamp=msg.get("timestamp", ""),
                            ax=float(msg.get("ax", "nan")),
                            ay=float(msg.get("ay", "nan")),
                            az=float(msg.get("az", "nan")),
                            label=current_label,
                            trial_id=current_trial,
                            session_id=session_id,
                        )
                        buffer_rows.append(row)
                    except ValueError:
                        continue

                elif kind == "RESULT":
                    status = msg.get("status", "").lower()
                    label = msg.get("label", current_label or "unknown")
                    trial = msg.get("trial", current_trial or "000")
                    reason = msg.get("reason", "")

                    if status == "ok":
                        out_dir = ensure_dirs(out_root, label)
                        out_file = out_dir / f"gesture_{label}_{trial}_{session_id}.csv"
                        write_trial_csv(out_file, buffer_rows)
                        print(f"[ok] wrote {out_file} rows={len(buffer_rows)}")
                    else:
                        print(f"[fail] discarded label={label} trial={trial} rows={len(buffer_rows)} reason={reason}")

                    current_label = None
                    current_trial = None
                    buffer_rows = []

                elif kind == "INFO":
                    print(f"[info] {msg.get('message', '')}")

                else:
                    # ignore unknown lines quietly to stay robust
                    pass

        except KeyboardInterrupt:
            print("\n[capture] stopped by user.")
        finally:
            stop.set()


if __name__ == "__main__":
    main()
