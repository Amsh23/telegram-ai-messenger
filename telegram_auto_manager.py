#!/usr/bin/env python3
"""
🤖 Telegram Auto Manager - مدیریت خودکار تلگرام
ماژول کامل برای اجرا، کنترل و مدیریت تلگرام
"""

import subprocess
import time
import os
import pygetwindow as gw
import pyautogui
import psutil
from pathlib import Path
import logging

class TelegramAutoManager:
    """مدیر خودکار تلگرام"""
    
    def __init__(self, config):
        self.config = config
        self.telegram_window = None
        self.telegram_process = None
        self.is_initialized = False
        
        # تنظیم لاگر
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # متغیرهای محیطی
        self.enable_window_testing = config.get('ENABLE_WINDOW_TESTING', 'true').lower() == 'true'
        self.enable_chat_testing = config.get('ENABLE_CHAT_TESTING', 'true').lower() == 'true'
        self.window_titles = config.get('WINDOW_TITLES_TO_TRY', 'Telegram,Telegram Desktop,تلگرام,TelegramDesktop').split(',')
        self.window_classes = config.get('WINDOW_CLASSES_TO_TRY', 'Qt5QWindowIcon,TelegramDesktop').split(',')
        self.testing_interval = int(config.get('TESTING_INTERVAL_SECONDS', '30'))
        
        self.logger.info("✅ مدیر تلگرام راه‌اندازی شد")
    
    def start_telegram(self):
        """راه‌اندازی تلگرام"""
        try:
            self.logger.info("🚀 در حال راه‌اندازی تلگرام...")
            
            # مسیرهای احتمالی تلگرام
            telegram_paths = [
                os.path.expanduser("~/AppData/Roaming/Telegram Desktop/Telegram.exe"),
                "C:\\Program Files\\Telegram Desktop\\Telegram.exe",
                "C:\\Program Files (x86)\\Telegram Desktop\\Telegram.exe",
                os.path.expanduser("~/AppData/Local/Telegram Desktop/Telegram.exe")
            ]
            
            # بررسی اگر تلگرام در حال اجرا است
            if self.is_telegram_running():
                self.logger.info("✅ تلگرام در حال اجرا است")
                return True
            
            # تلاش برای راه‌اندازی
            for path in telegram_paths:
                if os.path.exists(path):
                    self.logger.info(f"📂 تلگرام پیدا شد: {path}")
                    subprocess.Popen([path])
                    time.sleep(5)  # انتظار برای بارگذاری
                    
                    if self.is_telegram_running():
                        self.logger.info("✅ تلگرام با موفقیت راه‌اندازی شد")
                        return True
            
            self.logger.error("❌ تلگرام پیدا نشد یا راه‌اندازی نشد")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی تلگرام: {e}")
            return False
    
    def is_telegram_running(self):
        """بررسی اجرای تلگرام"""
        try:
            telegram_processes = ['Telegram.exe', 'telegram.exe', 'TelegramDesktop.exe']
            
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in telegram_processes:
                    self.telegram_process = proc
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی وضعیت تلگرام: {e}")
            return False
    
    def find_telegram_window(self):
        """پیدا کردن پنجره تلگرام با روش‌های مختلف"""
        try:
            self.logger.info("🔍 در حال جستجوی پنجره تلگرام...")
            
            # روش 1: جستجوی دقیق با عناوین مختلف
            for title in self.window_titles:
                title = title.strip()
                windows = gw.getWindowsWithTitle(title)
                
                for window in windows:
                    if window.visible and window.width > 0 and window.height > 0:
                        self.telegram_window = window
                        self.logger.info(f"✅ پنجره تلگرام پیدا شد: {title}")
                        return True
            
            # روش 2: جستجوی جزئی در عناوین
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if window.visible and window.title:
                    title_lower = window.title.lower()
                    if any(t.lower() in title_lower for t in ['telegram', 'تلگرام']):
                        if window.width > 400 and window.height > 300:  # حداقل اندازه
                            self.telegram_window = window
                            self.logger.info(f"✅ پنجره تلگرام پیدا شد (جستجوی جزئی): {window.title}")
                            return True
            
            # روش 3: بر اساس پروسه
            if self.is_telegram_running() and self.telegram_process:
                try:
                    import win32gui
                    import win32process
                    
                    def enum_windows_callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            if pid == self.telegram_process.pid:
                                windows.append(hwnd)
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(enum_windows_callback, windows)
                    
                    if windows:
                        # پیدا کردن پنجره اصلی (بزرگ‌ترین)
                        main_window = None
                        max_area = 0
                        
                        for hwnd in windows:
                            rect = win32gui.GetWindowRect(hwnd)
                            width = rect[2] - rect[0]
                            height = rect[3] - rect[1]
                            area = width * height
                            
                            if area > max_area and width > 400 and height > 300:
                                max_area = area
                                main_window = hwnd
                        
                        if main_window:
                            # تبدیل به شیء pygetwindow
                            for window in gw.getAllWindows():
                                if hasattr(window, '_hWnd') and window._hWnd == main_window:
                                    self.telegram_window = window
                                    self.logger.info("✅ پنجره تلگرام از طریق پروسه پیدا شد")
                                    return True
                
                except ImportError:
                    self.logger.warning("⚠️ win32gui در دسترس نیست، از روش دیگر استفاده می‌کنیم")
                except Exception as e:
                    self.logger.warning(f"⚠️ خطا در جستجوی بر اساس پروسه: {e}")
            
            self.logger.error("❌ پنجره تلگرام پیدا نشد")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پیدا کردن پنجره: {e}")
            return False
    
    def focus_telegram(self):
        """فوکوس کردن روی تلگرام با retry"""
        if not self.telegram_window:
            if not self.find_telegram_window():
                return False
        
        try:
            # تلاش برای فوکوس با retry
            for attempt in range(3):
                try:
                    self.telegram_window.activate()
                    time.sleep(0.5)
                    
                    # بررسی فوکوس
                    if hasattr(self.telegram_window, 'isActive') and self.telegram_window.isActive:
                        self.logger.info("✅ فوکوس روی تلگرام تنظیم شد")
                        return True
                    
                    # روش جایگزین
                    self.telegram_window.restore()
                    time.sleep(0.2)
                    self.telegram_window.activate()
                    time.sleep(0.5)
                    
                    if hasattr(self.telegram_window, 'isActive') and self.telegram_window.isActive:
                        self.logger.info("✅ فوکوس روی تلگرام تنظیم شد (روش دوم)")
                        return True
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ تلاش {attempt + 1} برای فوکوس ناموفق: {e}")
                    if attempt < 2:
                        time.sleep(1)
            
            self.logger.error("❌ نتوانستیم روی تلگرام فوکوس کنیم")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در فوکوس کردن: {e}")
            return False
    
    def maximize_telegram(self):
        """بزرگ کردن پنجره تلگرام"""
        try:
            if not self.telegram_window:
                if not self.find_telegram_window():
                    self.logger.error("❌ پنجره تلگرام پیدا نشد برای بزرگ کردن")
                    return False
            
            # بزرگ کردن پنجره
            self.telegram_window.maximize()
            time.sleep(0.5)
            
            # اطمینان از فوکوس
            self.telegram_window.activate()
            time.sleep(0.5)
            
            self.logger.info("✅ پنجره تلگرام بزرگ شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در بزرگ کردن پنجره: {e}")
            # تلاش با روش جایگزین
            try:
                if self.telegram_window:
                    # تنظیم اندازه دستی
                    screen_width = pyautogui.size().width
                    screen_height = pyautogui.size().height
                    
                    self.telegram_window.resizeTo(screen_width, screen_height)
                    self.telegram_window.moveTo(0, 0)
                    time.sleep(0.5)
                    
                    self.logger.info("✅ پنجره تلگرام بزرگ شد (روش جایگزین)")
                    return True
            except Exception as e2:
                self.logger.error(f"❌ خطا در روش جایگزین: {e2}")
            
            return False
    
    def force_maximize_telegram(self):
        """بزرگ کردن اجباری پنجره تلگرام"""
        try:
            self.logger.info("🔧 بزرگ کردن اجباری پنجره تلگرام...")
            
            # پیدا کردن پنجره
            if not self.find_telegram_window():
                return False
            
            # بزرگ کردن
            if not self.maximize_telegram():
                return False
            
            # بررسی اندازه نهایی
            if self.telegram_window:
                width = self.telegram_window.width
                height = self.telegram_window.height
                
                if width >= 1200 and height >= 800:
                    self.logger.info(f"✅ پنجره بزرگ شد: {width}x{height}")
                    return True
                else:
                    self.logger.warning(f"⚠️ اندازه پنجره کوچک: {width}x{height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در بزرگ کردن اجباری: {e}")
            return False
    
    def test_window_connection(self):
        """تست اتصال و تشخیص پنجره تلگرام"""
        try:
            self.logger.info("🧪 شروع تست اتصال پنجره...")
            
            # تست 1: پیدا کردن پنجره
            if not self.find_telegram_window():
                self.logger.error("❌ تست ناموفق: پنجره تلگرام پیدا نشد")
                return False
            
            # تست 2: فوکوس کردن
            if not self.focus_telegram():
                self.logger.error("❌ تست ناموفق: نتوانستیم روی پنجره فوکوس کنیم")
                return False
            
            # تست 3: گرفتن اسکرین‌شات
            screenshot = self.take_screenshot()
            if not screenshot:
                self.logger.error("❌ تست ناموفق: نتوانستیم اسکرین‌شات بگیریم")
                return False
            
            # تست 4: بررسی ابعاد پنجره
            if self.telegram_window.width < 800 or self.telegram_window.height < 600:
                self.logger.warning("⚠️ هشدار: ابعاد پنجره کوچک است، ممکن است مشکل ایجاد شود")
            
            self.logger.info("✅ تست اتصال پنجره موفقیت‌آمیز بود")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تست اتصال پنجره: {e}")
            return False
    
    def test_chat_access(self):
        """تست دسترسی به چت‌ها"""
        try:
            self.logger.info("🧪 شروع تست دسترسی چت...")
            
            # فوکوس روی تلگرام
            if not self.focus_telegram():
                return False
            
            # رفتن به لیست چت‌ها (Escape برای اطمینان)
            pyautogui.press('escape')
            time.sleep(0.5)
            
            # گرفتن اسکرین‌شات از لیست چت‌ها
            screenshot = self.take_screenshot()
            if not screenshot:
                self.logger.error("❌ نتوانستیم اسکرین‌شات از چت‌ها بگیریم")
                return False
            
            # بررسی ناحیه چت‌ها
            chat_region = self.get_chat_list_region()
            if not chat_region:
                self.logger.error("❌ نتوانستیم ناحیه چت‌ها را تشخیص دهیم")
                return False
            
            self.logger.info("✅ تست دسترسی چت موفقیت‌آمیز بود")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تست دسترسی چت: {e}")
            return False
    
    def test_message_sending(self):
        """تست ارسال پیام (بدون ارسال واقعی)"""
        try:
            self.logger.info("🧪 شروع تست ارسال پیام...")
            
            # فوکوس روی تلگرام
            if not self.focus_telegram():
                return False
            
            # تست تایپ کردن در فیلد پیام
            test_message = "تست اتصال - این پیام ارسال نمی‌شود"
            
            # پیدا کردن فیلد پیام (کلیک در پایین صفحه)
            if self.telegram_window:
                center_x = self.telegram_window.left + self.telegram_window.width // 2
                bottom_y = self.telegram_window.top + self.telegram_window.height - 100
                
                pyautogui.click(center_x, bottom_y)
                time.sleep(0.5)
                
                # تایپ پیام تستی
                pyautogui.write(test_message, interval=0.02)
                time.sleep(0.5)
                
                # پاک کردن پیام (بدون ارسال)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                
                self.logger.info("✅ تست تایپ و پاک کردن پیام موفقیت‌آمیز بود")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تست ارسال پیام: {e}")
            return False
    
    def get_telegram_status(self):
        """گرفتن وضعیت کامل تلگرام"""
        try:
            status = {
                'is_running': self.is_telegram_running(),
                'window_found': bool(self.telegram_window),
                'window_active': False,
                'window_size': None,
                'window_position': None
            }
            
            if self.telegram_window:
                try:
                    status['window_active'] = self.telegram_window.isActive
                    status['window_size'] = (self.telegram_window.width, self.telegram_window.height)
                    status['window_position'] = (self.telegram_window.left, self.telegram_window.top)
                except:
                    pass
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ خطا در گرفتن وضعیت: {e}")
            return {}
    
    def take_screenshot(self, save_file=None):
        """گرفتن اسکرین‌شات از تلگرام"""
        try:
            if not self.telegram_window:
                if not self.find_telegram_window():
                    self.logger.error("❌ پنجره تلگرام پیدا نشد برای اسکرین‌شات")
                    return None
            
            # فوکوس روی تلگرام
            if not self.focus_telegram():
                return None
            
            # گرفتن اسکرین‌شات از ناحیه پنجره
            left = self.telegram_window.left
            top = self.telegram_window.top
            width = self.telegram_window.width
            height = self.telegram_window.height
            
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # ذخیره اگر مسیر داده شده
            if save_file:
                screenshot.save(save_file)
                self.logger.info(f"📸 اسکرین‌شات تلگرام ذخیره شد: {save_file}")
            
            return screenshot
            
        except Exception as e:
            self.logger.error(f"❌ خطا در گرفتن اسکرین‌شات: {e}")
            return None
    
    def take_chat_list_screenshot(self, save_file=None):
        """گرفتن اسکرین‌شات از لیست چت‌ها"""
        try:
            if not self.focus_telegram():
                return None
            
            # رفتن به لیست اصلی چت‌ها
            pyautogui.press('escape')
            time.sleep(0.5)
            
            # گرفتن اسکرین‌شات از ناحیه چت‌ها
            if not self.telegram_window:
                return None
            
            # ناحیه سمت چپ (لیست چت‌ها)
            left = self.telegram_window.left
            top = self.telegram_window.top + 50  # بعد از نوار بالا
            width = min(400, self.telegram_window.width // 3)
            height = self.telegram_window.height - 100
            
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # تولید نام فایل خودکار
            if save_file is None:
                timestamp = int(time.time())
                save_file = f"chat_list_{timestamp}.png"
            
            screenshot.save(save_file)
            self.logger.info(f"📸 اسکرین‌شات لیست چت‌ها ذخیره شد: {save_file}")
            
            return screenshot
            
        except Exception as e:
            self.logger.error(f"❌ خطا در گرفتن اسکرین‌شات چت‌ها: {e}")
            return None
    
    def take_single_chat_screenshot(self, save_file=None):
        """گرفتن اسکرین‌شات از چت فعال"""
        try:
            if not self.focus_telegram():
                return None
            
            # گرفتن اسکرین‌شات از ناحیه چت فعال
            if not self.telegram_window:
                return None
            
            # ناحیه سمت راست (چت فعال)
            chat_left = self.telegram_window.left + min(400, self.telegram_window.width // 3)
            chat_top = self.telegram_window.top + 50
            chat_width = self.telegram_window.width - min(400, self.telegram_window.width // 3)
            chat_height = self.telegram_window.height - 100
            
            screenshot = pyautogui.screenshot(region=(chat_left, chat_top, chat_width, chat_height))
            
            # تولید نام فایل خودکار
            if save_file is None:
                timestamp = int(time.time())
                save_file = f"single_chat_{timestamp}.png"
            
            screenshot.save(save_file)
            self.logger.info(f"📸 اسکرین‌شات چت فعال ذخیره شد: {save_file}")
            
            return screenshot
            
        except Exception as e:
            self.logger.error(f"❌ خطا در گرفتن اسکرین‌شات چت فعال: {e}")
            return None
    
    def scan_and_screenshot_chats(self):
        """اسکن و عکس‌برداری از چت‌ها"""
        try:
            self.logger.info("📸 شروع اسکن و عکس‌برداری چت‌ها...")
            
            if not self.focus_telegram():
                return False
            
            # رفتن به لیست چت‌ها
            pyautogui.press('escape')
            time.sleep(1)
            
            # گرفتن اسکرین‌شات از لیست چت‌ها
            chat_list_screenshot = self.take_chat_list_screenshot()
            
            if chat_list_screenshot:
                self.logger.info("✅ اسکرین‌شات لیست چت‌ها گرفته شد")
            
            # اسکن چت‌های باز شده اخیر
            for i in range(5):  # 5 چت اول
                try:
                    # کلیک روی چت
                    chat_y = self.telegram_window.top + 150 + (i * 70)  # موقعیت تقریبی چت‌ها
                    chat_x = self.telegram_window.left + 200
                    
                    pyautogui.click(chat_x, chat_y)
                    time.sleep(1)
                    
                    # گرفتن اسکرین‌شات از چت
                    single_chat_screenshot = self.take_single_chat_screenshot()
                    
                    if single_chat_screenshot:
                        self.logger.info(f"✅ اسکرین‌شات چت {i+1} گرفته شد")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ خطا در چت {i+1}: {e}")
            
            self.logger.info("✅ اسکن و عکس‌برداری کامل شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در اسکن چت‌ها: {e}")
            return False
    
    def get_chat_list_region(self):
        """تشخیص ناحیه لیست چت‌ها"""
        try:
            if not self.telegram_window:
                return None
            
            # ناحیه سمت چپ که معمولاً چت‌ها آنجا هستند
            region = {
                'left': self.telegram_window.left,
                'top': self.telegram_window.top + 50,  # بعد از نوار بالا
                'width': min(400, self.telegram_window.width // 3),
                'height': self.telegram_window.height - 100
            }
            
            return region
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تشخیص ناحیه چت: {e}")
            return None
    
    def run_comprehensive_tests(self):
        """اجرای تست‌های کامل"""
        try:
            self.logger.info("🧪 شروع تست‌های کامل سیستم...")
            
            results = {
                'telegram_running': False,
                'window_connection': False,
                'chat_access': False,
                'message_test': False,
                'overall_status': 'FAILED'
            }
            
            # تست 1: بررسی اجرای تلگرام
            if self.is_telegram_running():
                results['telegram_running'] = True
                self.logger.info("✅ تست 1 موفق: تلگرام در حال اجرا است")
            else:
                self.logger.error("❌ تست 1 ناموفق: تلگرام در حال اجرا نیست")
                return results
            
            # تست 2: اتصال پنجره
            if self.test_window_connection():
                results['window_connection'] = True
                self.logger.info("✅ تست 2 موفق: اتصال پنجره")
            else:
                self.logger.error("❌ تست 2 ناموفق: مشکل در اتصال پنجره")
                return results
            
            # تست 3: دسترسی چت
            if self.test_chat_access():
                results['chat_access'] = True
                self.logger.info("✅ تست 3 موفق: دسترسی چت")
            else:
                self.logger.warning("⚠️ تست 3 ناموفق: مشکل در دسترسی چت")
            
            # تست 4: ارسال پیام
            if self.test_message_sending():
                results['message_test'] = True
                self.logger.info("✅ تست 4 موفق: تست پیام")
            else:
                self.logger.warning("⚠️ تست 4 ناموفق: مشکل در تست پیام")
            
            # بررسی وضعیت کلی
            if results['telegram_running'] and results['window_connection']:
                if results['chat_access'] and results['message_test']:
                    results['overall_status'] = 'EXCELLENT'
                elif results['chat_access'] or results['message_test']:
                    results['overall_status'] = 'GOOD'
                else:
                    results['overall_status'] = 'BASIC'
            
            self.logger.info(f"🎯 نتیجه نهایی تست‌ها: {results['overall_status']}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تست‌های کامل: {e}")
            return results
    
    def send_message(self, message):
        """ارسال پیام در تلگرام"""
        try:
            self.logger.info(f"📤 ارسال پیام: {message[:50]}...")
            
            # فوکوس روی تلگرام
            if not self.focus_telegram():
                return False
            
            # تایپ پیام
            pyautogui.write(message, interval=0.01)
            time.sleep(0.5)
            
            # ارسال پیام (Enter)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            self.logger.info("✅ پیام ارسال شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در ارسال پیام: {e}")
            return False
    
    def close_telegram(self):
        """بستن تلگرام"""
        try:
            self.logger.info("🚪 بستن تلگرام...")
            
            if self.telegram_process:
                self.telegram_process.terminate()
                time.sleep(2)
                
                if self.telegram_process.is_running():
                    self.telegram_process.kill()
                
                self.logger.info("✅ تلگرام بسته شد")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطا در بستن تلگرام: {e}")
            return False
