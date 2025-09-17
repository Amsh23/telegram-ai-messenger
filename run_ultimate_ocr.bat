@echo off
chcp 65001 > nul
echo 🤖 Ultimate Telegram OCR & Auto Response System
echo ===============================================
echo.

echo 📋 بررسی سیستم...

:: بررسی Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python نصب نیست!
    pause
    exit /b 1
)

:: بررسی Ollama
curl -s http://127.0.0.1:11434/api/tags > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama در حال اجرا نیست! لطفاً Ollama را راه‌اندازی کنید.
    echo.
    echo قدم‌های راه‌اندازی:
    echo 1. Ollama را باز کنید
    echo 2. در terminal اجرا کنید: ollama pull llama3.1:8b
    echo 3. در terminal اجرا کنید: ollama pull llava
    echo.
    pause
    exit /b 1
)

echo ✅ Python و Ollama آماده هستند!
echo.

:: نصب کتابخانه‌ها در صورت نیاز
echo 📦 بررسی کتابخانه‌ها...
pip install -q requests pillow pyautogui pygetwindow psutil pywin32

echo.
echo 🚀 راه‌اندازی سیستم OCR...
echo.

:: اجرای برنامه اصلی
python ultimate_telegram_ocr.py

echo.
echo ✅ اجرا تمام شد!
pause
