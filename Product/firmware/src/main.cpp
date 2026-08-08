#include "Particle.h"
#include "model_data.h"
#include <math.h>

SYSTEM_MODE(AUTOMATIC);
SYSTEM_THREAD(ENABLED);

namespace {
constexpr unsigned long kStatusIntervalMs = 2000;
constexpr uint8_t kAdxlPrimaryAddr = 0x53;
constexpr uint8_t kAdxlAltAddr = 0x1D;
constexpr uint8_t kAdxlRegDevid = 0x00;
constexpr uint8_t kAdxlRegPowerCtl = 0x2D;
constexpr uint8_t kAdxlRegDataFormat = 0x31;
constexpr uint8_t kAdxlRegDataStart = 0x32;
constexpr uint8_t kAdxlExpectedDevid = 0xE5;
constexpr float kAdxlScaleGPerLsb = 0.0039f; // full-resolution nominal scale
uint8_t gAdxlAddr = 0;
bool gAdxlReady = false;

// Toggle for inference/STATUS serial output to reduce flooding.
// Set to false (via ECHO_OFF) to silence the periodic heartbeat prints.
bool gEchoInference = true;

// ---- Inference pipeline constants (MUST match training config) ----
constexpr size_t kWindowSize = 50;          // 1.0 s @ 50 Hz
constexpr float kSampleIntervalMs = 20.0f;  // 50 Hz sampling cadence
constexpr size_t kChannels = 4;             // ax, ay, az + mag
constexpr float kZcEps = 1e-6f;             // zero-crossing deadband
// Pre-roll buffer: keep this many samples before the motion trigger so the
// actual triggering gesture is guaranteed to be inside the captured window.
constexpr size_t kPreRollCount = 10;        // 200 ms @ 50 Hz

struct Sample {
    float ax, ay, az;
};

Sample gWindow[kWindowSize];
size_t gWindowCount = 0;
bool gWindowReady = false;
unsigned long lastSampleMs = 0;
unsigned long lastStatusMs = 0;

// Pre-roll ring buffer: filled continuously in BASE_WAIT_MOTION so that when
// motion is detected, the samples just before the trigger are available to
// seed the capture window.
Sample gPreRoll[kPreRollCount];
size_t gPreRollCount = 0;
unsigned long lastPreRollSampleMs = 0;

// ---- Onboard RGB LED module ----
// Photon 2 onboard RGB LED is controlled via the Particle RGB API.
// Requirement: LED stays OFF until a gesture is registered.
struct LedFlash {
    uint8_t r, g, b;
    uint16_t onMs, offMs;
    uint8_t times;
    uint8_t flashed;
    unsigned long nextMs;
    bool isOn;
    bool active;
};
LedFlash gLedFlash = {0, 0, 0, 0, 0, 0, 0, 0, false, false};

void ledSolid(uint8_t r, uint8_t g, uint8_t b) {
    gLedFlash.active = false;
    RGB.control(true);
    RGB.color(r, g, b);
}

void ledOff() {
    gLedFlash.active = false;
    RGB.control(true);
    RGB.color(0, 0, 0);
}

void flashStart(uint8_t r, uint8_t g, uint8_t b, uint16_t onMs, uint16_t offMs, uint8_t times) {
    gLedFlash.r = r; gLedFlash.g = g; gLedFlash.b = b;
    gLedFlash.onMs = onMs; gLedFlash.offMs = offMs;
    gLedFlash.times = times;
    gLedFlash.flashed = 0;
    gLedFlash.isOn = false;
    gLedFlash.active = true;
    gLedFlash.nextMs = millis();
    RGB.control(true);
}

// Non-blocking flash step. Returns true while the pattern is active.
bool flashStep() {
    if (!gLedFlash.active) return false;
    const unsigned long now = millis();
    if (!gLedFlash.isOn) {
        if (now >= gLedFlash.nextMs) {
            RGB.color(gLedFlash.r, gLedFlash.g, gLedFlash.b);
            gLedFlash.isOn = true;
            gLedFlash.flashed++;
            gLedFlash.nextMs = now + gLedFlash.onMs;
        }
    } else {
        if (now >= gLedFlash.nextMs) {
            RGB.color(0, 0, 0);
            gLedFlash.isOn = false;
            if (gLedFlash.flashed >= gLedFlash.times) {
                gLedFlash.active = false;
                return false;
            }
            gLedFlash.nextMs = now + gLedFlash.offMs;
        }
    }
    return true;
}

// ---- Guided baseline capture state machine ----
// Flow:
//   Phase 0: stationary baseline (10 s, yellow flashing 0.5 on / 0.5 off)
//            -> saved as idle training samples + computes motion threshold
//   Phase 1: per-gesture capture (trials each):
//       tap1     -> flash BLUE x1 -> capture -> GREEN(ok)/RED(bad)
//       tap2     -> flash BLUE x2 -> capture -> GREEN(ok)/RED(bad)
//       tap3     -> flash BLUE x3 -> capture -> GREEN(ok)/RED(bad)
//       shake_lr -> flash RED/BLUE alternating x2 -> capture -> GREEN(ok)/RED(bad)
//   OK/BAD is confirmed manually over serial. On BAD the same gesture is retried
//   after a cooldown. Capture auto-starts on detected motion (past stationary floor).
enum BaselinePhase {
    BASE_IDLE,            // not collecting
    BASE_STATIONARY,      // 10 s yellow flashing, collecting stationary (idle)
    BASE_STATIONARY_DONE, // brief green + finalize threshold
    BASE_CUE,             // flashing cue for current gesture
    BASE_WAIT_MOTION,     // waiting for motion spike
    BASE_SAMPLING,        // capturing 1.0 s window
    BASE_AWAIT_CONFIRM,   // waiting for OK/BAD
    BASE_COOLDOWN_FAIL,   // red + cooldown, then retry same gesture
    BASE_COOLDOWN_OK,     // green + brief pause, then next trial
    BASE_DONE
};

const char* const kGestureLabels[4] = {"tap1", "tap2", "tap3", "shake_lr"};
constexpr size_t kGestureCount = 4;
constexpr size_t kGestureTrials = 5;        // trials per gesture
constexpr unsigned long kStationaryMs = 10000;   // 10 s stationary baseline
constexpr unsigned long kCuePauseMs = 600;       // pause between cue and motion wait
constexpr unsigned long kConfirmTimeoutMs = 20000; // max wait for OK/BAD
constexpr unsigned long kFailCooldownMs = 1500;   // cooldown after BAD
constexpr unsigned long kOkPauseMs = 800;         // pause after OK
constexpr float kMotionThresholdMin = 0.05f;      // minimum motion floor (g)
constexpr float kMotionThresholdMult = 3.0f;      // noise-floor multiplier

BaselinePhase gBasePhase = BASE_IDLE;
size_t gGestureIdx = 0;
size_t gTrial = 0;
size_t gSampleCount = 0;
unsigned long gPhaseMs = 0;

// Stationary statistics for motion threshold
double gMagMean = 0.0;
double gMagM2 = 0.0;
size_t gMagN = 0;
float gMotionThreshold = kMotionThresholdMin;

// Current gesture label for confirm handling
const char* gCurrentGestureLabel = nullptr;

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

// stat_v1 feature extraction (MUST mirror train.py channel_features)
void channelFeatures(const float* x, size_t n, float* out7) {
    float sum = 0.0f;
    for (size_t i = 0; i < n; ++i) sum += x[i];
    const float mean = sum / (float)n;

    float sq = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        float d = x[i] - mean;
        sq += d * d;
    }
    const float std = sqrtf(sq / (float)n);

