@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  Settlers III MapGen - installation automatique de Python
echo ============================================================
echo.
echo Ce script utilise winget pour installer Python 3.12 64 bits
echo si aucune installation Python utilisable n'est detectee.
echo.

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
    where winget >nul 2>nul
    if errorlevel 1 (
        echo ERREUR : winget est introuvable.
        echo.
        echo Installez Python 3.12 64 bits manuellement en cochant
        echo "Add Python to PATH", puis relancez install_and_run.bat.
        pause
        exit /b 1
    )

    echo Installation de Python 3.12...
    winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo ERREUR : l'installation automatique de Python a echoue.
        echo Installez Python manuellement puis relancez install_and_run.bat.
        pause
        exit /b 1
    )

    echo.
    echo Python vient d'etre installe.
    echo Fermez cette fenetre puis relancez install_and_run.bat
    echo afin que Windows recharge correctement le PATH.
    pause
    exit /b 0
)

echo Python est deja installe.
call install_and_run.bat
