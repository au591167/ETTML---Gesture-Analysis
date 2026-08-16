# Forberedelse til ETTML-præsentationen

## Formål

Præsentationen skal vise en sammenhængende teknisk historie fra problem til fysisk verificeret prototype. Den skal ikke genfortælle rapporten. Hvert slide skal besvare ét naturligt spørgsmål og skabe kontekst for eventuelle uddybninger.

## Anbefalet format

- **Demo:** højst 5 minutter og planlagt til cirka 3:30–4:00.
- **Teknisk præsentation:** kernespor på cirka 11–13 minutter.
- **Spørgsmålszoner:** fire naturlige overgange, ikke kunstige forsinkelser.
- **Slides:** 11 kerneslides inklusive titel og demo.
- **Backup:** detaljer om matematik, kode og pensum ligger på tabletten, ikke som teksttunge slides.

Den præcise tilladte præsentationstid fremgår ikke af den lokale projektbrief. Oplægget skal derfor kunne skaleres ved at forkorte slide 5, 7 og 10.

## Den røde tråd

`behov → fysisk bevægelse → måledata → brugbare features → model → embedded beslutning → observerbart output → evidens → begrænsning`

---

## Slide 1 – TinyML Gesture Reader

**Hovedbudskab:** Jeg har bygget en komplet lokal TinyML-kæde på en Photon 2.

**På slidet:**

- Projektets titel.
- “Gestusbaseret styring af en blackjack-simulation”.
- Particle Photon 2 + ADXL343.
- Stort prototypefoto.

**Sig kort:**

> “Projektet undersøger, om en lille embedded model kan omsætte fem accelerometerbaserede gestusser til kommandoer. Hele inferencen kører lokalt på en Particle Photon 2.”

**Visual:** `../Report/src/img/Circuit.jpg`.

**Tid:** 30–40 sekunder.

---

## Slide 2 – Fysisk demo

**Hovedbudskab:** Systemet fungerer fra virkelig bevægelse til lokal kommando og LED-feedback.

**På slidet:**

- En enkel gestusoversigt:
  - tap1 → stand;
  - tap2 → hit;
  - tap3 → exit;
  - shake → split;
  - idle → ingen handling.
- Ingen teknisk teori endnu.

**Demoforløb:**

1. Vis fysisk hardware.
2. Kør `STATUS` og peg på sensor, mode og window state.
3. Skift til `MODE LIVE`.
4. Vis én sikker tap-gestus og én shake.
5. Peg på `EVENT`, kommando og LED-feedback.
6. Stop demonstrationen, mens den stadig virker.

**Fallback ved hardwareproblem:**

> “Den levende demo reagerer ikke stabilt lige nu. Den registrerede verifikation viste korrekt build, flash, sensorstatus og events; jeg fortsætter med den tekniske kæde og viser de målte resultater senere.”

**Tid:** Planlagt 3:30–4:00; absolut maksimum 5:00.

---

## Slide 3 – Problem, scope og krav

**Hovedbudskab:** Det er en femklasseklassifikationsopgave og ikke et komplet blackjack-spil.

**På slidet:**

- Problemformuleringen i én linje.
- Fem klasser.
- Tre vigtigste kursuskrav: egen sensor, egne labels, lokal ML-inference.
- Scope-boks: “Gestusinterface – ikke spilimplementering”.

**Sig kort:**

> “Outputtet er én af fem diskrete kategorier, så opgaven er klassifikation. Projektets scope er selve gestusinterfacet. Det opfylder kursets centrale krav gennem en lokal sensor, egne labellede data, preprocessing, en trænet model og observerbart output.”

**Faglig kobling i noterne:** klassifikation, regression, anomaly detection, ML kontra regler og kursuskrav.

**Tid:** 60 sekunder.

### Spørgsmålszone 1

Kort overgang:

> “Det var problemet og afgrænsningen. Nu følger jeg dataens vej gennem systemet.”

---

## Slide 4 – Hardware og dataflow

**Hovedbudskab:** Systemet forbinder fysisk bevægelse med en reproducerbar beregningskæde.

**På slidet:**

- Vandret dataflow:
  `ADXL343 → 4 s / 1.600 samples → 28 features → scaler + MLP → filter → EVENT + RGB`.
