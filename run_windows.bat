@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Project environment not found. Running setup first...
    call install_windows.bat
    if errorlevel 1 exit /b 1
)

call .venv\Scripts\activate.bat

python -c "import streamlit, sys; version = tuple(int(part) for part in streamlit.__version__.split('.')[:2]); sys.exit(0 if version >= (1, 63) else 1)" >nul 2>nul
if errorlevel 1 (
    echo Updating project dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 goto :failed
)

python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
exit /b %errorlevel%

:failed
echo.
echo Dependency update failed. Check your internet connection and try again.
pause
exit /b 1
