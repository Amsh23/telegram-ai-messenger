#!/usr/bin/env python3
"""
🤖 Telegram OCR & Auto Response System - بهبود یافته
سیستم تشخیص متن و پاسخ‌دهی خودکار تلگرام
"""

import time
import json
import logging
import requests
import base64
import os
from io import BytesIO
from PIL import Image
import pyautogui
from telegram_auto_manager import TelegramAutoManager

class TelegramOCRSystemSimple:
    """سیستم OCR و پاسخ‌دهی خودکار تلگرام - نسخه ساده"""
    
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
    
    def analyze_image_with_ollama(self, image_path):
        """تحلیل تصویر با Ollama Vision"""
        try:
            self.logger.info(f"🔍 تحلیل تصویر با Ollama: {image_path}")
            
            # خواندن تصویر و تبدیل به base64
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # ارسال درخواست به Ollama Vision
            prompt = """
لطفاً این تصویر از تلگرام را تحلیل کنید و به سوالات زیر پاسخ دهید:

1. آیا پیام‌های خوانده نشده‌ای وجود دارد؟
2. اگر پیام جدیدی هست، متن آن چیست؟
3. چه نوع پیامی است؟ (متن، عکس، فایل و...)
4. آیا نیاز به پاسخ دارد؟

لطفاً پاسخ کوتاه و مفید دهید.
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.vision_model,
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('response', '').strip()
                
                if analysis:
                    self.logger.info(f"✅ تحلیل تصویر دریافت شد: {analysis[:100]}...")
                    return analysis
            
            return "تحلیل تصویر ناموفق بود"
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تحلیل تصویر: {e}")
            return "خطا در تحلیل تصویر"
    
    def generate_response_simple(self, analysis_text, chat_info):
        """تولید پاسخ ساده بر اساس تحلیل"""
        try:
            language = chat_info.get('language', 'fa')
            response_style = chat_info.get('response_style', 'friendly')
            
            # پرامپت برای تولید پاسخ
            if language == 'fa':
                system_prompt = f"""
بر اساس این تحلیل از تلگرام، یک پاسخ مناسب تولید کنید:

تحلیل: {analysis_text}

قوانین پاسخ:
- کوتاه و مفید باشد (حداکثر 100 کاراکتر)
- سبک: {response_style}
- فارسی باشد
- اگر پیام جدیدی نیست، "پیام جدیدی نیست" بگویید
- اگر پیام هست اما خاص نیست، تشکر کنید

پاسخ:"""
            else:
                system_prompt = f"""
Based on this Telegram analysis, generate an appropriate response:

Analysis: {analysis_text}

Response rules:
- Short and helpful (max 100 characters)
- Style: {response_style}
- English language
- If no new message, say "No new message"
- If message exists but not specific, thank them

