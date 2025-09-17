#!/usr/bin/env python3
"""
🤖 Telegram OCR & Auto Response System
سیستم تشخیص متن و پاسخ‌دهی خودکار تلگرام
"""

import time
import json
import logging
import requests
import base64
from io import BytesIO
from PIL import Image
import easyocr
import pyautogui
from telegram_auto_manager import TelegramAutoManager

class TelegramOCRSystem:
    """سیستم OCR و پاسخ‌دهی خودکار تلگرام"""
    
    def __init__(self, config_file="admin_config.json"):
        # بارگذاری تنظیمات
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # راه‌اندازی لاگر
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # راه‌اندازی مدیر تلگرام
        self.telegram_manager = TelegramAutoManager(self.config)
        
        # راه‌اندازی OCR
        try:
            self.ocr_reader = easyocr.Reader(['fa', 'en'], gpu=False)
            self.logger.info("✅ OCR Reader راه‌اندازی شد")
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی OCR: {e}")
            self.ocr_reader = None
        
        # تنظیمات Ollama
        self.ollama_url = self.config.get('ollama_url', 'http://127.0.0.1:11434')
        self.text_model = self.config.get('ollama_text_model', 'llama3.1:8b')
        self.vision_model = self.config.get('ollama_vision_model', 'llava')
        
        # چت‌های مدیریت شده
        self.managed_chats = {
            chat['id']: chat for chat in self.config.get('managed_chats', [])
        }
        
        self.logger.info("🤖 سیستم OCR و پاسخ‌دهی خودکار راه‌اندازی شد")
    
    def take_telegram_screenshot(self):
        """گرفتن اسکرین‌شات از تلگرام"""
        try:
            self.logger.info("📸 گرفتن اسکرین‌شات از تلگرام...")
            
            # اطمینان از فوکوس روی تلگرام
            if not self.telegram_manager.focus_telegram():
                return None
            
            # گرفتن اسکرین‌شات
            timestamp = int(time.time())
            screenshot_file = f"telegram_ocr_{timestamp}.png"
            screenshot = self.telegram_manager.take_screenshot(screenshot_file)
            
            if screenshot:
                self.logger.info(f"✅ اسکرین‌شات ذخیره شد: {screenshot_file}")
                return screenshot_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطا در گرفتن اسکرین‌شات: {e}")
            return None
    
    def extract_text_from_image(self, image_path):
        """استخراج متن از تصویر با OCR"""
        try:
            if not self.ocr_reader:
                self.logger.error("❌ OCR Reader در دسترس نیست")
                return ""
            
            self.logger.info(f"🔍 تشخیص متن از {image_path}...")
            
            # خواندن تصویر
            results = self.ocr_reader.readtext(image_path)
            
            # استخراج متن‌ها
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # فقط نتایج با اطمینان بالا
                    extracted_texts.append(text.strip())
            
            # ترکیب متن‌ها
            full_text = "\n".join(extracted_texts)
            
            if full_text:
                self.logger.info(f"✅ متن استخراج شد: {len(full_text)} کاراکتر")
                self.logger.info(f"📝 نمونه متن: {full_text[:100]}...")
            else:
                self.logger.warning("⚠️ هیچ متنی تشخیص داده نشد")
            
            return full_text
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تشخیص متن: {e}")
            return ""
    
    def detect_unread_messages(self, image_path):
        """تشخیص پیام‌های خوانده نشده از تصویر"""
        try:
            # باز کردن تصویر
            image = Image.open(image_path)
            width, height = image.size
            
            # ناحیه لیست چت‌ها (سمت چپ)
            chat_list_region = (0, 50, min(400, width//3), height-50)
            chat_list_image = image.crop(chat_list_region)
            
            # ذخیره ناحیه چت‌ها برای OCR
            chat_list_file = f"chat_list_crop_{int(time.time())}.png"
            chat_list_image.save(chat_list_file)
            
            # تشخیص متن در لیست چت‌ها
            chat_text = self.extract_text_from_image(chat_list_file)
            
            # جستجوی نشانگرهای پیام خوانده نشده
            unread_indicators = ['•', '●', 'unread', 'new', '1', '2', '3', '4', '5']
            
            unread_chats = []
            lines = chat_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if any(indicator in line.lower() for indicator in unread_indicators):
                    # احتمال پیام خوانده نشده
                    unread_chats.append(line)
            
            self.logger.info(f"🔍 {len(unread_chats)} چت با پیام خوانده نشده پیدا شد")
            
            return unread_chats
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تشخیص پیام‌های خوانده نشده: {e}")
            return []
    
    def generate_response_ollama(self, message_text, chat_info):
        """تولید پاسخ با Ollama"""
        try:
            # تنظیمات پاسخ بر اساس چت
            response_style = chat_info.get('response_style', 'friendly')
            language = chat_info.get('language', 'fa')
            
            # پرامپت برای تولید پاسخ
            if language == 'fa':
                system_prompt = f"""
شما یک دستیار هوشمند هستید که باید به پیام‌های تلگرام پاسخ دهید.

سبک پاسخ: {response_style}
زبان: فارسی

قوانین:
- پاسخ کوتاه و مفید باشد (حداکثر 200 کاراکتر)
- مؤدبانه و دوستانه باشد
- اگر سوال خاصی نیست، تشکر کنید
- اگر اطلاعات ناقص است، سوال کنید

پیام دریافت شده: {message_text}

پاسخ مناسب:"""
            else:
                system_prompt = f"""
You are an AI assistant responding to Telegram messages.

Response style: {response_style}
Language: English

Rules:
- Keep responses short and helpful (max 200 characters)
- Be polite and friendly
- If no specific question, acknowledge
- If information is incomplete, ask questions

Received message: {message_text}

Appropriate response:"""
            
            # ارسال درخواست به Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.text_model,
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_response = result.get('response', '').strip()
                
                # تمیز کردن پاسخ
                if generated_response:
                    # حذف خطوط اضافی
                    generated_response = generated_response.split('\n')[0]
                    # محدود کردن طول
                    if len(generated_response) > 200:
                        generated_response = generated_response[:197] + "..."
                    
                    self.logger.info(f"✅ پاسخ تولید شد: {generated_response[:50]}...")
                    return generated_response
            
            # پاسخ پیش‌فرض
            if language == 'fa':
                return "سلام! پیام شما دریافت شد. چطور می‌تونم کمکتون کنم؟"
            else:
                return "Hello! Your message was received. How can I help you?"
                
        except Exception as e:
            self.logger.error(f"❌ خطا در تولید پاسخ: {e}")
            if chat_info.get('language', 'fa') == 'fa':
                return "متشکرم از پیامتون! بزودی بررسی می‌کنم."
            else:
                return "Thank you for your message! I'll review it soon."
    
    def click_on_chat(self, chat_position):
        """کلیک روی چت مشخص"""
        try:
            if not self.telegram_manager.telegram_window:
                return False
            
            # موقعیت تقریبی چت در لیست
            window = self.telegram_manager.telegram_window
            chat_x = window.left + 200  # وسط لیست چت‌ها
            chat_y = window.top + 150 + (chat_position * 70)  # فاصله چت‌ها
            
            pyautogui.click(chat_x, chat_y)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در کلیک روی چت: {e}")
            return False
    
    def send_response(self, response_text):
        """ارسال پاسخ در تلگرام"""
        try:
            return self.telegram_manager.send_message(response_text)
        except Exception as e:
            self.logger.error(f"❌ خطا در ارسال پاسخ: {e}")
            return False
    
    def process_telegram_auto_response(self):
        """پردازش خودکار تلگرام و پاسخ‌دهی"""
        try:
            self.logger.info("🤖 شروع پردازش خودکار تلگرام...")
            
            # گرفتن اسکرین‌شات از تلگرام
            screenshot_file = self.take_telegram_screenshot()
            if not screenshot_file:
                return False
            
            # تشخیص پیام‌های خوانده نشده
            unread_chats = self.detect_unread_messages(screenshot_file)
            
            if not unread_chats:
                self.logger.info("📭 هیچ پیام خوانده نشده‌ای پیدا نشد")
                return True
            
            self.logger.info(f"💬 {len(unread_chats)} چت با پیام جدید پیدا شد")
            
            # پردازش هر چت
            for i, chat_line in enumerate(unread_chats[:3]):  # حداکثر 3 چت اول
                try:
                    self.logger.info(f"📱 پردازش چت {i+1}: {chat_line[:30]}...")
                    
                    # کلیک روی چت
                    if not self.click_on_chat(i):
                        continue
                    
                    # گرفتن اسکرین‌شات از چت باز شده
                    time.sleep(1)
                    chat_screenshot = self.telegram_manager.take_single_chat_screenshot()
                    
                    if not chat_screenshot:
                        continue
                    
                    # تشخیص متن از چت
                    chat_text = self.extract_text_from_image(f"single_chat_{int(time.time())}.png")
                    
                    if not chat_text:
                        self.logger.warning(f"⚠️ متنی در چت {i+1} تشخیص داده نشد")
                        continue
                    
                    # یافتن اطلاعات چت
                    chat_info = {'response_style': 'friendly', 'language': 'fa'}
                    
                    # تولید پاسخ
                    response = self.generate_response_ollama(chat_text, chat_info)
                    
                    if response:
                        # ارسال پاسخ
                        if self.send_response(response):
                            self.logger.info(f"✅ پاسخ برای چت {i+1} ارسال شد")
                        else:
                            self.logger.error(f"❌ خطا در ارسال پاسخ چت {i+1}")
                    
                    time.sleep(2)  # تاخیر بین چت‌ها
                    
                except Exception as e:
                    self.logger.error(f"❌ خطا در پردازش چت {i+1}: {e}")
                    continue
            
            self.logger.info("✅ پردازش خودکار تکمیل شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پردازش خودکار: {e}")
            return False
    
    def run_continuous_monitoring(self, interval=30):
        """اجرای نظارت مداوم"""
        try:
            self.logger.info(f"🔄 شروع نظارت مداوم (هر {interval} ثانیه)...")
            
            while True:
                try:
                    self.logger.info("🔍 بررسی پیام‌های جدید...")
                    
                    # پردازش تلگرام
                    self.process_telegram_auto_response()
                    
                    self.logger.info(f"⏱️ انتظار {interval} ثانیه تا بررسی بعدی...")
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("⏹️ نظارت توسط کاربر متوقف شد")
                    break
                except Exception as e:
                    self.logger.error(f"❌ خطا در نظارت: {e}")
                    time.sleep(10)  # انتظار کوتاه و ادامه
                    
        except Exception as e:
            self.logger.error(f"❌ خطا در نظارت مداوم: {e}")

def main():
    """تست سیستم OCR و پاسخ‌دهی"""
    print("🤖 راه‌اندازی سیستم OCR و پاسخ‌دهی خودکار تلگرام...")
    
    try:
        # ایجاد سیستم
        ocr_system = TelegramOCRSystem()
        
        print("\n🎯 انتخاب حالت اجرا:")
        print("1️⃣ تست یکبار (بررسی فوری)")
        print("2️⃣ نظارت مداوم (هر 30 ثانیه)")
        print("3️⃣ فقط تست OCR")
        
        choice = input("\nانتخاب کنید (1-3): ").strip()
        
        if choice == "1":
            print("\n🧪 شروع تست یکبار...")
            ocr_system.process_telegram_auto_response()
            
        elif choice == "2":
            print("\n🔄 شروع نظارت مداوم...")
            ocr_system.run_continuous_monitoring()
            
        elif choice == "3":
            print("\n📸 تست OCR...")
            screenshot = ocr_system.take_telegram_screenshot()
            if screenshot:
                text = ocr_system.extract_text_from_image(screenshot)
                print(f"📝 متن تشخیص داده شده:\n{text}")
        
        else:
            print("❌ انتخاب نامعتبر!")
            
    except Exception as e:
        print(f"❌ خطا در اجرا: {e}")

if __name__ == "__main__":
    main()
