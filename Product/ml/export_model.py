"""
Model export utility for Photon 2 integration.

This exporter trains a compact MLP on the configured dataset, fits a
StandardScaler, and serializes the real trained weights + scaler as C arrays
so the firmware can run actual on-device inference (not a placeholder).

Artifacts generated:
- Product/firmware/src/model_data.h
- Product/firmware/src/model_data.cpp  (real forward pass)
- Product/ml/artifacts/export_summary.json
- Product/ml/artifacts/scaler.json   (mean/std per feature, for parity checks)
- Product/ml/artifacts/model.pkl     (sklearn model, for reproducibility)
"""

from __future__ import annotations

import argparse
import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# Reuse the training pipeline.
from train import (
    load_config as train_load_config,
    load_raw_data,
    build_dataset,
    validate_class_coverage,
)


def load_config(path: str = "Product/ml/config.yaml") -> Dict[str, Any]:
    return train_load_config(path)


# Imports are checked explicitly so export cannot silently deploy a placeholder.
try:
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPClassifier

    HAS_SKLEARN = True
except Exception:  # pragma: no cover
    HAS_SKLEARN = False


def compute_feature_count(cfg: Dict[str, Any]) -> int:
    per_channel = 7
    channels = 3 + (1 if bool(cfg["preprocessing"]["use_magnitude_channel"]) else 0)
    return per_channel * channels


def sanitize_cpp_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def fmt_float_array(values) -> str:
    """Format a 1-d sequence of floats as a compact C float array literal.

    Ensures every value is a valid C++ float literal: integer-valued floats
    (e.g. zero-crossing counts like 22.0) MUST include a decimal point so the
    compiler parses them as floating literals (22f is invalid; 22.0f is not).
    """
    parts = []
    for v in values:
        s = f"{float(v):.10g}"
        if "." not in s and "e" not in s and "E" not in s:
            s += ".0"
        parts.append(s + "f")
    lines = []
    for i in range(0, len(parts), 8):
        lines.append("  " + ", ".join(parts[i : i + 8]) + ("," if i + 8 < len(parts) else ""))
    return "\n".join(lines)


def generate_header(cfg: Dict[str, Any], classes: List[str], feature_count: int, hidden: List[int]) -> str:
    conf = cfg["decision_logic"]["confidence_threshold"]
    smooth = cfg["decision_logic"]["smoothing_windows"]
    debounce = cfg["decision_logic"]["debounce_ms"]

    class_enum: List[str] = []
    for i, c in enumerate(classes):
        token = c.upper().replace("-", "_")
        class_enum.append(f"  CLASS_{token} = {i}")
    class_enum_text = ",\n".join(class_enum)

    layer_sizes = [feature_count] + list(hidden) + [len(classes)]
    layer_sizes_text = ",\n".join([f"  {n}" for n in layer_sizes])

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

// Neural network topology (fully connected, ReLU hidden, softmax output).
constexpr std::size_t kNumLayers = {len(layer_sizes)};
constexpr std::size_t kLayerSizes[kNumLayers] = {{
{layer_sizes_text}
}};

enum GestureClass : std::int32_t {{
{class_enum_text}
}};

extern const char* const kClassNames[kNumClasses];
extern const char* const kCommandMap[kNumClasses];

/*
 * Real inference API contract for firmware integration.
 * model_infer() applies the serialized scaler + MLP forward pass and
 * writes kNumClasses class scores into out_scores.
 */
