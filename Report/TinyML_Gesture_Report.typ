#set document(title: "TinyML Gesture Reader for Blackjack Decision Support (Simulation)")
#set text(lang: "en")
#set page(numbering: "1")

#align(center)[
  #text(size: 1.6em, weight: "bold")[TinyML Gesture Reader for Blackjack Decision Support (Simulation)]
  
  #v(0.8em)
  Course: ETTML-01 Tiny Machine Learning\
  Student: [Your Name]\
  Date: [Submission Date]\
  Platform: Particle Photon 2 + ADXL343\
  Project Type: Embedded TinyML Classification System
]

#pagebreak()

#outline(title: [Table of Contents])

#pagebreak()

= Abstract
This report presents the theoretical basis for a TinyML gesture recognition system implemented on embedded hardware, framed as a general gesture reader with a blackjack-oriented demo interface. The purpose is to map recognized hand gestures to simulated blackjack decisions without requiring a full game engine backend. In scope, gesture semantics are defined as: one tap (stand), two taps (hit), lateral shake (split), and three taps (exit).

From a TinyML perspective, the project is situated at the intersection of machine learning, signal processing, and low-power embedded systems. According to the course framing, TinyML emphasizes inference near the data source on microcontrollers with constrained memory and energy budgets, often yielding lower latency and lower communication cost than cloud-dependent pipelines. This constraint-driven context motivates compact model design, disciplined preprocessing, and explicit optimization trade-offs.

The theoretical workflow follows standard supervised classification principles for time-series sensor data: acquisition, labeling, preprocessing (including windowing and scaling), model selection, and deployment-aware evaluation. The report’s early sections therefore focus on conceptual foundations—problem framing, requirement logic, and architecture rationale—rather than implementation details or measured outcomes.

= 1. Introduction
Tiny Machine Learning (TinyML) concerns the deployment of machine learning methods on highly resource-constrained embedded devices. In practical terms, this means operating under tight limits in memory, compute throughput, and power, while still producing dependable real-time predictions. The course material frames this as edge intelligence: pushing computation close to the data source to reduce latency, preserve privacy, and avoid the energy and bandwidth overhead of transmitting raw streams.

Within this context, gesture recognition is a representative TinyML problem because accelerometer signals are temporal, noisy, and user-dependent. Traditional rule-based programming can encode simple thresholds, but becomes brittle when gesture execution varies in speed, amplitude, or orientation. Supervised learning methods are therefore theoretically appropriate: they model statistical regularities in labeled examples and generalize to unseen executions when data coverage and preprocessing are sufficient.

Machine learning theory from the referenced literature further supports this framing. A standard supervised pipeline requires (1) representative labeled data, (2) suitable features or sequence representation, (3) a model class matched to complexity constraints, and (4) evaluation procedures that separate training behavior from generalization behavior. Core concerns include overfitting versus underfitting, noise robustness, and metric selection beyond raw accuracy (for instance, class-wise precision/recall and confusion structure).

This project adopts that foundation in an embedded interaction scenario: a general TinyML gesture reader whose immediate demonstration target is blackjack decision support in simulation form. The emphasis is therefore on reliable classification and low-latency response logic rather than full game-state reasoning.

= 2. Project Description
== 2.1 Problem Context
Human-machine interaction on microcontroller systems is often limited to fixed mechanical controls. Gesture-based interaction offers a more natural and compact alternative but introduces classification uncertainty because inertial signals are affected by user variability and environmental noise. In TinyML terms, the problem is not merely recognizing patterns, but doing so under constrained hardware budgets with predictable latency.

For this reason, the project is positioned as a classification problem over short temporal windows of tri-axial accelerometer data. The key theoretical challenge is separability: selected gesture classes should be sufficiently distinct in signal space after preprocessing so that a compact embedded model can maintain stable inference quality.

