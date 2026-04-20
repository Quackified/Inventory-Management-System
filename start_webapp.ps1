$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"

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

if (-not (Test-Path $venvPython)) {
  throw "Python executable not found in .venv: $venvPython. Run setup_and_run.ps1 first."
}

$backendJob = Start-Job -ScriptBlock {
  param($backendPath, $venvPython, $backendPort)
  Set-Location $backendPath
  & $venvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port $backendPort --app-dir .
} -ArgumentList $backendPath, $venvPython, ([int](Get-EnvValue -EnvFilePath (Join-Path $backendPath ".env") -Key "APP_PORT" -DefaultValue "20006"))

$backendPort = [int](Get-EnvValue -EnvFilePath (Join-Path $backendPath ".env") -Key "APP_PORT" -DefaultValue "20006")
$env:VITE_API_BASE_URL = "http://127.0.0.1:$backendPort"
Write-Host "Backend URL: $($env:VITE_API_BASE_URL)" -ForegroundColor DarkGray
Write-Host "Frontend URL: http://127.0.0.1:20005" -ForegroundColor DarkGray

Write-Host "Backend started in background job. Frontend will run in this window." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop frontend, then backend will be stopped automatically." -ForegroundColor Cyan

try {
  Set-Location $frontendPath
  npm run dev
} finally {
  if ($backendJob -and $backendJob.State -eq "Running") {
    Stop-Job $backendJob | Out-Null
  }
  if ($backendJob) {
    Remove-Job $backendJob -Force | Out-Null
  }
}