- Lille foto eller markering af Photon 2 og ADXL343.
- `400 Hz = 2,5 ms mellem samples`.

**Sig kort:**

> “Accelerometeret måler X, Y og Z ved 400 Hz. Fire sekunder giver 1.600 samples. De komprimeres til 28 features, skaleres og klassificeres. Til sidst stabiliserer regler outputtet, før en kommando udsendes.”

**Faglig kobling i noterne:** accelerometer, I2C, sampling, Nyquist, vinduer og edge inference.

**Visual:** `assets/system-dataflow.svg`.

**Tid:** 75 sekunder.

---

## Slide 5 – Dataindsamling som iterativ proces

**Hovedbudskab:** Sampling og datakvalitet blev ændret ud fra observerede fejl.

**På slidet:**

- `50 Hz → hurtige taps kunne overses → 400 Hz`.
- 25 accepterede optagelser, fem per klasse.
- Én bruger og én slutsession tydeligt markeret som begrænsning.
- Et lille udsnit af gestussignalerne.

**Sig kort:**

> “De første data ved 50 Hz havde 20 millisekunder mellem samples og kunne overse hurtige taps. Derfor blev sampling øget til 400 Hz. Den endelige session er balanceret, men meget lille: fem optagelser per klasse fra én person.”

**Faglig kobling i noterne:** labels, metadata, klassebalance, dataset bias, repræsentativitet og MLOps-iteration.

**Visual:** `assets/data-acquisition-overview.png`. De detaljerede klasseplots bruges som backup.

**Tid:** 75–90 sekunder.

---

## Slide 6 – Fra tidsserie til 28 features

**Hovedbudskab:** Feature engineering gør rå tidsserier små og forklarlige nok til en embedded model.

**På slidet:**

- X, Y, Z → mean removal.
- Magnitude: `√(x² + y² + z²)`.
- Fire kanaler × syv features = 28.
- Featurelisten i lille, men læsbar form.

**Sig kort:**

> “Gennemsnittet fjernes for at reducere statisk offset og orientering. Derefter beregnes magnitude. For hver af de fire kanaler beregnes syv statistiske features. Det komprimerer 4.800 rå XYZ-målinger plus 1.600 afledte magnitudeværdier til 28 inputtal, men mister noget tidslig information.”

**Faglig kobling i noterne:** preprocessing, magnitude, standardafvigelse, energi, peaks, tidsdomæne og feature engineering.

**Visual:** `assets/feature-pipeline.svg`.

**Tid:** 90 sekunder.

### Spørgsmålszone 2

Kort overgang:

> “Nu er de rå signaler blevet til modelinput. Næste del er, hvordan modellen lærer og bliver flyttet til Photon 2.”

---

## Slide 7 – StandardScaler og MLP

**Hovedbudskab:** Modellen er lille, men udfører rigtig ikke-lineær femklasseklassifikation.

**På slidet:**

- `z = (x − μ) / σ`.
- Netværket `28 → 32 ReLU → 16 ReLU → 5 softmax`.
- En meget kort forklaring: “træning justerer vægte; inference bruger dem”.

**Sig kort:**

> “StandardScaler bringer de 28 features på sammenlignelige skalaer og lærer kun sine værdier fra træningsdata. MLP'et kombinerer dem gennem to ReLU-lag og fem output. Softmax gør outputtene sammenlignelige. Under træningen justeres vægte med backpropagation; på Photon 2 udføres kun forward-pass.”

**Faglig kobling i noterne:** StandardScaler, data leakage, neuron, bias, ReLU, logits, softmax, loss, backpropagation og gradient descent.

**Visual:** `assets/mlp-architecture.svg`.

**Tid:** 90–105 sekunder.

---

## Slide 8 – Fra Python til robust firmware

**Hovedbudskab:** Trænings- og embedded-pipen har en fælles kontrakt, og output stabiliseres før handling.

**På slidet:**

- Python: data → scaler → trænet MLP → eksport.
- C++: samme 28 features → scaler → forward-pass.
- Beslutning: `score ≥ 0,75 → 3 ens → tap-kontrol → 4 s debounce`.

**Sig kort:**