== 2.2 Project Goal
The project goal is to define and demonstrate a deployable TinyML gesture interface that maps recognized classes to blackjack decision actions in a simulation-style interaction loop. The design intentionally excludes a full blackjack engine backend; instead, recognized commands are treated as control intents for demo responses.

This goal aligns with course expectations for an embedded artifact: local sensing, model-based prediction, and observable output behavior on Photon 2.

== 2.3 Gesture Vocabulary
Within current scope, the command mapping is:
- 1 tap: Stand
- 2 taps: Hit
- Shake (left-right): Split
- 3 taps: Exit

These labels are treated as class outcomes in a supervised setting, typically with an additional idle/non-gesture concept considered during dataset and decision-threshold design to control false triggers.

== 2.4 Deliverable Summary
At the theory level, the intended artifact combines:
- Embedded sensing of motion signals
- Supervised gesture classification
- Real-time command mapping for blackjack-oriented simulation behavior
- Design rationale grounded in TinyML constraints and model evaluation theory

== 2.5 Scope and Interaction Mapping
The present project scope is a blackjack decision-support simulation interface, not a full blackjack game engine. Accordingly, the TinyML subsystem is responsible for reliable gesture-to-command mapping rather than game-state computation. The interaction mapping is defined as: one tap (stand), two taps (hit), lateral shake (split), and three taps (exit). This constrained scope supports clearer verification of classification behavior under embedded limits and aligns with course emphasis on demonstrable sensing, inference, and output integration.

= 3. Requirements Analysis
This section links theoretical requirements to course constraints and machine learning fundamentals.

== 3.1 Functional Requirements
1. Local sensor acquisition must provide a time-series stream suitable for gesture inference.
2. The system must output class predictions (classification, not regression).
3. The ML component must be data-driven and trained on collected labeled examples, not only fixed rules.
4. Labeling must be coupled to metadata discipline (sampling assumptions, format consistency), since generalization depends on data quality and representativeness.
5. Predicted classes must map to externally observable actions in the simulation interface.

== 3.2 Non-Functional Requirements
1. Deployment target is Photon 2, imposing memory/latency constraints on model and preprocessing.
2. Reproducibility and shareability are required at project level (data/software/documentation organization).
3. Runtime behavior should prioritize responsiveness and stability in interactive use.
4. Theoretical quality criteria include robustness to execution variation and manageable false-positive behavior in non-intent periods.

== 3.3 Constraints
1. Embedded resource ceilings constrain model family and feature dimensionality.
2. Gesture ambiguity can produce overlap between classes, requiring class-definition discipline.
3. Data mismatch risk exists if training recordings are not representative of live usage style.
4. Timeline constraints prioritize a reliable demonstration pipeline over broad feature expansion.

= 4. System Design
== 4.1 High-Level Architecture
A TinyML gesture interface can be described in four conceptual layers:
1. Sensing layer: tri-axial acceleration acquisition.
2. Signal representation layer: preprocessing that makes samples comparable across trials.
3. Inference layer: compact classifier producing class posteriors or scores.
4. Interaction layer: command mapping to blackjack simulation responses (stand/hit/split/exit).

== 4.2 Dataflow
The theoretical dataflow is:
1. Continuous sampling at fixed cadence.
2. Temporal segmentation into analysis windows.
3. Window-level transformation (for example scaling and optional handcrafted features).
4. Model inference on each window.
5. Decision logic (e.g., thresholding/smoothing) for stability before command emission.

This structure reflects standard sequence-classification practice from ML literature, where preprocessing consistency between training and inference paths is critical.

== 4.3 Hardware Design
From a theory standpoint, hardware selection follows adequacy and constraint principles:
- Sensor modality must capture discriminative motion content for chosen gestures.
- MCU resources must accommodate inference and buffering.
- Optional local feedback channels support interpretability in interactive demos.

== 4.4 Communication Protocol
For simulation integration, output can be abstracted as compact class events. The protocol design principle is low overhead and deterministic parsing, suitable for real-time command loops where each event represents one inferred decision intent.

