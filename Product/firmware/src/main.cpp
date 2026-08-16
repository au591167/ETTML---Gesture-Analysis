#include "Particle.h"
#include "model_data.h"
#include <math.h>

SYSTEM_MODE(AUTOMATIC);
SYSTEM_THREAD(ENABLED);

namespace {
constexpr unsigned long kStatusIntervalMs = 2000;
// Release gate: enable LIVE only for firmware compiled with a current,
// class-complete exported model. The checked-in model uses pilot-v3 data.
constexpr bool kModelReadyForLive = true;
constexpr uint8_t kAdxlPrimaryAddr = 0x53;
constexpr uint8_t kAdxlAltAddr = 0x1D;
constexpr uint8_t kAdxlRegDevid = 0x00;
constexpr uint8_t kAdxlRegPowerCtl = 0x2D;
constexpr uint8_t kAdxlRegBwRate = 0x2C;
constexpr uint8_t kAdxlRegDataFormat = 0x31;
constexpr uint8_t kAdxlRegDataStart = 0x32;
constexpr uint8_t kAdxlExpectedDevid = 0xE5;
constexpr float kAdxlScaleGPerLsb = 0.0039f; // full-resolution nominal scale
uint8_t gAdxlAddr = 0;
bool gAdxlReady = false;

// OperatingMode answers "what is the device for right now?".  It is kept
// separate from BaselinePhase, which describes a short-lived step inside a
// TRAINING capture session.  Mixing these two concepts was the main source of
// ambiguity in the original control flow.
enum class OperatingMode : uint8_t {
    DEBUG,
    TRAINING,
    LIVE
};

OperatingMode gOperatingMode = OperatingMode::DEBUG;

// Toggle for inference/STATUS serial output to reduce flooding.
// Set to false (via ECHO_OFF) to silence the periodic heartbeat prints.
bool gEchoInference = true;

// ---- Inference pipeline constants (MUST match training config) ----
constexpr size_t kWindowSize = 1600;        // 4.0 s @ 400 Hz (pilot v3)
constexpr uint32_t kSampleIntervalUs = 2500; // 400 Hz sampling cadence
constexpr float kSampleIntervalMs = 20.0f;  // legacy guided-capture cadence
constexpr size_t kChannels = 4;             // ax, ay, az + mag
// Pre-roll buffer: keep this many samples before the motion trigger so the
// actual triggering gesture is guaranteed to be inside the captured window.
constexpr size_t kPreRollCount = 10;        // 200 ms @ 50 Hz
constexpr size_t kInferenceStride = 100;    // 0.25 s between predictions
constexpr size_t kPeakRefractorySamples = 8; // stat_v2 training parity
constexpr float kPeakThresholdFloorG = 0.05f;

struct Sample {
    float ax, ay, az;
};

Sample gWindow[kWindowSize];
size_t gWindowCount = 0;
bool gWindowReady = false;
uint32_t lastSampleUs = 0;
unsigned long lastStatusMs = 0;
unsigned long gLastCaptureSampleMs = 0;
uint32_t gSensorReadErrors = 0;
uint32_t gInferenceCount = 0;
uint32_t gInferenceTotalUs = 0;
uint32_t gInferenceMaxUs = 0;

// ---- High-rate tap oscilloscope diagnostic ----
// This experiment is intentionally separate from LIVE inference. It captures
// synchronized X/Y/Z samples at 400 Hz, buffers them in RAM, and emits the
// samples afterward so Serial printing cannot disturb acquisition.
constexpr size_t kTapScopeSampleCount = 1600;      // 4.0 s at 400 Hz
constexpr uint32_t kTapScopeIntervalUs = 2500;     // 2.5 ms
constexpr uint32_t kTapScopeCueTimeUs = 500000;    // 0.5 s pre-cue baseline
constexpr unsigned long kTapScopeCountdownMs = 3000;
float gTapScopeX[kTapScopeSampleCount];
float gTapScopeY[kTapScopeSampleCount];
float gTapScopeZ[kTapScopeSampleCount];
uint32_t gTapScopeTimeUs[kTapScopeSampleCount];
size_t gTapScopeCount = 0;
uint32_t gTapScopeStartedUs = 0;
uint32_t gTapScopeNextUs = 0;
unsigned long gTapScopeArmMs = 0;
enum class TapScopeState : uint8_t { IDLE, COUNTDOWN, CAPTURING };
TapScopeState gTapScopeState = TapScopeState::IDLE;
bool gTapScopeCueShown = false;

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
    uint8_t alternateR, alternateG, alternateB;
    uint16_t onMs, offMs;
    uint8_t times;
    uint8_t flashed;
    unsigned long nextMs;
    bool isOn;
    bool active;
    bool alternating;
};
LedFlash gLedFlash = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, false, false, false};

