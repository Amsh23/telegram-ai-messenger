@echo off
echo ========================================
echo   Telegram AI Messenger v2.0
echo   نسخه هوشمند با Ollama
echo ========================================
echo.

REM بررسی Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطا: Python نصب نیست!
    echo لطفاً ابتدا Python را از python.org نصب کنید
    pause
    exit /b 1
)

echo ✅ Python پیدا شد
echo.

REM نصب کتابخانه‌ها
echo 📦 نصب کتابخانه‌های مورد نیاز...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ خطا در نصب کتابخانه‌ها
    pause
    exit /b 1
)

echo ✅ کتابخانه‌ها نصب شدند
echo.

REM بررسی Ollama
echo 🤖 بررسی اتصال به Ollama...
curl -s http://127.0.0.1:11500/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  هشدار: Ollama در آدرس 127.0.0.1:11500 پاسخ نمی‌دهد!
    echo.
    echo برای استفاده کامل از قابلیت‌های AI:
    echo 1. مطمئن شوید Ollama در حال اجرا است
    echo 2. آدرس و پورت را بررسی کنید
    echo 3. مدل llama3.1:8b نصب شده باشد
    echo.
    echo آیا می‌خواهید بدون تست Ollama ادامه دهید؟ (y/n)
    set /p choice=انتخاب: 
    if /i "%choice%" neq "y" (
        echo برنامه لغو شد
        pause
        exit /b 1
    )
) else (
    echo ✅ Ollama در دسترس است
)

echo.
echo 🚀 شروع برنامه هوشمند...
python telegram_ai_messenger.py

if errorlevel 1 (
    echo.
    echo ❌ خطا در اجرای برنامه
    pause
)

echo.
echo برنامه بسته شد
pause