== 4.5 Design Choices and Rationale
1. Accelerometer-only sensing reduces hardware complexity while retaining sufficient signal richness for tap/shake class structures.
2. On-device inference matches TinyML goals: low latency, local autonomy, and reduced dependence on remote compute.
3. Compact model preference reflects embedded constraints and bias-variance balance under finite datasets.
4. Blackjack simulation scope provides a clear, testable interaction mapping while avoiding backend complexity not required by current objectives.

== 4.6 Design Targets and Runtime Strategy
To satisfy responsiveness and stability under Photon 2 constraints, the design follows a fixed-rate time-series inference strategy. Conceptually, accelerometer data is sampled at a constant cadence and segmented into short overlapping windows so that decisions can be produced frequently without requiring heavy models. A lightweight feature-based classifier is prioritized as the first deployment candidate because it typically offers stronger interpretability and lower runtime cost on MCU targets than higher-complexity sequence networks. To improve interaction reliability, the decision layer includes confidence gating and temporal stabilization (for example short-horizon smoothing/majority logic and debounce intervals) so isolated noisy predictions are less likely to trigger unintended commands.

= 5. Implementation
== 5.1 Data Acquisition Implementation
== 5.2 Dataset and Labeling Strategy
== 5.3 Preprocessing
== 5.4 Model Training
== 5.5 Model Optimization and Deployment
== 5.6 Embedded Firmware Integration
== 5.7 LED Output Mapping Example
== 5.8 Guided Continuous Data Collection
To improve data consistency and reduce labeling friction during practical sessions, the implementation plan includes a guided continuous capture mode. In this mode, firmware indicates the expected gesture class before each trial and streams raw accelerometer samples over serial while the host logger runs continuously. Trial acceptance is explicitly signaled by firmware, allowing the host to persist only validated recordings and discard failed attempts automatically. This creates a tighter data-quality loop than purely manual start/stop recording and supports more repeatable class-balanced collection in limited lab time.

The operator guidance strategy uses dedicated cue LEDs to indicate the expected gesture class (tap1, tap2, tap3, shake_lr), while RGB status feedback communicates acquisition state (ready, accepted, rejected). Conceptually, this human-in-the-loop protocol improves adherence to class intent and helps separate capture-time quality control from later model training. Training itself remains batch-oriented after collection blocks, which preserves reproducibility and keeps the runtime complexity on Photon 2 focused on inference rather than online learning.

== 5.9 Implementation Decision Log (Preparation to Execution)
Implementation was organized as an explicit action-to-decision pipeline to reduce integration risk under schedule pressure. First, model development was stabilized before full hardware dependency by validating training/export scaffolds and documenting reproducible command-level execution steps. Second, a guided capture protocol was selected over ad-hoc manual logging to improve label quality and trial consistency. Third, deployment readiness was formalized through a host-to-firmware checklist so preprocessing parity, class mapping integrity, and output behavior can be verified in a deterministic sequence.

From an engineering process perspective, this structure separates concerns into phases: pre-hardware software readiness, hardware bring-up, and post-wire retraining/deployment. The rationale is to avoid idle time while waiting for wiring completion and to preserve traceability for exam discussion and report defensibility. All operational steps, decisions, and outcomes are tracked in dedicated implementation documentation so that progress can be audited and repeated without relying on undocumented manual procedures.

= 6. Test and Verification
== 6.1 Test Objectives
== 6.2 Test Categories
== 6.3 Metrics
== 6.4 Acceptance Criteria
== 6.5 Result Tables

= 7. Discussion
== 7.1 Technical Reflection
== 7.2 Failure Modes
== 7.3 Mitigation

= 8. Conclusion

= 9. Future Work

= 10. Literature and Theory Basis

= 11. References

= Appendix A – Practical Build Checklist

= Appendix B – Oral Demo Script (Short)
