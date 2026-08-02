#include "model_data.h"

namespace tinyml_model {

const char* const kClassNames[kNumClasses] = {
  "idle",
  "tap1",
  "tap2",
  "tap3",
  "shake_lr"
};

const char* const kCommandMap[kNumClasses] = {
  "no_action",
  "stand",
  "hit",
  "exit",
  "split"
};

void model_init() {
  // Placeholder: initialize embedded model runtime here.
}

void model_infer(const float* /*features*/, std::size_t feature_count, float* out_scores, std::size_t out_len) {
  // Placeholder deterministic baseline:
  // - validates expected feature length
  // - returns idle class with score 1.0 and others 0.0
  if (!out_scores || out_len < kNumClasses) {
    return;
  }

  for (std::size_t i = 0; i < out_len; ++i) {
    out_scores[i] = 0.0f;
  }

  if (feature_count != kFeatureCount) {
    // Keep all zeros on mismatch as a safe fallback.
    return;
  }

  // Prefer idle when available; otherwise first class.
  std::size_t idle_idx = 0;
  for (std::size_t i = 0; i < kNumClasses; ++i) {
    if (kClassNames[i] && std::string(kClassNames[i]) == "idle") {
      idle_idx = i;
      break;
    }
  }
  out_scores[idle_idx] = 1.0f;
}

} // namespace tinyml_model
