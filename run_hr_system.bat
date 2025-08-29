@echo off
echo ========================================
echo HR Management System - MongoDB Edition
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Checking dependencies...

REM Check if required packages are installed
python -c "import pymongo, dash, pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK.

REM Check MongoDB connection
echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('localhost', 27017).admin.command('ping')" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: MongoDB connection failed
    echo Please ensure MongoDB is installed and running
    echo.
    echo To install MongoDB:
    echo 1. Download from https://www.mongodb.com/download-center/community
    echo 2. Install and start the MongoDB service
    echo 3. Ensure it's running on localhost:27017
    echo.
    pause
)

echo.
echo Choose an option:
echo 1. Launch Web Interface (Recommended)
echo 2. Launch Desktop GUI
echo 3. Run Data Migration
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting web interface...
    echo Dashboard will open at http://127.0.0.1:8050
    python app_mongo.py
) else if "%choice%"=="2" (
    echo Starting desktop GUI...
    python gui_launcher.py
) else if "%choice%"=="3" (
    echo Starting data migration...
    python migrate_to_mongo.py
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    pause
    goto :start
)

pause
