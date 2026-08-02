"""
Model export utility for Photon 2 integration.

Current implementation generates concrete firmware-facing C/C++ artifacts:
- Product/firmware/model_data.h
- Product/firmware/model_data.cpp
- Product/ml/artifacts/export_summary.json

This is a deterministic baseline export for integration readiness:
- It exports label map, feature metadata, and decision constants.
- It does not yet serialize trained model weights from sklearn.
- Firmware can compile against these artifacts and wire runtime inference adapter next.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_config(path: str = "Product/ml/config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute_feature_count(cfg: Dict[str, Any]) -> int:
    """
    stat_v1 uses 7 features per channel:
      mean, std, min, max, range, energy, zero_crossings
    channels: ax, ay, az (+ mag if enabled)
    """
    per_channel = 7
    channels = 3 + (1 if bool(cfg["preprocessing"]["use_magnitude_channel"]) else 0)
    return per_channel * channels


def sanitize_cpp_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate_header(cfg: Dict[str, Any], classes: List[str], feature_count: int) -> str:
    conf = cfg["decision_logic"]["confidence_threshold"]
    smooth = cfg["decision_logic"]["smoothing_windows"]
    debounce = cfg["decision_logic"]["debounce_ms"]

    class_enum: List[str] = []
    for i, c in enumerate(classes):
        token = c.upper().replace("-", "_")
        class_enum.append(f"  CLASS_{token} = {i}")

    class_enum_text = ",\n".join(class_enum)

    return f"""#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace tinyml_model {{

constexpr const char* kProjectName = "{sanitize_cpp_string(cfg["project"]["name"])}";
constexpr const char* kTargetMcu = "{sanitize_cpp_string(cfg["project"]["target_mcu"])}";
constexpr std::size_t kNumClasses = {len(classes)};
constexpr std::size_t kFeatureCount = {feature_count};

constexpr float kDecisionConfidenceThreshold = {float(conf):.6f}f;
constexpr std::uint32_t kDecisionDebounceMs = {int(debounce)}u;
constexpr std::size_t kDecisionSmoothingWindows = {int(smooth)}u;

enum GestureClass : std::int32_t {{
{class_enum_text}
}};

extern const char* const kClassNames[kNumClasses];
extern const char* const kCommandMap[kNumClasses];

/*
 * Placeholder inference API contract for firmware integration.
 * Replace implementation with real model runtime once model weights
 * serialization path is finalized.
 */
void model_init();
void model_infer(const float* features, std::size_t feature_count, float* out_scores, std::size_t out_len);

}} // namespace tinyml_model
"""


def generate_cpp(cfg: Dict[str, Any], classes: List[str], command_map: Dict[str, str]) -> str:
    class_names = ",\n".join([f'  "{sanitize_cpp_string(c)}"' for c in classes])
    command_names = ",\n".join(
        [f'  "{sanitize_cpp_string(command_map.get(c, "no_action"))}"' for c in classes]
    )

    return f"""#include "model_data.h"

namespace tinyml_model {{

const char* const kClassNames[kNumClasses] = {{
{class_names}
}};

const char* const kCommandMap[kNumClasses] = {{
{command_names}
}};

void model_init() {{
  // Placeholder: initialize embedded model runtime here.
}}

void model_infer(const float* /*features*/, std::size_t feature_count, float* out_scores, std::size_t out_len) {{
  // Placeholder deterministic baseline:
  // - validates expected feature length
  // - returns idle class with score 1.0 and others 0.0
  if (!out_scores || out_len < kNumClasses) {{
    return;
  }}

  for (std::size_t i = 0; i < out_len; ++i) {{
    out_scores[i] = 0.0f;
  }}

  if (feature_count != kFeatureCount) {{
    // Keep all zeros on mismatch as a safe fallback.
    return;
  }}

  // Prefer idle when available; otherwise first class.
  std::size_t idle_idx = 0;
  for (std::size_t i = 0; i < kNumClasses; ++i) {{
    if (kClassNames[i] && std::string(kClassNames[i]) == "idle") {{
      idle_idx = i;
      break;
    }}
  }}
  out_scores[idle_idx] = 1.0f;
}}

}} // namespace tinyml_model
"""


def main() -> None:
    cfg = load_config()
    out_dir = Path(cfg["export"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    firmware_dir = Path("Product/firmware")
    firmware_dir.mkdir(parents=True, exist_ok=True)

    classes = list(cfg["labels"]["classes"])
    command_mapping = dict(cfg["labels"]["command_mapping"])
    feature_count = compute_feature_count(cfg)

    header_text = generate_header(cfg, classes, feature_count)
    cpp_text = generate_cpp(cfg, classes, command_mapping)

    header_path = firmware_dir / "model_data.h"
    cpp_path = firmware_dir / "model_data.cpp"

    header_path.write_text(header_text, encoding="utf-8")
    cpp_path.write_text(cpp_text, encoding="utf-8")

    summary: Dict[str, Any] = {
        "project": cfg["project"]["name"],
        "target_mcu": cfg["project"]["target_mcu"],
        "model_family": cfg["model"]["family"],
        "classes": classes,
        "command_mapping": command_mapping,
        "preprocessing": cfg["preprocessing"],
        "features": cfg["features"],
        "decision_logic": cfg["decision_logic"],
        "firmware_artifacts": {
            "header": str(header_path).replace("\\", "/"),
            "source": str(cpp_path).replace("\\", "/"),
            "feature_count": feature_count,
        },
        "notes": [
            "Concrete firmware-facing C/C++ artifacts were generated.",
            "Current model_infer implementation is a placeholder adapter returning idle.",
            "Next step: serialize trained model parameters and replace placeholder inference.",
        ],
    }

    summary_path = out_dir / "export_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[OK] Wrote export summary: {summary_path}")
    print(f"[OK] Wrote firmware header: {header_path}")
    print(f"[OK] Wrote firmware source: {cpp_path}")
    print("[INFO] model_infer() is currently a deterministic placeholder (idle fallback).")
    print("[ROADMAP] Real trained-model runtime integration is a subsequent step.")


if __name__ == "__main__":
    main()
