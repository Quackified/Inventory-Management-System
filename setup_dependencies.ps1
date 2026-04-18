param(
    [switch]$SkipVenv,
    [string]$PythonCmd = "py -3"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Inventory Management System: Dependency Setup ===" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path "requirements.txt")) {
    throw "requirements.txt not found in project root."
}

if ($SkipVenv) {
    Write-Host "Using global/current Python environment..." -ForegroundColor Yellow
    $pythonExe = $null
} else {
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment (.venv)..." -ForegroundColor Yellow
        Invoke-Expression "$PythonCmd -m venv .venv"
    } else {
        Write-Host "Virtual environment already exists (.venv)." -ForegroundColor DarkYellow
    }
    $pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        throw "Python executable not found in .venv: $pythonExe"
    }
}

if ($SkipVenv) {
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    Invoke-Expression "$PythonCmd -m pip install --upgrade pip"

    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    Invoke-Expression "$PythonCmd -m pip install -r requirements.txt"
} else {
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    & $pythonExe -m pip install --upgrade pip

    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    & $pythonExe -m pip install -r requirements.txt
}

Write-Host "" 
Write-Host "Setup complete." -ForegroundColor Green
if (-not $SkipVenv) {
    Write-Host "Activate venv with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "Run app with: python main.py" -ForegroundColor Cyan
} else {
    Write-Host "Run app with your Python command, e.g.: py -3 main.py" -ForegroundColor Cyan
}
