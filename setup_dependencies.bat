@echo off
setlocal

echo === Inventory Management System: Dependency Setup ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_dependencies.ps1"

if %ERRORLEVEL% neq 0 (
  echo.
  echo Dependency setup failed.
  exit /b %ERRORLEVEL%
)

echo.
echo Dependency setup complete.
endlocal
