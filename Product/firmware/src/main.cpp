#include "Particle.h"
#include "model_data.h"

SYSTEM_MODE(AUTOMATIC);
SYSTEM_THREAD(ENABLED);

namespace {
constexpr unsigned long kStatusIntervalMs = 2000;
constexpr unsigned long kSensorPrintIntervalMs = 200;
constexpr uint8_t kAdxlPrimaryAddr = 0x53;
constexpr uint8_t kAdxlAltAddr = 0x1D;
constexpr uint8_t kAdxlRegDevid = 0x00;
constexpr uint8_t kAdxlRegPowerCtl = 0x2D;
constexpr uint8_t kAdxlRegDataFormat = 0x31;
constexpr uint8_t kAdxlRegDataStart = 0x32;
constexpr uint8_t kAdxlExpectedDevid = 0xE5;
constexpr float kAdxlScaleGPerLsb = 0.0039f; // full-resolution nominal scale
unsigned long lastStatusMs = 0;
unsigned long lastSensorPrintMs = 0;
uint8_t gAdxlAddr = 0;
bool gAdxlReady = false;

void printModelMetadata() {
    Serial.println("=== TinyML Gesture Firmware Scaffold ===");
    Serial.print("Project: ");
    Serial.println(tinyml_model::kProjectName);
    Serial.print("Target MCU: ");
    Serial.println(tinyml_model::kTargetMcu);
    Serial.print("Classes: ");
    Serial.println((int)tinyml_model::kNumClasses);
    Serial.print("Feature count: ");
    Serial.println((int)tinyml_model::kFeatureCount);
    Serial.print("Confidence threshold: ");
    Serial.printlnf("%.3f", tinyml_model::kDecisionConfidenceThreshold);
    Serial.print("Smoothing windows: ");
    Serial.println((int)tinyml_model::kDecisionSmoothingWindows);
    Serial.print("Debounce ms: ");
    Serial.println((int)tinyml_model::kDecisionDebounceMs);

    for (size_t i = 0; i < tinyml_model::kNumClasses; ++i) {
        Serial.print("Class[");
        Serial.print((int)i);
        Serial.print("] = ");
        Serial.print(tinyml_model::kClassNames[i]);
        Serial.print(" -> command: ");
        Serial.println(tinyml_model::kCommandMap[i]);
    }
    Serial.println("=======================================");
}

void runPlaceholderInferenceHeartbeat() {
    float features[tinyml_model::kFeatureCount] = {0.0f};
    float scores[tinyml_model::kNumClasses] = {0.0f};

    tinyml_model::model_infer(
        features,
        tinyml_model::kFeatureCount,
        scores,
        tinyml_model::kNumClasses
    );

    int bestIdx = 0;
    float bestScore = scores[0];
    for (size_t i = 1; i < tinyml_model::kNumClasses; ++i) {
        if (scores[i] > bestScore) {
            bestScore = scores[i];
            bestIdx = (int)i;
        }
    }

    Serial.print("Predicted class: ");
    Serial.print(tinyml_model::kClassNames[bestIdx]);
    Serial.print(" | command: ");
    Serial.print(tinyml_model::kCommandMap[bestIdx]);
    Serial.print(" | score: ");
    Serial.printlnf("%.3f", bestScore);
}
} // namespace

bool probeI2cAddress(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;
}

bool readRegister8(uint8_t addr, uint8_t reg, uint8_t& out) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0) {
        return false;
    }

    int requested = Wire.requestFrom((int)addr, 1);
    if (requested != 1 || Wire.available() < 1) {
        return false;
    }

    out = Wire.read();
    return true;
}

bool writeRegister8(uint8_t addr, uint8_t reg, uint8_t value) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.write(value);
    return Wire.endTransmission() == 0;
}

bool readRegisters(uint8_t addr, uint8_t startReg, uint8_t* out, size_t len) {
    Wire.beginTransmission(addr);
    Wire.write(startReg);
    if (Wire.endTransmission(false) != 0) {
        return false;
    }

    int requested = Wire.requestFrom((int)addr, (int)len);
    if (requested != (int)len || Wire.available() < (int)len) {
        return false;
    }

    for (size_t i = 0; i < len; ++i) {
        out[i] = Wire.read();
    }
    return true;
}