> “Vægte, biases og scalerværdier eksporteres til faste C++-arrays. Featureorden og preprocessing skal være identiske i Python og C++. En prediction udfører ikke straks en handling: den skal være sikker, stabil og for taps passe med det målte antal impacts.”

**Faglig kobling i noterne:** model deployment, feature parity, confidence, hybrid ML/regler og debounce.

**Visual:** `assets/deployment-decision-flow.svg`.

**Tid:** 90 sekunder.

---

## Slide 9 – Embedded runtime

**Hovedbudskab:** Sampling, inference, serial og LED er organiseret, så feedback ikke blokerer sensoren.

**På slidet:**

- Første vindue: 1.600 samples.
- Derefter: behold 1.500 + tilføj 100 → inference hvert 0,25 sekund.
- DEBUG, TRAINING og LIVE.
- Non-blocking LED/state machine.

**Sig kort:**

> “Efter det første firesekunders vindue forskydes bufferen med 100 samples, så modellen evalueres hvert kvart sekund. LED-mønstrene bruger ikke lange delay-kald. DEBUG, TRAINING og LIVE adskiller diagnostik, dataindsamling og brugerdrift.”

**Faglig kobling i noterne:** sliding window, stride, state machine, flash, RAM, latency og responstid.

**Tid:** 75 sekunder.

### Spørgsmålszone 3

Kort overgang:

> “Det var den implementerede kæde. Den sidste del er, hvilken evidens jeg faktisk har for, at den virker.”

---

## Slide 10 – Resultater og korrekt fortolkning

**Hovedbudskab:** Prototypen virker end-to-end, men accuracy-estimatet er meget usikkert.

**På slidet:**

- Confusion matrix stort og læsbart.
- 80 % = 4 af 5.
- Macro precision 70 %, recall 80 %, F1 73,3 %.
- Cross-validation 76 %.
- tap1 → tap2 som konkret fejl.

**Sig kort:**

> “Fire af fem held-out-optagelser blev klassificeret korrekt. Tap1 blev forvekslet med tap2. Én fejl ændrer accuracy med 20 procentpoint, så 80 procent er ikke et stabilt generaliseringsestimat. Cross-validation på 76 procent giver flere splits, men bygger stadig på de samme 25 optagelser.”

**CV-verifikation:** 76 % er reproduceret med stratificeret 5-fold, shuffle og seed 42. Fold-scorerne er 60, 60, 100, 80 og 80 %. Scaler og model fittes på ny i hver fold. Den nuværende standardkørsel af `train.py` udskriver ikke denne ekstra kontrol.

**Faglig kobling i noterne:** confusion matrix, accuracy, precision, recall, F1, macro average og cross-validation.

**Visual:** `../Report/src/img/confusion_matrix.png`.

**Tid:** 90 sekunder.

---

## Slide 11 – Fysisk evidens, konklusion og næste test

**Hovedbudskab:** Deployment er verificeret; generalisering er ikke.

**På slidet:**

- Inference: 345 µs mean, 364 µs max.
- Firmware: 27.950 B flash, 46.686 B RAM.
- Sensor read errors: 0 i den registrerede kontrol.
- To bokse:
  - **Dokumenteret:** fungerende end-to-end-prototype.
  - **Ikke dokumenteret:** robusthed for nye personer og situationer.
- Næste test: helt ny person eller session holdes blindt ude.

**Sig kort:**

> “Modellen passer på enheden og bruger omkring 0,35 millisekund per forward-pass. Den fysiske test verificerer hele kæden fra sensor til event og LED. Den er ikke en blind accuracy-test. Den vigtigste næste undersøgelse er derfor at holde en hel ny bruger eller session ude som testdata.”

**Faglig kobling i noterne:** inferenstid kontra responstid, generalisering, overfitting, blind test og low-power som ikke-målt område.

**Tid:** 75–90 sekunder.

### Spørgsmålszone 4

Afslut:

> “Min konklusion er derfor en fungerende lokal TinyML-prototype med begrænset evidens for generalisering. Jeg stopper her.”

---

## Samlet tidsbudget