    float mn = x[0], mx = x[0];
    for (size_t i = 1; i < n; ++i) {
        if (x[i] < mn) mn = x[i];
        if (x[i] > mx) mx = x[i];
    }
    const float rng = mx - mn;

    float esum = 0.0f;
    for (size_t i = 0; i < n; ++i) esum += x[i] * x[i];
    const float energy = esum / (float)n;

    int zc = 0;
    for (size_t i = 1; i < n; ++i) {
        float a = fabsf(x[i - 1]) < kZcEps ? 0.0f : x[i - 1];
        float b = fabsf(x[i]) < kZcEps ? 0.0f : x[i];
        if ((a < 0.0f) != (b < 0.0f)) ++zc;
    }

    out7[0] = mean;
    out7[1] = std;
    out7[2] = mn;
    out7[3] = mx;
    out7[4] = rng;
    out7[5] = energy;
    out7[6] = (float)zc;
}

void extractFeatures(float* features) {
    float ch[kWindowSize];
    size_t f = 0;

    for (size_t c = 0; c < kChannels; ++c) {
        for (size_t i = 0; i < kWindowSize; ++i) {
            float ax = gWindow[i].ax, ay = gWindow[i].ay, az = gWindow[i].az;
            if (c == 0) ch[i] = ax;
            else if (c == 1) ch[i] = ay;
            else if (c == 2) ch[i] = az;
            else ch[i] = sqrtf(ax * ax + ay * ay + az * az);
        }

        float s = 0.0f;
        for (size_t i = 0; i < kWindowSize; ++i) s += ch[i];
        const float m = s / (float)kWindowSize;
        for (size_t i = 0; i < kWindowSize; ++i) ch[i] -= m;

        float out7[7];
        channelFeatures(ch, kWindowSize, out7);
        for (size_t j = 0; j < 7; ++j) features[f++] = out7[j];
    }
}

