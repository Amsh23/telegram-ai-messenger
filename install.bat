@echo off
echo Installing required packages for Telegram Auto Messenger...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found. Installing packages...
pip install pyautogui pyperclip Pillow

echo.
echo Installation complete!
echo You can now run the program with: python telegram_auto_messenger.py
echo.
pause
