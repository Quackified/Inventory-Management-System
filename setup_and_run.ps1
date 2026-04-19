param(
    [switch]$Force,
    [switch]$ResetDb,
    [string]$PythonCmd = "py -3.12"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
$venvPath = Join-Path $root ".venv"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$setupStamp = Join-Path $root ".setup_complete"

function New-VenvFromCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    $pythonParts = $Command -split "\s+"
    if ($pythonParts.Count -eq 0) {
        throw "Invalid Python command: '$Command'"
    }

    Write-Host "Creating virtual environment (.venv) using: $Command" -ForegroundColor Yellow
    & $pythonParts[0] $pythonParts[1..($pythonParts.Count - 1)] -m venv $TargetPath
}

function Ensure-Dependencies {
    param(
        [switch]$Force,
        [string]$PythonCmd,
        [string]$Root,
        [string]$BackendPath,
        [string]$FrontendPath,
        [string]$VenvPath,
        [string]$VenvPython,
        [string]$SetupStamp
    )

    if (-not $Force -and (Test-Path $SetupStamp)) {
        Write-Host "Dependencies already set up. Use -Force to reinstall." -ForegroundColor Green
        return
    }

    if ($Force -and (Test-Path $VenvPath)) {
        Write-Host "Force enabled: removing existing .venv" -ForegroundColor DarkYellow
        try {
            Remove-Item $VenvPath -Recurse -Force
        } catch {
            Write-Warning "Could not remove .venv (likely in use). Continuing with the existing environment. Close terminals using .venv and rerun with -Force for a full rebuild."
        }
    }

    if (-not (Test-Path $VenvPython)) {
        New-VenvFromCommand -Command $PythonCmd -TargetPath $VenvPath
    }

    if (-not (Test-Path $VenvPython)) {
        throw "Python executable not found in .venv: $VenvPython"
    }

    $venvVersion = (& $VenvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
    if ([version]$venvVersion -ge [version]"3.13") {
        if ($PSBoundParameters.ContainsKey("PythonCmd")) {
            throw "Detected Python $venvVersion in .venv, which is not supported by this setup flow. Re-run with -PythonCmd 'py -3.12' or -PythonCmd 'py -3.11'."
        }

        Write-Warning "Detected Python $venvVersion in .venv. Rebuilding with Python 3.12 for compatibility."
        Remove-Item $VenvPath -Recurse -Force
        New-VenvFromCommand -Command "py -3.12" -TargetPath $VenvPath

        if (-not (Test-Path $VenvPython)) {
            throw "Failed to create .venv with Python 3.12"
        }
    }

    Write-Host "Bootstrapping pip/setuptools/wheel..." -ForegroundColor Yellow
    & $VenvPython -m ensurepip --upgrade
    & $VenvPython -m pip install --disable-pip-version-check --upgrade pip setuptools wheel

    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    & $VenvPython -m pip install --disable-pip-version-check -r (Join-Path $BackendPath "requirements.txt")

    if (Test-Path (Join-Path $FrontendPath "package.json")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        Push-Location $FrontendPath
        try {
            npm install
        } finally {
            Pop-Location
        }
    }

    New-Item -ItemType File -Path $SetupStamp -Force | Out-Null
    Write-Host "Dependency setup complete." -ForegroundColor Green
}

function Get-EnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$EnvFilePath,
        [Parameter(Mandatory = $true)]
        [string]$Key,
        [string]$DefaultValue = ""
    )

    if (-not (Test-Path $EnvFilePath)) {
        return $DefaultValue
    }

    foreach ($line in Get-Content $EnvFilePath) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $parts = $trimmed.Split("=", 2)
        if ($parts.Count -ne 2) {
            continue
        }

        if ($parts[0].Trim() -eq $Key) {
            return $parts[1].Trim().Trim('"').Trim("'")
        }
    }

    return $DefaultValue
}