// Map a predicted class index to a feedback LED color.
void flashClassFeedback(int classIdx) {
    if (classIdx == tinyml_model::CLASS_TAP1) flashStart(0, 0, 255, 150, 150, 1);       // blue x1
    else if (classIdx == tinyml_model::CLASS_TAP2) flashStart(0, 0, 255, 150, 150, 2);  // blue x2
    else if (classIdx == tinyml_model::CLASS_TAP3) flashStart(0, 0, 255, 150, 150, 3);  // blue x3
    else if (classIdx == tinyml_model::CLASS_SHAKE_LR) flashStart(255, 100, 0, 150, 150, 4); // orange rapid
    else ledOff();
}

void runInference() {
    float features[tinyml_model::kFeatureCount] = {0.0f};
    float scores[tinyml_model::kNumClasses] = {0.0f};

    extractFeatures(features);

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

    if (gEchoInference) {
        Serial.print("Predicted class: ");
        Serial.print(tinyml_model::kClassNames[bestIdx]);
        Serial.print(" | command: ");
        Serial.print(tinyml_model::kCommandMap[bestIdx]);
        Serial.print(" | score: ");
        Serial.printlnf("%.3f", bestScore);
    }

    // LED stays off until a confident, non-idle gesture is registered.
    if (bestScore >= tinyml_model::kDecisionConfidenceThreshold &&
        bestIdx != tinyml_model::CLASS_IDLE) {
        flashClassFeedback(bestIdx);
    } else {
        ledOff();
    }
}

} // namespace

// ---- I2C / ADXL343 helpers ----
bool probeI2cAddress(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;
}

bool readRegister8(uint8_t addr, uint8_t reg, uint8_t& out) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0) return false;
    int requested = Wire.requestFrom((int)addr, 1);
    if (requested != 1 || Wire.available() < 1) return false;
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
    if (Wire.endTransmission(false) != 0) return false;
    int requested = Wire.requestFrom((int)addr, (int)len);
    if (requested != (int)len || Wire.available() < (int)len) return false;
    for (size_t i = 0; i < len; ++i) out[i] = Wire.read();
    return true;
}

bool initAdxlMeasurementMode(uint8_t addr) {
    if (!writeRegister8(addr, kAdxlRegDataFormat, 0x0B)) return false; // FULL_RES +-16g
    if (!writeRegister8(addr, kAdxlRegPowerCtl, 0x08)) return false;   // MEASURE
    return true;
}

bool readAdxlRawXYZ(uint8_t addr, int16_t& x, int16_t& y, int16_t& z) {
    uint8_t buf[6] = {0};
    if (!readRegisters(addr, kAdxlRegDataStart, buf, sizeof(buf))) return false;
    x = (int16_t)((buf[1] << 8) | buf[0]);
    y = (int16_t)((buf[3] << 8) | buf[2]);
    z = (int16_t)((buf[5] << 8) | buf[4]);
    return true;
}

// Read one sample in g and return it via out. Returns true on success.
bool readSampleG(float& ax, float& ay, float& az) {
    int16_t rawX = 0, rawY = 0, rawZ = 0;
    if (!gAdxlReady) return false;
    if (!readAdxlRawXYZ(gAdxlAddr, rawX, rawY, rawZ)) return false;
    ax = rawX * kAdxlScaleGPerLsb;
    ay = rawY * kAdxlScaleGPerLsb;
    az = rawZ * kAdxlScaleGPerLsb;
    return true;
}