void model_init();
void model_infer(const float* features, std::size_t feature_count, float* out_scores, std::size_t out_len);

}} // namespace tinyml_model
"""


def _layer_meta(coefs, intercepts):
    """Return per-layer (in_dim, out_dim, weight_offset, bias_offset) list."""
    layer_meta = []
    cum_weight = 0
    cum_bias = 0
    for idx, w in enumerate(coefs):
        w = np.asarray(w, dtype=np.float64)
        in_dim, out_dim = w.shape
        layer_meta.append((in_dim, out_dim, cum_weight, cum_bias))
        cum_weight += in_dim * out_dim
        cum_bias += out_dim
    return layer_meta, cum_weight, cum_bias


def generate_cpp(
    cfg: Dict[str, Any],
    classes: List[str],
    command_map: Dict[str, str],
    scaler_mean,
    scaler_scale,
    coefs,
    intercepts,
    hidden_layers: List[int],
) -> str:
    class_names = ",\n".join([f'  "{sanitize_cpp_string(c)}"' for c in classes])
    command_names = ",\n".join(
        [f'  "{sanitize_cpp_string(command_map.get(c, "no_action"))}"' for c in classes]
    )

    feature_count = compute_feature_count(cfg)
    dims = [feature_count] + list(hidden_layers) + [len(classes)]
    n_layers = len(dims)

    mean_text = fmt_float_array(scaler_mean)
    scale_text = fmt_float_array(scaler_scale)

    # Flatten weights row-major per layer, concatenated.
    flat_weights = []
    for w in coefs:
        w = np.asarray(w, dtype=np.float64)
        flat_weights.append(fmt_float_array(w.flatten(order="C")))
    weights_text = ",\n".join(f"  {fw}" for fw in flat_weights)

    flat_biases = []
    for b in intercepts:
        flat_biases.append(fmt_float_array(np.asarray(b, dtype=np.float64)))
    biases_text = ",\n".join(f"  {fb}" for fb in flat_biases)

    layer_meta, total_weights, total_biases = _layer_meta(coefs, intercepts)
    meta_text = ",\n".join(
        f"  {{ {in_d}, {out_d}, {w_off} }}"
        for in_d, out_d, w_off, _b_off in layer_meta
    )
    bias_offsets_text = ",\n".join(f"  {b_off}" for _i, _o, _w, b_off in layer_meta)

    return f"""#include "model_data.h"
#include <math.h>

