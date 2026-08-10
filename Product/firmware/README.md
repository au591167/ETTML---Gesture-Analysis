# Photon 2 firmware

Particle Device OS firmware for ADXL343 acquisition, three operating modes,
embedded MLP inference, decision filtering, serial events, and non-blocking RGB
feedback.

## Source

- `src/main.cpp`: hardware, capture, features, modes, inference, and feedback
- `src/model_data.h/.cpp`: generated scaler and MLP parameters
- `project.properties`: Particle project metadata

Generated model files must be updated through `Product/ml/export_model.py`,
never by editing weights manually.

## Build and flash

```bash
particle compile photon2 Product/firmware --saveTo firmware.bin
particle flash TinyML_Node1 firmware.bin
```

## Commands

- `MODE DEBUG` — verbose diagnostics, no gesture actions
- `MODE TRAINING` — guided capture state machine
- `MODE LIVE` — inference, stable events, and RGB feedback
- `STATUS` — mode, sensor, buffer, timing, and error counters
- `TAP_SCOPE` — buffered 400 Hz XYZ capture used by the host GUI

See the [code walkthrough](../../docs/architecture/code-walkthrough.md).