// Emit a SAMPLE protocol line from given acceleration values in g.
void emitSampleValues(float ax, float ay, float az) {
    Serial.print("SAMPLE,timestamp=");
    Serial.print(millis());
    Serial.print(",ax=");
    Serial.printlnf("%.6f,ay=%.6f,az=%.6f", ax, ay, az);
}

// Read one sample in g and emit a SAMPLE protocol line. Returns true on success.
bool emitSample() {
    int16_t rawX = 0, rawY = 0, rawZ = 0;
    if (!readAdxlRawXYZ(gAdxlAddr, rawX, rawY, rawZ)) return false;
    const float ax = rawX * kAdxlScaleGPerLsb;
    const float ay = rawY * kAdxlScaleGPerLsb;
    const float az = rawZ * kAdxlScaleGPerLsb;
    emitSampleValues(ax, ay, az);
    return true;
}

float readMagnitude() {
    int16_t rawX = 0, rawY = 0, rawZ = 0;
    if (!readAdxlRawXYZ(gAdxlAddr, rawX, rawY, rawZ)) return 0.0f;
    const float ax = rawX * kAdxlScaleGPerLsb;
    const float ay = rawY * kAdxlScaleGPerLsb;
    const float az = rawZ * kAdxlScaleGPerLsb;
    return sqrtf(ax * ax + ay * ay + az * az);
}

// ---- Baseline capture ----
void startBaseline() {
    gBasePhase = BASE_STATIONARY;
    gGestureIdx = 0;
    gTrial = 0;
    gSampleCount = 0;
    gMagMean = 0.0;
    gMagM2 = 0.0;
    gMagN = 0;
    gMotionThreshold = kMotionThresholdMin;
    gPhaseMs = millis();
    gWindowCount = 0;
    gWindowReady = false;
    gPreRollCount = 0;
    Serial.println("INFO,message=baseline started: hold still for 10 s (yellow flashing)");
    flashStart(255, 255, 0, 500, 500, 20); // yellow flashing ~10 s
}

