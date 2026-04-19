$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
  throw "Python executable not found in .venv: $venvPython. Run setup_and_run.ps1 first."
}

$backendJob = Start-Job -ScriptBlock {
  param($backendPath, $venvPython)
  Set-Location $backendPath
  & $venvPython -m uvicorn app.main:app --reload --app-dir .
} -ArgumentList $backendPath, $venvPython

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
