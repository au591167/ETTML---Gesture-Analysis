# Slide 1 — TinyML Gesture Reader
> Layout: Titelslide med billede af den fysiske prototype

## Indhold
> Billede: `../Report/src/img/Circuit.jpg`

- Gestusbaseret styring af en blackjack-simulation
- Particle Photon 2 og ADXL343
- ETTML-01 — Tiny Machine Learning

---

# Slide 2 — Demo: Bevægelse bliver til en kommando
> Layout: Live-demo med en enkel statusboks og gestusoversigt

## Indhold
> Demo: `STATUS` → udfør gestus → `EVENT` i terminalen → RGB-feedback

- `tap1` → stand → blåt lys.
- `tap2` → hit → to blå pulser.
- `tap3` → exit → tre røde pulser.
- `shake_lr` → split → skiftende rødt og blåt lys.
- Hele inference-kæden kører lokalt på Photon 2 uden cloud-inference.

---

# Slide 3 — Problem, scope og kursuskrav
> Layout: Problemformulering til venstre og kravstatus til højre

## Indhold
> Diagram: Sensor → preprocessing → ML-model → observerbart output

- Kan en lille model på Photon 2 skelne mellem idle, ét, to og tre tryk samt en rystelse?
- Projektet fokuserer på gestusinterfacet og ikke på et komplet blackjack-spil.
- Systemet bruger Photon 2, en lokal sensor, egne labellede data og en ML-model.
- Forudsigelsen udføres på enheden og kommunikeres gennem USB og RGB-lys.
- Projektets tekniske kursuskrav er opfyldt og dokumenteret i rapporten.

---

# Slide 4 — Systemets dataflow
> Layout: Vandret systemdiagram fra fysisk bevægelse til feedback

## Indhold
> Diagram: ADXL343 → 4 s vindue → 28 features → scaler + MLP → beslutningsfilter → EVENT + RGB

- ADXL343 måler synkroniseret acceleration på X, Y og Z ved 400 Hz.
- Fire sekunder giver et vindue med 1.600 samples.
- Signalerne reduceres til 28 statistiske features.
- En StandardScaler og et MLP beregner fem klassesandsynligheder.
- Beslutningslogikken godkender eller afviser resultatet før output.

---

# Slide 5 — Teori: Hvorfor TinyML og klassifikation?
> Layout: To kolonner — TinyML-egenskaber og klassifikationsproblemet

## Indhold
> Diagram: Lokal sensor + lokal inference sammenlignet med cloud-forbindelse

- TinyML placerer signalbehandling og inference tæt på sensoren på en ressourcebegrænset enhed.
- Lokal inference giver lav kommunikationslatens og kan fungere uden netværksforbindelse.
- Outputtet er én af fem diskrete tilstande, så opgaven er klassifikation.
- Gestusser varierer i hastighed, kraft og retning og er derfor vanskelige at beskrive med få faste regler.
- Modellen skal lære mønstre i data, men samtidig være lille nok til microcontrolleren.

---

# Slide 6 — Praksis: Egne data og kvalitetskontrol
> Layout: Signalfigur til venstre og datasætoversigt til højre

## Indhold
> Figur: `../Report/src/img/gesture_signals.png`

- Det endelige datasæt indeholder 25 accepterede optagelser — fem fra hver klasse.
- Hver optagelse indeholder 1.600 samples samt label og relevante metadata.
- Klasser, tempo og kraft blev præsenteret i tilfældig rækkefølge under dataindsamlingen.
- Automatiske kontroller afviste forkert antal taps, bevægelse under idle og for svage shakes.
- 400 Hz blev valgt, fordi de første forsøg ved 50 Hz kunne overse hurtige taps.

---

# Slide 7 — Teori og praksis: Fra tidsserie til 28 features
> Layout: Fire signalkanaler øverst og featurematrix nederst

## Indhold
> Diagram: X, Y, Z og magnitude × 7 statistiske features = 28 modelinput

- Gennemsnittet fjernes fra hvert signal for at reducere statisk orientering og offset.
- Magnitude samler bevægelsesstyrken på tværs af de tre akser.
- Der beregnes standardafvigelse, minimum, maksimum, range og energi.
- Peak count beskriver antallet af tydelige impulser, mens max abs diff beskriver bratte ændringer.
- Feature engineering komprimerer 4.800 rå XYZ-målinger plus 1.600 afledte magnitudeværdier til 28 forklarbare tal.

---

# Slide 8 — Teori: Skalering og MLP
> Layout: Netværksdiagram med 28–32–16–5 og scaler foran

## Indhold
> Diagram: 28 features → StandardScaler → 32 ReLU → 16 ReLU → 5 softmax-output

- StandardScaler beregner z-scores, så features med store tal ikke automatisk dominerer.
- Scalerens middelværdier og skalaer læres kun fra træningsdata.
- MLP'et har to skjulte lag med 32 og 16 neuroner.
- ReLU giver modellen mulighed for at lære ikke-lineære sammenhænge.
- Softmax omsætter de fem output til sammenlignelige klassesandsynligheder.