void runBaseline() {
    if (gBasePhase == BASE_IDLE) {
        flashStep();
        return;
    }

    const unsigned long now = millis();
    flashStep();

    switch (gBasePhase) {
    case BASE_STATIONARY: {
        if (now - gPhaseMs >= kStationaryMs) {
            // Finalize stationary statistics -> idle trial complete
            ledSolid(0, 255, 0); // green
            Serial.println("RESULT,status=ok,label=idle,trial=1");
            const double variance = gMagN > 0 ? gMagM2 / (double)gMagN : 0.0;
            const double std = sqrt(variance);
            float thr = (float)(kMotionThresholdMult * std);
            if (thr < kMotionThresholdMin) thr = kMotionThresholdMin;
            gMotionThreshold = thr;
            Serial.printlnf("INFO,message=stationary baseline done: mag_mean=%.4f mag_std=%.4f motion_threshold=%.4f",
                            (float)gMagMean, (float)std, gMotionThreshold);
            gBasePhase = BASE_STATIONARY_DONE;
            gPhaseMs = now;
        } else if (gAdxlReady && (now - gPhaseMs) % (unsigned long)kSampleIntervalMs < 5) {
            // Collect one stationary sample per 20ms tick
            if (emitSample()) {
                float m = readMagnitude();
                gMagN++;
                double delta = m - gMagMean;
                gMagMean += delta / (double)gMagN;
                gMagM2 += delta * (m - (float)gMagMean);
            }
        }
        break;
    }

    case BASE_STATIONARY_DONE:
        if (now - gPhaseMs >= 500) {
            ledOff();
            gSampleCount = 0;
            gPreRollCount = 0;
            gBasePhase = BASE_CUE;
            gPhaseMs = now;
        }
        break;

    case BASE_CUE: {
        size_t gi = gGestureIdx;
        size_t trial = gTrial + 1;
        const char* label = kGestureLabels[gi];
        gCurrentGestureLabel = label;
        Serial.print("PROMPT,label=");
        Serial.print(label);
        Serial.print(",trial=");
        Serial.println((int)trial);

        if (gi == 0) flashStart(0, 0, 255, 200, 200, 1);            // tap1 blue x1
        else if (gi == 1) flashStart(0, 0, 255, 200, 200, 2);       // tap2 blue x2
        else if (gi == 2) flashStart(0, 0, 255, 200, 200, 3);       // tap3 blue x3
        else if (gi == 3) flashStart(255, 0, 0, 150, 150, 4);       // shake_lr red/blue-ish rapid

        gSampleCount = 0;
        gWindowCount = 0;
        gPreRollCount = 0;
        gBasePhase = BASE_WAIT_MOTION;
        gPhaseMs = now + kCuePauseMs;
        break;
    }

    case BASE_WAIT_MOTION: {
        // Wait for cue flash to finish, then wait for a motion spike.
        if (now < gPhaseMs) break;
        if (gLedFlash.active) break;
        if (gAdxlReady && (now - lastPreRollSampleMs >= (unsigned long)kSampleIntervalMs)) {
            lastPreRollSampleMs = now;
            float ax, ay, az;
            if (readSampleG(ax, ay, az)) {
                // Fill pre-roll ring buffer (keep last kPreRollCount samples).
                gPreRoll[gPreRollCount % kPreRollCount] = {ax, ay, az};
                gPreRollCount++;

                float m = sqrtf(ax * ax + ay * ay + az * az);
                if (fabsf(m - (float)gMagMean) > gMotionThreshold) {
                    // Motion detected -> seed window with pre-roll samples AND
                    // emit them as SAMPLE lines so the host sees the full 50-sample
                    // window (10 pre-roll + 40 live), matching training parity.
                    size_t available = gPreRollCount < kPreRollCount ? gPreRollCount : kPreRollCount;
                    gWindowCount = 0;
                    for (size_t i = 0; i < available; ++i) {
                        size_t idx = (gPreRollCount - available + i) % kPreRollCount;
                        gWindow[gWindowCount++] = gPreRoll[idx];
                        emitSampleValues(gPreRoll[idx].ax, gPreRoll[idx].ay, gPreRoll[idx].az);
                    }
                    gBasePhase = BASE_SAMPLING;
                    gPhaseMs = now;
                    ledSolid(180, 180, 180); // dim white while capturing
                }
            }
        }
        break;
    }

    case BASE_SAMPLING:
        if (gAdxlReady && (now - gPhaseMs >= (unsigned long)kSampleIntervalMs)) {
            gPhaseMs = now;
            float ax, ay, az;
            if (readSampleG(ax, ay, az)) {
                if (gWindowCount < kWindowSize) {
                    gWindow[gWindowCount++] = {ax, ay, az};
                }
                emitSample();
            }
            if (gWindowCount >= kWindowSize) {
                ledOff();
                gBasePhase = BASE_AWAIT_CONFIRM;
                gPhaseMs = now;
                Serial.println("INFO,message=confirm_ready label="
                    + String(gCurrentGestureLabel ? gCurrentGestureLabel : "?")
                    + " trial=" + String((int)(gTrial + 1)));
            }
        }
        break;

    case BASE_AWAIT_CONFIRM:
        if (now - gPhaseMs >= kConfirmTimeoutMs) {
            // Timeout -> treat as BAD
            ledOff();
            flashStart(255, 0, 0, 200, 200, 2);
            Serial.print("RESULT,status=fail,label=");
            Serial.print(gCurrentGestureLabel ? gCurrentGestureLabel : "?");
            Serial.print(",trial=");
            Serial.print((int)(gTrial + 1));
            Serial.println(",reason=timeout");
            gBasePhase = BASE_COOLDOWN_FAIL;
            gPhaseMs = now;
        }
        break;

    case BASE_COOLDOWN_FAIL:
        if (now - gPhaseMs >= kFailCooldownMs) {
            ledOff();
            flashStart(255, 0, 0, 200, 200, 2);
            // Retry the same gesture/trial
            gSampleCount = 0;
            gWindowCount = 0;
            gPreRollCount = 0;
            gBasePhase = BASE_CUE;
            gPhaseMs = now;
        }
        break;

    case BASE_COOLDOWN_OK:
        if (now - gPhaseMs >= kOkPauseMs) {
            ledOff();
            gTrial++;
            if (gTrial >= kGestureTrials) {
                gTrial = 0;
                gGestureIdx++;
                if (gGestureIdx >= kGestureCount) {
                    gBasePhase = BASE_DONE;
                    Serial.println("INFO,message=baseline complete");
                    return;
                }
            }
            gSampleCount = 0;
            gWindowCount = 0;
            gPreRollCount = 0;
            gBasePhase = BASE_CUE;
            gPhaseMs = now;
        }
        break;

    case BASE_DONE:
        ledOff();
        break;

    default:
        break;
    }
}

