# 🔧 راهنمای نصب و راه‌اندازی سریع

## ⚡ نصب فوری (Quick Start)

### 1. نصب Python
```bash
# دانلود Python 3.8+ از python.org
# در ویندوز: "Add Python to PATH" را تیک بزنید
```

### 2. نصب Ollama
```bash
# دانلود از https://ollama.ai
# نصب در ویندوز یا لینوکس
```

### 3. نصب مدل AI
```bash
ollama pull llama3.1:8b
# یا
ollama pull llama3.2
```

### 4. دانلود پروژه
```bash
git clone https://github.com/Amsh23/telegram-ai-messenger.git
cd telegram-ai-messenger
```

### 5. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 6. اجرا
```bash
python telegram_ai_messenger.py
```

---

## 🔧 پیکربندی اولیه

### مرحله 1: تنظیم اکانت‌ها
فایل `ai_config.json` را باز کنید و اکانت‌های خود را اضافه کنید:

```json
{
  "telegram_accounts": [
    {
      "username": "اکانت اصلی",
      "telegram_path": "مسیر تلگرام خود را اینجا وارد کنید"
    }
  ]
}
```

**پیدا کردن مسیر تلگرام:**
- **Windows Store**: `C:\Program Files\WindowsApps\TelegramMessengerLLP.TelegramDesktop_*\Telegram.exe`
- **دسکتاپ معمولی**: `C:\Users\[نام کاربری]\AppData\Roaming\Telegram Desktop\Telegram.exe`
- **نصب سفارشی**: مسیری که تلگرام را نصب کرده‌اید

### مرحله 2: تنظیم گروه‌ها
```json
{
  "groups": [
    {
      "group_name": "نام گروه",
      "chat_id": "Chat ID گروه (مثال: -1001234567890)"
    }
  ]
}
```

**پیدا کردن Chat ID:**
1. به ربات @userinfobot پیام دهید
2. ربات را به گروه اضافه کنید
3. دستور `/start` را ارسال کنید
4. Chat ID را کپی کنید

### مرحله 3: تست اتصال
1. برنامه را اجرا کنید
2. دکمه "🤖 تست AI" را بزنید
3. اگر موفق بود، آماده استفاده هستید!

---

## 🎯 استفاده ساده

### ارسال پیام هوشمند:
1. اکانت و گروه را انتخاب کنید
2. پیام پایه را وارد کنید
3. دکمه "🚀 شروع ارسال هوشمند" را بزنید

### خواندن و پاسخ خودکار:
1. تلگرام را باز کنید
2. لیست چت‌ها در سمت چپ باشد
3. دکمه "👁️ خواندن و پاسخ به همه چت‌ها" را بزنید

---

## ⚠️ نکات مهم

1. **تلگرام باز باشد**: برنامه نیاز به تلگرام باز دارد
2. **Ollama فعال باشد**: مطمئن شوید سرویس Ollama اجرا است
3. **دسترسی‌ها**: به برنامه اجازه کنترل صفحه‌کلید و ماوس بدهید
4. **صفحه‌نمایش**: تلگرام در حالت windowed اجرا کنید

---

## 🚨 عیب‌یابی سریع

### خطا: "AI پاسخ نمی‌دهد"
```bash
# بررسی Ollama
ollama list
ollama serve
```

### خطا: "گروه پیدا نمی‌شود"
- Chat ID را دوباره بررسی کنید
- مطمئن شوید عضو گروه هستید

### خطا: "تلگرام باز نمی‌شود"  
- مسیر تلگرام را در `ai_config.json` بررسی کنید
- تلگرام را دستی اجرا کنید

---

## 🎁 مثال آماده

نمونه کامل `ai_config.json`:

```json
{
  "telegram_accounts": [
    {
      "username": "اکانت من",
      "telegram_path": "C:\\Users\\User\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe"
    }
  ],
  "groups": [
    {
      "group_name": "گروه تست",
      "chat_id": "-1001234567890"
    }
  ],
  "base_message": "سلام دوستان! چطورید؟",
  "interval_seconds": 60,
  "ollama_url": "http://127.0.0.1:11434",
  "ollama_model": "llama3.1:8b",
  "ai_enabled": true,
  "personality": "دوستانه و صمیمی",
  "message_variety": true,
  "use_emojis": true
}
```

---

## ✅ چک‌لیست آماده‌سازی

- [ ] Python نصب شده
- [ ] Ollama نصب و اجرا شده  
- [ ] مدل AI دانلود شده
- [ ] وابستگی‌ها نصب شده
- [ ] `ai_config.json` تنظیم شده
- [ ] تلگرام باز و قابل دسترس
- [ ] تست AI موفق بوده

## 🎉 آماده استفاده!

اگر همه مراحل را طی کردید، برنامه آماده استفاده است. موفق باشید! 🚀
