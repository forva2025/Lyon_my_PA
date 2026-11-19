@echo off
setlocal

echo ===============================================
echo  Download local models for Local RAG Assistant
echo ===============================================

where ollama >nul 2>nul
if not %errorlevel%==0 (
    echo Ollama was not found. Install it from https://ollama.com/download first.
    pause
    exit /b 1
)

echo Downloading Qwen3 1.7B generator...
ollama pull qwen3:1.7b
if errorlevel 1 goto :failed

echo.
echo Downloading Nomic embedding model...
ollama pull nomic-embed-text
if errorlevel 1 goto :failed

echo.
echo Both models were downloaded successfully.
echo Check them with: ollama list
pause
exit /b 0

:failed
echo.
echo A model download failed. Check your internet connection and try again.
pause
exit /b 1