// ---- Serial command / confirmation handling ----
void handleSerialCommand() {
    if (Serial.available() <= 0) return;
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.equalsIgnoreCase("START_BASELINE")) {
        startBaseline();
    } else if (cmd.equalsIgnoreCase("STOP_BASELINE")) {
        gBasePhase = BASE_IDLE;
        ledOff();
        Serial.println("INFO,message=baseline stopped");
    } else if (cmd.equalsIgnoreCase("ECHO_ON")) {
        gEchoInference = true;
        Serial.println("INFO,message=echo on");
    } else if (cmd.equalsIgnoreCase("ECHO_OFF")) {
        gEchoInference = false;
        Serial.println("INFO,message=echo off");
    } else if (gBasePhase == BASE_AWAIT_CONFIRM) {
        if (cmd.equalsIgnoreCase("OK")) {
            ledOff();
            flashStart(0, 255, 0, 200, 200, 2); // green
            Serial.print("RESULT,status=ok,label=");
            Serial.print(gCurrentGestureLabel ? gCurrentGestureLabel : "?");
            Serial.print(",trial=");
            Serial.println((int)(gTrial + 1));
            gBasePhase = BASE_COOLDOWN_OK;
            gPhaseMs = millis();
        } else if (cmd.equalsIgnoreCase("BAD")) {
            ledOff();
            flashStart(255, 0, 0, 200, 200, 2); // red
            Serial.print("RESULT,status=fail,label=");
            Serial.print(gCurrentGestureLabel ? gCurrentGestureLabel : "?");
            Serial.print(",trial=");
            Serial.print((int)(gTrial + 1));
            Serial.println(",reason=operator_reject");
            gBasePhase = BASE_COOLDOWN_FAIL;
            gPhaseMs = millis();
        }
    }
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
    if (primarySeen) chosenAddr = kAdxlPrimaryAddr;
    else if (altSeen) chosenAddr = kAdxlAltAddr;

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
        if (gAdxlReady) Serial.println("[ADXL] Measurement mode enabled.");
        else Serial.println("[ADXL] Failed to enable measurement mode.");
    } else {
        Serial.println("[ADXL] WARNING: DEVID mismatch (expected 0xE5).");
        gAdxlReady = false;
        gAdxlAddr = 0;
    }

    Serial.println("=========================");
}

void setup() {
    Serial.begin(115200);
    delay(3000); // allow monitor to attach

    RGB.control(true);
    ledOff();

    printAdxlDiagnostics();

    tinyml_model::model_init();
    printModelMetadata();

    Serial.println("Commands: START_BASELINE / STOP_BASELINE / OK / BAD / ECHO_ON / ECHO_OFF");
}

void loop() {
    handleSerialCommand();

    if (gBasePhase != BASE_IDLE) {
        runBaseline();
        return;
    }

    // Normal inference mode (LED off until a gesture is registered).
    if (gAdxlReady && (millis() - lastSampleMs >= (unsigned long)kSampleIntervalMs)) {
        lastSampleMs = millis();
        int16_t rawX = 0, rawY = 0, rawZ = 0;
        if (readAdxlRawXYZ(gAdxlAddr, rawX, rawY, rawZ)) {
            gWindow[gWindowCount].ax = rawX * kAdxlScaleGPerLsb;
            gWindow[gWindowCount].ay = rawY * kAdxlScaleGPerLsb;
            gWindow[gWindowCount].az = rawZ * kAdxlScaleGPerLsb;
            gWindowCount++;
            if (gWindowCount >= kWindowSize) {
                gWindowCount = 0;
                gWindowReady = true;
            }
        }
    }

    if (gWindowReady) {
        gWindowReady = false;
        runInference();
    }

    if (gEchoInference && millis() - lastStatusMs >= kStatusIntervalMs) {
        lastStatusMs = millis();
        Serial.printlnf(
            "STATUS window_filled=%d feature_count=%d",
            (int)gWindowCount, (int)tinyml_model::kFeatureCount
        );
    }
}
