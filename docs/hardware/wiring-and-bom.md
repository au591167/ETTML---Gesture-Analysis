# Hardware wiring and bill of materials

## Bill of materials

| Item | Quantity | Purpose |
|---|---:|---|
| Particle Photon 2 | 1 | MCU, USB serial, onboard RGB, and inference target |
| ADXL343 breakout | 1 | Three-axis acceleration over I2C |
| Breadboard | 1 | Prototype assembly |
| Jumper wires | 4–6 | Power and I2C connections |
| Data-capable USB cable | 1 | Power, flash, and serial |

The final firmware uses the Photon 2 onboard RGB LED through the Particle RGB
API. No external cue LEDs or current-limiting resistors are required by the
final build.

## Wiring

| ADXL343 | Photon 2 | Function |
|---|---|---|
| VCC/VIN | 3V3 | 3.3 V supply |
| GND | GND | Common reference |
| SDA | D0 / SDA | I2C data |
| SCL | D1 / SCL | I2C clock |
| CS | Breakout-specific I2C selection | Keep in I2C mode |
| SDO/ALT | GND or 3V3 | Selects address `0x53` or `0x1D` |

Firmware probes both supported addresses and verifies ADXL-compatible device ID
`0xE5` before enabling acquisition.

## Configured sensor mode

- Full-resolution ±16 g
- Nominal conversion: 0.0039 g/LSB
- Output data rate: 400 Hz
- Six-byte synchronized XYZ register read
- I2C bus: 400 kHz

## Bring-up checklist

1. Disconnect USB before changing wiring.
2. Verify no short between 3V3 and GND.
3. Confirm SDA/SCL and breakout I2C-select pins.
4. Connect USB and flash the firmware.
5. Run `STATUS`; require `sensor=ok` and zero read errors.
6. In DEBUG, run `TAP_SCOPE` to verify changing XYZ data.
7. Select `MODE LIVE` only after exporting a class-complete model.

## Primary references

- [Particle Photon 2 datasheet](https://docs.particle.io/reference/datasheets/wi-fi/photon-2-datasheet/)
- [Analog Devices ADXL343 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adxl343.pdf)
