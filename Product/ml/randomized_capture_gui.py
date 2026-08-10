#!/usr/bin/env python3
"""Balanced, randomized high-rate gesture pilot capture GUI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import queue
import random
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import serial


@dataclass(frozen=True)
class Trial:
    label: str
    force: str = "na"
    pace: str = "na"

    @property
    def instruction(self) -> str:
        if self.label == "idle":
            return "LEAVE THE DEVICE STILL"
        if self.label == "shake_lr":
            return "SHAKE LEFT–RIGHT ONCE"
        count = int(self.label[-1])
        return f"TAP {count} " + ("TIME" if count == 1 else "TIMES")

    @property
    def detail(self) -> str:
        if self.label == "idle":
            return "Do not touch the device during green"
        if self.label == "shake_lr":
            return "One natural left–right shake gesture, then stop"
        pace = "natural" if self.label == "tap1" else self.pace
        return f"{pace.upper()} pace · {self.force.upper()} force\nPerform once, then stop"

    @property
    def green_instruction(self) -> str:
        """Single glanceable instruction block used during active capture."""
        if self.label == "idle":
            return "LEAVE DEVICE STILL\nDO NOT TOUCH"
        if self.label == "shake_lr":
            return "SHAKE LEFT–RIGHT ONCE\nTHEN STOP"
        pace = "natural" if self.label == "tap1" else self.pace
        return (
            f"{self.instruction}\n"
            f"{pace.upper()} PACE · {self.force.upper()} FORCE\n"
            "ONCE, THEN STOP"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyACM1")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--series", type=int, default=1,
                        help="Number of balanced five-trial series")
    parser.add_argument(
        "--trial-counts",
        help="Focused schedule, e.g. tap2=6,tap3=9; overrides --series",
    )
    parser.add_argument("--seed", type=int)
    parser.add_argument("--session-id",
                        help="Resume an existing timestamped session")
    parser.add_argument("--output-root", type=Path,
                        default=Path("Product/data/pilot_v3"))
    return parser.parse_args()


class RandomizedCapture:
    def __init__(self, root: tk.Tk, args: argparse.Namespace) -> None:
        self.root, self.args = root, args
        self.rng = random.Random(args.seed)
        self.session_id = args.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = args.output_root / self.session_id
        self.accepted_dir = self.session_dir / "accepted"
        self.rejected_dir = self.session_dir / "rejected"
        self.messages: queue.Queue[tuple[str, object]] = queue.Queue()
        focused_counts = self.parse_trial_counts(args.trial_counts)
        if focused_counts:
            self.pending = self.make_focused_schedule(focused_counts)
            self.original_total = sum(focused_counts.values())
        else:
            self.pending = self.make_schedule(args.series)
            self.original_total = args.series * 5
        existing_labels = self.load_existing_labels()
        for label in existing_labels:
            for index, trial in enumerate(self.pending):
                if trial.label == label:
                    self.pending.pop(index)
                    break
        self.accepted = len(existing_labels)
        self.rejected = 0
        self.current: Trial | None = None
        self.current_result: tuple[pd.DataFrame, dict[str, float]] | None = None
        self.running = False
        self.countdown_generation = 0

        root.title("ETTML — Randomized Gesture Series")
        root.geometry("1000x720")
        root.minsize(850, 620)

        header = ttk.Frame(root, padding=14)
        header.pack(fill="x")
        self.progress = tk.StringVar()
        ttk.Label(header, textvariable=self.progress, font=("Sans", 16, "bold"),
                  anchor="center", justify="center").pack(fill="x")
        ttk.Label(header, text=f"Session {self.session_id}", font=("Sans", 12),
                  anchor="center", justify="center").pack(fill="x")

        self.cue = tk.Frame(root, bg="#174a7e", padx=22, pady=30)
        self.cue.pack(fill="both", expand=True, padx=20, pady=8)
        self.heading = tk.Label(self.cue, text="READY FOR RANDOMIZED SERIES",
                                bg="#174a7e", fg="white",
                                font=("Sans", 54, "bold"), wraplength=940,
                                anchor="center", justify="center")
        self.heading.pack(expand=True, fill="both")
        self.detail = tk.StringVar(value="The next condition remains hidden until Start trial")
        self.detail_label = tk.Label(self.cue, textvariable=self.detail,
                                     bg="#174a7e", fg="white",
                                     font=("Sans", 32, "bold"), wraplength=920,
                                     anchor="center", justify="center")
        self.detail_label.pack(fill="x", pady=(0, 18))
        self.timer = tk.StringVar(value="")
        self.timer_label = tk.Label(
            self.cue, textvariable=self.timer, bg="#174a7e", fg="white",
            font=("Sans", 38, "bold"), anchor="center", justify="center",
        )
        self.timer_label.pack(fill="x", pady=(0, 12))

        controls = ttk.Frame(root, padding=14)
        controls.pack(fill="x")
        self.status = tk.StringVar(value="Automatic series starting…")
        ttk.Label(controls, textvariable=self.status, font=("Sans", 16),
                  anchor="center", justify="center").pack(fill="x", pady=8)
        self.update_progress()
        root.after(50, self.poll)
        root.after(1500, self.start_trial)

    def load_existing_labels(self) -> list[str]:
        """Return accepted labels already present when resuming a session."""
        labels: list[str] = []
        if not self.accepted_dir.exists():
            return labels
        for path in sorted(self.accepted_dir.glob("*.csv")):
            try:
                frame = pd.read_csv(path, nrows=1)
                if not frame.empty and "label" in frame:
                    labels.append(str(frame.label.iloc[0]))
            except (OSError, ValueError):
                continue
        return labels

    def make_schedule(self, series: int) -> list[Trial]:
        schedule: list[Trial] = []
        forces = ["light", "normal", "firm"]
        paces = ["fast", "natural", "slow"]
        for _ in range(series):
            block = [
                Trial("idle"), Trial("shake_lr"),
                Trial("tap1", self.rng.choice(forces), "natural"),
                Trial("tap2", self.rng.choice(forces), self.rng.choice(paces)),
                Trial("tap3", self.rng.choice(forces), self.rng.choice(paces)),
            ]
            self.rng.shuffle(block)
            schedule.extend(block)
        return schedule

    @staticmethod
    def parse_trial_counts(specification: str | None) -> dict[str, int]:
        if not specification:
            return {}
        allowed = {"idle", "tap1", "tap2", "tap3", "shake_lr"}
        counts: dict[str, int] = {}
        for item in specification.split(","):
            try:
                label, count_text = item.split("=", 1)
                label = label.strip()
                count = int(count_text)
            except ValueError as error:
                raise ValueError(f"Invalid --trial-counts item: {item!r}") from error
            if label not in allowed or count <= 0:
                raise ValueError(f"Invalid focused trial count: {item!r}")
            counts[label] = count
        return counts

    def make_focused_schedule(self, counts: dict[str, int]) -> list[Trial]:
        """Create coverage-balanced conditions, then randomize presentation."""
        forces = ["light", "normal", "firm"]
        paces = ["fast", "natural", "slow"]
        schedule: list[Trial] = []
        for label, count in counts.items():
            if label in {"idle", "shake_lr"}:
                schedule.extend(Trial(label) for _ in range(count))
                continue
            if label == "tap1":
                conditions = [Trial(label, forces[i % 3], "natural") for i in range(count)]
            else:
                # A rotated 3x3 grid preserves balanced pace/force marginals
                # for batches of three, six, or nine instead of exhausting one
                # pace before moving to the next.
                grid = [
                    Trial(label, forces[(pace_index + repeat) % 3], pace)
                    for repeat in range(3)
                    for pace_index, pace in enumerate(paces)
                ]
                conditions = [grid[i % len(grid)] for i in range(count)]
            self.rng.shuffle(conditions)
            schedule.extend(conditions)
        self.rng.shuffle(schedule)
        return schedule

    def update_progress(self) -> None:
        self.progress.set(
            f"Accepted {self.accepted}/{self.original_total} · "
            f"Pending {len(self.pending)} · Rejected attempts {self.rejected}"
        )

    def set_cue(self, colour: str, heading: str, detail: str) -> None:
        self.cue.config(bg=colour)
        self.heading.config(bg=colour, text=heading)
        self.detail_label.config(bg=colour)
        self.timer_label.config(bg=colour)
        self.detail.set(detail)
        self.timer.set("")

    def start_trial(self) -> None:
        if self.running or not self.pending:
            return
        self.current = self.pending.pop(0)
        self.running = True
        self.set_cue("#d6a800", "WAIT", "Yellow countdown — do not move yet")
        self.status.set("Connecting and arming high-rate capture…")
        threading.Thread(target=self.capture_worker, daemon=True).start()
        self.update_progress()

    def capture_worker(self) -> None:
        assert self.current is not None
        samples: list[tuple[int, float, float, float]] = []
        cue_time_us = 500000
        try:
            with serial.Serial(self.args.port, self.args.baud, timeout=0.25) as device:
                device.reset_input_buffer()
                device.write(b"MODE DEBUG\n")
                time.sleep(0.1)
                device.write(b"TAP_SCOPE\n")
                device.flush()
                deadline = time.monotonic() + 35
                while time.monotonic() < deadline:
                    line = device.readline().decode("utf-8", errors="replace").strip()
                    if line.startswith("SCOPE,phase=countdown"):
                        duration_ms = 3000
                        if "duration_ms=" in line:
                            duration_ms = int(
                                line.split("duration_ms=", 1)[1].split(",", 1)[0]
                            )
                        self.messages.put(("countdown", duration_ms))
                    elif line.startswith("SCOPE,phase=precue"):
                        self.messages.put(("precue", None))
                    elif line.startswith("SCOPE,phase=go"):
                        if "cue_time_us=" in line:
                            cue_time_us = int(line.split("cue_time_us=", 1)[1].split(",", 1)[0])
                        self.messages.put(("go", self.current))
                    elif line.startswith("SCOPE_DATA,") and not line.startswith("SCOPE_DATA,time_us"):
                        parts = line.split(",")
                        if len(parts) == 5:
                            _, timestamp, x, y, z = parts
                            samples.append((int(timestamp), float(x), float(y), float(z)))
                            if len(samples) % 100 == 0:
                                self.messages.put(("transfer", (len(samples), 1600)))
                    elif line.startswith("SCOPE,phase=complete"):
                        break
            if len(samples) < 1584:
                raise RuntimeError(f"Received only {len(samples)}/1600 samples")
            frame = self.make_frame(samples, cue_time_us)
            metrics = self.metrics(frame)
            self.current_result = (frame, metrics)
            self.messages.put(("review", metrics))
        except Exception as error:
            self.messages.put(("error", str(error)))

    @staticmethod
    def make_frame(samples: list[tuple[int, float, float, float]], cue_time_us: int) -> pd.DataFrame:
        frame = pd.DataFrame(samples, columns=["time_us", "x_g", "y_g", "z_g"])
        frame["time_ms"] = frame.time_us / 1000
        frame["cue_time_us"] = cue_time_us
        baseline = frame[frame.time_us < cue_time_us][["x_g", "y_g", "z_g"]].median()
        for axis in "xyz":
            frame[f"{axis}_delta_g"] = frame[f"{axis}_g"] - baseline[f"{axis}_g"]
        frame["dynamic_magnitude_g"] = np.sqrt(sum(frame[f"{a}_delta_g"] ** 2 for a in "xyz"))
        return frame

    @staticmethod
    def metrics(frame: pd.DataFrame) -> dict[str, float]:
        i = int(frame.dynamic_magnitude_g.idxmax())
        cue_ms = float(frame.cue_time_us.iloc[0]) / 1000
        magnitude = frame.dynamic_magnitude_g.to_numpy()
        active = np.flatnonzero(magnitude >= 0.35)
        event_count = 0
        active_span_ms = 0.0
        if len(active):
            event_count = 1
            active_span_ms = float(frame.time_ms.iloc[active[-1]] - frame.time_ms.iloc[active[0]])
            previous = active[0]
            for index in active[1:]:
                if frame.time_us.iloc[index] - frame.time_us.iloc[previous] > 150000:
                    event_count += 1
                previous = index
        peak_axis = max(float(frame[f"{axis}_delta_g"].abs().max()) for axis in "xyz")
        raw_peak_axis = max(float(frame[f"{axis}_g"].abs().max()) for axis in "xyz")
        return {
            "samples": float(len(frame)),
            "median_interval_us": float(frame.time_us.diff().median()),
            "peak_magnitude_g": float(frame.dynamic_magnitude_g.max()),
            "peak_time_ms": float(frame.time_ms.iloc[i]),
            "cue_latency_ms": float(frame.time_ms.iloc[i] - cue_ms),
            "peak_axis_g": peak_axis,
            "dynamic_rms_g": float(np.sqrt(np.mean(magnitude ** 2))),
            "active_span_ms": active_span_ms,
            "event_count": float(event_count),
            "clipped": float(raw_peak_axis >= 15.5),
        }

    @staticmethod
    def validate(trial: Trial, metrics: dict[str, float]) -> tuple[bool, str]:
        """Apply conservative class-specific automatic quality gates."""
        if metrics["clipped"]:
            return False, "sensor clipping detected"
        if trial.label == "idle":
            if metrics["peak_magnitude_g"] <= 0.15:
                return True, "stationary signal confirmed"
            return False, "movement detected during idle"
        if trial.label.startswith("tap"):
            expected = int(trial.label[-1])
            observed = int(metrics["event_count"])
            if metrics["peak_axis_g"] < 0.40:
                return False, "impact too close to idle"
            if observed != expected:
                return False, f"detected {observed} impact events; expected {expected}"
            return True, f"detected {observed} impact events"
        if trial.label == "shake_lr":
            if metrics["dynamic_rms_g"] < 0.10:
                return False, "shake energy too close to idle"
            if metrics["active_span_ms"] < 300:
                return False, "motion was not sustained long enough"
            return True, "sustained motion confirmed"
        return False, "unknown trial label"

    def save(self, accepted: bool) -> tuple[Path, Path]:
        assert self.current is not None and self.current_result is not None
        frame, metrics = self.current_result
        target = self.accepted_dir if accepted else self.rejected_dir
        target.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Metadata values must never become path components. Keep filenames
        # portable even if a future condition contains spaces or punctuation.
        def safe_token(value: str) -> str:
            return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value)

        stem = "_".join(
            safe_token(value) for value in
            (self.current.label, self.current.pace, self.current.force, stamp)
        )
        csv_path, png_path = target / f"{stem}.csv", target / f"{stem}.png"
        frame["label"] = self.current.label
        frame["requested_pace"] = self.current.pace
        frame["requested_force"] = self.current.force
        frame["session_id"] = self.session_id
        frame["operator_accepted"] = accepted
        frame.to_csv(csv_path, index=False)
        fig, ax = plt.subplots(figsize=(10, 4.5))
        for axis in "xyz":
            ax.plot(frame.time_ms, frame[f"{axis}_delta_g"], lw=.85, label=axis.upper())
        cue_ms = frame.cue_time_us.iloc[0] / 1000
        ax.axvline(cue_ms, color="green", ls="--", lw=1.2, label="Green cue")
        ax.axhline(0, color="black", lw=.6)
        ax.set(title=f"{self.current.label} — {self.current.pace}, {self.current.force}",
               xlabel="Time (ms)", ylabel="Baseline-relative acceleration (g)")
        ax.grid(alpha=.2); ax.legend(); fig.tight_layout(); fig.savefig(png_path, dpi=160)
        plt.close(fig)
        metadata = {
            "session_id": self.session_id, "label": self.current.label,
            "pace": self.current.pace, "force": self.current.force,
            "operator_accepted": accepted, **metrics,
        }
        csv_path.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
        return csv_path, png_path

    def accept_trial(self) -> None:
        paths = self.save(True)
        self.accepted += 1
        self.finish_review(f"Accepted and saved: {paths[0].name}")

    def reject_trial(self) -> None:
        paths = self.save(False)
        assert self.current is not None
        self.pending.append(self.current)
        self.rejected += 1
        self.finish_review(f"Rejected and archived: {paths[0].name}")

    def finish_review(self, status: str) -> None:
        self.current = None; self.current_result = None; self.running = False
        self.update_progress()
        if self.accepted >= self.original_total and not self.pending:
            self.set_cue("#174a7e", "SERIES COMPLETE", "All balanced conditions accepted")
            self.status.set(f"Saved under {self.session_dir}")
        else:
            self.status.set(status)
            self.root.after(2000, self.start_trial)

    def poll(self) -> None:
        try:
            while True:
                kind, payload = self.messages.get_nowait()
                if kind == "countdown":
                    self.begin_countdown(int(payload))
                elif kind == "precue":
                    self.countdown_generation += 1
                    assert self.current is not None
                    self.set_cue("#d6a800", self.current.green_instruction, "")
                    self.timer.set("GET READY · 0.5 s")
                    self.status.set("High-rate baseline recording has started")
                elif kind == "go":
                    self.countdown_generation += 1
                    trial: Trial = payload  # type: ignore[assignment]
                    self.set_cue("#159447", trial.green_instruction, "")
                    self.status.set("Perform the displayed gesture now")
                    self.begin_green_timer(3500)
                elif kind == "review":
                    self.countdown_generation += 1
                    metrics: dict[str, float] = payload  # type: ignore[assignment]
                    assert self.current is not None
                    accepted, reason = self.validate(self.current, metrics)
                    if accepted:
                        self.set_cue("#174a7e", "ACCEPTED",
                                     f"{reason}\nPeak {metrics['peak_magnitude_g']:.2f} g")
                        self.accept_trial()
                    else:
                        self.set_cue("#9c2f2f", "RETRY", reason)
                        self.reject_trial()
                elif kind == "transfer":
                    received, expected = payload  # type: ignore[misc]
                    percentage = min(100, round(100 * received / expected))
                    self.set_cue(
                        "#174a7e", "PROCESSING",
                        f"Receiving and validating data\n{percentage}%",
                    )
                    self.status.set(f"Received {received}/{expected} samples")
                elif kind == "error":
                    self.countdown_generation += 1
                    if self.current is not None:
                        self.pending.insert(0, self.current)
                    self.current = None; self.running = False
                    self.set_cue("#174a7e", "CAPTURE FAILED", "Condition returned to queue")
                    self.status.set(f"Capture failed: {payload}")
                    self.update_progress()
                    self.root.after(2500, self.start_trial)
        except queue.Empty:
            pass
        self.root.after(50, self.poll)

    def begin_countdown(self, duration_ms: int) -> None:
        """Show a large yellow countdown without blocking serial capture."""
        self.countdown_generation += 1
        generation = self.countdown_generation
        seconds = max(1, int(np.ceil(duration_ms / 1000)))

        def show(value: int) -> None:
            if generation != self.countdown_generation or not self.running:
                return
            if value <= 0:
                return
            assert self.current is not None
            self.set_cue(
                "#d6a800", f"NEXT ACTION\n{self.current.green_instruction}", ""
            )
            self.timer.set(str(value))
            self.status.set("Preparing the next randomized instruction")
            self.root.after(1000, lambda: show(value - 1))

        show(seconds)

    def begin_green_timer(self, duration_ms: int) -> None:
        """Display capture time remaining while preserving GUI responsiveness."""
        generation = self.countdown_generation
        deadline = time.monotonic() + duration_ms / 1000.0

        def update() -> None:
            if generation != self.countdown_generation or not self.running:
                return
            remaining = max(0.0, deadline - time.monotonic())
            self.timer.set(f"{remaining:0.1f} s remaining")
            if remaining > 0:
                self.root.after(100, update)
            else:
                self.set_cue(
                    "#174a7e", "PROCESSING",
                    "Capture complete\nWaiting for buffered data",
                )
                self.status.set("The device is transferring 1,600 samples")

        update()


def main() -> None:
    args = parse_args()
    root = tk.Tk()
    RandomizedCapture(root, args)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()


if __name__ == "__main__":
    main()
