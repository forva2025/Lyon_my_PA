@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Project environment not found. Running setup first...
    call install_windows.bat
    if errorlevel 1 exit /b 1
)

call .venv\Scripts\activate.bat
python -m streamlit run app.py
