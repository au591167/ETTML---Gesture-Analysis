# Reference Notes (Project-Relevant Only)
## TinyML Gesture Interface – Source Mapping for Report + Oral Exam

This file helps you:
1) cite relevant theory cleanly in the report, and  
2) revise key concepts likely to be asked in the oral exam.

---

## 1. Primary Course Sources (ETTML-01)

### 1.1 Semester/Exam Project Requirements
**Use for report sections:** Requirements Analysis, Methodology, Verification, Conclusion

Key points to reference:
- Must design an embedded artifact using **Particle Photon 2**.
- Must collect and label your **own sensor dataset**.
- Must implement ML/AI model on embedded target.
- Report minimum sections required:
  - Introduction
  - Project Description
  - Requirements Analysis
  - System Design
  - Implementation
  - Test/Verification
  - Conclusion
- Report target length: approximately 20 pages.
- Oral exam includes short demo + technical presentation.
- Data should include metadata and be stored in suitable formats (e.g., CSV).

**How to cite in report text (example):**
> The project design follows the ETTML semester exam requirements for Photon 2-based embedded ML, self-collected labeled sensor data, and report structure.

---

### 1.2 Hardware Page
**Use for report sections:** System Design, Hardware Choice, Discussion

Relevant points:
- Course hardware focus includes Photon 2.
- Motion sensing context with accelerometer/IMU is directly aligned.
- TinyML edge deployment on modern low-power MCU platforms is emphasized.

**Use in oral answer:**
- “I selected ADXL343 motion sensing because it aligns with course hardware direction and supports a realistic TinyML motion classification problem.”

---

### 1.3 Software Page
**Use for report sections:** Implementation, Toolchain, Reproducibility

Relevant points:
- Python ecosystem for data analysis and ML.
- VSCode + Particle Workbench for Photon 2 firmware workflow.
- Embedded ML tool options discussed in course: EMLearn, AIfES, TinyML workflows.
- Iterative ML-ops style tuning/deployment mindset is encouraged.

**Use in oral answer:**
- “I followed an iterative train-deploy-measure loop, consistent with TinyML workflow practice.”

---

### 1.4 Welcome + Literature Pages
**Use for report sections:** Introduction, Motivation, Relevance to TinyML

Relevant points:
- TinyML = ML + embedded systems + signal processing.
- Strong value of local processing: lower energy and latency.
- Course learning outcomes include data collection, model design/deployment, and constrained optimization.

**Use in oral answer:**
- “This project demonstrates exactly the TinyML value proposition: local inference with responsive behavior and reduced dependency on external compute.”

---

## 2. Project Description Source Notes
**File:** Project_Description_TinyML_Gesture_Interface_Provisio.txt  
**Use for report sections:** Project Description, Objectives, Scope, Expected Outcome

Extractable references:
- Gesture-based user interface objective.
- ADXL343-based acceleration classification in real time.
- Integration role with Provisio (command interface, not full prediction engine).
- Full TinyML pipeline expected: acquisition → preprocessing → training → deployment.
- Potential metrics: accuracy, latency, memory/resource use, robustness.

**Use in oral answer:**
- “This is intentionally scoped as an intelligent gesture interface component for Provisio, not the Provisio prediction engine itself.”

---

## 3. Book 1: Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (3rd ed.)
## Relevance for this project
Use as practical ML methodology foundation.

Suggested concept-level references (not chapter overloading):
- End-to-end ML project workflow
- Dataset preparation and split discipline
- Model evaluation and error analysis
- Overfitting control and regularization
- Deployment-minded model simplification

**What to quote/paraphrase in your report:**
- Proper training/validation/test separation is essential for trustworthy performance claims.
- Data preprocessing consistency between training and deployment is mandatory.
- Model complexity should match available data and hardware constraints.

**Oral exam quick-use points:**
- Why data split matters.
- Why confusion matrix is better than only reporting accuracy.
- Why simpler models can outperform complex models on constrained data/hardware.

---

## 4. Book 2: Machine Learning with PyTorch and Scikit-Learn
## Relevance for this project
Use as beginner-friendly conceptual reinforcement.

Project-relevant themes:
- Supervised learning for classification tasks.
- Training pipeline fundamentals.
- Feature scaling and preprocessing.
- Evaluation metrics (accuracy, confusion matrix, precision/recall mindset).
- Overfitting/bias-variance intuition.
- Iterative improvement approach.

**What to use in report framing:**
- Gesture recognition is a supervised multiclass classification problem.
- Robust evaluation requires class-level analysis, not just a single aggregate score.
- Preprocessing quality strongly affects model stability.

**Do not over-focus for this report:**
- Advanced NLP transformers / GAN / graph chapters (not relevant to your artifact scope).

---

## 5. Suggested In-Text Citation Anchors (Simple and Safe)
Use these short citation anchors in draft text:
- (ETTML Course, Semester Project Requirements)
- (ETTML Course, Hardware Module)
- (ETTML Course, Software Module)
- (Project Description: TinyML Gesture Interface for Provisio)
- (Géron, *Hands-On Machine Learning*, 3rd ed.)
- (Raschka et al., *Machine Learning with PyTorch and Scikit-Learn*)

---

## 6. Suggested Bibliography Entries (Draft)
> Replace with your preferred citation style (APA/IEEE/Harvard) before final submission.

1. ETTML-01 Tiny Machine Learning course materials (Welcome, Hardware, Software, Literature, Semester/Exam Project), Aarhus University Brightspace.  
2. Project Description – Tiny Machine Learning Gesture Interface for Provisio (local project document).  
3. Géron, A. *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*, 3rd Edition, O’Reilly.  
4. Raschka, S., Liu, Y., Mirjalili, V. *Machine Learning with PyTorch and Scikit-Learn*, Packt, 2022.

---

## 7. “If Asked Why These References?” (Oral Defense Line)
- Course documents define compliance requirements and grading scope.
- Project description defines exact system scope and objectives.
- Géron supports practical ML workflow and evaluation rigor.
- Raschka et al. supports conceptual clarity for classification, preprocessing, and model assessment.

This creates a coherent chain: **requirements → implementation method → evaluation rationale**.
