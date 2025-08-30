@echo off
echo ===========================================
echo    Business Dashboard - Enhanced Version
echo ===========================================
echo.
echo Starting Business Dashboard with sample data...
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    ".venv\Scripts\python.exe" app_gui.py
) else (
    echo Virtual environment not found, using system Python...
    python app_gui.py
)

echo.
echo Dashboard closed.
pause