// Decision history implements the configuration exported with the model.
// A gesture becomes an event only after N consecutive confident predictions.
int gDecisionHistory[tinyml_model::kDecisionSmoothingWindows] = {0};
float gDecisionScores[tinyml_model::kDecisionSmoothingWindows] = {0.0f};
size_t gDecisionHistoryCount = 0;
unsigned long gLastGestureEventMs = 0;

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
    gLedFlash.alternateR = r; gLedFlash.alternateG = g; gLedFlash.alternateB = b;
    gLedFlash.onMs = onMs; gLedFlash.offMs = offMs;
    gLedFlash.times = times;
    gLedFlash.flashed = 0;
    gLedFlash.isOn = false;
    gLedFlash.active = true;
    gLedFlash.alternating = false;
    gLedFlash.nextMs = millis();
    RGB.control(true);
}

void flashStartAlternating(
    uint8_t r1, uint8_t g1, uint8_t b1,
    uint8_t r2, uint8_t g2, uint8_t b2,
    uint16_t onMs, uint16_t offMs, uint8_t times
) {
    flashStart(r1, g1, b1, onMs, offMs, times);
    gLedFlash.alternateR = r2;
    gLedFlash.alternateG = g2;
    gLedFlash.alternateB = b2;
    gLedFlash.alternating = true;
}

const char* operatingModeName(OperatingMode mode) {
    switch (mode) {
    case OperatingMode::DEBUG: return "DEBUG";
    case OperatingMode::TRAINING: return "TRAINING";
    case OperatingMode::LIVE: return "LIVE";
    }
    return "UNKNOWN";
}

void resetInferenceState() {
    gWindowCount = 0;
    gWindowReady = false;
    gDecisionHistoryCount = 0;
    gLastGestureEventMs = 0;
    ledOff();
}

