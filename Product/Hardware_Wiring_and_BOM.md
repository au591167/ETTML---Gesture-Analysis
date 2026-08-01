# Hardware Wiring and BOM
## TinyML Gesture Interface (Particle Photon 2 + ADXL343 + RGB LED)

This document defines the physical build for the project artifact.

---

## 1. Bill of Materials (BOM)

| Item | Qty | Purpose | Notes |
|---|---:|---|---|
| Particle Photon 2 | 1 | Main MCU / inference target | Course-required platform |
| ADXL343 breakout | 1 | 3-axis acceleration sensing | I2C mode |
| RGB LED (common cathode preferred) | 1 | Visual gesture feedback | Can substitute 3 single LEDs |
| Resistors 220Ω–330Ω | 3 | Current limiting for RGB channels | One per R/G/B channel |
| Breadboard | 1 | Prototype assembly | Half-size is sufficient |
| Jumper wires | ~15 | Connections | Male-male typically |
| USB cable (Photon 2) | 1 | Power + programming + serial | Data-capable cable |
| Optional: push button | 1 | Start/stop capture mode | Not mandatory |
| Optional: 10kΩ resistor | 1 | Button pull-up/down | If external pull needed |

---

## 2. Electrical and Safety Notes
- Photon 2 logic level is 3.3V.  
- ADXL343 should be powered at 3.3V when using 3.3V logic I2C.  
- Always use current-limiting resistors for LED channels.  
- Disconnect power before rewiring.  
- Verify pin labels on your specific ADXL343 breakout board (different vendors expose slightly different names).

---

## 3. ADXL343 Wiring (I2C Recommended)

## 3.1 Typical ADXL343 Breakout Pins
Common pins:
- VIN / VCC
- GND
- SDA
- SCL
- CS
- SDO / ALT ADDRESS
- INT1 / INT2 (optional)

## 3.2 Connection Table (Generic Photon 2 I2C)
> Use the Photon 2 board pin names configured as I2C in your firmware/workbench setup.

| ADXL343 Pin | Photon 2 | Purpose |
|---|---|---|
| VIN / VCC | 3V3 | Sensor power |
| GND | GND | Ground reference |
| SDA | I2C SDA pin | Data line |
| SCL | I2C SCL pin | Clock line |
| CS | 3V3 | Force I2C mode on many breakouts |
| SDO / ALT ADDR | GND or 3V3 | I2C address select (0x53 or 0x1D equivalent mapping) |
| INT1 (optional) | GPIO input | Interrupt events (tap/activity) |
| INT2 (optional) | GPIO input | Secondary interrupt line |

### Address note
- If SDO/ALT is LOW, one I2C address is used.
- If SDO/ALT is HIGH, alternate address is used.
- Match firmware sensor address to your wiring.

---

## 4. RGB LED Wiring

### Assumption
Common-cathode RGB LED (recommended for simple PWM drive).

| RGB LED Pin | Connection |
|---|---|
| Cathode (common -) | GND |
| Red anode | Photon GPIO/PWM via 220Ω resistor |
| Green anode | Photon GPIO/PWM via 220Ω resistor |
| Blue anode | Photon GPIO/PWM via 220Ω resistor |

If using common-anode RGB LED:
- Connect common pin to 3V3 and invert output logic in firmware.

---

## 5. Suggested GPIO Allocation (Example)
> Adjust if these pins conflict with your board setup or libraries.

| Function | Suggested Pin Type |
|---|---|
| I2C SDA | Dedicated SDA |
| I2C SCL | Dedicated SCL |
| LED Red | PWM-capable GPIO |
| LED Green | PWM-capable GPIO |
| LED Blue | PWM-capable GPIO |
| Optional button | Digital input GPIO |

---

## 6. Pre-Power Checklist
- [ ] Confirm no short between 3V3 and GND.
- [ ] Confirm LED resistors are present.
- [ ] Confirm ADXL343 CS is set for I2C mode.
- [ ] Confirm SDA/SCL are not swapped.
- [ ] Confirm USB cable supports data.

---

## 7. Bring-Up Procedure (5–10 min)
1. Power Photon 2 over USB.
2. Flash minimal I2C scanner / ADXL test firmware.
3. Verify sensor address appears and data updates while moving board.
4. Flash LED test firmware (cycle R/G/B).
5. Flash integrated firmware (sensor + inference + LED/serial).

---

## 8. Common Troubleshooting
### Sensor not detected
- Check SDA/SCL swap.
- Check CS state (I2C vs SPI mode).
- Check sensor address configuration.

### Constant zero/noisy values
- Verify power and ground stability.
- Confirm correct ADXL343 range/output data settings.
- Check wiring contact quality on breadboard.

### LED not behaving
- Check resistor wiring and LED polarity.
- Ensure correct common-cathode/common-anode firmware logic.
- Verify selected pins support PWM (if using brightness control).

---

## 9. Hardware Documentation for Final Submission
Include in repository:
- Wiring table (this file)
- Photo(s) of assembled prototype
- Optional schematic diagram (PDF)
- Datasheet links used for Photon 2 and ADXL343