function Test-BackendHealth {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HealthUrl
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $HealthUrl -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

Write-Host "=== Inventory Management System: Initial Setup ===" -ForegroundColor Cyan

Push-Location $root
try {
    Write-Host "Step 1/4: Dependency setup" -ForegroundColor Yellow
    Ensure-Dependencies -Force:$Force -PythonCmd $PythonCmd -Root $root -BackendPath $backendPath -FrontendPath $frontendPath -VenvPath $venvPath -VenvPython $venvPython -SetupStamp $setupStamp

    if (-not (Test-Path $venvPython)) {
        throw "Python executable not found in .venv: $venvPython"
    }

    Write-Host "Step 2/4: Database prep" -ForegroundColor Yellow
    if ($ResetDb) {
        $schemaPath = Join-Path $root "database\schema.sql"
        $seedPath = Join-Path $root "database\seed_data.sql"
        $envPath = Join-Path $backendPath ".env"
        $dbResetScript = Join-Path $root "database\reset_db.py"

        if (-not (Test-Path $dbResetScript)) {
            throw "Database reset helper not found: $dbResetScript"
        }
        if (-not (Test-Path $schemaPath)) {
            throw "Schema file not found: $schemaPath"
        }
        if (-not (Test-Path $seedPath)) {
            throw "Seed file not found: $seedPath"
        }

        Write-Host "Resetting database using schema + seed files..." -ForegroundColor Yellow
        & $venvPython $dbResetScript --schema $schemaPath --seed $seedPath --env-file $envPath
    } else {
        Write-Host "Skipping database reset. Use -ResetDb to rebuild schema + seed data." -ForegroundColor DarkGray
    }

    Write-Host "Step 3/4: Starting backend API" -ForegroundColor Yellow
    $backendPort = [int](Get-EnvValue -EnvFilePath (Join-Path $backendPath ".env") -Key "APP_PORT" -DefaultValue "8001")
    $healthUrl = "http://127.0.0.1:$backendPort/health"
    if (Test-BackendHealth -HealthUrl $healthUrl) {
        Write-Host "Backend already healthy on $healthUrl. Reusing the existing process." -ForegroundColor Green
        $backendJob = $null
    } else {
    Write-Host "Starting backend (background job)..." -ForegroundColor Yellow
    $backendJob = Start-Job -ScriptBlock {
        param($backendPath, $venvPython, $backendPort)
        Set-Location $backendPath
        & $venvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port $backendPort --app-dir .
    } -ArgumentList $backendPath, $venvPython, $backendPort

    Write-Host "Waiting for backend health check..." -ForegroundColor Yellow
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        if ($backendJob.State -in @("Failed", "Stopped", "Completed")) {
            $backendOutput = Receive-Job -Job $backendJob -Keep | Out-String
            throw "Backend job exited early. Output:`n$backendOutput"
        }
        if (Test-BackendHealth -HealthUrl $healthUrl) {
            $ready = $true
            break
        } else {
            [System.Threading.Thread]::Sleep(1000)
        }
    }

    if (-not $ready) {
        if ($backendJob) {
            $backendOutput = Receive-Job -Job $backendJob -Keep | Out-String
            throw "Backend did not become ready on $healthUrl. Output:`n$backendOutput"
        }

        throw "A process is already using port $backendPort, but $healthUrl is not responding. Stop the existing process or free the port, then rerun."
    }
    }

    Write-Host "Step 4/4: Starting frontend dev server" -ForegroundColor Yellow
    Write-Host "Starting frontend in this window..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop frontend, then backend will be stopped automatically." -ForegroundColor Cyan

    try {
        Push-Location $frontendPath
        npm run dev
    } finally {
        Pop-Location
        if ($backendJob -and $backendJob.State -eq "Running") {
            Stop-Job $backendJob | Out-Null
        }
        if ($backendJob) {
            Remove-Job $backendJob -Force | Out-Null
        }
    }
} finally {
    Pop-Location
}