---

# Slide 9 — Praksis: Fra Python-model til C++-firmware
> Layout: Python-pipeline til venstre, Photon 2-pipeline til højre og fælles kontrakt i midten

## Indhold
> Diagram: Træning → eksport af scaler, klasser og vægte → C++ forward-pass

- Python bruges til databehandling, træning, evaluering og eksport.
- Modelparametre og scaler-værdier genereres som faste C++-arrays.
- Firmwaren udfører en reel forward-pass med skalering, MLP og softmax.
- Rækkefølgen af preprocessing og de 28 features skal være identisk i Python og C++.
- Eksporten er fail-closed, så en fejlet træning ikke overskriver en fungerende model.

---

# Slide 10 — Praksis: Robust beslutningslogik
> Layout: Beslutningsflow med godkendelses- og afvisningsgrene

## Indhold
> Diagram: Softmax → confidence ≥ 0,75 → tre ens vinduer → tap-kontrol → debounce → EVENT

- En prediction under 0,75 confidence udløser ingen handling.
- Den samme sikre klasse skal observeres tre gange i træk.
- En supplerende slagtæller hjælper med at skelne ét, to og tre taps.
- Fire sekunders debounce forhindrer, at én gestus udløser flere kommandoer.
- Kombinationen er en hybrid løsning: ML genkender bevægelsesmønstret, mens regler stabiliserer outputtet.

---

# Slide 11 — Praksis: Non-blocking embedded arkitektur
> Layout: Ringbuffer og parallelle runtime-opgaver

## Indhold
> Diagram: Sampling, serial, inference og LED som kooperative tilstandsmaskiner

- De første 1.600 samples fylder et firesekunders vindue.
- Derefter beholdes de nyeste 1.500 samples, og 100 nye giver inference hvert 0,25 sekund.
- LED-controlleren bruger ikke `delay()` og blokerer derfor ikke sensorens sampling.
- `DEBUG`, `TRAINING` og `LIVE` adskiller fejlsøgning, dataindsamling og drift.
- `STATUS` synliggør blandt andet sensorstatus, mode, timing og read errors.

---

# Slide 12 — Resultater: Offline klassifikation
> Layout: Confusion matrix til venstre og nøgletal til højre

## Indhold
> Figur: `../Report/src/img/confusion_matrix.png`

- Held-out accuracy: **80 % — 4 af 5 testvinduer**.
- Macro precision: **70,0 %**.
- Macro recall: **80,0 %**.
- Macro F1: **73,3 %**.
- `tap1` blev forvekslet med `tap2`; femfolds-cross-validation gav **76 %**.

---

# Slide 13 — Resultater: På den fysiske enhed
> Layout: Prototypebillede med fire målte nøgletal

## Indhold
> Billede: `../Report/src/img/Circuit.jpg`

- Inference mean: **345 µs**; maksimum: **364 µs**.
- Firmwareforbrug: **27.950 B flash** og **46.686 B RAM**.
- Sensor read errors under den registrerede LIVE-kontrol: **0**.
- Firmware blev kompileret, flashed og afprøvet fysisk i LIVE-mode.
- Den fysiske test verificerede end-to-end-funktion, men var ikke en blind accuracy-test.

---

# Slide 14 — Konklusion
> Layout: Tre konklusionsbokse — funktion, performance og evidens

## Indhold
> Diagram: Bevægelse → lokal inference → blackjack-kommando og lys

- Hele TinyML-kæden fungerer fra egen sensor og egne data til lokal inference og synligt output.
- Modellen opfylder projektmålet på 80 % i det valgte split og ligger langt under latensmålet på 50 ms.
- Modellen og runtime-bufferen passer uden problemer på Photon 2.
- Projektet demonstrerer en fungerende embedded prototype.
- Resultaterne dokumenterer ikke endnu robust generalisering til nye personer og situationer.

---

# Slide 15 — Refleksion og næste eksperiment
> Layout: Begrænsninger til venstre og prioriteret forbedringsplan til højre

## Indhold
> Diagram: Nuværende evidens → begrænsning → næste validering

- Datasættet har kun fem forsøg pr. klasse fra én person og én slut-session.
- Én fejl ændrer held-out accuracy med 20 procentpoint.
- Trænings- og testdata fra samme session kan overvurdere generalisering.
- Næste test bør holde en hel ny session eller person ude som blindt testsæt.
- Derefter bør idle false triggers, flere brugere og Python/C++ feature-paritet måles systematisk.

---

# Slide 16 — Perspektivering og spørgsmål
> Layout: Enkel afslutningsslide med tre udviklingsspor

## Indhold
> Diagram: Data → responsivitet → optimering

- Flere brugere, monteringer og optagedage vil give et mere troværdigt datasæt.
- Bevægelsesudløste, kortere vinduer kan reducere systemets oplevede responstid.
- Kvantisering kan undersøges som optimering, selv om modellen allerede passer på enheden.
- BLE eller ekstra sensorer kan senere udvide brugergrænsefladen.
- Spørgsmål.
