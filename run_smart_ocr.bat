@echo off
echo 🤖 سیستم OCR و پاسخ‌دهی خودکار تلگرام - نسخه بهبود یافته
echo ==============================================================

REM بررسی Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python پیدا نشد!
    pause
    exit /b 1
)

echo ✅ Python یافت شد

REM بررسی تلگرام
echo 🔍 بررسی تلگرام...
tasklist /FI "IMAGENAME eq Telegram.exe" 2>NUL | find /I /N "Telegram.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ تلگرام در حال اجرا است
) else (
    echo ⚠️ تلگرام اجرا نشده - لطفاً تلگرام را باز کنید
    pause
)

REM بررسی Ollama
echo 🔍 بررسی Ollama...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama در حال اجرا نیست
    echo دستور اجرا: ollama serve
    echo سپس در ترمینال دیگر: ollama pull llava
    pause
) else (
    echo ✅ Ollama در حال اجرا است
)

echo.
echo 🎯 این سیستم:
echo   📸 از تلگرام عکس می‌گیرد
echo   👁️ با Ollama Vision تصویر را تحلیل می‌کند  
echo   🤖 پاسخ هوشمند تولید می‌کند
echo   📤 خودکار جواب می‌دهد
echo.
echo آماده هستید؟
pause

echo 🚀 شروع سیستم...
python telegram_ocr_simple.py

pause