Response:"""
            
            # ارسال درخواست
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.text_model,
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "max_tokens": 100
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_response = result.get('response', '').strip()
                
                if generated_response:
                    # تمیز کردن پاسخ
                    generated_response = generated_response.split('\n')[0]
                    if len(generated_response) > 100:
                        generated_response = generated_response[:97] + "..."
                    
                    self.logger.info(f"✅ پاسخ تولید شد: {generated_response}")
                    return generated_response
            
            # پاسخ پیش‌فرض
            if language == 'fa':
                return "سلام! پیام شما دریافت شد 👍"
            else:
                return "Hello! Message received 👍"
                
        except Exception as e:
            self.logger.error(f"❌ خطا در تولید پاسخ: {e}")
            if chat_info.get('language', 'fa') == 'fa':
                return "متشکرم از پیامتان! 🙏"
            else:
                return "Thank you for your message! 🙏"
    
    def detect_unread_messages_simple(self, analysis):
        """تشخیص ساده پیام‌های خوانده نشده"""
        try:
            # کلمات کلیدی که نشان‌دهنده پیام جدید هستند
            new_message_keywords = [
                'پیام جدید', 'پیام خوانده نشده', 'unread', 'new message',
                'notification', 'دریافت', 'ارسال شده', 'جدید'
            ]
            
            analysis_lower = analysis.lower()
            
            # بررسی وجود کلمات کلیدی
            has_new_message = any(keyword in analysis_lower for keyword in new_message_keywords)
            
            if has_new_message:
                self.logger.info("📬 پیام جدید تشخیص داده شد")
                return True
            else:
                self.logger.info("📭 پیام جدیدی تشخیص داده نشد")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ خطا در تشخیص پیام: {e}")
            return False
    
    def click_on_first_chat(self):
        """کلیک روی اولین چت"""
        try:
            if not self.telegram_manager.telegram_window:
                return False
            
            window = self.telegram_manager.telegram_window
            # موقعیت اولین چت در لیست
            chat_x = window.left + 200
            chat_y = window.top + 150
            
            pyautogui.click(chat_x, chat_y)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در کلیک روی چت: {e}")
            return False
    
    def process_telegram_smart(self):
        """پردازش هوشمند تلگرام"""
        try:
            self.logger.info("🤖 شروع پردازش هوشمند تلگرام...")
            
            # گرفتن اسکرین‌شات از تلگرام
            screenshot_file = self.take_telegram_screenshot()
            if not screenshot_file:
                return False
            
            # تحلیل تصویر با Ollama Vision
            analysis = self.analyze_image_with_ollama(screenshot_file)
            
            # تشخیص پیام جدید
            has_new_message = self.detect_unread_messages_simple(analysis)
            
            if not has_new_message:
                self.logger.info("📭 هیچ پیام جدیدی پیدا نشد")
                return True
            
            self.logger.info("💬 پیام جدید پیدا شد - آماده پاسخ‌دهی...")
            
            # کلیک روی اولین چت
            if not self.click_on_first_chat():
                return False
            
            # یافتن اطلاعات چت
            chat_info = {'response_style': 'friendly', 'language': 'fa'}
            
            # تولید پاسخ
            response = self.generate_response_simple(analysis, chat_info)
            
            if response and "پیام جدیدی نیست" not in response.lower():
                # ارسال پاسخ
                if self.telegram_manager.send_message(response):
                    self.logger.info(f"✅ پاسخ ارسال شد: {response}")
                else:
                    self.logger.error("❌ خطا در ارسال پاسخ")
            else:
                self.logger.info("ℹ️ نیازی به ارسال پاسخ نیست")
            
            self.logger.info("✅ پردازش هوشمند تکمیل شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پردازش هوشمند: {e}")
            return False
    
    def run_monitoring(self, interval=60):
        """نظارت مداوم"""
        try:
            self.logger.info(f"🔄 شروع نظارت مداوم (هر {interval} ثانیه)...")
            
            while True:
                try:
                    self.logger.info("🔍 بررسی تلگرام...")
                    
                    # پردازش تلگرام
                    self.process_telegram_smart()
                    
                    self.logger.info(f"⏱️ انتظار {interval} ثانیه...")
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("⏹️ نظارت متوقف شد")
                    break
                except Exception as e:
                    self.logger.error(f"❌ خطا در نظارت: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            self.logger.error(f"❌ خطا در نظارت مداوم: {e}")

def main():
    """اجرای سیستم"""
    print("🤖 سیستم OCR و پاسخ‌دهی خودکار تلگرام - نسخه بهبود یافته")
    print("=" * 70)
    
    try:
        # ایجاد سیستم
        ocr_system = TelegramOCRSystemSimple()
        
        print("\n🎯 انتخاب حالت:")
        print("1️⃣ تست یکبار")
        print("2️⃣ نظارت مداوم (60 ثانیه)")
        print("3️⃣ فقط تحلیل تصویر")
        
        choice = input("\nانتخاب (1-3): ").strip()
        
        if choice == "1":
            print("\n🧪 تست یکبار...")
            ocr_system.process_telegram_smart()
            
        elif choice == "2":
            print("\n🔄 نظارت مداوم...")
            ocr_system.run_monitoring()
            
        elif choice == "3":
            print("\n📸 تحلیل تصویر...")
            screenshot = ocr_system.take_telegram_screenshot()
            if screenshot:
                analysis = ocr_system.analyze_image_with_ollama(screenshot)
                print(f"📝 تحلیل:\n{analysis}")
        
        else:
            print("❌ انتخاب نامعتبر!")
            
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
