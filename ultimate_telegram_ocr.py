#!/usr/bin/env python3
"""
🤖 Ultimate Telegram OCR & Auto Response System
سیستم کامل و پیشرفته OCR و پاسخ‌دهی خودکار تلگرام
"""

import time
import json
import logging
import requests
import base64
import os
import subprocess
import psutil
from io import BytesIO
from PIL import Image
import pyautogui
import pygetwindow as gw
import win32gui
import win32process

class UltimateTelegramOCR:
    """سیستم کامل OCR و پاسخ‌دهی تلگرام"""
    
    def __init__(self, config_file="admin_config.json"):
        # بارگذاری تنظیمات
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # راه‌اندازی لاگر
        self.setup_logger()
        
        # مسیر تلگرام
        self.telegram_path = self.config.get('telegram_path', '')
        if not self.telegram_path:
            self.logger.error("❌ مسیر تلگرام در تنظیمات مشخص نشده!")
            raise ValueError("مسیر تلگرام مشخص نشده")
        
        # متغیرهای پنجره
        self.telegram_window = None
        self.telegram_process = None
        
        # تنظیمات Ollama
        self.ollama_url = self.config.get('ollama_url', 'http://127.0.0.1:11434')
        self.text_model = self.config.get('ollama_text_model', 'llama3.1:8b')
        self.vision_model = self.config.get('ollama_vision_model', 'llava')
        
        # چت‌های مدیریت شده
        self.managed_chats = {
            chat['id']: chat for chat in self.config.get('managed_chats', [])
        }
        
        self.logger.info("🤖 سیستم کامل OCR تلگرام راه‌اندازی شد")
        self.logger.info(f"📂 مسیر تلگرام: {self.telegram_path}")
    
    def setup_logger(self):
        """راه‌اندازی لاگر"""
        self.logger = logging.getLogger(__name__)
        
        # پاک کردن handlers قبلی
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler('telegram_ocr.log', encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def start_telegram(self):
        """راه‌اندازی تلگرام از مسیر مشخص شده"""
        try:
            self.logger.info("🚀 بررسی وضعیت تلگرام...")
            
            # بررسی اجرای تلگرام
            if self.is_telegram_running():
                self.logger.info("✅ تلگرام در حال اجرا است")
                return True
            
            # بررسی وجود فایل
            if not os.path.exists(self.telegram_path):
                self.logger.error(f"❌ فایل تلگرام پیدا نشد: {self.telegram_path}")
                return False
            
            self.logger.info(f"🚀 راه‌اندازی تلگرام از: {self.telegram_path}")
            
            # اجرای تلگرام
            subprocess.Popen([self.telegram_path])
            
            # انتظار برای بارگذاری
            for i in range(10):
                time.sleep(1)
                if self.is_telegram_running():
                    self.logger.info("✅ تلگرام با موفقیت راه‌اندازی شد")
                    return True
                self.logger.info(f"⏳ انتظار برای بارگذاری... ({i+1}/10)")
            
            self.logger.error("❌ تلگرام راه‌اندازی نشد")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی تلگرام: {e}")
            return False
    
    def is_telegram_running(self):
        """بررسی اجرای تلگرام از مسیر مشخص"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and proc.info['exe'].lower() == self.telegram_path.lower():
                        self.telegram_process = proc
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی تلگرام: {e}")
            return False
    
    def find_telegram_window(self):
        """پیدا کردن پنجره تلگرام واقعی"""
        try:
            self.logger.info("🔍 جستجوی پنجره تلگرام...")
            
            if not self.is_telegram_running():
                self.logger.error("❌ تلگرام در حال اجرا نیست")
                return False
            
            # روش 1: جستجو با pygetwindow
            all_windows = gw.getAllWindows()
            self.logger.info(f"📊 تعداد کل پنجره‌ها: {len(all_windows)}")
            
            telegram_windows = []
            for window in all_windows:
                try:
                    title = window.title.lower()
                    # فیلتر دقیق‌تر برای تلگرام
                    if ('telegram' in title and 
                        'visual studio' not in title and 
                        'vscode' not in title and
                        'notepad' not in title and
                        window.visible and 
                        window.width > 300 and 
                        window.height > 200):
                        telegram_windows.append(window)
                        self.logger.info(f"🔍 پنجره یافت شده: {window.title} ({window.width}x{window.height})")
                except:
                    continue
            
            if telegram_windows:
                # انتخاب بزرگ‌ترین پنجره
                self.telegram_window = max(telegram_windows, key=lambda w: w.width * w.height)
                self.logger.info(f"✅ پنجره تلگرام انتخاب شد: {self.telegram_window.title}")
                return True
            
            # روش 2: جستجو بر اساس PID
            self.logger.info("🔍 جستجو بر اساس PID...")
            telegram_pid = self.telegram_process.pid
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        if pid == telegram_pid:
                            window_title = win32gui.GetWindowText(hwnd)
                            if window_title:
                                rect = win32gui.GetWindowRect(hwnd)
                                width = rect[2] - rect[0]
                                height = rect[3] - rect[1]
                                windows.append((hwnd, window_title, width, height))
                                self.logger.info(f"🔍 پنجره PID یافت شده: {window_title} ({width}x{height})")
                    except:
                        pass
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # انتخاب بزرگ‌ترین
                main_window = max(windows, key=lambda w: w[2] * w[3])
                hwnd, title, width, height = main_window
                
                # ایجاد object ساده
                class SimpleWindow:
                    def __init__(self, hwnd, title, width, height):
                        self._hWnd = hwnd
                        self.title = title
                        self.width = width
                        self.height = height
                        rect = win32gui.GetWindowRect(hwnd)
                        self.left = rect[0]
                        self.top = rect[1]
                    
                    def activate(self):
                        win32gui.SetForegroundWindow(self._hWnd)
                        win32gui.ShowWindow(self._hWnd, 9)  # SW_RESTORE
                    
                    def restore(self):
                        win32gui.ShowWindow(self._hWnd, 9)  # SW_RESTORE
                
                self.telegram_window = SimpleWindow(hwnd, title, width, height)
                self.logger.info(f"✅ پنجره تلگرام با PID پیدا شد: {title}")
                return True
            
            # روش 3: جستجوی عمومی با کلمات کلیدی
            self.logger.info("🔍 جستجوی عمومی...")
            
            # نمایش همه پنجره‌های مرتبط برای دیباگ
            self.logger.info("📋 تمام پنجره‌های قابل مشاهده:")
            for window in gw.getAllWindows():
                try:
                    if window.visible and window.width > 200 and window.height > 100:
                        self.logger.info(f"   📌 {window.title} ({window.width}x{window.height})")
                except:
                    continue
            
            # جستجوی دقیق تلگرام
            for window in gw.getAllWindows():
                try:
                    if window.visible and window.width > 400 and window.height > 300:
                        title_lower = window.title.lower()
                        # جستجوی دقیق‌تر
                        if (title_lower.strip() == 'telegram' or 
                            title_lower.startswith('telegram ') or
                            title_lower.endswith(' telegram') or
                            (len(title_lower) < 50 and 'telegram' in title_lower and 
                             'visual studio' not in title_lower and 'vscode' not in title_lower)):
                            self.telegram_window = window
                            self.logger.info(f"✅ پنجره مشابه پیدا شد: {window.title}")
                            return True
                except:
                    continue
            
            self.logger.error("❌ هیچ پنجره تلگرامی پیدا نشد")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پیدا کردن پنجره: {e}")
            return False
    
    def focus_telegram(self):
        """فوکوس روی تلگرام"""
        try:
            if not self.telegram_window:
                if not self.find_telegram_window():
                    return False
            
            # فوکوس با retry
            for attempt in range(3):
                try:
                    self.telegram_window.activate()
                    time.sleep(0.5)
                    
                    # بررسی ساده
                    self.logger.info("✅ فوکوس روی تلگرام تنظیم شد")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ تلاش {attempt + 1} ناموفق: {e}")
                    if attempt < 2:
                        time.sleep(1)
            
            self.logger.error("❌ نتوانستیم فوکوس کنیم")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در فوکوس: {e}")
            return False
    
    def take_telegram_screenshot(self):
        """گرفتن اسکرین‌شات از تلگرام"""
        try:
            self.logger.info("📸 گرفتن اسکرین‌شات از تلگرام...")
            
            if not self.focus_telegram():
                return None
            
            # گرفتن اسکرین‌شات
            left = self.telegram_window.left
            top = self.telegram_window.top
            width = self.telegram_window.width
            height = self.telegram_window.height
            
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # ذخیره
            timestamp = int(time.time())
            filename = f"telegram_real_{timestamp}.png"
            screenshot.save(filename)
            
            self.logger.info(f"✅ اسکرین‌شات ذخیره شد: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ خطا در اسکرین‌شات: {e}")
            return None
    
    def analyze_with_ollama_vision(self, image_path):
        """تحلیل تصویر با Ollama Vision"""
        try:
            self.logger.info("🔍 تحلیل تصویر با Ollama Vision...")
            
            # خواندن تصویر
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            prompt = """
لطفاً این تصویر از تلگرام را دقیق تحلیل کنید:

1. آیا پیام‌های خوانده نشده وجود دارد؟ (نقطه قرمز، شماره، نشانگر)
2. چه متنی در چت‌ها دیده می‌شود؟
3. آیا چت فعالی باز است؟
4. اگر پیام جدیدی هست، محتوای آن چیست؟
5. چه نوع پیامی است؟ (متن، عکس، فایل)

پاسخ دقیق و کامل دهید:
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.vision_model,
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('response', '').strip()
                
                self.logger.info(f"✅ تحلیل کامل شد: {analysis[:100]}...")
                return analysis
            
            self.logger.error(f"❌ خطا در تحلیل: {response.status_code}")
            return "تحلیل ناموفق"
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تحلیل Ollama: {e}")
            return "خطا در تحلیل"
    
    def detect_new_messages(self, analysis):
        """تشخیص پیام‌های جدید از تحلیل"""
        try:
            keywords = [
                'پیام جدید', 'خوانده نشده', 'unread', 'new message',
                'نقطه قرمز', 'شماره', 'نشانگر', 'notification',
                'دریافت شده', 'ارسال شده'
            ]
            
            analysis_lower = analysis.lower()
            has_new = any(keyword in analysis_lower for keyword in keywords)
            
            if has_new:
                self.logger.info("📬 پیام جدید تشخیص داده شد")
                return True
            else:
                self.logger.info("📭 پیام جدیدی نیست")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ خطا در تشخیص پیام: {e}")
            return False
    
    def generate_smart_response(self, analysis):
        """تولید پاسخ هوشمند"""
        try:
            self.logger.info("🤖 تولید پاسخ هوشمند...")
            
            prompt = f"""
بر اساس این تحلیل از تلگرام، یک پاسخ مناسب تولید کن:

تحلیل: {analysis}

قوانین:
- اگر پیام جدیدی نیست، "هیچ پیام جدیدی نیست" بگو
- اگر پیام جدید هست، پاسخ مناسب و مؤدبانه بده
- پاسخ کوتاه باشد (حداکثر 100 کاراکتر)
- فارسی باشد
- طبیعی و دوستانه باشد

پاسخ:"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.text_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 150
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_response = result.get('response', '').strip()
                
                # تمیز کردن پاسخ
                if generated_response:
                    generated_response = generated_response.split('\n')[0]
                    if len(generated_response) > 100:
                        generated_response = generated_response[:97] + "..."
                    
                    self.logger.info(f"✅ پاسخ تولید شد: {generated_response}")
                    return generated_response
            
            return "سلام! پیام شما دریافت شد 👍"
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تولید پاسخ: {e}")
            return "متشکرم از پیامتان! 🙏"
    
    def send_message(self, message):
        """ارسال پیام در تلگرام"""
        try:
            self.logger.info(f"📤 ارسال پیام: {message}")
            
            if not self.focus_telegram():
                return False
            
            # کلیک در فیلد پیام
            center_x = self.telegram_window.left + self.telegram_window.width // 2
            bottom_y = self.telegram_window.top + self.telegram_window.height - 100
            
            pyautogui.click(center_x, bottom_y)
            time.sleep(0.5)
            
            # تایپ پیام
            pyautogui.write(message, interval=0.02)
            time.sleep(0.5)
            
            # ارسال
            pyautogui.press('enter')
            time.sleep(0.5)
            
            self.logger.info("✅ پیام ارسال شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در ارسال: {e}")
            return False
    
    def click_on_first_unread_chat(self):
        """کلیک روی اولین چت خوانده نشده"""
        try:
            if not self.telegram_window:
                return False
            
            # موقعیت تقریبی اولین چت
            chat_x = self.telegram_window.left + 200
            chat_y = self.telegram_window.top + 150
            
            pyautogui.click(chat_x, chat_y)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در کلیک چت: {e}")
            return False
    
    def process_telegram_complete(self):
        """پردازش کامل تلگرام"""
        try:
            self.logger.info("🚀 شروع پردازش کامل تلگرام...")
            
            # راه‌اندازی تلگرام
            if not self.start_telegram():
                return False
            
            time.sleep(2)
            
            # پیدا کردن پنجره
            if not self.find_telegram_window():
                return False
            
            # گرفتن اسکرین‌شات
            screenshot_file = self.take_telegram_screenshot()
            if not screenshot_file:
                return False
            
            # تحلیل تصویر
            analysis = self.analyze_with_ollama_vision(screenshot_file)
            
            # تشخیص پیام جدید
            has_new_message = self.detect_new_messages(analysis)
            
            if not has_new_message:
                self.logger.info("📭 هیچ پیام جدیدی نیست")
                return True
            
            # کلیک روی چت
            if not self.click_on_first_unread_chat():
                return False
            
            # تولید پاسخ
            response = self.generate_smart_response(analysis)
            
            if "هیچ پیام جدیدی نیست" not in response:
                # ارسال پاسخ
                if self.send_message(response):
                    self.logger.info("✅ پاسخ ارسال شد")
                else:
                    self.logger.error("❌ خطا در ارسال پاسخ")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پردازش کامل: {e}")
            return False
    
    def run_continuous_monitoring(self, interval=60):
        """نظارت مداوم"""
        try:
            self.logger.info(f"🔄 شروع نظارت مداوم (هر {interval} ثانیه)")
            
            while True:
                try:
                    self.logger.info("🔍 بررسی تلگرام...")
                    
                    success = self.process_telegram_complete()
                    
                    if success:
                        self.logger.info("✅ بررسی کامل شد")
                    else:
                        self.logger.warning("⚠️ مشکل در بررسی")
                    
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
    """اجرای برنامه اصلی"""
    print("🤖 سیستم کامل OCR و پاسخ‌دهی خودکار تلگرام")
    print("=" * 60)
    
    try:
        # ایجاد سیستم
        ocr_system = UltimateTelegramOCR()
        
        print("\n🎯 حالت‌های عملکرد:")
        print("1️⃣ تست کامل یکبار")
        print("2️⃣ نظارت مداوم (60 ثانیه)")
        print("3️⃣ فقط راه‌اندازی تلگرام")
        print("4️⃣ فقط تحلیل اسکرین‌شات")
        
        choice = input("\nانتخاب کنید (1-4): ").strip()
        
        if choice == "1":
            print("\n🧪 اجرای تست کامل...")
            success = ocr_system.process_telegram_complete()
            if success:
                print("✅ تست موفقیت‌آمیز!")
            else:
                print("❌ مشکل در تست!")
                
        elif choice == "2":
            print("\n🔄 شروع نظارت مداوم...")
            ocr_system.run_continuous_monitoring()
            
        elif choice == "3":
            print("\n🚀 راه‌اندازی تلگرام...")
            success = ocr_system.start_telegram()
            if success:
                print("✅ تلگرام راه‌اندازی شد!")
            else:
                print("❌ مشکل در راه‌اندازی!")
                
        elif choice == "4":
            print("\n📸 گرفتن اسکرین‌شات و تحلیل...")
            if ocr_system.start_telegram() and ocr_system.find_telegram_window():
                screenshot = ocr_system.take_telegram_screenshot()
                if screenshot:
                    analysis = ocr_system.analyze_with_ollama_vision(screenshot)
                    print(f"\n📝 تحلیل:\n{analysis}")
                    
        else:
            print("❌ انتخاب نامعتبر!")
            
    except Exception as e:
        print(f"❌ خطا در اجرا: {e}")

if __name__ == "__main__":
    main()
