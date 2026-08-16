# One-click start af Photon 2-demoen

## Normal eksamensstart

1. Installér Particle CLI eller Particle Workbench på laptoppen.
2. Log ind mindst én gang med `particle login`.
3. Tilslut Photon 2 med USB og sørg for, at ADXL343 er forbundet.
4. Dobbeltklik på `START-PHOTON2-DEMO.cmd` i repositoryets rod.

Scriptet kontrollerer den eksporterede model, cloud-kompilerer firmwaren, flasher
den lokalt over USB, finder Photon 2-serialporten, sender `MODE LIVE` og kræver
svaret `MODE,current=LIVE` før det melder demoen klar.

## Hurtig aktivering uden ny firmwareflash

Hvis den korrekte firmware allerede er installeret, kan LIVE-mode aktiveres
uden en ny kompilering eller flash:

```powershell
.\Start-Photon2-Demo.ps1 -ActivateOnly
```

## Kontrol uden ændringer

Dette kontrollerer CLI, modelkontrakt og USB-forbindelse uden at kompilere,
flashe eller ændre enhedens mode:

```powershell
.\Start-Photon2-Demo.ps1 -CheckOnly
```

## Alternative parametre

```powershell
# Angiv serialport, hvis flere enheder er tilsluttet
.\Start-Photon2-Demo.ps1 -Port COM3

# Byg kun binærfilen
.\Start-Photon2-Demo.ps1 -BuildOnly

# Flash gennem Particle Cloud i stedet for lokalt USB
.\Start-Photon2-Demo.ps1 -FlashMethod Cloud -DeviceName TinyML_Node1
```

Den normale lokale flash bruger `--application-only`, så scriptet ikke forsøger
at opdatere Device OS under eksamensforberedelsen.
