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
    echo Python 3 est introuvable.
    echo Lancez d'abord install_and_run.bat ou install_python_and_run.bat.
    pause
    exit /b 1
)

%PYTHON_CMD% run_gui.py
if errorlevel 1 pause
