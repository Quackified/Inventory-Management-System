@echo off
setlocal

echo === Inventory Management System: Initial Setup ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_and_run.ps1"

if %ERRORLEVEL% neq 0 (
  echo.
  echo Setup or launch failed.
  exit /b %ERRORLEVEL%
)

echo.
echo Setup and launch finished.
endlocal