@echo off
chcp 65001 >nul
title 🎯 راه‌اندازی Vision AI

echo.
echo ======================================
echo 🚀 راه‌اندازی سیستم Vision AI
echo ======================================
echo.

echo 📋 مرحله 1: بررسی Ollama...
ping -n 1 localhost >nul 2>&1
if errorlevel 1 (
    echo ❌ اتصال شبکه مشکل دارد
    pause
    exit /b 1
)

echo 📋 مرحله 2: بررسی Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python نصب نیست
    echo 💡 Python را از python.org دانلود کنید
    pause
    exit /b 1
)

echo 📋 مرحله 3: تست سیستم Vision...
echo.
python test_vision_system.py

echo.
echo 📋 مرحله 4: اجرای برنامه اصلی...
echo 🎯 برنامه Vision AI در حال شروع...
echo.

python telegram_ai_messenger.py

echo.
echo 🎉 تمام شد!
pause
