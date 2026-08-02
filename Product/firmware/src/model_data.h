#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace tinyml_model {

constexpr const char* kProjectName = "tinyml-gesture-blackjack-sim";
constexpr const char* kTargetMcu = "Particle Photon 2";
constexpr std::size_t kNumClasses = 5;
constexpr std::size_t kFeatureCount = 28;

constexpr float kDecisionConfidenceThreshold = 0.750000f;
constexpr std::uint32_t kDecisionDebounceMs = 300u;
constexpr std::size_t kDecisionSmoothingWindows = 3u;

enum GestureClass : std::int32_t {
  CLASS_IDLE = 0,
  CLASS_TAP1 = 1,
  CLASS_TAP2 = 2,
  CLASS_TAP3 = 3,
  CLASS_SHAKE_LR = 4
};

extern const char* const kClassNames[kNumClasses];
extern const char* const kCommandMap[kNumClasses];

/*
 * Placeholder inference API contract for firmware integration.
 * Replace implementation with real model runtime once model weights
 * serialization path is finalized.
 */
void model_init();
void model_infer(const float* features, std::size_t feature_count, float* out_scores, std::size_t out_len);

} // namespace tinyml_model
