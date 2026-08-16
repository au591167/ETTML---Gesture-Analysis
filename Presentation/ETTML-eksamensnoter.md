# ETTML – fagligt opslagsværk til eksamen

> Dette er et tabletvenligt opslagsværk, ikke et manuskript, der skal læses fra start til slut.
> Find det konkrete faglige emne i oversigten, læs **Vigtige pointer** først, og brug derefter resten til at uddybe svaret.

## Dokumentets struktur

Dokumentets hovedrækkefølge følger præsentationen. Hvert slide får sit eget område med:

- slidebudskabet i én sætning;
- korte talepointer;
- de faglige begreber, der hører til slidet;
- projektets konkrete tal og kodekoblinger;
- uddybende forklaringer, som kan findes hurtigt under eksamen.

Hvis eksaminator spørger uden for præsentationens aktuelle område, bruges det globale begrebsindeks længere nede.

## Præsentationens flow

### Slide 1 – Tiny Machine Learning

Titel, navn og eksamenspræsentation.

### Slide 2 – Agenda

Projekt og demonstration → hardware og data → features og model → træning og deployment → resultater.

### Slide 3 – Projektintroduktion

Projektets problem, formål, fem klasser, lokale inferens og konkrete output.

### Slide 4 – Demo

Fra fysisk gestus til klassifikation, `EVENT`, blackjack-kommando og RGB-feedback.

### Slide 5 – Hardware (ADXL343)

Photon 2, ADXL343, X/Y/Z, tyngdekraft, støj, måleområde, opløsning og I2C.

### Slide 6 – Fysisk orientering og datalæring

Startantagelsen om Y som op/ned korrigeres til Y venstre/højre, X frem/tilbage og Z op/ned. Data viste samtidig, at taps gav stærkere respons på Z end først forventet, og den endelige pipeline anvender derfor alle tre akser plus magnitude.

### Slide 7 – Samlet pipeline for systemet

ADXL343 → sampling → vindue → features → scaler → MLP → beslutningsfilter → output.

### Slide 8 – Dataindsamling

Rå sensordata, stationær baseline, motion-trigger, 400 Hz og firesekunders optagelser.

### Slide 9 – Datasæt og kvalitetskontrol

Labels, 25 balancerede optagelser, randomisering, automatiske kontroller, bias og begrænsninger.

### Slide 10 – Fra tidsserie til 28 features

Mean removal, magnitude, syv statistiske features per kanal og komprimering af tidsserien.

### Slide 11 – Kodefokus: feature extraction

`train.py`: fire kanaler gennemløbes, middelværdien fjernes, og syv statistikker tilføjes i fast rækkefølge.

### Slide 12 – Skalering og neural model

StandardScaler, neuroner, vægte, bias, MLP `28 → 32 → 16 → 5`, ReLU og softmax.

### Slide 13 – Træning og evaluering

Supervised learning, backpropagation, stratificeret 80/20 holdout, metrics og 5-fold cross-validation.

### Slide 14 – Kodefokus: split, scaler og træning

`train.py`: `train_test_split`, stratificering, seed 42, `fit_transform(train)`, `transform(test)` og `model.fit()`.

### Slide 15 – Deployment på Photon 2

Offline træning, eksport til C++, forward-pass, inferens, confidence, stabilisering, tap-kontrol og debounce.

### Slide 16 – Kodefokus: inference og beslutning

`main.cpp` og `model_data.cpp`: features, fem scores, valg af højeste score og filtrering til en stabil `EVENT`.

### Slide 17 – Resultater

Accuracy, cross-validation, confusion matrix, inferenstid, hukommelse og fysisk verifikation.

### Slide 18 – Aktuel datastatus og næste skridt

Rapportens 25-optagelses-snapshot, den større kandidatpulje, balancering, retræning og ny evaluering.

## Sådan bruges dokumentet

Hvert fagligt begreb har sin egen overskrift. Under overskriften står først en enkel forklaring i hele sætninger og derefter de vigtigste pointer som bullets. Hvor det er relevant, står der også et konkret eksempel fra projektet og ekstra teori.

Et kort svar kan normalt bygges sådan:

> “Begrebet betyder … Det bruges, fordi … I mit projekt bruges det til … En vigtig begrænsning er …”

## Globalt begrebsindeks

### Akut hjælp

