# 🚀 راهنمای کامل و پیشرفته تلگرام AI مسنجر

## 📚 فهرست مطالب

1. [معرفی و ویژگی‌ها](#معرفی-و-ویژگیها)
2. [نصب و راه‌اندازی](#نصب-و-راهاندازی)
3. [معماری سیستم](#معماری-سیستم)
4. [راهنمای توسعه](#راهنمای-توسعه)
5. [تنظیمات پیشرفته](#تنظیمات-پیشرفته)
6. [عیب‌یابی](#عیبیابی)
7. [بهینه‌سازی عملکرد](#بهینهسازی-عملکرد)
8. [توسعه‌های آینده](#توسعههای-آینده)

---

## 🎯 معرفی و ویژگی‌ها

### هدف پروژه
این پروژه یک سیستم پیشرفته و هوشمند برای تشخیص خودکار چت‌های تلگرام و پاسخ‌دهی هوشمند با شخصیت Littlejoy (گربه دوستانه) است.

### ویژگی‌های کلیدی

#### 🔍 تشخیص پیشرفته UI
- **تشخیص چندگانه چت‌های خوانده‌نشده**: 3 روش مختلف (رنگ badge، کنتراست، OCR)
- **layout detection هوشمند**: تشخیص خودکار نواحی مختلف تلگرام
- **پشتیبانی از resolutionهای مختلف**: adaptive sizing
- **فیلتر پیشرفته پیام‌ها**: 50+ الگوی فیلتر برای دقت بالا

#### 🤖 پاسخ‌دهی هوشمند
- **تحلیل محتوایی پیشرفته**: تشخیص سلام، تشکر، سوال، احساسات
- **امتیازدهی کیفیت پیام**: سیستم scoring برای انتخاب بهترین پیام‌ها
- **شخصیت Littlejoy منحصربه‌فرد**: 40+ نوع پاسخ مختلف با emoji گربه
- **پاسخ‌های context-aware**: تطبیق با محتوای واقعی پیام

#### 🛡️ ایمنی و پایداری
- **Safe interaction protocols**: کنترل کامل تعاملات
- **Error handling پیشرفته**: fallback mechanisms
- **Comprehensive logging**: ردیابی کامل عملیات
- **Validation چندمرحله‌ای**: اطمینان از صحت عملیات

---

## 🛠️ نصب و راه‌اندازی

### پیش‌نیازها

#### نرم‌افزارهای ضروری
```bash
Python 3.8+ (توصیه: 3.10+)
Windows 10/11
Telegram Desktop
```

#### کتابخانه‌های Python
```bash
pip install -r requirements.txt
```

#### محتوای `requirements.txt`:
```
pyautogui==0.9.54
pyperclip==1.8.2
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.0.0
pygetwindow==0.0.9
requests==2.31.0
```

#### کتابخانه‌های اختیاری (برای ویژگی‌های پیشرفته):
```bash
pip install pytesseract  # برای OCR تشخیص badge ها
pip install pywin32      # برای کنترل پیشرفته Windows
```

### راه‌اندازی اولیه

#### 1. کلون کردن پروژه
```bash
git clone https://github.com/Amsh23/telegram-ai-messenger.git
cd telegram-ai-messenger
```

#### 2. تنظیم محیط
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 3. تنظیم تلگرام
- تلگرام Desktop را نصب و راه‌اندازی کنید
- حساب کاربری خود را تنظیم کنید
- فولدرهای مورد نظر را ایجاد کنید (مثل Littlejoy🐈)

#### 4. اجرای اولیه
```bash
python telegram_ai_messenger.py
```

---

## 🏗️ معماری سیستم

### ساختار کلی پروژه

```
telegram-ai-messenger/
├── telegram_ai_messenger.py     # فایل اصلی برنامه
├── requirements.txt             # وابستگی‌ها
├── ai_config.json              # تنظیمات (ایجاد خودکار)
├── test_*.py                   # فایل‌های تست
├── *.md                        # مستندات
└── screenshots/                # اسکرین‌شات‌های debug
```

### کلاس‌های اصلی

#### `TelegramUIDetector`
مسئول تشخیص عناصر رابط کاربری تلگرام:

```python
class TelegramUIDetector:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.confidence_threshold = 0.8
        # تعریف نواحی مختلف UI
        
    def detect_telegram_window(self):
        """تشخیص پنجره تلگرام با روش‌های مختلف"""
        
    def detect_unread_chats(self):
        """تشخیص چت‌های خوانده‌نشده با 3 روش"""
        
    def find_chat_items(self):
        """پیدا کردن آیتم‌های چت در لیست"""
```

#### `TelegramAIMessenger`
کلاس اصلی برنامه:

```python
class TelegramAIMessenger:
    def __init__(self):
        self.ui_detector = TelegramUIDetector()
        self.setup_gui()
        
    def safe_read_messages(self):
        """خواندن پیام‌ها با فیلتر پیشرفته"""
        
    def generate_littlejoy_reply_improved(self):
        """تولید پاسخ هوشمند"""
        
    def screenshot_telegram_and_reply(self):
        """فرآیند کامل تشخیص و پاسخ"""
```

### الگوریتم‌های کلیدی

#### تشخیص چت‌های خوانده‌نشده

```python
def detect_unread_chats_advanced(self):
    """
    روش 1: تشخیص badge های آبی
    - 3 محدوده رنگ آبی مختلف
    - HoughCircles detection
    - دقت: 85-90%
    
    روش 2: تحلیل کنتراست
    - تشخیص تغییرات نور
    - morphological operations
    - دقت: 70-80%
    
    روش 3: OCR تشخیص اعداد
    - pytesseract برای اعداد badge
    - تشخیص اعداد کوچک
    - دقت: 60-70%
    
    ترکیب نتایج و حذف تکراری
    """
```

#### فیلتر پیشرفته پیام‌ها

```python
def advanced_message_filter(self, messages):
    """
    مرحله 1: فیلتر الگویی
    - 50+ الگوی regex
    - حذف محتوای سیستمی
    
    مرحله 2: امتیازدهی کیفیت
    - طول و ساختار (0-3 امتیاز)
    - محتوای معنادار (0-4 امتیاز)
    - نسبت حروف (0-2 امتیاز)
    - عدم الگوهای مشکوک (0-2 امتیاز)
    - زمینه مناسب (0-2 امتیاز)
    
    مرحله 3: انتخاب نهایی
    - حداقل امتیاز: 4
    - حداکثر 5 پیام
    - مرتب‌سازی بر اساس کیفیت
    """
```

---

## 👨‍💻 راهنمای توسعه

### اضافه کردن ویژگی جدید

#### 1. اضافه کردن نوع پاسخ جدید

```python
# در تابع generate_littlejoy_reply_improved
if any(word in full_context for word in ['موضوع_جدید', 'کلیدواژه']):
    responses = [
        "🐈 پاسخ مخصوص موضوع جدید",
        "😸 پاسخ دوم",
        "🐾 پاسخ سوم"
    ]
    return random.choice(responses)
```

#### 2. اضافه کردن فیلتر جدید

```python
# در لیست filter_patterns
r'^الگوی_جدید.*$',  # توضیح الگو
r'^\d+\s*کلیدواژه.*$',  # الگو با عدد
```

#### 3. تست ویژگی جدید

```python
def test_new_feature():
    messenger = TelegramAIMessenger()
    test_messages = ["پیام تست"]
    result = messenger.new_feature(test_messages)
    assert result is not None
    print("✅ ویژگی جدید کار می‌کند")
```

### بهبود دقت تشخیص

#### تنظیم پارامترهای OpenCV
```python
# برای تشخیص بهتر دایره‌ها
circles = cv2.HoughCircles(
    blue_mask, 
    cv2.HOUGH_GRADIENT, 
    dp=1,           # رزولوشن
    minDist=20,     # حداقل فاصله بین دایره‌ها
    param1=30,      # threshold بالای Canny
    param2=15,      # threshold انباشت
    minRadius=3,    # حداقل شعاع
    maxRadius=25    # حداکثر شعاع
)
```

#### بهبود فیلتر رنگی
```python
# محدوده‌های رنگ دقیق‌تر
blue_ranges = [
    ([100, 100, 100], [130, 255, 255]),  # آبی استاندارد
    ([90, 120, 120], [120, 255, 255]),   # آبی روشن‌تر
    ([110, 80, 80], [140, 255, 255]),    # آبی تیره‌تر
    ([95, 100, 150], [125, 255, 255]),   # آبی متوسط
]
```

### debugging و نظارت

#### فعال‌سازی debug mode
```python
# در ابتدای فایل
DEBUG_MODE = True

# ذخیره تصاویر debug
if DEBUG_MODE:
    cv2.imwrite(f'debug_screenshot_{timestamp}.png', screenshot)
    cv2.imwrite(f'debug_mask_{timestamp}.png', blue_mask)
```

#### سیستم لاگ پیشرفته
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_ai.log'),
        logging.StreamHandler()
    ]
)
```

---

## ⚙️ تنظیمات پیشرفته

### فایل `ai_config.json`

```json
{
    "telegram_accounts": [
        {
            "username": "اکانت اصلی",
            "telegram_path": "C:/Users/User/AppData/Roaming/Telegram Desktop/Telegram.exe",
            "enabled": true
        }
    ],
    "ai_settings": {
        "response_delay": 2,
        "max_messages_per_chat": 5,
        "confidence_threshold": 0.8,
        "debug_mode": false
    },
    "ui_detection": {
        "chat_height": 65,
        "sidebar_ratio": 0.28,
        "badge_min_radius": 3,
        "badge_max_radius": 25
    },
    "message_filter": {
        "min_quality_score": 4,
        "max_message_length": 1000,
        "min_letter_ratio": 0.2
    }
}
```

### تنظیمات عملکرد

#### بهینه‌سازی سرعت
```python
# کاهش delay ها برای سرعت بیشتر (احتمال کاهش دقت)
pyautogui.PAUSE = 0.1

# افزایش delay ها برای دقت بیشتر
pyautogui.PAUSE = 0.5
```

#### تنظیم حساسیت تشخیص
```python
# حساسیت بالا (ممکن است false positive بیشتر)
confidence_threshold = 0.6

# حساسیت کم (ممکن است پیام‌هایی را از دست بدهد)
confidence_threshold = 0.9
```

---

## 🐛 عیب‌یابی

### مشکلات رایج و راه‌حل‌ها

#### مشکل: چت‌های خوانده‌نشده تشخیص داده نمی‌شوند

**تشخیص:**
```bash
python -c "
from telegram_ai_messenger import TelegramUIDetector
detector = TelegramUIDetector()
unread = detector.detect_unread_chats()
print(f'تعداد چت‌های تشخیص داده شده: {len(unread)}')
"
```

**راه‌حل‌ها:**
1. بررسی رزولوشن صفحه و scaling
2. تنظیم محدوده‌های رنگ آبی
3. فعال‌سازی debug mode برای تصاویر

#### مشکل: پیام‌های نامربوط خوانده می‌شوند

**راه‌حل:**
```python
# افزایش حداقل امتیاز کیفیت
min_required_score = 6  # به جای 4

# اضافه کردن فیلترهای بیشتر
additional_filters = [
    r'^pattern_جدید.*$',
    r'^\w+_مشکوک\w+$'
]
```

#### مشکل: پاسخ‌ها تکراری هستند

**راه‌حل:**
```python
# اضافه کردن پاسخ‌های جدید
new_responses = [
    "🐈 پاسخ جدید 1",
    "😸 پاسخ جدید 2", 
    "🐾 پاسخ جدید 3"
]
```

### ابزارهای debugging

#### اسکرین‌شات debug
```python
def save_debug_screenshot(self, img, name):
    timestamp = int(time.time())
    filename = f'debug_{name}_{timestamp}.png'
    cv2.imwrite(filename, img)
    print(f"Debug image saved: {filename}")
```

#### لاگ تفصیلی
```python
def detailed_log(self, message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")
```

---

## 🚀 بهینه‌سازی عملکرد

### بهبود سرعت

#### 1. کش کردن تصاویر
```python
class ImageCache:
    def __init__(self):
        self.cache = {}
    
    def get_screenshot(self, region):
        key = f"{region}_{int(time.time())//5}"  # cache برای 5 ثانیه
        if key not in self.cache:
            self.cache[key] = pyautogui.screenshot(region=region)
        return self.cache[key]
```

#### 2. پردازش موازی
```python
import concurrent.futures

def process_multiple_chats(self, chat_positions):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(self.process_single_chat, pos) 
                  for pos in chat_positions[:3]]
        results = [future.result() for future in futures]
    return results
```

### بهبود دقت

#### 1. تشخیص adaptive
```python
def adaptive_detection(self, screenshot):
    # تشخیص کیفیت تصویر
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    variance = np.var(gray)
    
    # تنظیم پارامترها بر اساس کیفیت
    if variance > 1000:  # تصویر واضح
        param1, param2 = 30, 15
    else:  # تصویر کم‌کیفیت
        param1, param2 = 20, 10
        
    return cv2.HoughCircles(..., param1=param1, param2=param2)
```

#### 2. machine learning integration
```python
# برای آینده: استفاده از ML برای تشخیص بهتر
def ml_chat_detection(self, image):
    # پیاده‌سازی مدل CNN برای تشخیص چت‌ها
    pass
```

---

## 🔮 توسعه‌های آینده

### ویژگی‌های در دست توسعه

#### 1. یادگیری خودکار
```python
class LearningSystem:
    def learn_from_conversation(self, messages, responses, feedback):
        """یادگیری از مکالمات موفق برای بهبود پاسخ‌ها"""
        pass
    
    def adapt_to_user_style(self, user_id, messages):
        """تطبیق سبک پاسخ با سبک کاربر"""
        pass
```

#### 2. پشتیبانی چندزبانه
```python
class MultiLanguageSupport:
    def detect_language(self, message):
        """تشخیص زبان پیام"""
        pass
    
    def generate_response_in_language(self, message, language):
        """تولید پاسخ به زبان مناسب"""
        pass
```

#### 3. تحلیل احساسات پیشرفته
```python
class AdvancedSentimentAnalysis:
    def analyze_emotion(self, message):
        """تحلیل دقیق احساسات پیام"""
        pass
    
    def generate_empathetic_response(self, emotion, message):
        """تولید پاسخ همدلانه"""
        pass
```

### API و Integration

#### REST API
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/process_chat', methods=['POST'])
def process_chat():
    data = request.json
    messages = data.get('messages', [])
    response = messenger.generate_response(messages)
    return jsonify({'response': response})
```

#### Webhook Support
```python
def setup_webhook(self, url):
    """تنظیم webhook برای دریافت پیام‌ها"""
    pass

def send_webhook_response(self, response_data):
    """ارسال پاسخ از طریق webhook"""
    pass
```

---

## 📞 پشتیبانی و کمک

### منابع مفید

#### مستندات رسمی
- [OpenCV Documentation](https://docs.opencv.org/)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [Python Regex Guide](https://docs.python.org/3/library/re.html)

#### مثال‌های کاربردی
```python
# تست سریع سیستم
python test_reply_only.py

# تست کامل with GUI
python test_enhanced_system.py

# debugging mode
python telegram_ai_messenger.py --debug
```

#### گزارش باگ
برای گزارش مشکلات، لطفاً شامل کنید:
1. نسخه Python و OS
2. پیام خطا کامل
3. اسکرین‌شات (در صورت امکان)
4. فایل‌های log

### مشارکت در پروژه

#### Fork و Pull Request
1. Fork کنید repository را
2. branch جدید ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request ارسال کنید

#### استانداردهای کد
- استفاده از docstring برای توابع
- کامنت‌گذاری کدهای پیچیده
- نام‌گذاری معنادار متغیرها
- رعایت PEP 8

---

## 📄 لایسنس و حقوق

این پروژه تحت لایسنس MIT منتشر شده است. برای استفاده تجاری یا توزیع، لطفاً مطالعه کنید فایل LICENSE را.

---

**نکته نهایی:** این راهنما به‌طور مداوم به‌روزرسانی می‌شود. برای آخرین نسخه، repository GitHub را بررسی کنید.

---

*ساخته شده با ❤️ برای جامعه توسعه‌دهندگان Python*