namespace tinyml_model {{

const char* const kClassNames[kNumClasses] = {{
{class_names}
}};

const char* const kCommandMap[kNumClasses] = {{
{command_names}
}};

// ---- Serialized inference parameters (generated by export_model.py) ----

// StandardScaler: (feature - mean) / scale
static const float kScalerMean[kFeatureCount] = {{
{mean_text}
}};
static const float kScalerScale[kFeatureCount] = {{
{scale_text}
}};

// MLP weights flattened row-major per layer, concatenated.
// Layer l spans kWeightsFlat[kWeightOffset[l] .. +inDim*outDim).
constexpr std::size_t kNumLayersWs = {n_layers - 1};
static const std::size_t kWeightMeta[kNumLayersWs][3] = {{
{meta_text}
}};
static const std::size_t kBiasOffset[kNumLayersWs] = {{
{bias_offsets_text}
}};
static const float kWeightsFlat[{total_weights}] = {{
{weights_text}
}};
static const float kBiasesFlat[{total_biases}] = {{
{biases_text}
}};

static void relu_inplace(float* v, std::size_t n) {{
  for (std::size_t i = 0; i < n; ++i) {{
    if (v[i] < 0.0f) v[i] = 0.0f;
  }}
}}

void model_init() {{
  // No dynamic allocation; parameters are static const. Nothing to do.
}}

void model_infer(const float* features, std::size_t feature_count, float* out_scores, std::size_t out_len) {{
  if (!out_scores || out_len < kNumClasses) {{
    return;
  }}
  for (std::size_t i = 0; i < out_len; ++i) {{
    out_scores[i] = 0.0f;
  }}
  if (!features || feature_count != kFeatureCount) {{
    return;
  }}

  // Static buffers sized for max(kFeatureCount, 64) activations.
  static float act[64];
  static float next[64];

  // 1) Standardize input features.
  for (std::size_t i = 0; i < kFeatureCount; ++i) {{
    float denom = kScalerScale[i] > 1e-9f ? kScalerScale[i] : 1.0f;
    act[i] = (features[i] - kScalerMean[i]) / denom;
  }}

  // 2) Forward through each layer (ReLU on hidden, none on output).
  for (std::size_t li = 0; li < kNumLayersWs; ++li) {{
    const std::size_t inDim = kWeightMeta[li][0];
    const std::size_t outDim = kWeightMeta[li][1];
    const std::size_t wOff = kWeightMeta[li][2];
    const std::size_t bOff = kBiasOffset[li];
    for (std::size_t o = 0; o < outDim; ++o) {{
      float acc = kBiasesFlat[bOff + o];
      for (std::size_t i = 0; i < inDim; ++i) {{
        acc += act[i] * kWeightsFlat[wOff + i * outDim + o];
      }}
      next[o] = acc;
    }}
    for (std::size_t i = 0; i < outDim; ++i) {{
      act[i] = next[i];
    }}
    if (li < kNumLayersWs - 1) {{
      relu_inplace(act, outDim);
    }}
  }}

  // 3) Softmax over the kNumClasses final logits.
  float maxv = act[0];
  for (std::size_t i = 1; i < kNumClasses; ++i) {{
    if (act[i] > maxv) maxv = act[i];
  }}
  float sum = 0.0f;
  for (std::size_t i = 0; i < kNumClasses; ++i) {{
    float e = expf(act[i] - maxv);
    act[i] = e;
    sum += e;
  }}
  if (sum > 1e-12f) {{
    for (std::size_t i = 0; i < kNumClasses; ++i) {{
      out_scores[i] = act[i] / sum;
    }}
  }}
}}

}} // namespace tinyml_model
"""


def _train_and_export(cfg: Dict[str, Any]):
    """Train the MLP on the current dataset and return (payload, model, le)."""
    raw_dir = Path(cfg["data"]["raw_dir"])
    file_glob = cfg["data"]["file_glob"]

    df = load_raw_data(raw_dir, file_glob)
    required = set(cfg["data"]["expected_columns"])
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    X, y = build_dataset(cfg, df)
    if len(X) == 0:
        raise ValueError(
            "No training windows produced. Add recordings or reduce window_seconds/sample_rate_hz."
        )
    validate_class_coverage(cfg, y)

    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    class_counts = np.bincount(y_enc)
    min_class_count = int(class_counts.min()) if len(class_counts) > 0 else 0
    stratify_arg = y_enc if min_class_count >= 2 else None

    X_train, _X_test, y_train, _y_test = train_test_split(
        X,
        y_enc,
        test_size=cfg["evaluation"]["test_size"],
        random_state=cfg["evaluation"]["random_state"],
        stratify=stratify_arg,
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)

    mlp_cfg = cfg["model"]["mlp"]
    model = MLPClassifier(
        hidden_layer_sizes=tuple(mlp_cfg["hidden_layers"]),
        activation=mlp_cfg["activation"],
        max_iter=mlp_cfg["epochs"],
        batch_size=mlp_cfg["batch_size"],
        learning_rate_init=mlp_cfg["learning_rate"],
        random_state=cfg["evaluation"]["random_state"],
    )
    model.fit(X_train_s, y_train)

    classes = list(cfg["labels"]["classes"])
    # sklearn orders classes alphabetically; map sklearn outputs -> config class indices.
    skl_classes = list(le.classes_)
    skl_to_cfg = [classes.index(c) for c in skl_classes]

    coefs = [np.asarray(c, dtype=np.float64) for c in model.coefs_]
    intercepts = [np.asarray(b, dtype=np.float64) for b in model.intercepts_]

    # Expand the final layer from (hidden, n_actual_classes) to
    # (hidden, len(classes)) so outputs align with kClassNames. Classes absent
    # from the data (e.g. idle with no windows) get zero weights/biases.
    last_w = coefs[-1]     # (hidden, n_actual)
    last_b = intercepts[-1]  # (n_actual,)
    n_hidden_last = last_w.shape[0]
    full_w = np.zeros((n_hidden_last, len(classes)), dtype=np.float64)
    full_b = np.zeros((len(classes),), dtype=np.float64)
    for skl_idx, cfg_idx in enumerate(skl_to_cfg):
        full_w[:, cfg_idx] = last_w[:, skl_idx]
        full_b[cfg_idx] = last_b[skl_idx]
    coefs[-1] = full_w
    intercepts[-1] = full_b

    payload = {
        "scaler_mean": scaler.mean_,
        "scaler_scale": scaler.scale_,
        "coefs": coefs,
        "intercepts": intercepts,
        "hidden_layers": list(mlp_cfg["hidden_layers"]),
        "classes": classes,
        "sklearn_classes": skl_classes,
        "n_samples": int(len(X)),
        "n_features": int(X.shape[1]),
    }
    return payload, model, le


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and atomically export the TinyML model.")
    parser.add_argument("--config", default="Product/ml/config.yaml", help="Path to YAML config")
    args = parser.parse_args()
    cfg = load_config(args.config)
    out_dir = Path(cfg["export"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

# Particle project source root (where main.cpp lives). The Particle CLI
    # compiles all .cpp under the project dir recursively, so the model files
    # must live ONLY in src/ to avoid duplicate-symbol link errors.
    firmware_dir = Path("Product/firmware/src")
    firmware_dir.mkdir(parents=True, exist_ok=True)

    classes = list(cfg["labels"]["classes"])
    command_mapping = dict(cfg["labels"]["command_mapping"])
    feature_count = compute_feature_count(cfg)

    if not HAS_SKLEARN:
        raise RuntimeError("numpy/scikit-learn are required; existing artifacts were not changed.")

    # Complete training and serialization in memory before touching deployed files.
    payload, model, le = _train_and_export(cfg)
    hidden = payload["hidden_layers"]
    header_text = generate_header(cfg, classes, feature_count, hidden)
    cpp_text = generate_cpp(
        cfg, classes, command_mapping, payload["scaler_mean"], payload["scaler_scale"],
        payload["coefs"], payload["intercepts"], hidden,
    )
    scaler_json = {
        "mean": [float(x) for x in payload["scaler_mean"]],
        "scale": [float(x) for x in payload["scaler_scale"]],
        "feature_count": feature_count,
    }
    notes = [
        "Real MLP weights + StandardScaler serialized for firmware.",
        "model_infer() performs a real forward pass (scale + MLP + softmax).",
    ]

    header_path = firmware_dir / "model_data.h"
    cpp_path = firmware_dir / "model_data.cpp"

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
        "real_inference": True,
        "notes": notes,
    }

    summary_path = out_dir / "export_summary.json"

    # Stage every output first. os.replace is atomic per file, preventing truncated
    # artifacts; no deployed file is touched if training or staging fails.
    outputs = {
        header_path: header_text.encode("utf-8"),
        cpp_path: cpp_text.encode("utf-8"),
        out_dir / "scaler.json": json.dumps(scaler_json, indent=2).encode("utf-8"),
        out_dir / "model.pkl": pickle.dumps(model),
        out_dir / "label_encoder.pkl": pickle.dumps(le),
        summary_path: json.dumps(summary, indent=2).encode("utf-8"),
    }
    staged = []
    try:
        for target, data in outputs.items():
            fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((Path(temp_name), target))
        for temp_path, target in staged:
            os.replace(temp_path, target)
    finally:
        for temp_path, _target in staged:
            if temp_path.exists():
                temp_path.unlink()

    print(f"[OK] Wrote export summary: {summary_path}")
    print(f"[OK] Wrote firmware header: {header_path}")
    print(f"[OK] Wrote firmware source: {cpp_path}")
    print(f"[OK] Trained on {payload['n_samples']} windows, {payload['n_features']} features.")
    print("[OK] model_infer() now runs a REAL MLP forward pass.")


if __name__ == "__main__":
    main()
