@echo off
chcp 65001 >nul
title 🎯 Telegram AI Admin Pro v3.0

echo.
echo ==========================================
echo 🚀 Telegram AI Admin Pro v3.0
echo ==========================================
echo 💼 ادمین هوشمند حرفه‌ای برای تلگرام
echo.

echo 📋 بررسی پیش‌نیازها...

echo 🔍 بررسی Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python نصب نیست
    echo 💡 لطفاً Python 3.8+ را از python.org نصب کنید
    pause
    exit /b 1
)
echo ✅ Python آماده است

echo 🔍 بررسی Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama پیدا نشد
    echo 💡 اگر نصب نیست: https://ollama.ai
    echo 🔄 ادامه بدون Ollama...
) else (
    echo ✅ Ollama آماده است
)

echo 📦 نصب کتابخانه‌های Pro...
pip install -r requirements_pro.txt

echo.
echo 🎯 اجرای Admin Pro...
echo 📊 رابط کاربری پیشرفته در حال بارگذاری...
echo.

python telegram_admin_pro.py

echo.
echo 🎉 پایان اجرای Admin Pro
pause