bool initAdxlMeasurementMode(uint8_t addr) {
    // FULL_RES + +/-16g (range bits set to 0b11, FULL_RES bit set)
    if (!writeRegister8(addr, kAdxlRegDataFormat, 0x0B)) {
        return false;
    }
    // MEASURE bit
    if (!writeRegister8(addr, kAdxlRegPowerCtl, 0x08)) {
        return false;
    }
    return true;
}

bool readAdxlRawXYZ(uint8_t addr, int16_t& x, int16_t& y, int16_t& z) {
    uint8_t buf[6] = {0};
    if (!readRegisters(addr, kAdxlRegDataStart, buf, sizeof(buf))) {
        return false;
    }

    x = (int16_t)((buf[1] << 8) | buf[0]);
    y = (int16_t)((buf[3] << 8) | buf[2]);
    z = (int16_t)((buf[5] << 8) | buf[4]);
    return true;
}

void printAdxlDiagnostics() {
    Serial.println("=== ADXL343 I2C Probe ===");
    Serial.println("Expected wiring: D0=SDA, D1=SCL, 3V3, GND");

    Wire.begin();
    Wire.setSpeed(CLOCK_SPEED_100KHZ);

    const bool primarySeen = probeI2cAddress(kAdxlPrimaryAddr);
    const bool altSeen = probeI2cAddress(kAdxlAltAddr);

    Serial.print("Probe 0x53: ");
    Serial.println(primarySeen ? "ACK" : "no response");
    Serial.print("Probe 0x1D: ");
    Serial.println(altSeen ? "ACK" : "no response");

    uint8_t chosenAddr = 0;
    if (primarySeen) {
        chosenAddr = kAdxlPrimaryAddr;
    } else if (altSeen) {
        chosenAddr = kAdxlAltAddr;
    }

    if (chosenAddr == 0) {
        Serial.println("[ADXL] No device found at 0x53 or 0x1D.");
        Serial.println("[ADXL] Check wiring and power, then reboot.");
        Serial.println("=========================");
        gAdxlReady = false;
        gAdxlAddr = 0;
        return;
    }

    Serial.print("[ADXL] Candidate address: 0x");
    if (chosenAddr < 16) Serial.print("0");
    Serial.println(chosenAddr, HEX);

    uint8_t devid = 0;
    if (!readRegister8(chosenAddr, kAdxlRegDevid, devid)) {
        Serial.println("[ADXL] Failed to read DEVID register (0x00).");
        Serial.println("=========================");
        gAdxlReady = false;
        gAdxlAddr = 0;
        return;
    }

    Serial.print("[ADXL] DEVID read: 0x");
    if (devid < 16) Serial.print("0");
    Serial.println(devid, HEX);

    if (devid == kAdxlExpectedDevid) {
        Serial.println("[ADXL] Device identity confirmed (ADXL343-compatible).");
        gAdxlAddr = chosenAddr;
        gAdxlReady = initAdxlMeasurementMode(gAdxlAddr);
        if (gAdxlReady) {
            Serial.println("[ADXL] Measurement mode enabled.");
        } else {
            Serial.println("[ADXL] Failed to enable measurement mode.");
        }
    } else {
        Serial.println("[ADXL] WARNING: DEVID mismatch (expected 0xE5).");
        gAdxlReady = false;
        gAdxlAddr = 0;
    }

    Serial.println("=========================");
}

void setup() {
    Serial.begin(115200);

    // Give monitor time to attach after reset so startup diagnostics are not missed.
    delay(3000);

    printAdxlDiagnostics();

    tinyml_model::model_init();
    printModelMetadata();
}

void loop() {
    if (gAdxlReady && (millis() - lastSensorPrintMs >= kSensorPrintIntervalMs)) {
        lastSensorPrintMs = millis();

        int16_t ax = 0, ay = 0, az = 0;
        if (readAdxlRawXYZ(gAdxlAddr, ax, ay, az)) {
            const float axg = ax * kAdxlScaleGPerLsb;
            const float ayg = ay * kAdxlScaleGPerLsb;
            const float azg = az * kAdxlScaleGPerLsb;
            Serial.printlnf(
                "ADXL raw: x=%d y=%d z=%d | g: x=%.3f y=%.3f z=%.3f",
                (int)ax, (int)ay, (int)az, axg, ayg, azg
            );
        } else {
            Serial.println("[ADXL] Read error on data registers.");
        }
    }

    if (millis() - lastStatusMs >= kStatusIntervalMs) {
        lastStatusMs = millis();
        runPlaceholderInferenceHeartbeat();
    }
}
