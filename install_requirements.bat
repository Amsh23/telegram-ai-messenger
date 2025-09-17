@echo off
chcp 65001
echo.
echo ===============================================
echo 🚀 نصب کتابخانه‌های Telegram Admin Pro v3.0
echo ===============================================
echo.

echo 📦 نصب کتابخانه‌های اصلی...
pip install pyautogui==0.9.54
pip install pyperclip==1.8.2
pip install Pillow==10.0.0
pip install requests==2.31.0
pip install opencv-python==4.12.0.88
pip install numpy==2.2.6
pip install python-telegram-bot==20.7

echo.
echo 🔧 نصب کتابخانه‌های کنترل پنجره...
pip install pygetwindow==0.0.9
pip install pywinauto==0.6.8
pip install psutil==5.9.5

echo.
echo ⌨️ نصب کتابخانه‌های کیبورد و ماوس...
pip install keyboard==0.13.5
pip install mouse==0.7.1

echo.
echo 🌐 نصب کتابخانه‌های محیط...
pip install python-dotenv==1.0.0

echo.
echo 👁️ نصب کتابخانه‌های OCR...
pip install pytesseract==0.3.10
pip install easyocr==1.7.0

echo.
echo ✅ نصب کامل شد!
echo.
echo 📋 لیست کتابخانه‌های نصب شده:
pip list | findstr /i "pyautogui pyperclip pillow requests opencv numpy telegram pygetwindow pywinauto psutil keyboard mouse dotenv"

echo.
echo 🎯 حالا می‌توانید Telegram Admin Pro را اجرا کنید!
echo.
pause
