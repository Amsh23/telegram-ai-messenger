@echo off
echo 🤖 سیستم OCR و پاسخ‌دهی خودکار تلگرام
echo ==========================================

REM بررسی Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python پیدا نشد!
    echo لطفاً Python را نصب کنید
    pause
    exit /b 1
)

echo ✅ Python یافت شد

REM بررسی تلگرام
echo 🔍 بررسی وضعیت تلگرام...
tasklist /FI "IMAGENAME eq Telegram.exe" 2>NUL | find /I /N "Telegram.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ تلگرام در حال اجرا است
) else (
    echo ⚠️ تلگرام اجرا نشده - لطفاً تلگرام را باز کنید
    echo و سپس Enter بزنید تا ادامه دهیم...
    pause
)

REM بررسی Ollama
echo 🔍 بررسی وضعیت Ollama...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama در حال اجرا نیست - لطفاً Ollama را راه‌اندازی کنید
    echo دستور: ollama serve
    echo سپس Enter بزنید...
    pause
) else (
    echo ✅ Ollama در حال اجرا است
)

REM هشدار
echo.
echo 🎯 این سیستم قابلیت‌های زیر را دارد:
echo   📸 عکس‌برداری از تلگرام
echo   🔍 تشخیص متن با OCR
echo   🤖 تولید پاسخ هوشمند
echo   📤 ارسال خودکار پاسخ
echo.
echo ⚠️ توجه: مطمئن شوید که:
echo   • تلگرام باز است و روی چت‌های مورد نظر هستید
echo   • Ollama در حال اجرا است
echo   • دسترسی اینترنت برای OCR دارید
echo.
echo آماده هستید؟ (Enter بزنید)
pause

REM نصب وابستگی‌ها (در صورت نیاز)
echo 📦 بررسی وابستگی‌ها...
python -c "import easyocr, PIL, requests" >nul 2>&1
if errorlevel 1 (
    echo 📥 نصب وابستگی‌های OCR...
    pip install easyocr pillow requests
)

REM اجرای سیستم
echo 🚀 شروع سیستم OCR و پاسخ‌دهی...
echo.
python telegram_ocr_system.py

echo.
echo ⏹️ سیستم متوقف شد
pause
