# System diagram

```mermaid
flowchart LR
    HOST[Host PC<br/>capture / train / export]
    MCU[Particle Photon 2<br/>400 Hz acquisition + inference]
    ADXL[ADXL343<br/>3-axis accelerometer]
    RGB[Onboard RGB LED<br/>gesture feedback]
    SERIAL[USB serial<br/>commands + events]

    HOST <-->|USB| SERIAL
    SERIAL <--> MCU
    MCU <-->|I2C SDA/SCL| ADXL
    MCU --> RGB
```

The final prototype uses the Photon 2 onboard RGB LED; it does not require four
external cue LEDs. Wiring details are in the
[hardware guide](wiring-and-bom.md), and runtime behavior is in the
[operating-mode guide](../architecture/operating-modes-and-verification.md).