| Del | Måltid |
|---|---:|
| Titel | 0:35 |
| Demo | 3:30–4:00 |
| Problem og krav | 1:00 |
| Hardware og dataflow | 1:15 |
| Dataindsamling | 1:15 |
| Features | 1:30 |
| Scaler og MLP | 1:40 |
| Deployment og beslutning | 1:30 |
| Embedded runtime | 1:15 |
| Offline resultater | 1:30 |
| Konklusion og næste test | 1:15 |

Teknisk præsentation uden demo: cirka 12 minutter. Med demo: cirka 16 minutter. Hvis den tilladte tekniske tid er kortere, skæres detaljer fra slide 5, 7 og 9 uden at fjerne den røde tråd.

## Visuel asset-oversigt

### Brug direkte

- `Report/src/img/Circuit.jpg`: autentisk prototypefoto; velegnet til titel og fysisk verifikation.
- `Report/src/img/confusion_matrix.png`: tydelig konkret fejl og de fem testeksempler.
- `Report/src/img/gesture_signals.png`: dokumenterer forskelle og variation i de fem rå signaler.

### Nye diagrammer

- `Presentation/assets/system-dataflow.svg`: hele kæden i én linje.
- `Presentation/assets/feature-pipeline.svg`: fire signaler gange syv features.
- `Presentation/assets/mlp-architecture.svg`: scaler og netværket 28–32–16–5.
- `Presentation/assets/deployment-decision-flow.svg`: Python/C++-kontrakt og beslutningsfilter.
- `Presentation/assets/data-acquisition-overview.png`: fysisk hardware, tap2-signal og faktiske capture-metadata.
- `Presentation/assets/tap-count-comparison.png`: accepterede tap1/tap2/tap3-optagelser med event count.
- `Presentation/assets/quality-control-comparison.png`: godkendt og afvist tap1 med begrundelse.
- `Presentation/assets/sampling-50-vs-400.png`: pædagogisk illustration af sampleinterval og en smal impuls.
- `Presentation/assets/hardware-wiring.png`: præcis I2C-forbindelse og opstartskontrol.
- `Presentation/assets/sliding-window-timeline.png`: fire sekunders vindue og 0,25 s stride.
- `Presentation/assets/seven-features.png`: de syv featuredefinitioner og deres formål.
- `Presentation/assets/standard-scaler-concept.png`: konceptuel før/efter-skalering og leakage-reglen.
- `Presentation/assets/neuron-calculation.png`: vægtet sum, bias og ReLU.
- `Presentation/assets/training-vs-inference.png`: læringsloop på PC kontra fast forward-pass på enheden.
- `Presentation/assets/dataset-split-cv.png`: 20/5-split og femfolds-cross-validation.
- `Presentation/assets/cv-confusion-matrix.png`: reproduceret 5-fold-resultat med fejl per klasse.
- `Presentation/assets/classification-metrics.png`: TP/FP/FN/TN, precision, recall og F1.
- `Presentation/assets/evidence-boundary.png`: projektets dokumenterede og ikke-dokumenterede påstande.
- `Presentation/assets/gesture-command-map.png`: de fem klasser, fire kommandoer og RGB-feedback.
- `Presentation/assets/requirements-traceability.png`: kursuskrav koblet direkte til projektets evidens.
- `Presentation/assets/source-selection.png`: hvorfor kursusbrief, datablad, API, lærebog og egne målinger har forskellige roller.

### Undgå

- Generiske stockfotos af AI-hjerner eller cloud computing.
- Dekorative billeder uden forbindelse til eget projekt.
- Store tekstblokke på slides.
- Screenshots af kode, som ikke kan læses fra eksaminators afstand.
- Resultatgrafer uden tydelig forklaring af det lille testgrundlag.

## Praktisk demo-checkliste

- Photon 2, sensor og USB-kabel.
- Kendt fungerende firmware på enheden.
- Terminal og korrekt serial-port klar før eksamen.
- Notér de præcise kommandoer på tabletten.
- Slå notifikationer og automatisk skærmlås fra.
- Hav præsentation og noter lokalt, ikke kun i cloud.
- Hav rapportens billeder som separate lokale filer.
- Test `STATUS`, `MODE LIVE`, én tap og én shake før du går ind.
- Stop demoen tidligt, hvis den centrale funktion allerede er vist.
