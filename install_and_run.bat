@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python --version >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo.
    echo ============================================================
    echo  Python 3 est introuvable.
    echo ============================================================
    echo.
    echo Solution la plus simple :
    echo   1. Lancez install_python_and_run.bat
    echo      OU installez Python 3.12 64 bits manuellement.
    echo   2. Si vous l'installez manuellement, cochez "Add Python to PATH".
    echo   3. Relancez ensuite ce fichier.
    echo.
    echo Le raccourci Microsoft Store "python.exe" n'est pas une
    echo installation Python utilisable par MapGen.
    echo.
    pause
    exit /b 1
)

echo Python detecte : %PYTHON_CMD%
%PYTHON_CMD% --version
echo.
echo Installation/mise a jour des dependances...
%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 (
    echo ERREUR : impossible de mettre pip a jour.
    pause
    exit /b 1
)
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR : impossible d'installer les dependances.
    pause
    exit /b 1
)

echo.
echo Lancement de Settlers III MapGen...
%PYTHON_CMD% run_gui.py
if errorlevel 1 (
    echo.
    echo MapGen s'est termine avec une erreur.
    pause
    exit /b 1
)
