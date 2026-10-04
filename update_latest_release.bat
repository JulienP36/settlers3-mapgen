@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  Settlers III MapGen - Recuperer la derniere release STABLE
echo ============================================================
echo.

where powershell.exe >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Windows PowerShell est introuvable.
    echo Cet outil necessite Windows PowerShell.
    echo.
    pause
    exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\update_latest_release.ps1"
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
    echo [ERREUR] Le telechargement a echoue ^(code %RC%^).
) else (
    echo Termine.
)
echo.
pause
exit /b %RC%