- [Hvis jeg går blank](#1-hvis-jeg-går-blank)
- [Projektet på 60 sekunder](#2-projektet-på-60-sekunder)
- [Hele systemets dataflow](#3-hele-systemets-dataflow)

### Data og signaler

- [Accelerometer](#accelerometer)
- [Sensoropløsning, måleområde og enheder](#sensoropløsning-måleområde-og-enheder)
- [Sampling og samplingfrekvens](#sampling-og-samplingfrekvens)
- [Nyquist-frekvens og aliasing](#nyquist-frekvens-og-aliasing)
- [Filtrering](#filtrering)
- [Vinduer og sliding windows](#vinduer-og-sliding-windows)
- [Datasæt, labels og klassebalance](#6-datasættet-labels-og-klassebalance)
- [Metadata](#metadata)
- [Dataset bias og repræsentativitet](#dataset-bias-og-repræsentativitet)
- [Preprocessing](#preprocessing)
- [Magnitude](#magnitude)
- [Feature engineering](#feature-engineering)
- [Tidsdomæne og frekvensdomæne](#tidsdomæne-og-frekvensdomæne)
- [Feature selection](#feature-selection)

### Machine learning

- [Machine learning, deep learning og AI](#machine-learning-deep-learning-og-kunstig-intelligens)
- [Supervised learning](#supervised-learning)
- [Unsupervised learning](#unsupervised-learning)
- [Klassifikation, regression og anomaly detection](#klassifikation-regression-og-anomaly-detection)
- [StandardScaler](#8-standardscaler)
- [MLP](#mlp-multilayer-perceptron)
- [Neuron, vægte og bias](#neuron-vægte-og-bias)
- [ReLU](#relu)
- [Softmax](#softmax)
- [Forward-pass](#forward-pass)
- [Loss-funktion](#loss-funktion)
- [Backpropagation](#backpropagation)
- [Gradient descent og optimizer](#gradient-descent-og-optimizer)
- [Epoch, batch og iteration](#epoch-batch-og-iteration)
- [Konvergens](#konvergens)
- [Decision boundary](#decision-boundary)
- [Random forest og beslutningstræer](#random-forest-og-beslutningstræer)
- [Convolution](#convolution)
- [1D-CNN](#1d-cnn)
- [Train, validation og test](#train-validation-og-test)
- [Overfitting og generalisering](#overfitting-og-generalisering)
- [Data leakage](#data-leakage)

### Evaluering

- [Confusion matrix](#confusion-matrix)
- [TP, FP, FN og TN](#true-positive-false-positive-og-false-negative)
- [Accuracy](#accuracy)
- [Precision](#precision)
- [Recall](#recall)
- [F1-score](#f1-score)
- [Macro average](#macro-average)
- [Cross-validation](#cross-validation)
- [Projektets resultater](#projektets-resultater)

### Embedded TinyML

- [TinyML](#tinyml)
- [Edge computing og lokal inference](#edge-computing-og-lokal-inference)
- [Microcontroller kontra computer](#microcontroller-kontra-almindelig-computer)
- [Python-model til C++](#12-python-model-til-c)
- [TinyML-toolchain](#tinyml-toolchain)
- [emlearn](#emlearn)
- [AIfES](#aifes)
- [Edge Impulse](#edge-impulse)
- [CMSIS](#cmsis-og-hardwareoptimering)
- [Offline og on-device training](#offline-training-og-on-device-training)
- [Confidence threshold](#confidence-threshold)
- [Beslutningsstabilisering](#beslutningsstabilisering)
- [Debounce](#debounce)
- [Non-blocking firmware](#non-blocking-firmware)
- [Flash og RAM](#flash-og-ram)
- [Latency og responstid](#latency-og-responstid)
- [Kvantisering](#kvantisering)
- [Pruning](#pruning)
- [Low-power-design](#low-power-design)
- [K-means anomaly detection](#k-means-anomaly-detection)
- [GMM](#gaussian-mixture-model-gmm)
- [Autoencoder](#autoencoder-til-anomaly-detection)

### Projektforsvar

- [Problem, scope og kursuskrav](#4-problem-scope-og-kursuskrav)
- [Begrænsninger og næste eksperiment](#14-begrænsninger-og-næste-eksperiment)
- [Iterativ ML-udvikling](#iterativ-ml-udvikling-og-mlops-tankegang)
- [AI-brug](#ai-brug)
- [Kildegrundlag](#kildegrundlag-i-rapporten)
- [Kursusmateriale og projektkrav](#reference-1-kursets-tinyml-introduktion)
- [ADXL343-datablad](#reference-3-adxl343-databladet)
- [Photon 2-dokumentation](#reference-4-photon-2-dokumentation)
- [StandardScaler-dokumentation](#reference-5-scikit-learn-standardscaler)
- [MLPClassifier-dokumentation](#reference-6-scikit-learn-mlpclassifier)
- [Hands-On Machine Learning](#reference-7-hands-on-machine-learning)
- [Machine Learning with PyTorch and Scikit-Learn](#reference-9-machine-learning-with-pytorch-and-scikit-learn)
- [Valg af kildetype](#valg-af-kildetype)
- [Spørgsmålszoner](#spørgsmålszoner-i-præsentationen)

---

## 1. Hvis jeg går blank

### Min svarmodel

1. **Definition:** Hvad betyder begrebet?
2. **Formål:** Hvorfor bruger man det?
3. **Projekt:** Hvordan bruges det i min løsning?
4. **Begrænsning:** Hvad skal man være kritisk overfor?

### Sætninger jeg må bruge

- “Giv mig lige et øjeblik til at strukturere mit svar.”
- “Sådan som jeg forstår spørgsmålet, spørger I om …”
- “Jeg starter med det grundlæggende princip.”
- “I mit projekt kommer det konkret til udtryk ved …”
- “Jeg kan ikke huske den præcise detalje, men princippet er …”
- “Det målte jeg ikke direkte. Jeg ville undersøge det ved at …”
- “Jeg vil nødig gætte. Det, jeg kan forklare sikkert, er …”
- “Jeg vender lige tilbage til dataflowet, hvor jeg var nået til …”

### Mine fem holdepunkter

`KRAV → DATA → FEATURES → MODEL → RESULTAT`

---

## 2. Projektet på 60 sekunder

Jeg har bygget en gestusbaseret brugergrænseflade på en Particle Photon 2. En ADXL343-accelerationssensor måler bevægelse på X-, Y- og Z-aksen ved 400 Hz. Systemet opsamler fire sekunders data, fjerner signalernes gennemsnit og beregner 28 statistiske features. De bliver standardiseret og sendt gennem et lille neuralt netværk, som klassificerer vinduet som idle, ét tap, to taps, tre taps eller en venstre-højre-rystelse. Firmwaren filtrerer usikre og ustabile predictions, hvorefter en godkendt gestus bliver omsat til en blackjack-kommando og RGB-feedback. Hele inferencen foregår lokalt på microcontrolleren. Prototypen fungerer end-to-end, men datasættet er for lille til at dokumentere generalisering til nye brugere.

### Ultrakort version

> “Jeg har bygget en lokal TinyML-gestusklassifikator på en Photon 2. Den omdanner accelerometerdata til 28 features, klassificerer dem med et lille MLP og viser den godkendte kommando via USB og RGB-LED.”

---

## 3. Hele systemets dataflow

`fysisk gestus`

→ ADXL343 måler `ax`, `ay`, `az` ved 400 Hz

→ 4 sekunders vindue med 1.600 samples

→ gennemsnittet fjernes fra X, Y og Z

→ magnitude beregnes

→ 7 features beregnes for hver af 4 kanaler = 28 features

→ StandardScaler bruger træningssættets middelværdi og spredning

→ MLP med lagene 28–32–16–5

→ softmax giver fem klassescores/sandsynligheder

→ confidence, tre ens predictions, tap-kontrol og debounce

→ `EVENT` over USB og RGB-feedback

### Hovedpointen

Samme preprocessing, featureorden, scaler og modelparametre skal anvendes under træning i Python og inference i C++. Ellers modtager den deployede model andre input end dem, den blev trænet på.

---

## 4. Problem, scope og kursuskrav

### Problem

Kan en lille model på en Particle Photon 2 skelne mellem fem accelerometerbaserede tilstande og omsætte dem til kommandoer lokalt?

### Hvorfor klassifikation?

Outputtet er én af fem på forhånd definerede kategorier. Et kontinuerligt tal ville være regression, og registrering af noget ukendt eller unormalt ville være anomaly detection.

### Hvorfor ML frem for kun regler?

Gestusser varierer i hastighed, kraft, timing og retning. Et regelsystem kan godt tælle tydelige taps, men bliver hurtigt skrøbeligt, når hele bevægelsesmønstret varierer. Modellen lærer kombinationer af features, mens regler efter modellen stabiliserer outputtet.

## Machine learning, deep learning og kunstig intelligens

Kunstig intelligens er det brede område, hvor computere udfører opgaver, der forbindes med intelligent adfærd. Machine learning er en del af AI, hvor et system lærer mønstre fra data frem for kun at følge håndskrevne regler. Deep learning er en del af machine learning og bruger neurale netværk med flere lag.

- AI er den bredeste samlebetegnelse.
- Machine learning lærer parametre fra data.
- Deep learning anvender neurale netværk med flere lag.
- Et lille MLP kan kaldes et neuralt netværk, men “deep” er ikke en præcis garanti for, at modellen er avanceret.
- Valget bør bestemmes af opgaven, datamængden og hardwarebegrænsningerne.

**I mit projekt:** Der bruges supervised machine learning med et lille MLP. Systemet indeholder også traditionelle regler efter modellen.

## Edge computing og lokal inference

Edge computing betyder, at behandling udføres tæt på datakilden i stedet for at sende alle rå data til en central cloudtjeneste. TinyML er en særlig ressourcebegrænset form for edge AI, ofte på microcontrollere.

- Lokal behandling kan fungere uden netværk.
- Der sendes færre rå data, hvilket kan forbedre privatliv og reducere kommunikationsenergi.
- Kommunikationslatency kan undgås.
- Enheden har til gengæld begrænset RAM, flash, regnekraft og energi.
- Lokal inference betyder ikke automatisk, at hele systemet har lav responstid; dataopsamlingen kan stadig dominere.

**I mit projekt:** Accelerometerdata forlader ikke enheden for at blive klassificeret. Photon 2 udfører selv featureberegning og forward-pass.

### Scope

Projektet implementerer gestusinterfacet og kommandoerne til en blackjack-simulation. Det er ikke et komplet blackjack-spil.

### Kursuskrav opfyldt i projektet

- Particle Photon 2 som embedded platform.
- Lokal ADXL343-sensor.
- Egne indsamlede og labellede data.
- Preprocessing af sensormålinger.
- ML-klassifikation.
- Lokal inference på enheden.
- Observerbart output via USB og RGB-LED.
- Kode, data og dokumentation i repository.

---

## 5. Hardware og sampling

### Komponenter

- **Particle Photon 2:** Microcontroller-platformen, som sampler, beregner features og kører modellen.
- **ADXL343:** Tre-akset accelerometer forbundet over I2C.
- **RGB-LED:** Lokalt og synligt output.

### Accelerometer

Det måler acceleration langs tre akser. Målingerne indeholder både bevægelse og tyngdeaccelerationens projektion på akserne.

En stationær sensor viser derfor ikke nødvendigvis `x = 0`, `y = 0`, `z = 0`. Afhængigt af orienteringen vil tyngdekraften være fordelt på en eller flere akser, og den samlede magnitude vil typisk ligge omkring `1 g`. Små udsving under stilstand kan skyldes sensorstøj, offset, vibrationer og afrunding.

### ADXL343 i projektet

- Digitalt, tre-akset accelerometer.
- Forbundet til Photon 2 over I2C med `D0 = SDA` og `D1 = SCL`.
- Firmwaren undersøger adresserne `0x53` og `0x1D` og forventer device-ID `0xE5`.
- Sensorens Output Data Rate er sat til 400 Hz.
- Måleområdet er sat til ±16 g i full-resolution mode.
- Den nominelle omregning er cirka `0,0039 g` per rå LSB.
- De seks databytes fra sensoren samles til signed 16-bit-værdier for X, Y og Z og omregnes derefter til `g`.

**Vigtig forskel:** Sensorens Output Data Rate på 400 Hz betyder 400 målinger per sekund. I2C-clock på 400 kHz beskriver kommunikationsbussens bithastighed. De to tal er ikke det samme.

### 3D-akser og fysisk orientering – Slide 6

Et tre-akset accelerometer har et koordinatsystem, som sidder fast på selve sensoren:

- X og Y ligger i sensorchippen eller breakout-boardets plan.
- Z står vinkelret på sensorens plan.
- **Min startantagelse:** Y var op/ned og dermed den primære tapakse.
- **Den faktiske orientering i prototypen:** Y er venstre/højre, X er frem/tilbage, og Z er op/ned.
- Vender eller roterer man boardet, følger akserne med boardet; de følger ikke automatisk bordet eller rummet.
- Fortegnet viser retningen langs aksen. Et tap kan give både positive og negative udsving, fordi emnet påvirkes og derefter bevæger sig tilbage.
- Firmware-rækkefølgen er stadig `X, Y, Z`, uanset hvordan boardet fysisk er monteret.

**Projektets observation:** Ved stilstand var det gennemsnitlige signal cirka `Z = +0,91 g`, mens taps samlet havde cirka `0,304 g` mean-centreret RMS på Z mod `0,152 g` på Y. Det var derfor den fysiske antagelse om hovedretningen, der var forkert — ikke sensorens registerrækkefølge.

**Mundtligt anker til 3D-figuren:** “I starten antog jeg, at Y var op/ned og derfor den primære tapakse. Gennem dataanalysen og en kontrol af sensorens fysiske orientering fandt jeg ud af, at Y i min prototype går venstre/højre, X går frem/tilbage, og Z går op/ned. Det passer med, at taps gav omtrent dobbelt så høj RMS på Z som på Y. Registerdataene var hele tiden ordnet X, Y og Z; det var min fysiske fortolkning, jeg rettede. Den endelige pipeline bruger alle tre akser plus magnitude.”

### Kodekort: Fra seks registerbytes til X/Y/Z – Hardware og dataindsamling

Det forkortede udsnit på slidet svarer til `readAdxlRawXYZ()` og `readSampleG()` i `Product/firmware/src/main.cpp`:

```cpp
uint8_t b[6];
readRegisters(addr, 0x32, b, 6);

x = (int16_t)((b[1] << 8) | b[0]);
y = (int16_t)((b[3] << 8) | b[2]);
z = (int16_t)((b[5] << 8) | b[4]);

ax = x * 0.0039f;
ay = y * 0.0039f;
az = z * 0.0039f;
```

**Hvad gør koden?** Den læser én synkron tredimensionel accelerationsmåling og returnerer tre værdier i enheden `g`.

**Hvordan gør den?** ADXL343 har seks fortløbende dataregistre fra adresse `0x32`: to bytes per akse. Den første byte i hvert par er den mindst betydende byte, og den næste er den mest betydende. Shift `<< 8` flytter high-byte otte bit mod venstre, og bitvis OR `|` samler de to bytes. Cast til `int16_t` gør resultatet til et signed 16-bit-tal, så både negativ og positiv acceleration kan repræsenteres. Til sidst omregnes råtallet med cirka `0,0039 g/LSB`.

**Hvorfor læses alle seks bytes samlet?** Så X, Y og Z kommer fra samme sensoropdatering og repræsenterer bevægelsen på omtrent samme tidspunkt. Det er bedre end tre helt adskilte aflæsninger, hvor signalet kan nå at ændre sig imellem dem.

**Symbolerne i koden:**

- `uint8_t`: ét usigneret byte, værdier fra 0 til 255.
- `int16_t`: signed 16-bit-heltal, så negative målinger er mulige.
- `<< 8`: flyt bitmønstret otte pladser til venstre.
- `|`: kombinér bittene fra high-byte og low-byte.
- `0x32`: hexadecimal registeradresse for starten af ADXL343's X/Y/Z-data.
- `0.0039f`: scale factor i `g` per LSB; `f` markerer et `float`-tal i C++.

**Vigtigt hvis koden diskuteres:** Koden er ikke selve machine-learning-modellen. Den skaber de fysiske inputtal, som senere gemmes i vinduet, omdannes til features og gives til modellen.

### Fra rå sensordata til støjbaseline og inputsignal

Det første signalstudie bestod i at observere X-, Y- og Z-data ved stilstand og under taps. Formålet var at se sensorens normale niveau, støjens variation og størrelsen på et fysisk input, før der blev valgt tærskler og features.

I den guidede baseline holdes enheden stille i ti sekunder. De første to sekunder ignoreres, så berøring ved opstart ikke forurener idle-data eller støjestimatet. For hver måling beregnes magnitude:

`m = √(x² + y² + z²)`

Systemet beregner den stationære magnitudes middelværdi `μm` og standardafvigelse `σm`. Bevægelsestærsklen sættes til:

`motion threshold = max(0,05 g, 3 × σm)`

Et inputsignal registreres, når:

`|m − μm| > motion threshold`

- `μm` beskriver det normale stationære niveau.
- `σm` beskriver støjens normale variation.
- `3 × σm` gør tærsklen adaptiv til den målte støj.
- Minimumsværdien `0,05 g` forhindrer en alt for følsom trigger, hvis støjen er meget lille.
- Baseline-triggeren klassificerer ikke gestussen; den afgør kun, hvornår signalet tydeligt afviger fra stilstand.

**Vigtig afgrænsning:** Den guidede stationære baseline er en ældre capture-rutine med 20 ms polling, altså 50 Hz. Det endelige `pilot_v3`-datasæt og LIVE-modellens kontrakt bruger 400 Hz.

**Mundtligt anker:** “Jeg begyndte med at undersøge sensorens rå signal ved stilstand og under fysisk interaktion. Stilstand er ikke det samme som nul, fordi sensoren også måler tyngdekraft og støj. Derfor beregnede jeg en stationær magnitude-baseline og satte motion-threshold til det største af 0,05 g og tre gange støjens standardafvigelse. Det gav en datadrevet grænse mellem almindelig støj og et faktisk input.”

### Iterativ udvikling: fra rådata og akseantagelse til XYZ og magnitude

Efter forbindelsen mellem ADXL343 og Photon 2 var verificeret, blev de rå X-, Y- og Z-værdier observeret ved stilstand og under taps. Stilstandsdata blev brugt til at forstå tyngdekraft, offset og støj og til at etablere en stationær baseline. Derefter blev der indsamlet fem labellede optagelser per klasse: `idle`, `tap1`, `tap2`, `tap3` og `shake_lr`.

De fem optagelser per klasse udgør et **balanceret initialt datasæt**, ikke en separat støjbaseline for hver klasse. Ordet baseline bør her reserveres til den stationære støjmåling eller eventuelt en simpel første model.

Optagelserne blev kvalitetstjekket for blandt andet:

- præcis 1.600 samples og monotone timestamps;
- manglende værdier og clipping;
- tilstrækkelig fysisk bevægelse;
- klassespecifik adfærd;
- forventet impact count for `tap1`, `tap2` og `tap3`.

I en tidlig single-axis-diagnose blev det antaget, at et tap primært ville være synligt på en bestemt fysisk akse ud fra boardets vandrette placering. Dataanalysen viste, at sensorens fysiske akser ikke svarede til den intuitive retning i opstillingen. ADXL343 ændrer dog ikke dataorden til `X, Z, Y`: sensorregistrene og den endelige firmware bruger fortsat den faste rækkefølge `X, Y, Z`. Fejlen var fortolkningen af, hvilken fysisk retning de navngivne akser pegede i på det monterede breakout.

Den målte data understøtter konkret skiftet fra en forventet Y-dominans til fokus på Z-responsen:

- Ved idle er det gennemsnitlige rå niveau cirka `X = 0,04 g`, `Y = 0,03 g` og `Z = 0,91 g`. Tyngdekraften ligger altså hovedsageligt på den rapporterede Z-akse i den anvendte montering.
- På tværs af `tap1`, `tap2` og `tap3` er det gennemsnitlige mean-centrede peak cirka `7,64 g` på Z mod `4,48 g` på Y.
- Tap-signalets RMS er cirka `0,304 g` på Z mod `0,152 g` på Y.
- Z er peak-dominant i 10 af de 15 endelige tap-optagelser; X er dominant i fire og Y i én.
- Ved `shake_lr` har Y derimod højere vedvarende RMS end Z. Alle tre akser indeholder derfor stadig nyttig klasseinformation.

Det er vigtigt at skelne mellem tre ting:

1. **Datastrømmens rækkefølge:** ADXL343-registerdata læses og gemmes som `X, Y, Z`.
2. **Fysisk orientering:** I den konkrete montering svarer den kraftigste normale taprespons hovedsageligt til den rapporterede Z-akse, selv om Y først blev antaget at være hovedaksen.
3. **Modelvægtning:** Den endelige featurepipeline giver de samme syv features til X, Y og Z og hardcoder ikke en større Z-vægt. StandardScaler normaliserer hver feature, hvorefter MLP'et lærer vægte ud fra, hvilke mønstre der adskiller klasserne.

Den højere Z-amplitude giver et tydeligere signalgrundlag for taps, men større rå amplitude er ikke automatisk det samme som større neural vægt efter StandardScaler. En kontrolleret feature- eller akseablation ville være nødvendig for at bevise præcis, hvor meget modelaccuracy alene skyldes Z-kanalen.

Den endelige løsning undgår derfor at afhænge af én antaget tap-akse:

- alle tre akser læses synkroniseret;
- syv features beregnes separat for X, Y og Z;
- magnitude tilføjes som en fjerde kanal;
- mean removal reducerer statisk offset og en del af orienteringens påvirkning.

Magnitude og brugen af alle tre akser gør løsningen mindre afhængig af én bestemt akse, men gør den ikke fuldstændig rotationsinvariant. Nye monteringer og orienteringer bør stadig indgå i fremtidige trænings- og testdata.

**Mundtlig udviklingshistorie:** “Da jeg først tilsluttede ADXL343, undersøgte jeg de rå X-, Y- og Z-data. Ved stilstand var værdierne ikke nul på grund af tyngdekraft, offset og støj, så jeg målte først en stationær baseline. Derefter indsamlede jeg fem labellede optagelser af hver klasse og kontrollerede blandt andet signalets kvalitet og det forventede antal impacts for tap-klasserne. I de tidlige forsøg antog jeg, at tapresponsen primært ville ligge på Y, men dataanalysen viste, at Z havde næsten dobbelt så høj RMS for tap-signalerne. Det betød, at min fortolkning af sensorens fysiske orientering var forkert, selv om datastrømmen stadig var ordnet som X, Y og Z. Jeg flyttede derfor fokus væk fra den tidlige Y-antagelse og anvendte i den endelige pipeline alle tre akser samt magnitude. Det gav modellen adgang til den kraftige Z-respons uden at kassere information fra X og Y. Resultaterne blev bedre, men uden en kontrolleret akseablation kan jeg ikke tilskrive hele forbedringen til Z alene.”

## Sensoropløsning, måleområde og enheder

En sensors måleområde angiver de mindste og største fysiske værdier, den kan repræsentere. Opløsning beskriver det mindste trin, der kan skelnes. Et større måleområde reducerer risikoen for clipping, men kan give grovere effektiv opløsning afhængigt af sensoren.

- Acceleration angives ofte i `g`, hvor cirka `1 g` svarer til tyngdeaccelerationen.
- Clipping eller saturation opstår, hvis den fysiske værdi ligger uden for sensorens valgte område.
- Rå heltalsmålinger skal omregnes med sensorens scale factor.
- Sensorstøj er variation i målingen, som ikke skyldes den ønskede bevægelse.
- Måleområde, opløsning, samplingfrekvens og enheder bør gemmes som metadata.

**I mit projekt:** ADXL343 anvendes i ±16 g full-resolution og konverteres til acceleration i `g`. Området er valgt for at kunne rumme hurtige taps uden saturation.

### Sampling og samplingfrekvens

400 Hz betyder 400 samples per sekund:

`sampleinterval = 1 / 400 s = 0,0025 s = 2,5 ms`

Fire sekunder giver:

`400 samples/s × 4 s = 1.600 samples`

### Hvorfor 400 Hz?

De første forsøg ved 50 Hz havde 20 ms mellem samples og kunne overse dele af hurtige taps. Ved 400 Hz er der 2,5 ms mellem samples, hvilket giver bedre tidslig opløsning. Ulemperne er mere data, større buffer og potentielt mere højfrekvent støj.

## Nyquist-frekvens og aliasing

Når et kontinuerligt signal samples, kan frekvenser over halvdelen af samplingfrekvensen ikke repræsenteres entydigt. Halvdelen af samplingfrekvensen kaldes Nyquist-frekvensen. Aliasing betyder, at for hurtige signaldele fejlagtigt ser ud som lavere frekvenser i de samplede data.

- Ved 400 Hz er Nyquist-frekvensen 200 Hz.
- Samplingfrekvensen bør være mere end dobbelt så høj som den højeste relevante signalfrekvens.
- Et analogt eller digitalt low-pass-filter kan dæmpe uønskede høje frekvenser.
- En høj samplingfrekvens giver flere detaljer, men øger data-, hukommelses- og energibehovet.
- Projektets valg af 400 Hz blev fundet empirisk; der blev ikke udført en fuld frekvensanalyse af gestusserne.

## Filtrering

Filtrering bruges til at fremhæve relevante dele af et signal eller dæmpe støj. Et low-pass-filter dæmper høje frekvenser, et high-pass-filter dæmper lave frekvenser, og et band-pass-filter beholder et bestemt frekvensområde.

- Filtrering er preprocessing og kan ændre de informationer, modellen ser.
- Et anti-aliasing-filter anvendes før eller som del af samplingkæden for at dæmpe frekvenser over Nyquist-grænsen.
- Kraftig filtrering kan fjerne korte taps, som netop er relevante i dette projekt.
- Filtervalg bør baseres på signalets frekvensindhold og ikke kun på intuition.

**I mit projekt:** Der anvendes mean removal og engineered features, men ikke et egentligt udviklet digitalt low-pass- eller band-pass-filter i modelpipen.

### I2C

I2C er en seriel bus med en datalinje, SDA, og en clocklinje, SCL. Enheder identificeres med adresser. Firmwaren kontrollerer sensorens adresse og device-ID ved opstart.

---

## 6. Datasættet, labels og klassebalance

### Hurtigt svar

Det deployede datasæt har 25 accepterede optagelser: fem optagelser for hver af fem klasser. Alle kommer fra én person og én afsluttende session. Hver optagelse varer fire sekunder og har 1.600 samples.

### Klasser

- `idle`
- `tap1`
- `tap2`
- `tap3`
- `shake_lr`

### Label og features

- **Label:** Det korrekte facit, eksempelvis `tap2`.
- **Feature:** En målbar numerisk repræsentation af en relevant egenskab ved inputtet, som modellen bruger som input til sin beslutning.

En feature er ikke nødvendigvis symbolsk og bestemmer ikke alene modellens output. Modellen lærer vægte, som afgør, hvordan alle features kombineres. I dette projekt er features hånddesignede statistiske beskrivelser af tidsserien, eksempelvis signalets variation, yderpunkter, energi, peaks og hurtigste ændring.

Færre features gør ikke datasættet mindre i betydningen færre træningseksempler. Det reducerer **inputdimensionen**: Hver optagelse repræsenteres med 28 tal i stedet for tusindvis af samples. Det kan reducere modelstørrelse, RAM-behov og beregningsarbejde på en ressourcebegrænset enhed.

**Mundtligt anker:** “En feature er en numerisk egenskab, der er udledt af inputdata og givet til modellen. Den fortæller ikke alene, hvilket output der skal vælges; modellen lærer, hvordan flere features skal vægtes og kombineres. Jeg bruger bevidst et lille featureinput for at reducere inputdimension, modelstørrelse og beregning på Photon 2.”

## Metadata

Metadata er information om dataene, som ikke nødvendigvis er selve sensorsignalet, men som er nødvendig for at forstå, reproducere og kvalitetssikre det.

- Eksempler er label, samplingfrekvens, enhed, sensorområde, tidspunkt, bruger, session og optagebetingelser.
- Manglende metadata gør det svært at opdage forskelle mellem sessioner.
- Metadata kan bruges til at lave mere realistiske datasplit, eksempelvis efter person eller session.
- Metadata må ikke ukritisk bruges som modelfeatures, hvis de afslører labelen på en kunstig måde.

**I mit projekt:** CSV og tilhørende JSON beskriver blandt andet label, tempo, kraft, session og kvalitetskontrol.

## Dataset bias og repræsentativitet

Dataset bias opstår, når de indsamlede data systematisk ikke repræsenterer den virkelighed, modellen skal bruges i. En model kan kun lære den variation, som findes i dens data.

- Flere samples er ikke nok, hvis de alle kommer fra samme person og situation.
- Variation i bruger, montering, hastighed, kraft og optagedag kan være vigtig.
- Meget streng kvalitetsfiltrering kan skabe unaturligt rene data.
- Et balanceret datasæt løser klasseubalance, men ikke andre former for bias.

**I mit projekt:** Den største bias er én operatør og én afsluttende session.

### Hvorfor balancerede klasser?

Der er lige mange optagelser fra hver klasse. Det reducerer risikoen for, at modellen favoriserer en klasse alene, fordi den forekommer oftere.

### Kvalitetskontrol

Optagelser kunne afvises ved blandt andet forkert antal taps, for meget bevægelse under idle eller utilstrækkelig shake. Afvisning forbedrer labelkvaliteten, men kan også gøre datasættet mindre repræsentativt, hvis kun meget “rene” gestusser accepteres.

### Største begrænsning

25 optagelser er meget lidt. De kommer desuden fra samme person og session. Modellen kan derfor have lært netop denne persons og denne sessions mønstre frem for generelle gestusmønstre.

### Rapportens snapshot kontra den aktuelle datapulje

Rapportens model, confusion matrix og metrics tilhører det autoritative, balancerede snapshot i `pilot_v3/20260810_141717/accepted`: 25 optagelser, fem per klasse. `config.yaml` peger fortsat kun på denne mappe, så det er disse 25 optagelser, den deployede model er trænet og evalueret på.

På tværs af alle `pilot_v3`-sessioner findes der aktuelt 54 CSV-filer markeret som accepterede. Fem tidlige filer har kun 1.200 samples og følger derfor ikke den endelige kontrakt på 1.600 samples. Der er således 49 kontraktkompatible, accepterede optagelser til rådighed som en udvidet kandidatpulje:

- `idle`: 5
- `shake_lr`: 5
- `tap1`: 5
- `tap2`: 14
- `tap3`: 20

De 24 ekstra kontraktkompatible optagelser ligger kun i `tap2` og `tap3`, så den udvidede pulje er ikke klassebalanceret. De bør omtales som **yderligere indsamlede kandidatdata**, ikke som den rapporterede models træningsdata, før datasættet er kurateret, et nyt split er defineret, og modellen er retrænet og evalueret igen.

Hvis nye post-submission-optagelser ligger uden for repository, skal antal, klassefordeling, bruger/session og kvalitetsstatus dokumenteres, før tallet på præsentationen opdateres.

**Mundtligt anker:** “Rapportens dokumenterede resultater er et snapshot baseret på 25 balancerede optagelser. Jeg har fortsat dataarbejdet, og repository indeholder nu en større pulje af kontraktkompatible optagelser. De ekstra data er endnu ikke balancerede eller indarbejdet i den rapporterede model, så jeg adskiller tydeligt det afleverede resultat fra den videre udvikling. Næste trin er kuratering, balancering, retræning og en ny evaluering.”

---

## 7. Preprocessing og features

### Preprocessing

Preprocessing er de transformationer, der udføres på data, før modellen bruger dem.

### Fjernelse af gennemsnit

For hver akse trækkes vinduets gennemsnit fra hvert sample:

`centreret værdi = oprindelig værdi − vinduets gennemsnit`

Det reducerer statisk offset og påvirkningen fra enhedens orientering. Det kan samtidig fjerne information om absolut orientering, så det er et designvalg og ikke en universelt korrekt løsning.

### Magnitude

`magnitude = √(x² + y² + z²)`

Magnitude beskriver samlet bevægelsesstyrke på tværs af akserne og er mindre afhængig af, hvilken enkelt akse bevægelsen rammer.

### Feature engineering

Fire kanaler: X, Y, Z og magnitude.

Syv features per kanal:

1. standardafvigelse;
2. minimum;
3. maksimum;
4. range;
5. energi;
6. peak count;
7. maximum absolute difference.

`4 kanaler × 7 features = 28 features`

De syv features beskriver forskellige egenskaber ved én kanal:

1. **Standardafvigelse:** Hvor meget signalet varierer omkring sit gennemsnit.
2. **Minimum:** Det største negative udsving efter centrering.
3. **Maksimum:** Det største positive udsving efter centrering.
4. **Range:** `maksimum − minimum`; signalets samlede spændvidde.
5. **Energi:** Gennemsnittet af de kvadrerede samples, `mean(x²)`; et mål for samlet signalstyrke, ikke fysisk energi i joule.
6. **Peak count:** Antal tydelige lokale peaks i det absolutte signal. Implementationen bruger mindst `0,05 g` og mindst otte samples, svarende til 20 ms ved 400 Hz, mellem registrerede peaks.
7. **Maximum absolute difference:** Den største værdi af `|xᵢ − xᵢ₋₁|`; en indikator for den hurtigste ændring mellem to samples. Det er ikke helt det samme som fysisk jerk, fordi værdien ikke divideres med tidsforskellen.

Featurevektorens orden er X-features, Y-features, Z-features og til sidst magnitude-features. Python og C++ skal bruge præcis denne rækkefølge.

### Kodekort: Sådan bliver fire kanaler til 28 features – Slides 10–11

Det centrale princip i `extractFeatures()` er:

```cpp
for (size_t c = 0; c < 4; ++c) {
    for (size_t i = 0; i < 1600; ++i) {
        float ax = window[i].ax;
        float ay = window[i].ay;
        float az = window[i].az;
        if (c == 0) ch[i] = ax;
        else if (c == 1) ch[i] = ay;
        else if (c == 2) ch[i] = az;
        else ch[i] = sqrtf(ax*ax + ay*ay + az*az);
    }
    for (size_t i = 0; i < 1600; ++i)
        ch[i] -= mean;
    channelFeatures(ch, 1600, out7);
    for (size_t j = 0; j < 7; ++j)
        features[f++] = out7[j];
}
```

Udsnittet er forkortet for læsbarhed; i den faktiske kode ligger valg af kanal, beregning af gennemsnit og kopiering i hver sin løkke.

**Hvad gør koden?** Den bygger modellens inputvektor på 28 tal.

**Hvordan gør den?** Den gennemløber fire kanaler: X, Y, Z og magnitude. Hver kanal mean-centreres, `channelFeatures()` beregner syv statistikker, og `features[f++]` lægger dem efter hinanden i den aftalte rækkefølge.

**Hvorfor?** `1.600 × 3 = 4.800` rå akseværdier er en stor og tidsafhængig inputrepræsentation. De 28 features komprimerer signalet til variation, udsving, styrke, peaks og hurtige ændringer, så et lille MLP kan køre effektivt på Photon 2.

**Den vigtigste kodekontrakt:** Python-træningen og C++-firmwaren skal beregne de samme 28 features i samme orden. Hvis eksempelvis Y- og Z-grupperne byttes, modtager modellen andre egenskaber på de pladser, dens vægte er trænet til.

### Hvorfor feature engineering?

Det komprimerer tusindvis af rå målinger til få forklarlige tal. Det reducerer modellens størrelse og beregningsbehov, men kan kassere tidslig information, som en model på rå tidsserier kunne have udnyttet.

**Mundtligt anker:** “Fire sekunder giver 1.600 samples på hver fysisk akse. Jeg beregner også magnitude og udtrækker syv statistiske egenskaber fra hver af de fire kanaler. Det giver 28 inputs, som beskriver styrke, variation, peaks og hurtige ændringer. Det er en bevidst komprimering, der gør modellen mindre og mere forklarlig, men som også mister noget af den præcise tidslige rækkefølge.”

## Tidsdomæne og frekvensdomæne

Tidsdomænet beskriver, hvordan signalets værdi ændrer sig over tid. Frekvensdomænet beskriver, hvilke gentagelseshastigheder eller frekvenskomponenter signalet består af.

- Minimum, maksimum, energi og peak count er tidsdomænefeatures.
- En Fourier-transformation kan flytte analysen til frekvensdomænet.
- Frekvensfeatures kan være nyttige ved periodiske vibrationer eller lyd.
- Taps er korte transienter, mens en shake kan have mere periodisk struktur.
- Valg af domæne afhænger af, hvilke forskelle mellem klasserne man ønsker at fremhæve.

**I mit projekt:** De 28 features beregnes i tidsdomænet; FFT- eller spektrale features anvendes ikke.

## Feature selection

Feature selection betyder at vælge de mest informative inputfeatures og fjerne irrelevante eller stærkt redundante features.

- Færre features kan reducere beregning, hukommelse og overfitting.
- Features kan vurderes med domæneviden, visualisering, statistiske metoder eller modelbaseret importance.
- Feature selection skal udføres uden at lade testsættet påvirke valget.
- Feature engineering skaber features; feature selection vælger mellem dem.

**I mit projekt:** Der bruges et fast sæt på 28 features. Der blev ikke gennemført en systematisk feature-ablation, hvor features fjernes én ad gangen og effekten måles.

---

## 8. StandardScaler

### Hurtigt svar

StandardScaler bringer features over på sammenlignelige skalaer, så numerisk store features ikke automatisk får størst indflydelse.

### Formel

`z = (x − μ) / σ`

- `x`: featureværdien.
- `μ`: featureens gennemsnit i træningsdata.
- `σ`: featureens standardafvigelse i træningsdata.
- `z`: den standardiserede værdi.

Efter standardisering vil træningsdata typisk have middelværdi omkring 0 og standardafvigelse omkring 1 for hver feature.

### Data leakage

Scalerens `μ` og `σ` må kun beregnes fra træningsdata. Hvis testdata påvirker dem, opstår data leakage. De lærte værdier eksporteres til C++, så enheden bruger præcis samme transformation.

### Hvordan skaleringen bruges i projektet

For hver af de 28 featuredimensioner beregner `StandardScaler` sit eget gennemsnit og sin egen standardafvigelse på træningssættet. En `peak_count`-værdi skaleres derfor med statistikken for `peak_count`, mens en energiværdi skaleres med energifeaturens egen statistik.

Eksempel: Hvis en feature har træningsgennemsnit `8`, standardafvigelse `2` og den nye værdi er `12`, bliver den skalerede værdi `(12 − 8) / 2 = 2`. Den ligger dermed to standardafvigelser over træningsgennemsnittet.

De 28 middelværdier og 28 scale-værdier eksporteres som konstante arrays til firmwaren. Photon 2 fitter ikke en ny scaler, men genbruger træningssættets værdier. Hvis en scale-værdi er ekstremt tæt på nul, bruger C++-koden `1,0` som divisor for at undgå division med nul.

### Mean centering er ikke StandardScaler

- **Mean centering:** Udføres på de 1.600 samples i hvert enkelt vindue før feature extraction og reducerer vinduets statiske offset.
- **StandardScaler:** Udføres på de 28 færdige features og bruger statistik fra hele træningssættet til at gøre featuredimensionerne sammenlignelige.

StandardScaler gør ikke nødvendigvis data normalfordelte. Den centrerer hver feature omkring nul og giver den typisk standardafvigelse omkring én i træningsdataene.

**Mundtligt anker:** “De 28 features har forskellige numeriske størrelsesordener. Derfor trækker jeg træningsgennemsnittet fra hver feature og dividerer med dens standardafvigelse. Scaleren fittes kun på træningsdata for at undgå data leakage, og de samme værdier eksporteres til Photon 2, så preprocessing er identisk under træning og inferens.”

---

## MLP – Multilayer Perceptron

Et MLP er en type feedforward neuralt netværk. “Feedforward” betyder, at informationen bevæger sig i én retning: fra inputlaget gennem de skjulte lag og videre til outputlaget. Netværket lærer at kombinere inputtene ved hjælp af vægte og biases.

- Et MLP kan lære ikke-lineære sammenhænge.
- Inputlaget modtager de værdier, modellen skal arbejde med.
- De skjulte lag kombinerer værdierne og finder mønstre.
- Outputlaget giver én score for hver mulig klasse.
- Flere neuroner og lag giver større modelkapacitet, men også større risiko for overfitting og højere ressourceforbrug.

**I mit projekt:** MLP'et har strukturen `28 → 32 → 16 → 5`. Det modtager 28 features, har to skjulte lag og producerer fem klassescores.

## Neuron, vægte og bias

En kunstig neuron er en lille matematisk beregning. Den modtager flere input, ganger hvert input med en vægt, lægger resultaterne sammen og tilføjer en bias. Resultatet sendes normalt gennem en aktiveringsfunktion.

`z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b`

`a = f(z)`

- `x` er inputværdierne.
- `w` er vægtene, som afgør hvor meget hvert input betyder.
- `b` er bias, som forskyder neuronens resultat.
- Vægte og biases er parametre, modellen lærer under træningen.
- En neuron er ikke en fysisk node; den er en beregning i software.

**Enkelt eksempel:** Hvis en neuron modtager “energi” og “peak count”, kan træningen give de to features forskellige vægte afhængigt af, hvor nyttige de er til at skelne gestusser.

I modellen har det første skjulte lag 32 neuroner, og hvert neuron modtager alle 28 features. Det næste lag har 16 neuroner, og outputlaget har fem neuroner. Det giver:

- Første lag: `28 × 32` vægte + `32` biases = `928` parametre.
- Andet lag: `32 × 16` vægte + `16` biases = `528` parametre.
- Outputlag: `16 × 5` vægte + `5` biases = `85` parametre.
- I alt: `1.541` lærte modelparametre.

Det er antallet af vægte og biases, ikke antallet af neuroner.

**Mundtligt anker:** “Et neuron er en matematisk funktion. Det vægter sine inputs, lægger en bias til og bruger en aktiveringsfunktion. Vægtene bestemmer, hvor stærkt forskellige input påvirker neuronet, og de læres under træningen. Flere neuroner kan derfor lære forskellige kombinationer af de 28 features.”

## Aktiveringsfunktion

En aktiveringsfunktion bestemmer, hvordan en neurons beregnede værdi sendes videre. Uden ikke-lineære aktiveringsfunktioner ville flere lag stadig samlet set opføre sig som én lineær transformation, og netværket kunne ikke lære komplekse beslutningsgrænser.

- Aktiveringsfunktionen anvendes efter den vægtede sum.
- Den gør det muligt for netværket at beskrive ikke-lineære mønstre.
- Forskellige aktiveringsfunktioner har forskellige egenskaber.

**I mit projekt:** De skjulte lag bruger ReLU, mens outputtet omdannes med softmax.

## ReLU

ReLU betyder Rectified Linear Unit. Funktionen sender positive værdier videre uændret og erstatter negative værdier med nul.

`ReLU(x) = max(0, x)`

- Hvis input er `4`, bliver output `4`.
- Hvis input er `−4`, bliver output `0`.
- ReLU er enkel og billig at beregne.
- ReLU tilfører den ikke-linearitet, som gør de skjulte lag nyttige.
- En mulig ulempe er, at en neuron kan ende med altid at give nul; det kaldes nogle gange en “dead ReLU”.

**I mit projekt:** ReLU anvendes efter begge skjulte lag med henholdsvis 32 og 16 neuroner.

## Logits

Logits er modellens rå outputværdier før softmax. De behøver ikke ligge mellem 0 og 1 og behøver ikke summere til noget bestemt.

- Hver klasse har én logit.
- En større logit betyder, at modellen foretrækker den klasse relativt til de andre.
- Softmax omdanner logits til sammenlignelige positive værdier.

**I mit projekt:** Outputlaget producerer fem logits, én for hver gestusklasse.

## Softmax

Softmax omdanner modellens rå logits til fem positive scores, som tilsammen giver 1. Det gør det muligt at sammenligne klassernes relative sandsynlighed eller confidence.

`softmax(zᵢ) = exp(zᵢ) / Σ exp(zⱼ)`

- Eksponentialfunktionen gør alle værdier positive.
- Division med summen får værdierne til at summere til 1.
- Klassen med den største softmax-værdi vælges normalt som prediction.
- En høj softmax-score er ikke garanti for, at modellen har ret.
- Softmax-output kan være dårligt kalibreret, især med få træningsdata.

**I mit projekt:** Den højeste af fem softmax-scores er modellens klasseforslag. Forslaget skal også passere en confidence-grænse og beslutningslogikken, før en kommando udføres.

## Forward-pass

Et forward-pass er den beregning, der sender ét input gennem hele det trænede netværk for at producere et output. Under inference udføres kun forward-pass; modellen lærer ikke nye vægte på enheden.

- Input skaleres først.
- Hvert lag beregner vægtet sum, bias og aktivering.
- Outputlaget producerer logits.
- Softmax producerer klassescores.

**I mit projekt:** Forward-pass er implementeret i C++ på Photon 2 med de vægte og biases, der blev lært i Python.

Den konkrete rækkefølge er:

1. De 28 features standardiseres.
2. Første lag beregner `z₁ = W₁x + b₁`, hvorefter `a₁ = ReLU(z₁)` giver 32 aktiveringer.
3. Andet lag beregner `z₂ = W₂a₁ + b₂`, hvorefter `a₂ = ReLU(z₂)` giver 16 aktiveringer.
4. Outputlaget beregner `z₃ = W₃a₂ + b₃` og producerer fem logits.
5. Softmax omdanner de fem logits til positive klassescores, der summerer til 1.
6. Klassen med den største score bliver modellens kandidat.

Softmax-implementationen trækker først den største logit fra alle logits, før eksponentialfunktionen beregnes. Det ændrer ikke den matematiske fordeling, men reducerer risikoen for numerisk overflow.

**Mundtligt anker:** “Et forward-pass sender ét featureinput frem gennem den færdigtrænede model. Hvert lag beregner vægtede summer og biases, de skjulte lag anvender ReLU, og outputlaget anvender softmax. Der foregår ingen læring eller backpropagation på Photon 2; de eksporterede vægte bliver kun brugt.”

## Loss-funktion

En loss-funktion giver et tal for, hvor forkert modellens prediction er i forhold til den korrekte label. Træningens mål er at justere modellens parametre, så loss bliver mindre.

- En korrekt og sikker prediction giver typisk lav loss.
- En forkert og sikker prediction giver typisk høj loss.
- Loss bruges til træning; den er ikke det samme som accuracy.
- Ved flerklasseklassifikation bruges ofte cross-entropy loss.

**I mit projekt:** `MLPClassifier` håndterer loss-beregningen som en del af træningen. Firmwaren beregner ikke loss, fordi den kun udfører inference.

## Backpropagation

Backpropagation er algoritmen, der beregner, hvor meget hver vægt og bias bidrog til modellens fejl. Beregningen starter ved outputtet og bevæger sig baglæns gennem netværket ved hjælp af den matematiske kæderegel.

- Først udføres et forward-pass.
- Loss-funktionen måler fejlen.
- Backpropagation beregner gradienten for hver parameter.
- En gradient beskriver, hvordan en lille ændring af parameteren påvirker loss.
- Backpropagation ændrer ikke selv vægtene; den beregner den information, optimizeren bruger til at ændre dem.
- Processen gentages over mange træningseksempler.

**I mit projekt:** Scikit-learns `MLPClassifier` udfører backpropagation under træningen i Python. Der foregår ingen backpropagation på Photon 2.

## Gradient descent og optimizer

Gradient descent er princippet om at ændre modellens parametre i den retning, der reducerer loss. Optimizeren bruger gradienterne fra backpropagation til at beregne de konkrete opdateringer.

`ny vægt = gammel vægt − learning rate × gradient`

- Gradientens retning viser, hvordan loss vokser mest.
- Derfor bevæger man sig i den modsatte retning.
- Learning rate bestemmer størrelsen på hvert skridt.
- For høj learning rate kan springe forbi en god løsning.
- For lav learning rate kan gøre træningen meget langsom.

**I mit projekt:** Learning rate er sat til `0,001`. Det er en hyperparameter, ikke en værdi modellen selv lærer.

## Epoch, batch og iteration

En epoch betyder, at træningsalgoritmen har haft mulighed for at gennemgå hele træningssættet én gang. En batch er den gruppe træningseksempler, der behandles sammen før en parameteropdatering. En iteration er normalt én behandling af en batch.

- Flere epochs giver modellen flere muligheder for at lære, men kan øge overfitting.
- Små batches giver hyppigere og mere støjende opdateringer.
- Store batches kræver mere hukommelse.
- `max_iter` i scikit-learns `MLPClassifier` er en øvre grænse for træningsiterationer/epochs afhængigt af solverens arbejdsform.
- At træningen stopper ved grænsen betyder ikke nødvendigvis, at den er konvergeret.

**I mit projekt:** Den konfigurerede `batch_size` er 32, learning rate er 0,001, og `max_iter` er 500. Træningssættet har kun 20 optagelser, så scikit-learn begrænser i praksis batchen til størrelsen på træningssættet.

## Konvergens

Konvergens betyder, at optimeringen nærmer sig en stabil løsning, hvor loss ikke længere forbedres væsentligt. Manglende konvergens kan betyde, at modellen behøver flere iterationer, en anden learning rate, bedre skalering eller en anden model.

- Lavere training loss er ikke automatisk bedre generalisering.
- Man bør sammenligne trænings- og valideringsadfærd.
- En convergence warning er information om træningsprocessen, ikke i sig selv bevis på en ubrugelig model.

**I mit projekt:** Grænsen blev hævet fra 40 til 500, fordi 40 iterationer stoppede før konvergens på det endelige femklassedatasæt.

## Decision boundary

En decision boundary er grænsen i feature-rummet, hvor modellen skifter fra at foretrække én klasse til en anden. Med 28 features ligger grænsen i et 28-dimensionelt rum og kan derfor ikke visualiseres direkte på en almindelig todimensional graf.

- En lineær model bruger lineære grænser.
- Et MLP med ikke-lineære aktiveringer kan lære mere komplekse grænser.
- En mere kompleks grænse kan passe data bedre, men også overfitte.

**I mit projekt:** MLP'et lærer grænser mellem de fem gestusklasser ud fra kombinationer af de 28 features.

## Random forest og beslutningstræer

Et beslutningstræ laver en række if/else-lignende opdelinger af feature-rummet. En random forest kombinerer mange træer, som er trænet med variation i data og features, og afgør normalt klassifikationen ved afstemning.

- Træer kræver normalt ikke StandardScaler.
- De kan modellere ikke-lineære relationer.
- Et enkelt træ er let at fortolke, men kan overfitte.
- En forest er ofte mere robust, men fylder mere end ét træ.
- Træbaserede modeller kan konverteres til C og bruges på microcontrollere med værktøjer som emlearn.

**I mit projekt:** Træningskoden understøtter en random-forest-konfiguration, men den deployede model er et MLP.

## Deep learning

Deep learning bruger neurale netværk med flere lag til at lære repræsentationer direkte eller næsten direkte fra data. Det kan reducere behovet for hånddesignede features, men kræver ofte mere data og flere ressourcer.

- Deep learning er særligt stærkt til billeder, lyd og komplekse tidsserier.
- Mere kompleksitet er ikke automatisk bedre på små datasæt.
- Embedded deployment kan kræve kvantisering eller specialiserede biblioteker.
- Træning udføres ofte på en kraftig computer, mens kun inference deployeres.

**I mit projekt:** MLP'et er et lille neuralt netværk på engineered features. Det er langt mindre end typiske deep-learning-modeller på rå data.

## Convolution

En convolution anvender et lille filter eller en kernel på lokale områder af et signal. De samme kernel-vægte genbruges på tværs af signalet, så modellen kan genkende det samme lokale mønster forskellige steder.

- For en 1D-tidsserie bevæger kernelen sig langs tidsaksen.
- Weight sharing reducerer antallet af parametre sammenlignet med fuldt forbundne lag.
- Convolution kan lære lokale mønstre som kanter i billeder eller impulser i sensorsignaler.
- Kernel size bestemmer, hvor stort et lokalt område laget ser ad gangen.
- Flere convolution-lag kan kombinere simple lokale mønstre til mere komplekse mønstre.

## 1D-CNN

En 1D-CNN er et convolutional neural network til sekventielle data som lyd, vibrationer eller accelerometertidsserier. Den kan lære tidslige features direkte fra rå eller let behandlede samples.

- Den bevarer mere tidslig struktur end en model på kun globale statistikfeatures.
- Den kan være mere beregnings- og hukommelseskrævende.
- Den kræver normalt mere og mere varieret træningsdata.
- Inputformen og preprocessing skal stadig være identisk under træning og deployment.

**I mit projekt:** En 1D-CNN var en mulig kandidat, men featurebaseret MLP blev valgt på grund af det lille datasæt, forklarlighed og enklere C++-deployment.

---

## 10. Træning, test og generalisering

### Supervised learning

Modellen trænes på eksempler, hvor den korrekte klasse allerede er kendt.

## Unsupervised learning

Ved unsupervised learning har modellen ikke korrekte labels for hvert eksempel. Den forsøger i stedet at finde struktur, grupper eller afvigelser i dataene.

- Clustering er et eksempel på unsupervised learning.
- Det kan bruges til udforskning eller anomaly detection.
- Fundne grupper er ikke automatisk meningsfulde klasser; de skal fortolkes.
- Supervised og unsupervised beskriver træningssignalet, ikke om algoritmen er “simpel” eller “intelligent”.

**I mit projekt:** Gestusmodellen er supervised, fordi alle optagelser har en kendt label.

### Train, validation og test

#### Træningsdata

Bruges til at lære scalerens værdier og modellens vægte.

#### Testdata

Holdes ude af træningen og bruges til en afsluttende vurdering på usete eksempler.

#### Validation

Bruges normalt under modeludvikling til valg af model og hyperparametre. Et testsæt bør ikke bruges gentagne gange til at træffe udviklingsvalg, fordi det så indirekte bliver en del af udviklingen.

### Stratificeret 80/20 holdout

Et holdout-split opdeler datasættet én gang. Projektets 25 optagelser deles i:

- 80 % træning = 20 optagelser.
- 20 % test = 5 optagelser.

Splittet er stratificeret. Det betyder, at klassernes fordeling bevares. Da der er fem optagelser fra hver af fem klasser, indeholder træningssættet fire optagelser per klasse, mens testsættet indeholder én optagelse per klasse.

**Hvorfor:** Træningssættet bruges til at fitte scaler og model. Testsættet holdes ude af træningen og bruges som en afsluttende kontrol på usete optagelser. Stratificering forhindrer, at en klasse ved et tilfælde mangler i trænings- eller testdelen.

**Begrænsning:** Testsættet har kun fem eksempler. Én fejl ændrer accuracy med `1 / 5 = 20` procentpoint, så 80 % er ikke et præcist estimat for fremtidig generalisering.

**Mundtligt anker:** “Jeg anvender et stratificeret 80/20 holdout. Det giver 20 træningsoptagelser og fem testoptagelser, præcis én testoptagelse fra hver klasse. Testen er let at forklare, men meget følsom, fordi én fejl ændrer accuracy med 20 procentpoint.”

### Overfitting og generalisering

#### Overfitting

Overfitting betyder, at modellen lærer træningsdata meget specifikt, men klarer sig dårligt på nye data. Risikoen er høj her på grund af det lille datasæt og den samme bruger/session.

#### Generalisering

Generalisering er evnen til at fungere på nye data fra den virkelige målgruppe og anvendelse. Projektet dokumenterer funktionalitet, men ikke brugeruafhængig generalisering.

### Hyperparametre og parametre

- **Hyperparametre:** Valgt før træning, eksempelvis lagstørrelser, learning rate og maksimalt antal iterationer.
- **Lærte parametre:** Vægte, biases og scalerens værdier, som bestemmes ud fra træningsdata.

---

## 11. Resultater og metrics

### Projektets resultater

- Held-out accuracy: 80 %, altså 4 af 5 testoptagelser.
- Macro precision: 70,0 %.
- Macro recall: 80,0 %.
- Macro F1: 73,3 %.
- Femfolds-cross-validation: 76 %.
- `tap1` blev forvekslet med `tap2` i det valgte test-split.
- Inference: cirka 345 µs i gennemsnit og 364 µs maksimalt i den registrerede LIVE-test.
- Firmware: 27.950 B flash og 46.686 B RAM.

### Confusion matrix

Rækker viser normalt de sande klasser, og kolonner viser de forudsagte klasser. Diagonalen er korrekte predictions. Tal uden for diagonalen viser konkrete forvekslinger.

## True positive, false positive og false negative

Når én klasse vurderes ad gangen, kan predictionerne opdeles sådan:

- **True positive, TP:** Modellen forudsiger klassen, og det er korrekt.
- **False positive, FP:** Modellen forudsiger klassen, men den sande klasse er en anden.
- **False negative, FN:** Eksemplet tilhører klassen, men modellen vælger en anden.
- **True negative, TN:** Eksemplet tilhører ikke klassen, og modellen vælger den heller ikke.

I flerklasseklassifikation beregnes disse størrelser typisk separat for hver klasse ved at betragte den valgte klasse mod alle de andre.

### Accuracy

`accuracy = antal korrekte predictions / antal predictions`

Accuracy er let at forstå, men kan være misvisende ved ubalancerede klasser.

### Precision

`precision = TP / (TP + FP)`

Af alle de eksempler, modellen kaldte en bestemt klasse, hvor mange var faktisk den klasse?

### Recall

`recall = TP / (TP + FN)`

Af alle de virkelige eksempler fra en klasse, hvor mange fandt modellen?

### F1-score

`F1 = 2 × precision × recall / (precision + recall)`

F1 er det harmoniske gennemsnit af precision og recall og bliver lav, hvis en af dem er lav.

### Macro average

Metricen beregnes separat for hver klasse, og klasserne får derefter lige stor vægt i gennemsnittet.

### Cross-validation (CV) – fem testrunder med skiftende testdata

**Helt enkelt:** Forestil dig de 25 optagelser fordelt i fem bunker med fem optagelser i hver. Hver bunke indeholder én optagelse fra hver klasse. Modellen trænes og testes fem gange:

1. Træn på bunke 2–5, og test på bunke 1.
2. Træn på bunke 1, 3, 4 og 5, og test på bunke 2.
3. Fortsæt, indtil alle fem bunker har været testdata én gang.

I hver runde er der derfor 20 træningsoptagelser og fem testoptagelser. Til sidst beregnes gennemsnittet af de fem testresultater. “5-fold” betyder fem bunker, “cross-validation” betyder den gentagne evaluering, og “stratificeret” betyder, at alle klasser er repræsenteret i hver bunke.

Data opdeles flere gange, så hver del bruges som validering én gang. Det giver flere målinger end ét enkelt split, men femfolds-cross-validation på kun 25 optagelser er stadig baseret på meget få og tæt relaterede eksempler.

Projektets 76 % kan reproduceres med `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. De fem fold-accuracies er 60 %, 60 %, 100 %, 80 % og 80 %. I hver fold skal en ny StandardScaler og en ny MLP kun fittes på foldens træningsdel.

- Stratificering sikrer én optagelse fra hver klasse i hver testfold.
- Shuffle og seed 42 gør den valgte opdeling reproducerbar.
- Gennemsnittet er `(0,60 + 0,60 + 1,00 + 0,80 + 0,80) / 5 = 0,76`.
- Cross-validation skaber ikke nye personer eller sessioner.
- Den nuværende `train.py` udskriver kun det faste held-out-split; CV-resultatet kræver en separat kontrolberegning.

I femfolds-cross-validation opdeles datasættet i fem folds med fem optagelser i hver. Modellen trænes fem gange. I hver runde bruges fire folds, altså 20 optagelser, til træning og det resterende fold med fem optagelser til validering. Hver optagelse bliver dermed brugt som valideringsdata præcis én gang.

En ny StandardScaler og en ny MLP skal fittes inde i hver runde og kun på rundens træningsfolds. Hvis én fælles scaler fittes på alle 25 optagelser før cross-validation, har valideringsdata påvirket preprocessing, og resultatet indeholder data leakage.

Cross-validation reducerer afhængigheden af ét bestemt split, men den skaber hverken nye brugere, sessioner eller uafhængige målinger. Den måler derfor stabiliteten inden for det eksisterende lille datasæt, ikke brugeruafhængig generalisering.

**Mundtligt anker:** “Ved stratificeret 5-fold cross-validation træner jeg fem modeller. Hver gang trænes der på 20 optagelser og valideres på fem, med én optagelse fra hver klasse. Hver optagelse er valideringsdata én gang. Det giver flere vurderinger end et enkelt split, men løser ikke begrænsningen ved kun én bruger og én session.”

### Seed 42 og `random_state` – Slides 13–14: Træning og evaluering

**Placering i forklaringen:** Forklar seed umiddelbart efter det stratificerede 80/20-split og inden gennemgangen af 5-fold-resultaterne. Seed handler om, hvordan data blandes og fordeles, og hører derfor til evaluering — ikke til sensoropsamling, features eller selve inferensen.

Et seed er startværdien for en pseudo-random generator. Computeren skaber en tilsyneladende tilfældig rækkefølge ud fra startværdien. Når samme data, kode og seed bruges igen, fås den samme blanding og det samme datasplit.

`random_state=42` bruges til at gøre det stratificerede holdout-split og blandingen før cross-validation reproducerbar. Tallet 42 har ingen særlig matematisk fordel; et andet heltal kunne også anvendes. Det forbedrer ikke accuracy og gør ikke datasættet mere tilfældigt.

- Samme seed gør eksperimentet reproducerbart.
- Et andet seed kan give et andet split og dermed et andet resultat.
- Effekten kan være stor med kun 25 optagelser.
- Cross-validation reducerer afhængigheden af ét bestemt holdout-split, men fjerner ikke datasættets begrænsninger.
- 42 er et almindeligt kulturelt programmeringsvalg, blandt andet som reference til *The Hitchhiker's Guide to the Galaxy*.

**Mundtligt anker:** “Seed 42 fastlåser den pseudo-tilfældige blanding, så eksperimentet kan gentages med samme split. Tallet er vilkårligt og forbedrer ikke modellen. Med så få optagelser kan andre seeds give andre resultater, og derfor supplerer jeg holdout med cross-validation.”

### Hvorfor er 80 % usikkert?

Testsettet har kun fem eksempler. Én fejl ændrer accuracy med 20 procentpoint. Resultatet viser, at prototypen kan fungere, men er ikke præcis evidens for fremtidig performance.

## Kodeoverblik – fra `config.yaml` til metrics

### `config.yaml`: Parametre, ikke programlogik

YAML-filen samler de værdier, som Python-pipelinen skal bruge: datamappe, klasser, 400 Hz, fire sekunder, 0,25 sekunders stride, de syv features, MLP-lagene `[32, 16]`, testandel, seed og beslutningstærskler.

- **Hvad:** En menneskeligt læsbar konfigurationsfil.
- **Hvordan:** `load_config()` bruger `yaml.safe_load()` og returnerer værdierne som Python-dictionaries.
- **Hvorfor:** Parametre kan ændres og dokumenteres ét sted frem for at blive spredt som hardcodede værdier.
- **Begrænsning:** En værdi i config har kun effekt, hvis koden faktisk læser og anvender den. Config-filen udfører ikke noget i sig selv.

### `load_raw_data()`: Fra mange CSV-filer til én tabel

```python
files = sorted(raw_dir.rglob(file_glob))
for fp in files:
    df = pd.read_csv(fp)
    df["__source_file"] = fp.name
    chunks.append(df)
return pd.concat(chunks, ignore_index=True)
```

- `rglob()` finder CSV-filer rekursivt i datamappen.
- Hver fil indlæses som en pandas `DataFrame`.
- `__source_file` gemmer, hvilken fysisk optagelse hver række kommer fra.
- Tabellerne samles, men filgrænsen bevares gennem kolonnen.

**Hvorfor er filgrænsen vigtig?** Et træningsvindue må ikke begynde i slutningen af én optagelse og fortsætte ind i en anden gestus. `build_dataset()` grupperer derfor efter `__source_file`, før der dannes vinduer.

### `build_dataset()`: Ét eksempel per endelig optagelse

Det endelige datasæt har 1.600 samples per CSV, og vinduet kræver også 1.600 samples. Derfor giver hver fil præcis ét træningseksempel. Stride på 100 samples får først betydning, hvis en fil er længere end ét vindue. I LIVE-firmwaren betyder stride derimod, at 1.500 gamle samples beholdes, og 100 nye giver næste inference efter 0,25 sekund.

```python
for _, recording in df.groupby("__source_file"):
    for window in sliding_windows(recording, 400, 4.0, 0.25):
        X_list.append(extract_features_for_window(window, use_mag=True))
        y_list.append(majority_label(window))
```

**Output:** `X` er en matrix med én række per optagelse og 28 kolonner per række. `y` er den tilhørende liste af facitlabels.

### `LabelEncoder`: Tekstlabels bliver til heltal

`LabelEncoder.fit_transform(y)` omdanner eksempelvis klassestrenge til tal, som scikit-learn kan arbejde med. Scikit-learn sorterer normalt labels alfabetisk. Projektets ønskede firmwareorden er en anden, så `export_model.py` remapper outputlaget til rækkefølgen fra `config.yaml`.

Det er vigtigt, fordi outputneuron nummer 1 ellers kunne blive fortolket som den forkerte klasse på Photon 2, selv om de matematiske scores var korrekte.

### Split og stratificering

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc,
    test_size=0.2,
    random_state=42,
    stratify=y_enc,
)
```

- `test_size=0.2`: fem af 25 optagelser bliver testdata.
- `stratify=y_enc`: én optagelse fra hver klasse kommer i testdelen.
- `random_state=42`: det samme pseudo-tilfældige split kan genskabes.
- Funktionen returnerer både features og labels for train og test.

### StandardScaler uden data leakage

```python
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)
```

`fit_transform(X_train)` lærer middelværdi og standardafvigelse fra træningsdata og skalerer dem. `transform(X_test)` genbruger de allerede lærte værdier uden at lære fra testdata. Hvis der blev kaldt `fit_transform()` på testdata, ville evalueringen ikke længere simulere helt ukendte data.

### `model.fit()`: Her foregår træningen

`train_model()` opretter et `MLPClassifier` med lagene `28 → 32 → 16 → 5`. Kaldet:

```python
model.fit(X_train_s, y_train)
```

udfører den iterative træning. Scikit-learn håndterer forward-pass, loss, backpropagation og opdatering af vægte. At der kun står én linje betyder derfor ikke, at træningen matematisk kun er én operation; biblioteket skjuler træningsløkken bag API-kaldet.

**Batch size i den konkrete kørsel:** `config.yaml` angiver batch size 32, men holdout-træningsdelen indeholder kun 20 eksempler. Scikit-learn udsender derfor en advarsel og reducerer automatisk batch size til 20. Træningen er i praksis full-batch på dette meget lille træningssæt. Det stopper ikke træningen, men viser endnu en konsekvens af det lille datasæt.

### `predict()` og metrics

```python
y_pred = model.predict(X_test_s)
acc = accuracy_score(y_test, y_pred)
```

`predict()` udfører inference på de fem testeksempler. De forudsagte labels sammenlignes derefter med facit i `y_test`. Precision, recall, F1 og confusion matrix beregnes fra de samme to lister.

### `train.py` kontra `export_model.py`

- `train.py` bygger datasættet, træner en model og udskriver holdout-metrics. Den gemmer ikke den deployerede C++-model.
- `export_model.py` genbruger data- og featurefunktionerne, træner MLP'et og eksporterer scaler, vægte, biases og klasserækkefølge til `model_data.cpp` samt artefakter.
- Femfolds-cross-validation er en supplerende evaluering; den køres ikke af den nuværende `train.py`-hovedfunktion.

**Mundtligt anker:** “Konfigurationen styrer parametrene. Python indlæser hver CSV og bevarer optagelsesgrænserne, komprimerer hvert vindue til 28 features og laver et stratificeret 80/20-split. StandardScaler fittes kun på træningsdelen. `model.fit()` udfører selve træningen med backpropagation, og `predict()` evaluerer på holdout-data. Eksportscriptet omsætter derefter den lærte scaler og MLP-parametre til C++.”

---

## 12. Python-model til C++

### Træning i Python

Python-koden indlæser CSV-data, skaber vinduer, beregner features, splitter datasættet, fitter StandardScaler, træner MLP'et og beregner metrics.

### Eksport

Scalerens værdier, klassernes rækkefølge, modellens vægte og biases eksporteres som konstante C++-arrays.

### Inference i C++

Firmwaren beregner de samme features og udfører:

`skalering → lag 1 + ReLU → lag 2 + ReLU → outputlag + softmax`

Det er en rigtig forward-pass på enheden. Pickle-filen kører ikke direkte på Photon 2.

### Kodekort: Scaler og forward-pass – Slides 15–16

Det centrale princip i `model_infer()` i `Product/firmware/src/model_data.cpp` er:

```cpp
act[i] = (features[i] - scalerMean[i]) / scalerScale[i];

acc = kBiasesFlat[bOff + o];
for (size_t i = 0; i < inDim; ++i)
    acc += act[i] * kWeightsFlat[wOff + i*outDim + o];
next[o] = acc;

relu_inplace(act, outDim); // kun skjulte lag
// Til sidst: softmax til fem output-sandsynligheder
```

Udsnittet er pædagogisk forkortet; de eksporterede arrays hedder blandt andet `kScalerMean`, `kScalerScale`, `kWeightsFlat` og `kBiasesFlat` i den faktiske kode.

**Hvad gør koden?** Den omdanner de 28 features til fem klassescores og derefter fem tal mellem 0 og 1, som summerer til 1.

**Hvordan gør den?** Først anvendes den StandardScaler, der blev fitted på træningsdata. Derefter beregner hvert neuron en vægtet sum plus bias. ReLU fjerner negative aktiveringer i de skjulte lag, og softmax normaliserer outputlaget.

**Hvorfor ligger dette på Photon 2?** Det er inference: anvendelse af allerede lærte og eksporterede parametre på nye sensordata. Det kræver kun et forward-pass. Backpropagation, gradienter og ændring af vægte foregår kun under offline træning på computeren.

**Mundtligt anker:** “På Photon 2 starter modelkoden med at standardisere de 28 features med træningssættets gemte middelværdier og skalaer. Derefter beregner hvert lag vægtet sum plus bias. De skjulte lag bruger ReLU, og outputlaget bruger softmax. Det er kun et forward-pass med faste parametre; der trænes ikke på enheden.”

### Vigtig risiko

Featureorden og preprocessing skal være identiske i Python og C++. Selv en korrekt model giver forkerte resultater, hvis inputkontrakten afviger.

Projektet har ikke en færdig automatiseret “golden vector”-test, som sender præcis det samme vindue gennem både Python- og C++-implementationen og sammenligner alle 28 features og fem scores numerisk. Formlerne og rækkefølgen er implementeret parallelt og dokumenteret, men en sådan parity-test ville være den stærkeste næste verifikation af eksportkæden.

## TinyML-toolchain

En toolchain er kæden af værktøjer fra dataindsamling til en kørende embedded model. Der findes ikke én universel TinyML-proces; valg af værktøjer afhænger af model, hardware og krav.

- Data indsamles og analyseres typisk i Python eller notebooks.
- Modellen trænes og evalueres på en computer.
- Modellen konverteres eller eksporteres til et format, embedded software kan bruge.
- Firmware kompileres og flashes til enheden.
- Den deployede løsning måles på accuracy, latency, hukommelse, energi og robusthed.
- Resultaterne bruges til en ny iteration af data, features, model eller firmware.

**I mit projekt:** Python og scikit-learn bruges til træning. Egne eksportværktøjer genererer C++-arrays og forward-pass-kode til Particle Workbench-projektet.

## emlearn

emlearn er et værktøj til at konvertere udvalgte klassiske machine-learning-modeller til effektiv C-kode, så de kan køre på microcontrollere.

- Det kan blandt andet bruges til træbaserede modeller.
- Modellen trænes normalt i Python og konverteres derefter.
- Fordelen er, at man ikke behøver implementere hele inferencealgoritmen manuelt.
- Kun understøttede modeltyper og operationer kan konverteres.

**I mit projekt:** emlearn blev ikke brugt i den endelige løsning; MLP-parametrene blev eksporteret til en egen C++ forward-pass.

## AIfES

AIfES er et embedded neuralt-netværksbibliotek, der kan udføre inference og i nogle tilfælde træning direkte på microcontrollere.

- Det er rettet mod små neurale netværk på begrænset hardware.
- Det kan understøtte on-device training, hvor modellen lærer på selve enheden.
- Biblioteker reducerer implementeringsarbejde, men tilføjer deres egne API'er og begrænsninger.

**I mit projekt:** AIfES blev ikke brugt; netværkets forward-pass blev implementeret direkte i C++.

## Edge Impulse

Edge Impulse er en end-to-end-platform til indsamling, signalbehandling, modeltræning, evaluering og generering af embedded biblioteker.

- Platformen kan gøre prototyping og deployment hurtigere.
- Den indeholder færdige processing blocks og modelværktøjer.
- Abstraktionen gør processen lettere, men kan skjule nogle implementeringsdetaljer.
- Man skal stadig forstå data, validering og hardwarebegrænsninger.

**I mit projekt:** Pipen blev bygget med egne Python- og C++-komponenter frem for Edge Impulse.

## CMSIS og hardwareoptimering

CMSIS er Arm-standarder og biblioteker til Cortex-processorer. CMSIS-DSP og CMSIS-NN indeholder optimerede signalbehandlings- og neurale netværksoperationer, som kan udnytte processorens instruktioner bedre end generisk kode.

- Det kan reducere inferenstid og nogle gange hukommelsesforbrug.
- Det er mest relevant, når profiling viser en reel flaskehals.
- Optimering kan gøre koden mindre portabel og mere kompleks.
- Før og efter optimering skal numerisk korrekthed kontrolleres.

**I mit projekt:** Der blev ikke anvendt CMSIS-optimering. Forward-pass på cirka 0,35 ms var allerede langt under projektets mål på 50 ms.

## Offline training og on-device training

Ved offline training trænes modellen på en computer og deployeres derefter som faste parametre. Ved on-device training opdaterer den embedded enhed selv hele eller dele af modellen.

- Offline training giver adgang til mere regnekraft og nemmere analyse.
- On-device training kan muliggøre personlig tilpasning og løbende adaptation.
- On-device training kræver ekstra RAM, beregning, energi og sikker håndtering af nye data.
- Inference er normalt langt billigere end træning.

**I mit projekt:** Træningen er offline i Python. Photon 2 udfører kun inference og ændrer ikke modellens vægte.

### Designbegrundelse: Hvorfor ikke selvtræning på Photon 2?

Valget er en bevidst opdeling mellem en udviklingsplatform og en deployment-platform:

- Computeren har de nødvendige Python-værktøjer, mere regnekraft og bedre muligheder for at inspicere loss, metrics og fejl.
- Backpropagation kræver gemte aktiveringer, gradienter for vægte og biases samt ekstra optimizer-tilstand. Det kræver mere RAM, beregning og energi end et forward-pass.
- Supervised selvtræning kræver korrekte labels til nye input. Under normal LIVE-brug ved Photon 2 ikke automatisk, om brugerens bevægelse var `tap1`, `tap2` eller en anden klasse.
- Offline træning gør datasplit, preprocessing, modelversion og evaluering lettere at reproducere og kontrollere.
- På Photon 2 er opgaven at anvende en kontrolleret, færdigtrænet model hurtigt og stabilt, ikke at ændre modellen under brug.

Det er ikke en påstand om, at enhver form for on-device training er fysisk umulig. Den lille model kunne muligvis trænes eller finjusteres med en specialiseret implementation, men det ville kræve en anden data-, label- og valideringsarkitektur og lå uden for projektets scope.

**Mundtligt anker:** “Jeg har bevidst adskilt træning og deployment. Computeren udfører den dyre og kontrollerbare træningsproces med backpropagation, mens Photon 2 kun udfører den billigere forward-pass med faste parametre. Det reducerer RAM-, beregnings- og energibehovet, undgår problemet med manglende labels under LIVE-brug og gør modellen reproducerbar. On-device training er ikke principielt umuligt, men det er ikke nødvendigt eller implementeret i dette projekt.”

---

## 13. Firmware og beslutningslogik

### Vinduer og sliding windows

Det første vindue kræver 1.600 samples. Derefter beholdes de nyeste 1.500, og 100 nye samples giver en ny inference hvert 0,25 sekund.

### Confidence threshold

En prediction under 0,75 accepteres ikke som en handling. Det reducerer usikre events, men kan også afvise korrekte gestusser.

### Beslutningsstabilisering

Samme sikre klasse skal forekomme tre gange i træk. Det stabiliserer output, men tilføjer forsinkelse.

### Kodekort: `updateDecision()` – Slide 16

```cpp
const bool confident = score >= 0.75f;
const int candidate = confident ? classIdx : CLASS_IDLE;

// historikken opdateres med candidate
if (historyCount < 3) return -1;
if (history[0] != history[1] || history[1] != history[2])
    return -1;
if (nowMs - lastEventMs < 4000) return -1;

return history[0];
```

Udsnittet er forkortet, men følger den faktiske kontrolrækkefølge.

- **Hvad betyder `return -1`?** Der er endnu ingen godkendt handling. Det er en intern sentinel-værdi og ikke en modelklasse.
- **Hvad betyder `?:`?** Det er en ternary operator: hvis `confident` er sand, bruges `classIdx`; ellers bruges `CLASS_IDLE`.
- **Hvorfor tre ens?** En enkelt ustabil prediction må ikke udløse en kommando.
- **Hvorfor debounce?** Det samme fysiske input bliver liggende i flere overlappende vinduer og må kun udløse én handling.
- **Tradeoff:** Filtrene reducerer falske events, men øger latenstid og kan undertrykke korrekte, men kortvarigt ustabile gestusser.

### Tap-kontrol

En supplerende algoritme tæller tydelige impacts og hjælper med at skelne tap1, tap2 og tap3. Løsningen er derfor hybrid: ML klassificerer mønstret, og regler kontrollerer handlingen.

**Vigtig resultatgrænse:** Python-metrics måler MLP-klassifikationen på holdout-data. LIVE-firmwaren tilføjer bagefter impact count og beslutningsfiltre. Den komplette deployede adfærd er derfor en hybrid pipeline, og dens samlede event-performance er ikke identisk med holdout-accuracy for MLP'et alene.

### Debounce

Efter en godkendt gestus forhindrer fire sekunders debounce den samme fysiske gestus i at udløse flere kommandoer.

### Non-blocking firmware

LED-mønstrene styres som en tilstandsmaskine uden lange `delay()`-kald. Sampling og anden logik kan derfor fortsætte, mens LED'en blinker.

### Driftsformer

- **DEBUG:** Diagnostik og verbose output uden normale gestushandlinger.
- **TRAINING:** Guidet dataindsamling.
- **LIVE:** Lokal inference, events og RGB-feedback.

---

## 14. Begrænsninger og næste eksperiment

### Begrænsninger

- Kun 25 accepterede optagelser.
- Kun én person.
- Kun én afsluttende session i deploy-datasættet.
- Kun ét testeksempel per klasse.
- Mulig session leakage eller korrelation mellem train og test.
- `tap1` og `tap2` kan ligne hinanden.
- Kvalitetsfiltrering kan gøre data mindre realistiske.
- Fysisk LIVE-verifikation var ikke en blind accuracy-test.
- Lav inferenstid er ikke det samme som lav samlet brugeroplevet responstid.

### Bedste næste eksperiment

Indsaml data fra flere personer og sessioner. Hold en hel ny person eller session fuldstændigt ude under udviklingen og brug den som blind test. Mål derefter per-klasse performance, false triggers under længere idle-perioder og samlet responstid.

### Stærk konklusion

> “Projektet demonstrerer en fungerende end-to-end TinyML-prototype. Det dokumenterer ikke endnu robust generalisering til nye brugere eller situationer.”

## Iterativ ML-udvikling og MLOps-tankegang

Et ML-system udvikles normalt iterativt. Fejl kan skyldes data, labels, preprocessing, modellen, deployment eller ændringer i den virkelige verden. Derfor gentager man måling, analyse, ændring, deployment og overvågning.

- En bedre model kan ikke kompensere for dårlige eller irrelevante data.
- Offline metrics og live performance skal begge undersøges.
- Model-, scaler-, feature- og firmwareversioner skal passe sammen.
- Nye data kan vise, at krav eller klasser skal omdefineres.
- Monitoring kan afsløre data drift, timingproblemer og false triggers efter deployment.

**I mit projekt:** Forløbet gik fra 50 Hz-data til 400 Hz, kvalitetskontrolleret dataindsamling, ny træning, eksport, firmwarebuild og fysisk LIVE-verifikation.

---

## 15. Grundbegreber fra pensum

### TinyML

Machine learning på ressourcebegrænset embedded hardware tæt på sensoren. Fordele kan være offline funktion, lav kommunikationslatens, mindre datatransmission og lokal behandling. Ulemper er begrænset RAM, flash, regnekraft og energi.

## Microcontroller kontra almindelig computer

En microcontroller samler processor, hukommelse og hardwareperiferi på en chip og er lavet til styring tæt på sensorer og aktuatorer. Den har normalt færre ressourcer end en pc og kører ofte uden et fuldt desktop-operativsystem.

- RAM og flash er begrænsede og har forskellige roller.
- Real-time-adfærd og forudsigelig timing kan være vigtigere end maksimal throughput.
- Sensorinterfaces som I2C, SPI og ADC er centrale.
- Dynamisk hukommelse og store runtime-frameworks undgås ofte.
- Modellen skal vurderes som del af hele firmwareproduktet, ikke isoleret.

**I mit projekt:** Photon 2 sampler ADXL343, holder en tidsseriebuffer, beregner features, kører modellen og styrer serial-output og LED.

### Klassifikation, regression og anomaly detection

Forudsigelse af en diskret kategori. Bruges i projektet.

#### Regression

Forudsigelse af en kontinuerlig numerisk værdi, eksempelvis temperatur eller resterende levetid.

#### Anomaly detection

Identifikation af observationer, som afviger fra det normale. Det kan bruges, når man har gode normaldata, men få eksempler på alle mulige fejl.

### Inference

Anvendelse af en allerede trænet model på nye input. Træning lærer parametrene; inference bruger dem.

Den samlede inferenskæde i projektet er:

1. Photon 2 opsamler 1.600 XYZ-samples i et firesekunders vindue.
2. Magnitude beregnes, og kanalerne mean-centres.
3. De 28 features beregnes i samme orden som under træning.
4. Features standardiseres med de eksporterede scaler-parametre.
5. MLP'et udfører forward-pass og softmax.
6. Den største score giver en klassekandidat.
7. Confidence-threshold, tre ens predictions, tap-kontrol og debounce afgør, om kandidaten må blive til en handling.

Det første komplette vindue kræver fire sekunders data. Derefter beholdes de nyeste 1.500 samples, og 100 nye samples giver en ny modelkørsel hvert `100 / 400 = 0,25` sekund.

Den registrerede modelinferens tog cirka 345 µs i gennemsnit og 364 µs maksimalt. Timeren ligger omkring `model_infer()` efter `extractFeatures()`. Tallet omfatter derfor scaler og MLP-forward-pass, men ikke fire sekunders dataopsamling eller feature extraction. Lav modelinferens er således ikke det samme som 345 µs samlet brugeroplevet responstid.

Softmax-outputtet er en relativ modelscore og ikke en garanti for en korrekt eller perfekt kalibreret sandsynlighed. Derfor kræver firmwaren mindst `0,75` confidence og stabilitet over tre predictions, før en ikke-idle-klasse accepteres.

**Mundtligt anker:** “Inferens er anvendelsen af den allerede trænede model på nye data. Photon 2 beregner de samme features og den samme skalering som Python og udfører derefter et forward-pass. Vægtene ændres ikke. Modellens kandidat filtreres bagefter af confidence og stabilitetsregler, før en kommando udsendes.”

### Latency og responstid

Tiden fra et relevant startpunkt til et resultat. Man skal angive, om man mener modelberegning, vinduesopsamling eller samlet brugeroplevet responstid.

### Flash og RAM

- **Flash:** Permanent lager til firmware og modelkonstanter.
- **RAM:** Arbejdshukommelse til blandt andet buffers, mellemresultater og runtime-tilstand.

### Kvantisering

Repræsentation af vægte og eventuelt aktiveringer med lavere præcision, eksempelvis int8 frem for float32. Det kan reducere størrelse og beregningsbehov, men kan påvirke accuracy. Projektets endelige model bruger float32 og er ikke kvantiseret.

- Float32 bruger normalt 32 bit per tal, mens int8 bruger 8 bit.
- Int8-vægte kan derfor fylde omtrent en fjerdedel før anden overhead.
- Skalering og zero-point bruges ofte til at mappe mellem reelle værdier og heltal.
- Post-training quantization udføres efter træning.
- Quantization-aware training simulerer kvantisering under træningen.
- Accuracy og numerisk paritet skal måles efter konverteringen.

**I mit projekt:** Kvantisering blev ikke nødvendig for at få modellen til at passe eller opfylde latensmålet. Det er perspektivering, ikke et udført resultat.

## Pruning

Pruning fjerner vægte, neuroner eller forbindelser, som vurderes at bidrage lidt til modellens output. Målet er en mindre eller billigere model.

- Unstructured pruning sætter individuelle vægte til nul.
- Structured pruning fjerner hele neuroner, kanaler eller filtre.
- En sparse model bliver kun hurtigere, hvis runtime og hardware kan udnytte sparsiteten.
- Fine-tuning efter pruning kan genvinde tabt accuracy.
- Pruning skal evalueres på både modelkvalitet og den reelle embedded implementering.

**I mit projekt:** Modellen blev ikke prunet, fordi den allerede var lille og hurtig nok.

## Low-power-design

Low-power-design handler om at reducere enhedens energiforbrug, ikke kun modellens inferenstid. Sensor, CPU, radio, LED og vågentid bidrager alle til forbruget.

- Enheden kan sove mellem relevante målinger.
- Lavere samplingfrekvens reducerer ofte sensor- og CPU-arbejde.
- Eventbaseret aktivering kan undgå kontinuerlig tung inference.
- Lokal behandling kan være billigere end at sende rå data trådløst.
- Energi per inference og gennemsnitligt effektforbrug er forskellige målinger.
- Optimering kræver faktiske strømmålinger; hurtig kode er ikke automatisk lavenergi.

**I mit projekt:** Energiforbruget blev ikke målt. Systemet prioriterede funktionalitet og kontinuerlig sampling ved 400 Hz.

## K-means anomaly detection

K-means grupperer data omkring et valgt antal centre. Ved anomaly detection kan afstanden til det nærmeste center bruges som anomaly score: stor afstand kan betyde, at observationen ikke ligner normaldataene.

- K-means er unsupervised.
- Antallet af klynger, `k`, vælges på forhånd.
- Features bør ofte skaleres før afstandsberegning.
- Metoden antager nogenlunde kompakte grupper og kan være følsom over for outliers.
- En threshold afgør, hvornår en afstand betragtes som anomal.

**I mit projekt:** K-means anvendes ikke; alle fem ønskede klasser er labellede og trænes supervised.

## Gaussian Mixture Model – GMM

En GMM beskriver data som en blanding af flere Gaussiske fordelinger. Den kan give en likelihood for, hvor sandsynligt et nyt eksempel er under den lærte normalfordeling. Lav likelihood kan bruges som tegn på en anomaly.

- GMM er probabilistisk og kan beskrive overlappende grupper.
- Hver komponent har blandt andet middelværdi og kovarians.
- Antal komponenter vælges som en modelbeslutning.
- Metoden afhænger af, hvor rimeligt de Gaussiske antagelser passer til dataene.

**I mit projekt:** GMM anvendes ikke, fordi opgaven er direkte femklasseklassifikation.

## Autoencoder til anomaly detection

En autoencoder er et neuralt netværk, der trænes til at genskabe sit input gennem en komprimeret intern repræsentation. Hvis den primært trænes på normaldata, vil en stor reconstruction error på et nyt input kunne indikere en anomaly.

- Encoderen komprimerer inputtet.
- Decoderen forsøger at rekonstruere det.
- Reconstruction error måler forskellen mellem input og rekonstruktion.
- En threshold omsætter fejlen til normal/anomal.
- Hvis autoencoderen er for kraftig, kan den også blive god til at rekonstruere anomalier.

**I mit projekt:** En autoencoder anvendes ikke. Projektet har labels for alle fem kendte klasser og bruger derfor supervised klassifikation.

---

## AI-brug

AI blev brugt til forslag, fejlsøgning, struktur og sproglig redigering. De fysiske valg, dataindsamlingen, målingerne og den endelige vurdering blev udført og kontrolleret gennem kodegennemgang, træning, build og fysisk test. Med mere tid ville jeg dokumentere flere teoretiske mellemregninger og valideringer selvstændigt.

## Kildegrundlag i rapporten

Rapportens kilder har forskellige funktioner. En primær teknisk kilde dokumenterer konkrete krav eller specifikationer. En lærebog forklarer teori og metode. Projektets egne filer og målinger dokumenterer, hvad der faktisk blev implementeret og observeret.

- Brug producentens datablad til hardwareegenskaber.
- Brug bibliotekets officielle dokumentation til den præcise softwareadfærd.
- Brug lærebøger til generelle ML-principper og sammenhænge.
- Brug egne data, kode og målinger til projektets resultater.
- En ekstern kilde kan ikke erstatte evidens for, at ens egen prototype virker.

## Reference [1] – kursets TinyML-introduktion

Kursussiden *Welcome to TinyML* beskriver kursets forståelse af TinyML som krydsfeltet mellem machine learning, signalbehandling og embedded IoT. Den fremhæver datasæt, preprocessing, feature engineering, embedded deployment, optimering og low-power-design.

- Kilden bruges til at placere projektet i kursets faglige ramme.
- Den er valgt, fordi den er den officielle beskrivelse af netop dette kursus.
- Den er ikke en detaljeret videnskabelig definition af alle TinyML-emner.
- En lærebog eller forskningsartikel kunne give mere teori, men kan ikke definere underviserens konkrete kursusmål.

**I rapporten:** [1] understøtter introduktionens beskrivelse af, hvad kurset arbejder med.

## Reference [2] – semesterprojektets krav

Projektbriefen er den autoritative kilde til afleveringskrav, hardwarekrav og eksamensform.

- Den kræver Photon 2, lokal sensor, egne labellede data, preprocessing og en ML-/DL-algoritme.
- Den kræver observerbart output og deling af kode, data og dokumentation.
- Den siger, at rapporten bør sigte mod cirka 20 sider.
- Den angiver højst fem minutters demo og cirka 50/50 mellem rapport og øvrigt pensum.
- Ingen lærebog kan bruges som alternativ til de lokale eksamenskrav.

**I rapporten:** [2] bruges i introduktion, kravsporbarhed og forklaringen af, hvorfor løsningen ikke må være ren regelprogrammering.

## Reference [3] – ADXL343-databladet

Analog Devices' datablad er den primære tekniske kilde til accelerometerets elektriske og målte egenskaber.

- Det dokumenterer måleområderne ±2, ±4, ±8 og ±16 g.
- Det dokumenterer full-resolution scale factor på cirka 3,9 mg per LSB.
- Det beskriver output data rates, registre, I2C-adresser, device-ID og støjegenskaber.
- Producentens datablad vælges frem for en tilfældig tutorial, fordi specifikationerne kommer fra den ansvarlige producent.
- En library-guide kan vise kodebrug, men er svagere som kilde til sensorens fysiske grænser.

**I rapporten:** [3] understøtter sensorområde, opløsning, maksimal samplingfrekvens og bemærkningen om støj over 100 Hz.

## Reference [4] – Photon 2-dokumentation

Particles officielle Photon 2-datablad dokumenterer den konkrete embedded platforms processor, hukommelse og interfaces.

- Photon 2 har en 200 MHz Arm Cortex-M33.
- Dokumentationen angiver den tilgængelige flash og RAM.
- Producentdokumentationen er valgt, fordi hardwarevarianter og Device OS-forhold kan være produktspecifikke.
- En generel Cortex-M33-kilde beskriver CPU-arkitekturen, men ikke nødvendigvis Photon 2-kortets samlede ressourcer.

**I rapporten:** [4] bruges til at vurdere, om model, buffer og firmware kan være på enheden.

## Reference [5] – scikit-learn StandardScaler

Den officielle API-dokumentation beskriver den konkrete `StandardScaler`, som koden anvender.

- Dokumentationen angiver transformationen `z = (x − μ) / σ`.
- `fit` lærer middelværdi og skala fra træningsdata.
- `transform` genbruger de lærte værdier på nye data.
- API-dokumentationen er valgt frem for kun en lærebog, fordi den beskriver den faktiske klasse og dens implementeringskontrakt.
- Lærebøgerne forklarer bedre, hvorfor skalering hjælper optimeringen, men er ikke den mest præcise kilde til API-adfærd.

**I rapporten:** [5] citeres direkte ved StandardScaler-formlen og eksporten af scalerens værdier til C++.

## Reference [6] – scikit-learn MLPClassifier

Scikit-learns officielle user guide beskriver den modelklasse, der faktisk trænes.

- Den beskriver et feedforward MLP med supervised træning.
- Den forklarer backpropagation og de understøttede aktiveringsfunktioner.
- Ved flerklasseklassifikation anvendes softmax på outputtet.
- Dokumentationen er valgt til implementeringspåstande, fordi projektet bruger `MLPClassifier` direkte.
- En generel neural-netværksbog kan forklare matematikken dybere, men ikke nødvendigvis scikit-learns konkrete standarder og attributter.

**I rapporten:** [6] citeres ved beskrivelsen af MLP, backpropagation og softmax.

## Reference [7] – Hands-On Machine Learning

Aurélien Gérons *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*, tredje udgave, er bred baggrundslitteratur til den samlede ML-proces.

Relevante kapitler i den lokale PDF:

- Kapitel 1, PDF-side 31: machine-learning-landskabet.
- Kapitel 2, PDF-side 67: et end-to-end machine-learning-projekt.
- Kapitel 3, PDF-side 131: klassifikation, confusion matrix, precision og recall.
- Kapitel 4, PDF-side 159: træning, loss og optimering.
- Kapitel 7, PDF-side 239: ensembles og random forests.
- Kapitel 9, PDF-side 287: unsupervised learning og clustering.
- Kapitel 10, PDF-side 327: neuroner, MLP, backpropagation, ReLU og softmax.
- Kapitel 15, PDF-side 565: sekvensbehandling med blandt andet CNN'er.
- Kapitel 17, PDF-side 663: autoencodere.
- Appendix A, PDF-side 807: projektcheckliste fra problem til deployment.

- Bogen er valgt, fordi den forbinder teori med praktiske scikit-learn-workflows.
- Den er mere pædagogisk og sammenhængende end en samling API-sider.
- Den bruger også Keras og TensorFlow, som ikke er projektets deploymentteknologi.
- Derfor bruges den bedst til generelle principper, ikke som bevis for den konkrete firmware.

**Vigtig præcision:** [7] står i rapportens litteraturliste, men er ikke citeret ved en bestemt sætning i brødteksten. Den bør omtales som baggrundslitteratur.

## Reference [8] – scikit-learn-artiklen

Pedregosa et al. fra *Journal of Machine Learning Research* introducerer scikit-learn som et open-source machine-learning-bibliotek til Python.

- Artiklen er en fagfællebedømt kilde til bibliotekets akademiske oprindelse og design.
- Den er ikke den bedste kilde til nutidige detaljer om en bestemt API-metode.
- Officiel API-dokumentation er mere præcis for `StandardScaler` og `MLPClassifier`.
- Artiklen kan begrunde valg af scikit-learn som etableret værktøj, men ikke projektets målte accuracy.

**Vigtig præcision:** [8] står i litteraturlisten, men er ikke citeret ved en bestemt sætning i rapportens brødtekst.

## Reference [9] – Machine Learning with PyTorch and Scikit-Learn

Raschka, Liu og Mirjalilis *Machine Learning with PyTorch and Scikit-Learn* er særlig relevant til preprocessing, evaluering og neural-netværksfundamentet.

Relevante kapitler i den lokale PDF:

- Kapitel 1, PDF-side 30: supervised, unsupervised og reinforcement learning samt ML-workflow.
- Kapitel 3, PDF-side 82: klassifikationsalgoritmer i scikit-learn.
- Kapitel 4, PDF-side 134: train/test-split, feature scaling og feature selection.
- Kapitel 6, PDF-side 200: k-fold-cross-validation, hyperparametre og metrics.
- Kapitel 7, PDF-side 234: ensemble learning.
- Kapitel 10, PDF-side 334: K-means og clustering.
- Kapitel 11, PDF-side 364: MLP implementeret fra bunden, forward-pass og backpropagation.
- Kapitel 12, PDF-side 398: neurale netværk og aktiveringsfunktioner.
- Kapitel 14, PDF-side 480: convolutional neural networks.
- Kapitel 15, PDF-side 528: sekventielle data.

- Bogen er valgt, fordi dens scikit-learn-kapitler ligger tæt på projektets faktiske workflow.
- Den forklarer matematik og metode dybere end API-dokumentationen.
- PyTorch-delene er baggrundsviden og blev ikke brugt til implementeringen.

**Vigtig præcision:** [9] står i rapportens litteraturliste, men er ikke citeret ved en bestemt sætning i brødteksten. Den bør omtales som baggrundslitteratur.

## Reference [10] og [11] – AI-værktøjer

BlackBox AI's og OpenAI Codex' officielle sider bruges kun til transparent at identificere de anvendte hjælpeværktøjer.

- De er ikke kilder til sensorens specifikationer.
- De er ikke kilder til projektets målinger eller modelresultater.
- De dokumenterer ikke, at AI-genereret kode er korrekt.
- Korrekthed blev i stedet kontrolleret gennem kodegennemgang, data, træning, build og fysisk test.

## Valg af kildetype

Den korte prioritering er:

1. **Kursuskrav:** Kursets egen projektbrief.
2. **Hardwaretal:** Producentens datablad.
3. **Konkret softwareadfærd:** Officiel API- eller user-guide.
4. **Generel teori:** Anerkendte lærebøger og fagfællebedømte artikler.
5. **Egne resultater:** Reproducerbar kode, data, logs og fysisk måling.

Den samme kilde er ikke bedst til alt. Et datablad er stærkt til sensorens elektriske specifikationer, men forklarer ikke cross-validation. En lærebog forklarer backpropagation, men dokumenterer ikke Photon 2's RAM. Officiel scikit-learn-dokumentation forklarer API'en, men beviser ikke, at den deployede C++-kode er numerisk identisk.

---

## Spørgsmålszoner i præsentationen

1. Efter **problem, krav og hardware**.
2. Efter **dataindsamling og preprocessing**.
3. Efter **model, matematik og deployment**.
4. Efter **resultater, begrænsninger og konklusion**.

Forslag til indledning:

> “Jeg har struktureret præsentationen kronologisk. Jeg er autistisk, og pludselige kontekstskift kan gøre det svært for mig at fastholde strukturen, selv når jeg kender stoffet. Det hjælper mig, hvis spørgsmål så vidt muligt kommer ved mine fire tydelige stoppunkter. Jeg holder selv en kort pause ved hvert af dem.”
