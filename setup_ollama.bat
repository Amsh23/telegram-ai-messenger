@echo off
chcp 65001 >nul
title 🔥 راه‌اندازی Ollama Vision

echo.
echo ======================================
echo 🔥 نصب و راه‌اندازی Ollama + Vision
echo ======================================
echo.

echo 📋 مرحله 1: بررسی Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama نصب نیست
    echo 💡 لطفا Ollama را از https://ollama.ai دانلود کنید
    echo 📥 بعد از نصب این فایل را دوباره اجرا کنید
    pause
    exit /b 1
)

echo ✅ Ollama نصب شده
echo.

echo 📋 مرحله 2: دانلود مدل Vision...
echo 🔄 دانلود llava model (ممکن است چند دقیقه طول بکشد)...
ollama pull llava

echo.
echo 📋 مرحله 3: دانلود مدل Text...
echo 🔄 دانلود llama3.1:8b model...
ollama pull llama3.1:8b

echo.
echo 📋 مرحله 4: راه‌اندازی سرور...
echo 🚀 شروع Ollama server...
start /min ollama serve

echo.
echo 📋 مرحله 5: تست عملکرد...
timeout /t 5 /nobreak >nul

echo 🔍 بررسی مدل‌های نصب شده:
ollama list

echo.
echo 🎉 آماده سازی تمام شد!
echo 🚀 حالا می‌توانید Vision AI را اجرا کنید
echo.

pause
