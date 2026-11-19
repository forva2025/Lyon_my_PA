@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo  Local RAG Assistant - Windows setup
echo ===============================================

where py >nul 2>nul
if %errorlevel%==0 (
    py -3.11 -m venv .venv >nul 2>nul
    if errorlevel 1 py -3 -m venv .venv
) else (
    where python >nul 2>nul
    if not %errorlevel%==0 (
        echo Python was not found. Install Python 3.11 64-bit from https://www.python.org/downloads/
        echo During installation, enable "Add Python to PATH".
        pause
        exit /b 1
    )
    python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment creation failed.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :failed
pip install -r requirements.txt
if errorlevel 1 goto :failed

echo.
echo Setup complete.
echo Next: install Ollama, then run the two model download commands in README.md.
echo When the models are installed, double-click run_windows.bat.
pause
exit /b 0

:failed
echo.
echo Installation failed. Check the error above and your internet connection.
pause
exit /b 1