// Non-blocking flash step. Returns true while the pattern is active.
bool flashStep() {
    if (!gLedFlash.active) return false;
    const unsigned long now = millis();
    if (!gLedFlash.isOn) {
        if (now >= gLedFlash.nextMs) {
            const bool useAlternate = gLedFlash.alternating && (gLedFlash.flashed % 2 == 1);
            RGB.color(
                useAlternate ? gLedFlash.alternateR : gLedFlash.r,
                useAlternate ? gLedFlash.alternateG : gLedFlash.g,
                useAlternate ? gLedFlash.alternateB : gLedFlash.b
            );
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
constexpr unsigned long kIdleSettleMs = 2000;    // hands off before idle capture
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

// stat_v2 feature extraction (MUST mirror train.py channel_features).
// Feature order per channel:
//   std, min, max, range, energy, peak_count, max_abs_diff
// Peak count and max_abs_diff replace the redundant post-centering mean and
// broad zero-crossing count. They preserve temporal evidence needed to tell
// one, two, and three taps apart while keeping the model input at 28 values.
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

    float maxAbsDiff = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        if (i > 0) {
            const float d = fabsf(x[i] - x[i - 1]);
            if (d > maxAbsDiff) maxAbsDiff = d;
        }
    }

    // A fixed physical threshold performed better than a fraction of the
    // strongest impulse: with an adaptive fraction, one unusually strong first
    // tap could hide the second/third valid tap in the same window.
    const float peakThreshold = kPeakThresholdFloorG;
    size_t peakCount = 0;
    size_t lastPeak = 0;
    bool havePeak = false;
    for (size_t i = 1; i + 1 < n; ++i) {
        const float prev = fabsf(x[i - 1]);
        const float current = fabsf(x[i]);
        const float next = fabsf(x[i + 1]);
        const bool localMaximum = current >= prev && current > next;
        const bool outsideRefractory = !havePeak || i - lastPeak >= kPeakRefractorySamples;
        if (current >= peakThreshold && localMaximum && outsideRefractory) {
            peakCount++;
            lastPeak = i;
            havePeak = true;
        }
    }

    out7[0] = std;
    out7[1] = mn;
    out7[2] = mx;
    out7[3] = rng;
    out7[4] = energy;
    out7[5] = (float)peakCount;
    out7[6] = maxAbsDiff;
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

// Count separated impact envelopes in the same way as the automatic capture
// validator. This is a decision guard, not a replacement classifier: the MLP
// still separates idle/tap/shake, while physics resolves adjacent tap counts.
int countImpactEvents() {
    constexpr size_t kBaselineSamples = 200;       // first 0.5 s at 400 Hz
    constexpr float kImpactThresholdG = 0.35f;
    constexpr size_t kSeparationSamples = 60;      // 150 ms below threshold
    float bx = 0.0f, by = 0.0f, bz = 0.0f;
    for (size_t i = 0; i < kBaselineSamples; ++i) {
        bx += gWindow[i].ax; by += gWindow[i].ay; bz += gWindow[i].az;
    }
    bx /= kBaselineSamples; by /= kBaselineSamples; bz /= kBaselineSamples;

    int events = 0;
    size_t lastActive = 0;
    bool haveActive = false;
    for (size_t i = 0; i < kWindowSize; ++i) {
        const float dx = gWindow[i].ax - bx;
        const float dy = gWindow[i].ay - by;
        const float dz = gWindow[i].az - bz;
        if (sqrtf(dx * dx + dy * dy + dz * dz) < kImpactThresholdG) continue;
        if (!haveActive || i - lastActive > kSeparationSamples) events++;
        lastActive = i;
        haveActive = true;
    }
    return events;
}

// LIVE LED contract. Intervals are start-to-start: a 250 ms pulse followed by
// 250 ms off gives tap2 a 0.5 s cadence; 165+165 ms approximates 0.33 s.
void flashClassFeedback(int classIdx) {
    if (classIdx == tinyml_model::CLASS_TAP1) flashStart(0, 0, 255, 1000, 0, 1);
    else if (classIdx == tinyml_model::CLASS_TAP2) flashStart(0, 0, 255, 250, 250, 2);
    else if (classIdx == tinyml_model::CLASS_TAP3) flashStart(255, 0, 0, 165, 165, 3);
    else if (classIdx == tinyml_model::CLASS_SHAKE_LR) {
        flashStartAlternating(255, 0, 0, 0, 0, 255, 500, 500, 4);
    }
    else ledOff();
}

// Convert raw classifier output into a stable application event.  Classification
// and action are intentionally separate: softmax answers "what does this window
// resemble?", while this function answers "is it safe to act now?".
int updateDecision(int classIdx, float score, unsigned long nowMs) {
    const bool confident = score >= tinyml_model::kDecisionConfidenceThreshold;
    const int candidate = confident ? classIdx : tinyml_model::CLASS_IDLE;

    if (gDecisionHistoryCount < tinyml_model::kDecisionSmoothingWindows) {
        gDecisionHistory[gDecisionHistoryCount] = candidate;
        gDecisionScores[gDecisionHistoryCount] = score;
        gDecisionHistoryCount++;
    } else {
        for (size_t i = 1; i < tinyml_model::kDecisionSmoothingWindows; ++i) {
            gDecisionHistory[i - 1] = gDecisionHistory[i];
            gDecisionScores[i - 1] = gDecisionScores[i];
        }
        const size_t last = tinyml_model::kDecisionSmoothingWindows - 1;
        gDecisionHistory[last] = candidate;
        gDecisionScores[last] = score;
    }

    if (gDecisionHistoryCount < tinyml_model::kDecisionSmoothingWindows) return -1;
    const int stableClass = gDecisionHistory[0];
    if (stableClass == tinyml_model::CLASS_IDLE) return -1;
    for (size_t i = 1; i < tinyml_model::kDecisionSmoothingWindows; ++i) {
        if (gDecisionHistory[i] != stableClass) return -1;
    }
    if (nowMs - gLastGestureEventMs < tinyml_model::kDecisionDebounceMs) return -1;

    gLastGestureEventMs = nowMs;
    gDecisionHistoryCount = 0; // a new event requires a fresh stable sequence
    return stableClass;
}

void runInference() {
    float features[tinyml_model::kFeatureCount] = {0.0f};
    float scores[tinyml_model::kNumClasses] = {0.0f};

    extractFeatures(features);

    const unsigned long inferenceStartUs = micros();
    tinyml_model::model_infer(
        features,
        tinyml_model::kFeatureCount,
        scores,
        tinyml_model::kNumClasses
    );
    const uint32_t inferenceUs = (uint32_t)(micros() - inferenceStartUs);
    gInferenceCount++;
    gInferenceTotalUs += inferenceUs;
    if (inferenceUs > gInferenceMaxUs) gInferenceMaxUs = inferenceUs;

    int bestIdx = 0;
    float bestScore = scores[0];
    for (size_t i = 1; i < tinyml_model::kNumClasses; ++i) {
        if (scores[i] > bestScore) {
            bestScore = scores[i];
            bestIdx = (int)i;
        }
    }

    const int impactEvents = countImpactEvents();
    const bool learnedTap = bestIdx == tinyml_model::CLASS_TAP1 ||
                            bestIdx == tinyml_model::CLASS_TAP2 ||
                            bestIdx == tinyml_model::CLASS_TAP3;
    if (learnedTap && impactEvents >= 1 && impactEvents <= 3) {
        bestIdx = impactEvents == 1 ? tinyml_model::CLASS_TAP1 :
                  impactEvents == 2 ? tinyml_model::CLASS_TAP2 :
                                      tinyml_model::CLASS_TAP3;
    }

    if (gOperatingMode == OperatingMode::DEBUG && gEchoInference) {
        Serial.print("Predicted class: ");
        Serial.print(tinyml_model::kClassNames[bestIdx]);
        Serial.print(" | command: ");
        Serial.print(tinyml_model::kCommandMap[bestIdx]);
        Serial.print(" | score: ");
        Serial.printlnf("%.3f", bestScore);
        Serial.printlnf("DEBUG,inference_us=%lu", (unsigned long)inferenceUs);
    }

    const int eventClass = updateDecision(bestIdx, bestScore, millis());
    if (eventClass >= 0 && gOperatingMode == OperatingMode::LIVE) {
        Serial.print("EVENT,class=");
        Serial.print(tinyml_model::kClassNames[eventClass]);
        Serial.print(",command=");
        Serial.print(tinyml_model::kCommandMap[eventClass]);
        Serial.print(",score=");
        Serial.printlnf("%.3f", bestScore);
        flashClassFeedback(eventClass);
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
    if (!writeRegister8(addr, kAdxlRegBwRate, 0x0C)) return false;    // 400 Hz LIVE/model ODR
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

void startTapScope() {
    if (!gAdxlReady) {
        Serial.println("ERROR,message=TAP_SCOPE requires a working ADXL343");
        return;
    }
    if (gOperatingMode != OperatingMode::DEBUG) {
        Serial.println("ERROR,message=TAP_SCOPE is available only in DEBUG mode");
        return;
    }
    resetInferenceState();
    gTapScopeCount = 0;
    gTapScopeCueShown = false;
    gTapScopeArmMs = millis();
    gTapScopeState = TapScopeState::COUNTDOWN;
    ledSolid(255, 180, 0); // amber: prepare to tap
    Serial.printlnf("SCOPE,phase=countdown,duration_ms=%lu",
                    kTapScopeCountdownMs);
    Serial.println("SCOPE,message=tap once immediately after GO");
}

// Returns true while the scope experiment owns sensor acquisition.
bool runTapScope() {
    if (gTapScopeState == TapScopeState::IDLE) return false;

    if (gTapScopeState == TapScopeState::COUNTDOWN) {
        if (millis() - gTapScopeArmMs < kTapScopeCountdownMs) return true;
        // Fast-mode I2C is required for reliable six-byte XYZ reads at 400 Hz.
        Wire.setSpeed(CLOCK_SPEED_400KHZ);
        if (!writeRegister8(gAdxlAddr, kAdxlRegBwRate, 0x0C)) { // 400 Hz ODR
            Serial.println("ERROR,message=failed to configure ADXL343 for 400 Hz");
            gTapScopeState = TapScopeState::IDLE;
            return false;
        }
        gTapScopeStartedUs = micros();
        gTapScopeNextUs = gTapScopeStartedUs;
        gTapScopeState = TapScopeState::CAPTURING;
        // Keep the LED yellow for the first 500 ms. This produces a measured
        // pre-cue baseline and removes ambiguity about when green became visible.
        Serial.println("SCOPE,phase=precue,rate_hz=400,axes=xyz,samples=1600,cue_time_us=500000");
        return true;
    }

    const uint32_t nowUs = micros();
    if (!gTapScopeCueShown && nowUs - gTapScopeStartedUs >= kTapScopeCueTimeUs) {
        // Ensure the desktop receives GO before the visible cue. Without this
        // flush, USB CDC could retain the short line until the post-capture
        // data dump, making the GUI turn green seconds after the firmware cue.
        Serial.println("SCOPE,phase=go,cue_time_us=500000");
        Serial.flush();
        gTapScopeCueShown = true;
        ledSolid(0, 255, 0); // green: tap now
        // Do not catch up missed deadlines after the synchronous cue flush.
        gTapScopeNextUs = micros();
        return true;
    }
    if ((int32_t)(nowUs - gTapScopeNextUs) < 0) return true;

    float ax = 0.0f, ay = 0.0f, az = 0.0f;
    if (readSampleG(ax, ay, az)) {
        gTapScopeTimeUs[gTapScopeCount] = nowUs - gTapScopeStartedUs;
        gTapScopeX[gTapScopeCount] = ax;
        gTapScopeY[gTapScopeCount] = ay;
        gTapScopeZ[gTapScopeCount] = az;
        ++gTapScopeCount;
    } else {
        ++gSensorReadErrors;
    }
    // Advance from the prior deadline rather than from now, avoiding gradual
    // scheduler drift over the 1.5-second recording.
    gTapScopeNextUs += kTapScopeIntervalUs;

    if (gTapScopeCount < kTapScopeSampleCount) return true;

    writeRegister8(gAdxlAddr, kAdxlRegBwRate, 0x0C); // restore 400 Hz model ODR
    Wire.setSpeed(CLOCK_SPEED_400KHZ);
    Serial.println("SCOPE_DATA,time_us,x_g,y_g,z_g");
    for (size_t i = 0; i < gTapScopeCount; ++i) {
        Serial.printlnf("SCOPE_DATA,%lu,%.6f,%.6f,%.6f",
                        (unsigned long)gTapScopeTimeUs[i], gTapScopeX[i],
                        gTapScopeY[i], gTapScopeZ[i]);
    }
    Serial.printlnf("SCOPE,phase=complete,samples=%d", (int)gTapScopeCount);
    ledOff();
    gTapScopeState = TapScopeState::IDLE;
    return false;
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
    gOperatingMode = OperatingMode::TRAINING;
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
    gLastCaptureSampleMs = 0;
    Serial.println("INFO,message=baseline started: hold still for 10 s (yellow flashing)");
    // Frame stationary data exactly like every other labeled trial.  Host tools
    // ignore unframed SAMPLE lines, which is why the earlier implementation
    // announced idle success without ever writing an idle CSV.
    Serial.println("PROMPT,label=idle,trial=1");
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
            // Finalize the noise estimate after the complete stationary period.
            ledSolid(0, 255, 0); // green
            const double variance = gMagN > 0 ? gMagM2 / (double)gMagN : 0.0;
            const double std = sqrt(variance);
            float thr = (float)(kMotionThresholdMult * std);
            if (thr < kMotionThresholdMin) thr = kMotionThresholdMin;
            gMotionThreshold = thr;
            Serial.printlnf("INFO,message=stationary baseline done: mag_mean=%.4f mag_std=%.4f motion_threshold=%.4f",
                            (float)gMagMean, (float)std, gMotionThreshold);
            gBasePhase = BASE_STATIONARY_DONE;
            gPhaseMs = now;
        } else if (gAdxlReady && now - gLastCaptureSampleMs >= (unsigned long)kSampleIntervalMs) {
            gLastCaptureSampleMs = now;
            Sample sample;
            if (readSampleG(sample.ax, sample.ay, sample.az)) {
                // Use the same physical read for CSV output and noise statistics.
                // Ignore the first two seconds so touching the board or starting
                // the host command cannot contaminate the idle label.
                const bool settled = now - gPhaseMs >= kIdleSettleMs;
                if (settled && gSampleCount < kWindowSize) {
                    emitSampleValues(sample.ax, sample.ay, sample.az);
                    gSampleCount++;
                    if (gSampleCount == kWindowSize) {
                        Serial.println("RESULT,status=ok,label=idle,trial=1");
                    }
                }
                if (settled) {
                    const float m = sqrtf(sample.ax * sample.ax + sample.ay * sample.ay + sample.az * sample.az);
                    gMagN++;
                    double delta = m - gMagMean;
                    gMagMean += delta / (double)gMagN;
                    gMagM2 += delta * (m - (float)gMagMean);
                }
            } else {
                gSensorReadErrors++;
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
                    // Motion detected -> seed the legacy guided-capture window
                    // with pre-roll samples and emit them to the host. This path
                    // polls at 50 Hz; final pilot_v3 capture uses TAP_SCOPE at
                    // 400 Hz and the LIVE model uses the 1,600-sample contract.
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
            } else {
                gSensorReadErrors++;
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
                // Emit the exact sample stored in gWindow; never perform a
                // second sensor read for the same logical sampling tick.
                emitSampleValues(ax, ay, az);
            } else {
                gSensorReadErrors++;
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
void printModeStatus() {
    Serial.print("MODE,current=");
    Serial.println(operatingModeName(gOperatingMode));
}

void setOperatingMode(OperatingMode nextMode) {
    if (gOperatingMode == nextMode &&
        !(nextMode == OperatingMode::TRAINING && gBasePhase == BASE_IDLE)) {
        printModeStatus();
        return;
    }

    // Every transition cancels mode-specific work.  This prevents a partially
    // filled inference window or capture timer leaking into the next mode.
    gBasePhase = BASE_IDLE;
    resetInferenceState();
    gOperatingMode = nextMode;
    gEchoInference = nextMode == OperatingMode::DEBUG;

    Serial.print("INFO,message=mode changed to ");
    Serial.println(operatingModeName(nextMode));
    printModeStatus();

    if (nextMode == OperatingMode::TRAINING) {
        startBaseline();
    }
}

void printCommandHelp() {
    Serial.println("Commands:");
    Serial.println("  MODE DEBUG     - verbose inference diagnostics, no gesture LED actions");
    Serial.println("  MODE TRAINING  - guided labeled data capture");
    Serial.println("  MODE LIVE      - quiet inference with EVENT and LED feedback");
    Serial.println("  MODE?          - print current operating mode");
    Serial.println("  START_BASELINE / STOP_BASELINE / OK / BAD - training controls");
    Serial.println("  ECHO_ON / ECHO_OFF - DEBUG serial verbosity");
    Serial.println("  TAP_SCOPE       - capture 4.0 s of XYZ acceleration at 400 Hz (DEBUG only)");
    Serial.println("  STATUS / HELP");
}

void handleSerialCommand() {
    if (Serial.available() <= 0) return;
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.equalsIgnoreCase("MODE DEBUG")) {
        setOperatingMode(OperatingMode::DEBUG);
    } else if (cmd.equalsIgnoreCase("MODE TRAINING")) {
        setOperatingMode(OperatingMode::TRAINING);
    } else if (cmd.equalsIgnoreCase("MODE LIVE")) {
        if (kModelReadyForLive) {
            setOperatingMode(OperatingMode::LIVE);
        } else {
            Serial.println("ERROR,message=LIVE locked: collect/train/export dataset v2 and rebuild firmware");
        }
    } else if (cmd.equalsIgnoreCase("MODE?")) {
        printModeStatus();
    } else if (cmd.equalsIgnoreCase("HELP")) {
        printCommandHelp();
    } else if (cmd.equalsIgnoreCase("TAP_SCOPE")) {
        startTapScope();
    } else if (cmd.equalsIgnoreCase("STATUS")) {
        const uint32_t meanUs = gInferenceCount > 0 ? gInferenceTotalUs / gInferenceCount : 0;
        Serial.printlnf(
            "STATUS,mode=%s,sensor=%s,window=%d,inferences=%lu,mean_us=%lu,max_us=%lu,read_errors=%lu",
            operatingModeName(gOperatingMode), gAdxlReady ? "ok" : "error",
            (int)gWindowCount, (unsigned long)gInferenceCount,
            (unsigned long)meanUs, (unsigned long)gInferenceMaxUs,
            (unsigned long)gSensorReadErrors
        );
    } else if (cmd.equalsIgnoreCase("START_BASELINE")) {
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
    Wire.setSpeed(CLOCK_SPEED_400KHZ);

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

    Serial.println("Default mode: DEBUG (safe diagnostics; no gesture actions)");
    printCommandHelp();
    printModeStatus();
}

void loop() {
    handleSerialCommand();

    // A scope capture temporarily owns the sensor and suspends the ordinary
    // DEBUG inference sampler. Samples are printed only after capture ends.
    if (runTapScope()) return;

    if (gOperatingMode == OperatingMode::TRAINING) {
        runBaseline();
        return;
    }

    // LED animation is advanced independently of inference; no delay() calls
    // are needed, so serial handling and 400 Hz acquisition remain responsive.
    flashStep();

    // DEBUG and LIVE share the exact same sensor/model path.  They differ only
    // in presentation: DEBUG prints diagnostics; LIVE emits stable events.
    if (!kModelReadyForLive) {
        if (gOperatingMode == OperatingMode::DEBUG && gEchoInference &&
            millis() - lastStatusMs >= kStatusIntervalMs) {
            lastStatusMs = millis();
            Serial.printlnf("STATUS,mode=DEBUG,model=stale_v1,sensor=%s,read_errors=%lu",
                            gAdxlReady ? "ok" : "error", (unsigned long)gSensorReadErrors);
        }
        return;
    }
    const uint32_t nowUs = micros();
    if (gAdxlReady && (uint32_t)(nowUs - lastSampleUs) >= kSampleIntervalUs) {
        lastSampleUs = nowUs;
        Sample sample;
        if (readSampleG(sample.ax, sample.ay, sample.az)) {
            gWindow[gWindowCount] = sample;
            gWindowCount++;
            if (gWindowCount >= kWindowSize) {
                gWindowReady = true;
            }
        } else {
            gSensorReadErrors++;
        }
    }

    if (gWindowReady) {
        gWindowReady = false;
        runInference();
        // Retain the overlapping 3.75 s and acquire 0.25 s of new samples.
        for (size_t i = kInferenceStride; i < kWindowSize; ++i) {
            gWindow[i - kInferenceStride] = gWindow[i];
        }
        gWindowCount = kWindowSize - kInferenceStride;
    }

    if (gOperatingMode == OperatingMode::DEBUG && gEchoInference &&
        millis() - lastStatusMs >= kStatusIntervalMs) {
        lastStatusMs = millis();
        Serial.printlnf(
            "STATUS,mode=DEBUG,window=%d,features=%d,read_errors=%lu",
            (int)gWindowCount, (int)tinyml_model::kFeatureCount,
            (unsigned long)gSensorReadErrors
        );
    }
}
