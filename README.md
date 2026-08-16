# ETTML TinyML Gesture Analysis

TinyML semester project for recognizing five accelerometer states on a
Particle Photon 2: idle, one tap, two taps, three taps, and a left-right shake.
Inference runs locally and maps accepted gestures to blackjack-simulation
commands and RGB feedback.

## Final result

- Hardware: Particle Photon 2 + ADXL343 over I2C
- Capture: synchronized XYZ at 400 Hz, 4 seconds, 1,600 samples
- Dataset: 25 accepted balanced trials, five per class
- Features: 28 statistical features over X/Y/Z/magnitude
- Model: StandardScaler + MLP 28–32–16–5
- Held-out result: 80% on five test windows (small-sample limitation applies)
- Embedded inference: 345 µs mean, 364 µs maximum in the recorded LIVE check
- Build: 27,950 B flash and 46,686 B RAM
- Deployment: compiled, flashed, and physically verified in LIVE mode

The complete academic report is available as
[PDF](Report/TinyML_Gesture_Report.pdf) and
[Typst source](Report/TinyML_Gesture_Report.typ).

## Repository map

| Path | Contents |
|---|---|
| [`Product/firmware/`](Product/firmware/) | Particle firmware and generated embedded model |
| [`Product/ml/`](Product/ml/) | Capture, training, export, and figure-generation pipeline |
| [`Product/data/`](Product/data/) | Deploy dataset, diagnostics, and archived baselines |
| [`docs/`](docs/) | Architecture, hardware, verification, and historical documentation |
| [`Report/`](Report/) | Submission PDF, Typst source, and report figures |
| [`Presentation/`](Presentation/) | Final exam deck, tablet notes, visual assets, and deck generator |
| [`Project Planning/`](Project%20Planning/) | Supplied course material and reference books |

## One-click Photon 2 demo

On Windows, connect the Photon 2 and double-click
[`START-PHOTON2-DEMO.cmd`](START-PHOTON2-DEMO.cmd). The script validates the
embedded model, compiles the Photon 2 firmware, flashes it over USB, sends
`MODE LIVE`, and confirms that the device entered LIVE mode.

To activate an already-flashed device without rebuilding:

```powershell
.\Start-Photon2-Demo.ps1 -ActivateOnly
```

See the [one-click deployment guide](docs/deployment/one-click-photon2-demo.md)
for checks and alternative parameters.

## Reproduce

```bash
source .venv/bin/activate
python Product/ml/train.py --config Product/ml/config.yaml
python Product/ml/export_model.py --config Product/ml/config.yaml
python Product/ml/generate_figures.py
particle compile photon2 Product/firmware --saveTo firmware.bin
```

See the [ML workflow](Product/ml/README.md),
[firmware guide](Product/firmware/README.md), and
[documentation index](docs/README.md) for details.

## LIVE mapping

| Gesture | Command | RGB feedback |
|---|---|---|
| One tap | Stand | One blue pulse for 1 second |
| Two taps | Hit | Two blue pulses at 0.5-second cadence |
| Three taps | Exit | Three red pulses at approximately 0.33-second cadence |
| Left-right shake | Split | Red-blue-red-blue at 1-second cadence |
| Idle | None | LED off |

## Limitations

The deployed dataset contains one operator and one final capture session. The
80% test result contains only one held-out example per class. It demonstrates a
working end-to-end prototype, not user-independent generalization.

## Author

Erik Kjær Klint — ETTML-01 Tiny Machine Learning semester project.

