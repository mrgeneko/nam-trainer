@echo off
REM NAM Trainer launcher script for Windows
REM Detects available Python and runs the queue window

cd /d "%~dp0"

REM Find Python interpreter
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Python not found. Please install Python 3.10 or later.
        echo Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

REM Check Python version
for /f "delims=" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Using %PYTHON_VERSION%

REM Check if nam-full is available
where nam-full >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: nam-full not found in PATH.
    echo Install with: pip install neural-amp-modeler[cli]
    echo.
)

REM Run the queue window
%PYTHON_CMD% test_queue.py
