# 🎯 Telegram AI Messenger - نسخه‌های مختلف

## 📊 خلاصه پروژه

این پروژه یک سیستم پیشرفته مدیریت تلگرام با هوش مصنوعی است که در سه نسخه مختلف ارائه شده:

### 🚀 نسخه‌های موجود

#### v1.0 - نسخه پایه
**فایل اصلی**: `telegram_ai_messenger.py`
- ✅ پاسخ‌دهی ساده با AI
- ✅ مدیریت تک چت
- ✅ رابط کاربری ساده
- ✅ ارسال پیام‌های هوشمند

#### v2.0 - Vision AI
**فایل اصلی**: `telegram_ai_messenger.py` (ارتقا یافته)
- ✅ Computer Vision با Ollama llava
- ✅ تحلیل اسکرین‌شات بلادرنگ
- ✅ تشخیص پیام‌ها از تصویر
- ✅ پاسخ‌دهی خودکار بر اساس محتوای بصری
- ✅ مانیتورینگ عملکرد

#### v3.0 - Admin Pro (حرفه‌ای)
**فایل اصلی**: `telegram_admin_pro.py`
- ✅ مدیریت همزمان چندین چت و گروه
- ✅ رابط کاربری پیشرفته (GUI)
- ✅ سیستم آمار و گزارش‌دهی
- ✅ امنیت و کنترل دسترسی
- ✅ قابلیت فروش و استفاده تجاری
- ✅ پایگاه داده SQLite
- ✅ لاگ‌گیری حرفه‌ای

### 📁 ساختار پروژه

```
telegram-ai-messenger/
├── v1.0 (پایه)
│   ├── telegram_ai_messenger.py
│   ├── ai_config.json
│   └── run.bat
│
├── v2.0 (Vision)
│   ├── telegram_ai_messenger.py (ارتقا یافته)
│   ├── ai_config.json (+ تنظیمات Vision)
│   ├── run_vision_ai.bat
│   ├── test_vision_system.py
│   └── REALTIME_VISION_GUIDE.md
│
├── v3.0 (Admin Pro)
│   ├── telegram_admin_pro.py
│   ├── admin_config.json
│   ├── run_admin_pro.bat
│   ├── requirements_pro.txt
│   └── ADMIN_PRO_GUIDE.md
│
└── مستندات و راهنماها
    ├── README.md
    ├── GUIDE.md
    ├── CHANGELOG.md
    └── سایر راهنماها...
```

### 🎯 نحوه استفاده هر نسخه

#### نسخه 1.0 (ساده)
```bash
python telegram_ai_messenger.py
# یا
run.bat
```

#### نسخه 2.0 (Vision)
```bash
# نصب مدل Vision
ollama pull llava

# اجرا
python telegram_ai_messenger.py
# یا
run_vision_ai.bat
```

#### نسخه 3.0 (Pro)
```bash
# نصب کتابخانه‌های Pro
pip install -r requirements_pro.txt

# اجرا
python telegram_admin_pro.py
# یا
run_admin_pro.bat
```

### 🔄 مقایسه نسخه‌ها

| ویژگی | v1.0 | v2.0 | v3.0 |
|--------|------|------|------|
| پاسخ‌دهی AI | ✅ | ✅ | ✅ |
| Computer Vision | ❌ | ✅ | ✅ |
| مدیریت چندگانه چت | ❌ | ❌ | ✅ |
| رابط کاربری پیشرفته | ❌ | ❌ | ✅ |
| آمار و گزارش | ❌ | محدود | ✅ |
| امنیت و لایسنس | ❌ | ❌ | ✅ |
| استفاده تجاری | ❌ | محدود | ✅ |
| پایگاه داده | ❌ | ❌ | ✅ |

### 💼 موارد استفاده

#### v1.0 - مناسب برای:
- کاربران خانگی
- تست و یادگیری
- پروژه‌های ساده

#### v2.0 - مناسب برای:
- کاربران پیشرفته
- نیاز به تحلیل بصری
- پاسخ‌دهی بلادرنگ

#### v3.0 - مناسب برای:
- کسب و کارها
- مراکز پشتیبانی
- مدیریت حرفه‌ای
- فروش و ارائه خدمات

### 🔧 پیش‌نیازهای هر نسخه

#### مشترک همه نسخه‌ها:
- Python 3.8+
- Ollama + llama3.1:8b
- کتابخانه‌های پایه Python

#### اضافی برای v2.0:
- مدل llava
- حافظه بیشتر (8GB+ RAM)

#### اضافی برای v3.0:
- کتابخانه‌های پیشرفته GUI
- SQLite
- حافظه بیشتر (16GB+ RAM توصیه)

### 📈 مسیر ارتقا

```
v1.0 (شروع) → v2.0 (Vision) → v3.0 (Pro)
     ↓              ↓              ↓
  یادگیری      ← پیشرفته     ← حرفه‌ای
```

### 🎉 انتخاب نسخه مناسب

#### برای شروع: نسخه 1.0
- ساده و سریع
- یادگیری مفاهیم
- تست اولیه

#### برای کاربری پیشرفته: نسخه 2.0
- قابلیت‌های Vision
- عملکرد بهتر
- تحلیل پیشرفته

#### برای استفاده حرفه‌ای: نسخه 3.0
- مدیریت کامل
- آمار دقیق
- قابلیت فروش

---

## 🚀 شروع سریع

### برای کاربران جدید:
```bash
# شروع با نسخه 1.0
python telegram_ai_messenger.py
```

### برای کاربران پیشرفته:
```bash
# نسخه 2.0 با Vision
ollama pull llava
python telegram_ai_messenger.py
# کلیک روی دکمه Vision
```

### برای استفاده حرفه‌ای:
```bash
# نسخه 3.0 Pro
pip install -r requirements_pro.txt
python telegram_admin_pro.py
```

**انتخاب نسخه مناسب برای نیاز خود و شروع کنید!** 🎯
