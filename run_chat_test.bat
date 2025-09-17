@echo off
echo 🧪 تست اتصالات چت و آمار تلگرام
echo ================================

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
    echo ⚠️ تلگرام اجرا نشده - شروع تلگرام...
    echo لطفاً تلگرام را دستی باز کنید و سپس Enter بزنید
    pause
)

REM اجرای تست
echo 🚀 شروع تست...
echo.
python test_chat_connections.py

echo.
echo ⏹️ تست تمام شد
pause
