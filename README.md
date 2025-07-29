# 🤖 Telegram AI Auto Messenger

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Ollama](https://img.shields.io/badge/Ollama-AI-green?style=for-the-badge&logo=ai)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**یک مسنجر خودکار هوشمند برای تلگرام با قدرت هوش مصنوعی Ollama**

</div>

## 🌟 ویژگی‌ها

### 🧠 **هوش مصنوعی پیشرفته**
- تولید خودکار پیام‌های خلاقانه و متنوع
- پشتیبانی کامل از Ollama (LLaMA, Mistral, CodeLlama و...)
- شخصیت‌های مختلف AI (دوستانه، شوخ، آموزشی، رسمی)
- تنظیمات دقیق برای کیفیت و سبک پیام‌ها

### 📱 **ارتباط هوشمند با تلگرام**
- پیدا کردن خودکار گروه‌ها با Chat ID یا نام
- ارسال خودکار پیام‌ها با فواصل زمانی قابل تنظیم
- پشتیبانی از تلگرام دسکتاپ (Windows Store و نسخه معمولی)
- گزارش‌دهی و لاگ کامل عملیات

### 🎨 **رابط کاربری زیبا**
- طراحی مدرن و کاربرپسند
- تب‌های جداگانه برای تنظیمات مختلف
- نمایش وضعیت لحظه‌ای
- پیش‌نمایش و تست پیام‌های AI

## 📸 تصاویر

<div align="center">

### رابط اصلی برنامه
![Main Interface](https://via.placeholder.com/800x600/2c3e50/white?text=Telegram+AI+Messenger+Interface)

### تنظیمات هوش مصنوعی
![AI Settings](https://via.placeholder.com/800x600/3498db/white?text=AI+Configuration+Panel)

</div>

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

```bash
# Python 3.7 یا بالاتر
python --version

# نصب Ollama
# برای Windows:
# دانلود از ollama.ai و نصب
```

### نصب خودکار

```bash
# 1. کلون ریپازیتوری
git clone https://github.com/Amsh23/telegram-ai-messenger.git
cd telegram-ai-messenger

# 2. اجرای نصب خودکار
run_ai.bat
```

### نصب دستی

```bash
# 1. نصب کتابخانه‌ها
pip install -r requirements.txt

# 2. نصب مدل Ollama
ollama pull llama3.1:8b

# 3. اجرای برنامه
python telegram_ai_messenger.py
```

## 🛠️ تنظیمات

### 🎯 تنظیمات اصلی

| پارامتر | توضیح | مثال |
|---------|--------|-------|
| Chat ID | شناسه گروه تلگرام | `-4973474959` |
| نام گروه | نام گروه (جایگزین Chat ID) | `my_group` |
| فاصله زمانی | فاصله بین پیام‌ها (ثانیه) | `30` |
| پیام پایه | پیام پایه برای AI | `سلام دوستان!` |

### 🤖 تنظیمات هوش مصنوعی

| پارامتر | توضیح | پیش‌فرض |
|---------|--------|----------|
| آدرس Ollama | URL سرور Ollama | `http://127.0.0.1:11434` |
| مدل | مدل AI مورد استفاده | `llama3.1:8b` |
| شخصیت | سبک نوشتاری AI | `دوستانه و صمیمی` |
| تنوع پیام | فعال‌سازی تنوع | `فعال` |
| استفاده از ایموجی | اضافه کردن ایموجی | `فعال` |

## 💡 نحوه استفاده

### مرحله 1: آماده‌سازی
```bash
# اجرای سریع
python simple_test.py
```
- گزینه 1: تست ارسال پیام
- تلگرام و گروه را باز کنید
- روی نوار پیام کلیک کنید

### مرحله 2: تنظیم AI
```bash
# اجرای برنامه اصلی
python telegram_ai_messenger.py
```
1. **تست اتصال**: روی "🤖 تست AI" کلیک کنید
2. **تولید نمونه**: "🎯 تولید پیام تست" را امتحان کنید
3. **تنظیم شخصیت**: شخصیت مورد نظر را انتخاب کنید

### مرحله 3: شروع ارسال
1. **باز کردن تلگرام**: "📱 باز کردن تلگرام"
2. **شروع**: "🚀 شروع ارسال هوشمند"
3. **نظارت**: لاگ‌ها را دنبال کنید

## 🔧 عیب‌یابی

### مشکلات رایج

#### پیام ارسال نمی‌شود
```bash
# راه‌حل:
1. مطمئن شوید روی نوار پیام کلیک کرده‌اید
2. تلگرام در حالت windowed باشد
3. دسترسی ارسال پیام داشته باشید
```

#### Ollama متصل نمی‌شود
```bash
# بررسی سرویس:
curl http://127.0.0.1:11434/api/tags

# یا اجرای مجدد:
ollama serve
```

#### گروه پیدا نمی‌شود
```bash
# بررسی کنید:
1. Chat ID صحیح است؟
2. عضو گروه هستید؟
3. نام گروه دقیق است؟
```

## 📁 ساختار پروژه

```
telegram-ai-messenger/
├── 📄 telegram_ai_messenger.py    # برنامه اصلی هوشمند
├── 📄 telegram_auto_messenger.py  # نسخه ساده
├── 📄 simple_test.py              # ابزار تست
├── 📄 requirements.txt            # کتابخانه‌ها
├── 📄 run_ai.bat                  # اجرای خودکار
├── 📄 config.json                 # تنظیمات ساده
├── 📄 ai_config.json              # تنظیمات AI
├── 📄 README.md                   # راهنما
├── 📄 QUICK_START.md              # شروع سریع
└── 📄 GUIDE.md                    # راهنمای کامل
```

## 🎭 شخصیت‌های AI

### دوستانه و صمیمی 😊
```
مثال: "سلام عزیزان! امیدوارم روز خوبی داشته باشید ✨"
```

### شوخ و سرگرم‌کننده 😄
```
مثال: "چه خبر از دنیای شلوغ شما؟ 😂 امیدوارم حالتون عالی باشه!"
```

### آموزشی و مفید 📚
```
مثال: "نکته روز: آیا می‌دانستید که یادگیری مداوم کلید موفقیت است؟ 💡"
```

### رسمی و حرفه‌ای 👔
```
مثال: "احترام، امیدوارم در بهترین حال باشید. روز پربرکتی داشته باشید."
```

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم! 

### نحوه مشارکت:
1. Fork کنید
2. برنچ جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

### ایده‌هایی برای مشارکت:
- 🎨 بهبود رابط کاربری
- 🧠 اضافه کردن مدل‌های AI جدید
- 📱 پشتیبانی از پلتفرم‌های جدید
- 🌍 ترجمه به زبان‌های مختلف
- 📊 اضافه کردن آمار و گزارش‌ها

## 📜 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

## 🙏 تشکر ویژه

- [Ollama](https://ollama.ai) برای ارائه پلتفرم AI محلی
- [PyAutoGUI](https://pyautogui.readthedocs.io/) برای اتوماسیون GUI
- جامعه توسعه‌دهندگان Python

## 📞 ارتباط و پشتیبانی

- 🐛 گزارش باگ: [Issues](https://github.com/Amsh23/telegram-ai-messenger/issues)
- 💡 درخواست ویژگی: [Feature Requests](https://github.com/Amsh23/telegram-ai-messenger/issues)
- 📧 ایمیل: support@telegram-ai-messenger.com

## ⭐ ستاره بدهید!

اگر این پروژه برایتان مفید بود، ستاره بدهید! ⭐

---

<div align="center">

**ساخته شده با ❤️ توسط [Amsh23](https://github.com/Amsh23)**

**Telegram AI Auto Messenger - Where AI Meets Automation** 🤖✨

</div>
