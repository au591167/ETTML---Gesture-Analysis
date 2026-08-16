# TinyML Gesture Reader

> Gestusbaseret styring af en blackjack-simulation  
> Particle Photon 2 + ADXL343  
> Erik Kjær Klint · ETTML-01

![Fysisk prototype](../Report/src/img/Circuit.jpg)

---

# Demo: bevægelse bliver til en kommando

![Gestusser, kommandoer og RGB-feedback](assets/gesture-command-map.png)

**Demo:** `STATUS` → `MODE LIVE` → gestus → `EVENT` + RGB

> Hele inferencen kører lokalt på Photon 2.

---

# Problem, scope og kursuskrav

## Problem

Kan en lille embedded model skelne mellem fem accelerometerbaserede tilstande?

## Scope

Gestusinterfacet og kommandoerne – ikke et komplet blackjack-spil.

## Centrale krav

- Photon 2 og lokal sensor
- egne indsamlede og labellede data
- preprocessing og ML-klassifikation
- lokal inference og observerbart output

> **Stop 1:** Problem og afgrænsning er etableret.

---

# Hardware og dataflow

![Systemets dataflow](assets/system-dataflow.png)

`400 Hz = 2,5 ms mellem samples`

---

# Dataindsamling som iterativ proces

## Fra 50 Hz til 400 Hz

- 50 Hz gav 20 ms mellem samples og kunne overse hurtige taps.
- 400 Hz gav 2,5 ms mellem samples.
- Kvalitetskontrol afviste blandt andet forkert tap count og bevægelse under idle.

## Endeligt deploy-datasæt

- 25 accepterede optagelser
- fem per klasse
- én bruger og én slutsession

![Dataindsamling fra sensor til CSV](assets/data-acquisition-overview.png)

---

# Fra tidsserie til 28 features

![Feature pipeline](assets/feature-pipeline.png)

> Lille og forklarligt modelinput – men noget tidslig information går tabt.

> **Stop 2:** De rå signaler er nu blevet til modelinput.

---

# StandardScaler og MLP

![MLP-arkitektur](assets/mlp-architecture.png)

- Scalerens `μ` og `σ` læres kun fra træningsdata.
- Backpropagation bruges under træning i Python.
- Photon 2 udfører kun forward-pass.

---

# Fra Python-model til stabil handling

![Deployment og beslutningsflow](assets/deployment-decision-flow.png)

- Samme preprocessing og featureorden i Python og C++.
- ML klassificerer bevægelsesmønstret.
- Regler stabiliserer den brugeroplevede handling.

---

# Embedded runtime uden blokering

![Sliding window og stride](assets/sliding-window-timeline.png)

## Tre driftsformer

- `DEBUG`: diagnostik
- `TRAINING`: guidet dataindsamling
- `LIVE`: events og RGB-feedback

## Non-blocking firmware

LED, sampling, serial og inference drives som kooperative tilstande uden lange `delay()`-kald.

> **Stop 3:** Den implementerede embedded kæde er forklaret.

---

# Offline resultater – og deres usikkerhed

![Confusion matrix](../Report/src/img/confusion_matrix.png)

| Metric | Resultat |
|---|---:|
| Accuracy | 80 % = 4 af 5 |
| Macro precision | 70,0 % |
| Macro recall | 80,0 % |
| Macro F1 | 73,3 % |
| 5-fold cross-validation | 76 % |

`tap1` blev forvekslet med `tap2`.

> Én fejl ændrer test-accuracy med 20 procentpoint.

---

# Konklusion: deployment virker, generalisering er åben

## Dokumenteret

- lokal end-to-end-inference på Photon 2
- 345 µs mean og 364 µs max per forward-pass
- 27.950 B flash og 46.686 B RAM
- 0 sensor read errors i den registrerede LIVE-kontrol
- fysisk verificeret `EVENT` og RGB-feedback

## Ikke dokumenteret

- robusthed for nye personer, monteringer og situationer
- stabil brugeruafhængig accuracy
- energiforbrug

## Næste vigtigste eksperiment

Hold en hel ny bruger eller optagesession blindt ude som testsæt.

> **Stop 4:** En fungerende prototype med begrænset evidens for generalisering.

---

# Backup – ét, to og tre taps i rå data

![Sammenligning af tap1, tap2 og tap3](assets/tap-count-comparison.png)

---

# Backup – automatisk kvalitetskontrol

![Godkendt og afvist tap-optagelse](assets/quality-control-comparison.png)

---

# Backup – alle fem klasser

![Accelerometersignaler for alle fem gestusklasser](../Report/src/img/gesture_signals.png)

---

# Backup – hvorfor sampling blev hævet

![Illustration af 50 Hz kontra 400 Hz](assets/sampling-50-vs-400.png)

---

# Backup – hardwareforbindelsen

![Photon 2 og ADXL343 over I2C](assets/hardware-wiring.png)

---

# Backup – sporbarhed til kursuskrav

![Kursuskrav og konkret projektevidens](assets/requirements-traceability.png)

---

# Backup – de syv features

![Featuredefinitioner og formler](assets/seven-features.png)

---

# Backup – StandardScaler

![StandardScaler før og efter](assets/standard-scaler-concept.png)

---

# Backup – beregningen i en neuron

![Vægtet sum, bias og ReLU](assets/neuron-calculation.png)

---

# Backup – træning kontra inference

![Træning i Python og inference i C++](assets/training-vs-inference.png)

---

# Backup – train/test og cross-validation

![Datasplit og femfolds-cross-validation](assets/dataset-split-cv.png)

---

# Backup – cross-validation-fejl per klasse

![Reproduceret cross-validation confusion matrix](assets/cv-confusion-matrix.png)

---

# Backup – classification metrics

![Precision, recall og F1](assets/classification-metrics.png)

---

# Backup – evidensgrænsen

![Dokumenteret og ikke dokumenteret](assets/evidence-boundary.png)

---

# Backup – valg af kilder

![Kildetype efter påstand](assets/source-selection.png)
