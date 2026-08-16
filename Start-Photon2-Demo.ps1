[CmdletBinding()]
param(
    [ValidateSet("Local", "Cloud")]
    [string]$FlashMethod = "Local",

    [string]$DeviceName = "TinyML_Node1",

    [string]$Port,

    [switch]$BuildOnly,

    [switch]$ActivateOnly,

    [switch]$CheckOnly,

    [int]$ActivationTimeoutSeconds = 90
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Invoke-Particle {
    param([string[]]$Arguments)
    & $script:ParticleExe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Particle CLI fejlede: particle $($Arguments -join ' ')"
    }
}

function Get-PhotonPorts {
    $raw = (& $script:ParticleExe serial list 2>&1 | Out-String)
    $matches = [regex]::Matches($raw, '(?im)^\s*(COM\d+)\s+-\s+Photon 2\b')
    return @($matches | ForEach-Object { $_.Groups[1].Value.ToUpperInvariant() } | Select-Object -Unique)
}

function Resolve-PhotonPort {
    if ($Port) {
        return $Port.ToUpperInvariant()
    }

    $ports = @(Get-PhotonPorts)
    if ($ports.Count -eq 1) {
        return $ports[0]
    }
    if ($ports.Count -gt 1) {
        throw "Flere Photon 2-enheder blev fundet ($($ports -join ', ')). Kør igen med -Port COMx."
    }
    return $null
}

function Set-PhotonLiveMode {
    $deadline = [DateTime]::UtcNow.AddSeconds($ActivationTimeoutSeconds)
    $lastError = "Photon 2 serialport blev ikke fundet."

    while ([DateTime]::UtcNow -lt $deadline) {
        $selectedPort = Resolve-PhotonPort
        if (-not $selectedPort) {
            Start-Sleep -Seconds 2
            continue
        }

        $serial = $null
        try {
            $serial = [System.IO.Ports.SerialPort]::new(
                $selectedPort,
                115200,
                [System.IO.Ports.Parity]::None,
                8,
                [System.IO.Ports.StopBits]::One
            )
            $serial.NewLine = "`n"
            $serial.ReadTimeout = 500
            $serial.WriteTimeout = 1000
            $serial.DtrEnable = $true
            $serial.Open()

            # setup() waits three seconds. Waiting here also covers a device
            # that has only just reappeared after the firmware flash.
            Start-Sleep -Seconds 4
            $serial.DiscardInBuffer()
            $serial.WriteLine("MODE LIVE")
            Start-Sleep -Milliseconds 700
            $serial.WriteLine("MODE?")
            Start-Sleep -Milliseconds 900
            $response = $serial.ReadExisting()

            if ($response -match 'MODE,current=LIVE') {
                Write-Host $response.Trim() -ForegroundColor DarkGray
                Write-Host "Photon 2 kører nu i LIVE-mode på $selectedPort." -ForegroundColor Green
                return
            }

            $lastError = "Enheden svarede ikke med MODE,current=LIVE. Svar: $($response.Trim())"
        }
        catch {
            $lastError = $_.Exception.Message
        }
        finally {
            if ($serial) {
                if ($serial.IsOpen) { $serial.Close() }
                $serial.Dispose()
            }
        }

        Start-Sleep -Seconds 2
    }

    throw "Kunne ikke aktivere LIVE-mode inden for $ActivationTimeoutSeconds sekunder. $lastError"
}

$repoRoot = $PSScriptRoot
$firmwareDir = Join-Path $repoRoot "Product\firmware"
$mainCpp = Join-Path $firmwareDir "src\main.cpp"
$modelHeader = Join-Path $firmwareDir "src\model_data.h"
$buildDir = Join-Path $firmwareDir "build\current"

if ($BuildOnly -and $ActivateOnly) {
    throw "-BuildOnly og -ActivateOnly kan ikke bruges samtidig."
}

$particleCommand = Get-Command particle -ErrorAction SilentlyContinue
if (-not $particleCommand) {
    throw "Particle CLI blev ikke fundet. Installér Particle CLI/Workbench og kør scriptet igen."
}
$script:ParticleExe = $particleCommand.Source

Write-Step "Kontrollerer firmware og modelkontrakt"
if (-not (Test-Path -LiteralPath $mainCpp)) {
    throw "Firmwarekilden blev ikke fundet: $mainCpp"
}
if (-not (Test-Path -LiteralPath $modelHeader)) {
    throw "Den eksporterede model blev ikke fundet: $modelHeader"
}
$mainText = Get-Content -LiteralPath $mainCpp -Raw
$modelText = Get-Content -LiteralPath $modelHeader -Raw
if ($mainText -notmatch 'kModelReadyForLive\s*=\s*true') {
    throw "LIVE er låst i firmwaren: kModelReadyForLive er ikke true."
}
if ($modelText -notmatch 'kFeatureCount\s*=\s*28') {
    throw "Modelkontrakten er uventet: scriptet forventer 28 features."
}
Write-Host "Model klar: 28 features og LIVE release-gate er åben." -ForegroundColor Green

if ($CheckOnly) {
    Write-Step "Kontrollerer Particle CLI og USB-forbindelse"
    Write-Host "Particle CLI: $script:ParticleExe"
    $ports = @(Get-PhotonPorts)
    if ($ports.Count -eq 0) {
        Write-Host "Ingen Photon 2 blev fundet på USB. Tilslut enheden før demo-start." -ForegroundColor Yellow
    } else {
        Write-Host "Photon 2 fundet på: $($ports -join ', ')" -ForegroundColor Green
    }
    Write-Host "Check fuldført; intet blev kompileret, flashet eller ændret." -ForegroundColor Green
    exit 0
}

if ($ActivateOnly) {
    Write-Step "Aktiverer den allerede installerede firmware"
    Set-PhotonLiveMode
    exit 0
}

Write-Step "Kontrollerer Particle-login"
$whoAmI = (& $script:ParticleExe whoami 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0 -or $whoAmI -notmatch '>\s*\S+@\S+') {
    Write-Host "Particle-login mangler. Loginvinduet åbnes nu." -ForegroundColor Yellow
    Invoke-Particle @("login")
} else {
    Write-Host $whoAmI.Trim() -ForegroundColor Green
}

Write-Step "Cloud-kompilerer Photon 2-firmwaren"
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$firmwareBinary = Join-Path $buildDir "gesture-demo-$timestamp.bin"
Invoke-Particle @("compile", "photon2", $firmwareDir, "--saveTo", $firmwareBinary)
if (-not (Test-Path -LiteralPath $firmwareBinary)) {
    throw "Kompileringen meldte succes, men binærfilen blev ikke fundet: $firmwareBinary"
}
Write-Host "Firmware bygget: $firmwareBinary" -ForegroundColor Green

if ($BuildOnly) {
    Write-Host "BuildOnly fuldført; Photon 2 blev ikke flashet." -ForegroundColor Green
    exit 0
}

if ($FlashMethod -eq "Local") {
    Write-Step "Flasher Photon 2 lokalt over USB"
    Invoke-Particle @("flash", "--local", "--application-only", "--yes", $firmwareBinary)
} else {
    Write-Step "Flasher $DeviceName gennem Particle Cloud"
    Invoke-Particle @("flash", "--cloud", "--yes", $DeviceName, $firmwareBinary)
}

Write-Step "Venter på Photon 2 og aktiverer LIVE-mode"
Set-PhotonLiveMode

Write-Host "`nDEMO KLAR: udfør en gestus og observer EVENT + RGB-feedback." -ForegroundColor Green

