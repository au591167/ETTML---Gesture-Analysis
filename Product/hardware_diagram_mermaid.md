# Hardware Diagram (Mermaid Scaffold)
## TinyML Gesture Reader — Photon 2 + ADXL343 + Cue LEDs + RGB Status LED

This diagram is a **clean scaffold** for report and implementation documentation.  
Use Mermaid-compatible preview/export to generate a figure for the final report.

```mermaid
flowchart LR
    USB[USB Power + Serial]
    HOST[Host PC\ncapture_guided.py / train.py / export_model.py]
    MCU[Particle Photon 2]
    ADXL[ADXL343\nI2C Accelerometer]
    CUE[4x Cue LEDs\n(tap1/tap2/tap3/shake_lr)]
    RGB[RGB Status LED\nready/ok/fail]

    USB --> MCU
    HOST <-->|Serial USB| MCU
    MCU <-->|I2C SDA/SCL| ADXL
    MCU --> CUE
    MCU --> RGB
```

## Wiring Intent (High-Level)

- **ADXL343 (I2C)**
  - VCC -> 3V3
  - GND -> GND
  - SDA -> Photon2 SDA
  - SCL -> Photon2 SCL
  - CS -> 3V3 (force I2C mode on many breakouts)
  - SDO/ALT -> GND or 3V3 (address select)

- **Cue LEDs (4 total)**
  - One GPIO output per cue LED
  - Each LED in series with 220–330Ω resistor to GND (or equivalent wiring style)

- **RGB Status LED**
  - Common cathode recommended
  - R/G/B channels each through 220–330Ω resistor to PWM-capable GPIO pins
  - Common cathode -> GND

## Behavioral Mapping (for implementation + report)

- Cue LEDs:
  - LED1 -> expected `tap1`
  - LED2 -> expected `tap2`
  - LED3 -> expected `tap3`
  - LED4 -> expected `shake_lr`

- RGB status:
  - Blue -> ready for next input
  - Green flash -> accepted sample
  - Red flash -> rejected sample

## Notes
- Final physical pin numbers should follow `Product/Hardware_Wiring_and_BOM.md`.
- Keep this diagram synchronized with firmware protocol documentation (`Product/firmware/INFERENCE_INTEGRATION_PLAN.md`).
