@echo off
setlocal
echo ============================================
echo  ATLAS - First-time setup
echo ============================================
echo.
if not exist venv\Scripts\activate.bat (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Python is not installed or not on PATH.
        pause
        exit /b 1
    )
) else (
    echo Existing virtual environment found.
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)
echo.
echo ============================================
echo  Setup complete!
echo  Double-click run.bat to launch ATLAS.
echo ============================================
pause
endlocal
