@echo off
chcp 65001
echo.
echo ===============================================
echo 🚀 Telegram Admin Pro v3.0 با امکانات جدید
echo ===============================================
echo.

echo 📋 ویژگی‌های جدید:
echo   ✅ آمار زنده (Live Statistics)
echo   ✅ تست اتصالات
echo   ✅ سیستم هیبرید Vision AI + OCR
echo   ✅ تشخیص بهتر چت‌های خوانده نشده
echo.

echo 🔧 بررسی پیش‌نیازها...

REM بررسی Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python نصب نیست!
    echo لطفاً Python 3.8+ نصب کنید.
    pause
    exit /b 1
)

echo ✅ Python موجود است

REM بررسی کتابخانه‌های اصلی
echo 📦 بررسی کتابخانه‌های ضروری...
python -c "import requests, pyautogui, tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ برخی کتابخانه‌ها موجود نیست
    echo آیا می‌خواهید کتابخانه‌ها را نصب کنید؟ (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo 📥 نصب کتابخانه‌ها...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo ❌ خطا در نصب کتابخانه‌ها
            pause
            exit /b 1
        )
    ) else (
        echo ❌ برای اجرا نیاز به کتابخانه‌ها دارید
        pause
        exit /b 1
    )
)

echo ✅ کتابخانه‌ها آماده هستند

REM بررسی فایل .env
if not exist ".env" (
    echo ⚠️ فایل .env موجود نیست
    echo یک فایل .env نمونه ایجاد می‌شود...
    echo LICENSE_KEY=PERMANENT_ACTIVATION_KEY > .env
    echo ollama_url=http://127.0.0.1:11434 >> .env
    echo vision_model=llava >> .env
    echo vision_timeout=180 >> .env
    echo ✅ فایل .env ایجاد شد
)

echo.
echo 🚀 راه‌اندازی Telegram Admin Pro...
echo.
echo 📖 راهنما:
echo   • در اولین اجرا، مدل OCR دانلود می‌شود (یکبار)
echo   • تب "مانیتورینگ" را برای مشاهده آمار زنده باز کنید
echo   • از دکمه‌های تست برای بررسی اتصالات استفاده کنید
echo.

REM اجرای برنامه
python telegram_admin_pro.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ خطا در اجرای برنامه
    echo.
    echo 🔍 راهکارهای احتمالی:
    echo   1. فایل admin.log را بررسی کنید
    echo   2. مطمئن شوید Ollama در حال اجرا است
    echo   3. از دکمه "تست اتصالات" استفاده کنید
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ برنامه با موفقیت بسته شد
pause
