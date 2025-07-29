#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram AI Auto Messenger with Ollama
تلگرام مسنجر خودکار هوشمند با Ollama
"""

import time
import subprocess
import pyautogui
import pyperclip
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import threading
import json
import os
import requests
import random
from datetime import datetime
import re
import winreg
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageTk
import io
import pygetwindow as gw
import glob

# غیرفعال کردن failsafe برای عملیات طولانی
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.2

class TelegramUIDetector:
    """کلاس هوشمند برای تشخیص عناصر رابط کاربری تلگرام"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.confidence_threshold = 0.8
        self.chat_list_region = None
        self.message_area_region = None
        self.input_box_region = None
        self.send_button_region = None
        
    def take_screenshot(self, region=None):
        """گرفتن اسکرین‌شات از ناحیه مشخص"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"خطا در گرفتن اسکرین‌شات: {e}")
            return None
    
    def detect_telegram_window(self):
        """تشخیص پنجره تلگرام و تعیین نواحی مختلف"""
        try:
            screenshot = self.take_screenshot()
            if screenshot is None:
                return False
            
            # تشخیص رنگ‌های مشخصه تلگرام (آبی تیره برای header)
            # رنگ header تلگرام معمولاً در حدود این مقادیر است
            telegram_blue_lower = np.array([100, 50, 50])  # HSV
            telegram_blue_upper = np.array([130, 255, 255])
            
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            blue_mask = cv2.inRange(hsv, telegram_blue_lower, telegram_blue_upper)
            
            # پیدا کردن contours
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # بزرگترین contour که احتمالاً header تلگرام است
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                if w > 400 and h > 30:  # حداقل اندازه برای header
                    # تعیین نواحی بر اساس موقعیت header
                    self.chat_list_region = (0, y + h, 350, self.screen_height - y - h)
                    self.message_area_region = (350, y + h, self.screen_width - 350, self.screen_height - y - h - 80)
                    self.input_box_region = (350, self.screen_height - 80, self.screen_width - 350 - 50, 40)
                    self.send_button_region = (self.screen_width - 50, self.screen_height - 80, 50, 40)
                    return True
            
            # روش جایگزین: تعیین نواحی بر اساس اندازه صفحه
            self.set_default_regions()
            return True
            
        except Exception as e:
            print(f"خطا در تشخیص پنجره تلگرام: {e}")
            self.set_default_regions()
            return False
    
    def set_default_regions(self):
        """تنظیم نواحی پیش‌فرض"""
        self.chat_list_region = (0, 80, 350, self.screen_height - 160)
        self.message_area_region = (350, 80, self.screen_width - 350, self.screen_height - 160)
        self.input_box_region = (350, self.screen_height - 80, self.screen_width - 400, 40)
        self.send_button_region = (self.screen_width - 50, self.screen_height - 80, 50, 40)
    
    def find_chat_items(self):
        """پیدا کردن آیتم‌های چت در لیست"""
        try:
            if not self.chat_list_region:
                self.detect_telegram_window()
            
            screenshot = self.take_screenshot(self.chat_list_region)
            if screenshot is None:
                return []
            
            # تبدیل به grayscale برای بهتر کردن تشخیص
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # تشخیص خطوط افقی (جداکننده چت‌ها)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            detect_horizontal = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            
            chat_positions = []
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                if w > 200:  # عرض مناسب برای یک چت
                    # محاسبه موقعیت واقعی روی صفحه
                    real_x = self.chat_list_region[0] + x + w//2
                    real_y = self.chat_list_region[1] + y + 30  # وسط آیتم چت
                    chat_positions.append((real_x, real_y))
            
            # اگر خط‌ها پیدا نشد، از روش تقسیم‌بندی یکنواخت استفاده کن
            if not chat_positions:
                chat_height = 70  # تقریبی ارتفاع هر چت
                num_chats = self.chat_list_region[3] // chat_height
                for i in range(min(15, num_chats)):  # حداکثر 15 چت
                    x = self.chat_list_region[0] + 175  # وسط لیست
                    y = self.chat_list_region[1] + 35 + (i * chat_height)
                    chat_positions.append((x, y))
            
            return chat_positions[:15]  # حداکثر 15 چت برمی‌گردانیم
            
        except Exception as e:
            print(f"خطا در یافتن آیتم‌های چت: {e}")
            return []
    
    def find_message_input_box(self):
        """پیدا کردن باکس ورودی پیام"""
        try:
            if not self.input_box_region:
                self.detect_telegram_window()
            
            screenshot = self.take_screenshot(self.input_box_region)
            if screenshot is None:
                return None
            
            # تشخیص ناحیه‌های روشن (باکس ورودی معمولاً روشن است)
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # threshold برای پیدا کردن نواحی روشن
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # پیدا کردن contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 200 and 20 < h < 60:  # اندازه مناسب برای input box
                    # محاسبه موقعیت واقعی
                    real_x = self.input_box_region[0] + x + w//2
                    real_y = self.input_box_region[1] + y + h//2
                    return (real_x, real_y)
            
            # موقعیت پیش‌فرض
            return (self.input_box_region[0] + self.input_box_region[2]//2, 
                   self.input_box_region[1] + self.input_box_region[3]//2)
            
        except Exception as e:
            print(f"خطا در یافتن باکس ورودی: {e}")
            return None
    
    def find_send_button(self):
        """پیدا کردن دکمه ارسال"""
        try:
            if not self.send_button_region:
                self.detect_telegram_window()
            
            screenshot = self.take_screenshot(self.send_button_region)
            if screenshot is None:
                return None
            
            # تشخیص رنگ آبی دکمه ارسال
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            blue_lower = np.array([100, 100, 100])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # پیدا کردن contours
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                if cv2.contourArea(largest_contour) > 100:  # حداقل اندازه
                    real_x = self.send_button_region[0] + x + w//2
                    real_y = self.send_button_region[1] + y + h//2
                    return (real_x, real_y)
            
            # موقعیت پیش‌فرض
            return (self.send_button_region[0] + self.send_button_region[2]//2,
                   self.send_button_region[1] + self.send_button_region[3]//2)
            
        except Exception as e:
            print(f"خطا در یافتن دکمه ارسال: {e}")
            return None
    
    def detect_unread_chats(self):
        """تشخیص چت‌های خوانده نشده"""
        try:
            if not self.chat_list_region:
                self.detect_telegram_window()
            
            screenshot = self.take_screenshot(self.chat_list_region)
            if screenshot is None:
                return []
            
            # تشخیص رنگ آبی badge های پیام خوانده نشده
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            blue_lower = np.array([100, 100, 100])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # پیدا کردن دایره‌های کوچک (badge ها)
            circles = cv2.HoughCircles(blue_mask, cv2.HOUGH_GRADIENT, 1, 20,
                                     param1=30, param2=15, minRadius=5, maxRadius=20)
            
            unread_positions = []
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    # تبدیل به موقعیت واقعی و تخمین موقعیت چت
                    chat_x = self.chat_list_region[0] + 175
                    chat_y = self.chat_list_region[1] + y
                    unread_positions.append((chat_x, chat_y))
            
            return unread_positions
            
        except Exception as e:
            print(f"خطا در تشخیص چت‌های خوانده نشده: {e}")
            return []

class TelegramAIMessenger:
    def __init__(self):
        self.is_running = False
        self.message_thread = None
        self.config_file = "ai_config.json"
        self.detected_accounts = []
        
        # تشخیص هوشمند UI
        self.ui_detector = TelegramUIDetector()
        
        self.load_config()
        
        # پیکربندی pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        # تشخیص خودکار اکانت‌های تلگرام
        self.auto_detect_telegram_accounts()
        
        self.setup_gui()
    
    def screenshot_telegram_and_reply(self):
        """
        نسخه بهبود یافته: اسکرین‌شات دقیق و تشخیص صحیح چت‌ها
        """
        # گرفتن مسیر تلگرام از کانفیگ
        selected_account = self.account_var.get().strip() if hasattr(self, 'account_var') else "تلگرام Portable"
        account_info = next((acc for acc in self.config.get("telegram_accounts", []) if acc["username"] == selected_account), None)
        
        if not account_info:
            self.log_message("❌ اطلاعات اکانت انتخاب شده پیدا نشد!")
            return
        
        telegram_path = account_info.get("telegram_path", "")
        self.log_message(f"� شروع اسکرین‌شات بهبود یافته: {selected_account}")
        self.log_message("🐈 تشخیص دقیق چت‌ها و پیام‌ها")
        
        try:
            # مرحله 1: باز کردن تلگرام
            self.log_message(f"📱 باز کردن تلگرام: {os.path.basename(telegram_path)}")
            subprocess.Popen([telegram_path])
            time.sleep(6)  # زمان بیشتر برای بارگذاری
            
            # مرحله 2: پیدا کردن پنجره اصلی
            target_window = self.find_main_telegram_window()
            if not target_window:
                self.log_message("❌ پنجره اصلی تلگرام پیدا نشد!")
                return
            
            self.log_message(f"✅ پنجره اصلی: '{target_window.title}' - {target_window.width}x{target_window.height}")
            
            # مرحله 3: فعال‌سازی پنجره
            self.safe_activate_window_improved(target_window)
            
            # مرحله 4: fullscreen قدرتمند
            if not self.force_maximize_telegram():
                self.log_message("⚠️ نتوانستیم کاملاً maximize کنیم، ادامه می‌دهیم...")
            
            # مرحله 5: مراحل دستی fullscreen
            self.manual_fullscreen_steps()
            
            # مرحله 6: اسکرین‌شات تأیید شده
            screenshot, screenshot_path = self.take_verified_screenshot()
            if not screenshot:
                self.log_message("❌ مشکل در اسکرین‌شات")
                return
            
            self.log_message(f"✅ اسکرین‌شات نهایی: {screenshot_path}")
            
            # مرحله 7: تشخیص layout هوشمند
            chat_region, message_region, input_region, send_region = self.smart_layout_detection(screenshot)
            
            # مرحله 8: تشخیص چت‌ها
            chat_positions = self.detect_chat_list_improved(screenshot, chat_region)
            
            if not chat_positions:
                self.log_message("❌ چتی پیدا نشد")
                return
            
            # مرحله 9: پردازش چت‌ها
            self.log_message(f"🔄 پردازش {min(len(chat_positions), 5)} چت...")
            
            success_count = 0
            for i, (chat_x, chat_y) in enumerate(chat_positions[:5]):
                if not self.is_running:
                    break
                
                self.log_message(f"\n--- چت {i+1} ---")
                
                # کلیک روی چت
                if not self.safe_click(chat_x, chat_y, f"چت {i+1}"):
                    continue
                
                time.sleep(2)
                
                # خواندن پیام‌ها
                messages = self.safe_read_messages(message_region)
                
                if messages:
                    self.log_message(f"📖 {len(messages)} پیام دریافت شد:")
                    for msg in messages:
                        self.log_message(f"   • {msg[:60]}...")
                    
                    # تولید پاسخ Littlejoy
                    reply = self.generate_littlejoy_reply_improved(messages)
                    
                    # ارسال پاسخ
                    if self.safe_send_message(reply, input_region):
                        self.log_message(f"✅ پاسخ ارسال شد: {reply[:50]}...")
                        success_count += 1
                    else:
                        self.log_message("❌ مشکل در ارسال")
                else:
                    self.log_message("⚠️ پیامی یافت نشد")
                
                time.sleep(3)  # فاصله بین چت‌ها
            
            self.log_message(f"\n✅ پردازش کامل! {success_count}/{min(len(chat_positions), 5)} چت موفق")
            
        except Exception as e:
            self.log_message(f"❌ خطا در اسکرین‌شات بهبود یافته: {e}")
            import traceback
            self.log_message(f"جزئیات خطا: {traceback.format_exc()}")
    
    def find_main_telegram_window(self):
        """پیدا کردن پنجره اصلی تلگرام (بزرگترین پنجره)"""
        try:
            all_windows = gw.getAllWindows()
            telegram_windows = []
            
            for window in all_windows:
                window_title = window.title.lower()
                if ('telegram' in window_title and 
                    'messenger' not in window_title and
                    'ai' not in window_title and
                    window.width > 400 and window.height > 300):  # حداقل اندازه معقول
                    telegram_windows.append(window)
                    self.log_message(f"📱 پنجره: '{window.title}' - {window.width}x{window.height}")
            
            if not telegram_windows:
                self.log_message("❌ هیچ پنجره تلگرام مناسب پیدا نشد")
                return None
            
            # انتخاب بزرگترین پنجره
            main_window = max(telegram_windows, key=lambda w: w.width * w.height)
            return main_window
            
        except Exception as e:
            self.log_message(f"❌ خطا در جستجوی پنجره: {e}")
            return None
    
    def safe_activate_window_improved(self, window):
        """فعال‌سازی بهبود یافته پنجره"""
        try:
            window.activate()
            time.sleep(1)
            self.log_message("✅ پنجره فعال شد")
        except:
            center_x = window.left + window.width // 2
            center_y = window.top + window.height // 2
            pyautogui.click(center_x, center_y)
            time.sleep(1)
            self.log_message("✅ پنجره با کلیک فعال شد")
    
    def force_maximize_telegram(self):
        """اجبار برای maximize کردن تلگرام"""
        try:
            self.log_message("💪 اجبار برای maximize کردن...")
            
            # تلاش چندگانه F11
            for i in range(3):
                pyautogui.press('f11')
                time.sleep(1.5)
                
                # بررسی اندازه پنجره
                window = self.find_main_telegram_window()
                if window and window.width > 2000:  # اگر کافی بزرگ شد
                    self.log_message(f"✅ موفق! اندازه: {window.width}x{window.height}")
                    return True
            
            # ترکیب کلیدها
            combinations = [['alt', 'enter'], ['win', 'up']]
            
            for combo in combinations:
                pyautogui.hotkey(*combo)
                time.sleep(2)
                pyautogui.press('f11')
                time.sleep(2)
                
                window = self.find_main_telegram_window()
                if window and window.width > 2000:
                    self.log_message(f"✅ موفق با ترکیب!")
                    return True
            
            return False
            
        except Exception as e:
            self.log_message(f"❌ خطا در maximize: {e}")
            return False
    
    def manual_fullscreen_steps(self):
        """مراحل دستی fullscreen"""
        try:
            self.log_message("🎯 اجرای مراحل دستی fullscreen...")
            
            # مرحله 1: Escape و کلیک وسط
            pyautogui.press('escape')
            time.sleep(0.5)
            
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height // 2)
            time.sleep(0.5)
            
            # مرحله 2: تلاش‌های F11
            for attempt in range(3):
                pyautogui.press('f11')
                time.sleep(2)
                
                window = self.find_main_telegram_window()
                if window:
                    coverage = (window.width * window.height) / (screen_width * screen_height)
                    if coverage > 0.8:
                        self.log_message("✅ Fullscreen موفقیت‌آمیز!")
                        return True
            
            return False
        except Exception as e:
            self.log_message(f"❌ خطا در fullscreen دستی: {e}")
            return False
    
    def take_verified_screenshot(self):
        """گرفتن اسکرین‌شات تأیید شده"""
        try:
            time.sleep(3)
            screenshot = pyautogui.screenshot()
            
            timestamp = int(time.time())
            path = f"telegram_verified_{timestamp}.png"
            screenshot.save(path)
            
            # تحلیل کیفیت
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            height, width = img.shape[:2]
            
            screen_w, screen_h = pyautogui.size()
            coverage = (width * height) / (screen_w * screen_h)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            variance = np.var(gray)
            
            self.log_message(f"� اسکرین‌شات: {width}x{height}, پوشش: {coverage:.1%}, تنوع: {variance:.1f}")
            
            if coverage > 0.7 and variance > 100 and width > 2000:
                self.log_message(f"✅ اسکرین‌شات خوب")
            else:
                self.log_message(f"⚠️ اسکرین‌شات ممکن است مشکل داشته باشد")
            
            return screenshot, path
            
        except Exception as e:
            self.log_message(f"❌ خطا در اسکرین‌شات: {e}")
            return None, None
    
    def smart_layout_detection(self, screenshot):
        """تشخیص هوشمند layout"""
        try:
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            height, width = img.shape[:2]
            
            # تقسیم‌بندی بر اساس نسبت طلایی تلگرام
            sidebar_width = int(width * 0.28)  # 28% عرض
            
            chat_list = {
                'x': 10, 'y': 90,
                'width': sidebar_width - 20,
                'height': height - 180
            }
            
            message_area = {
                'x': sidebar_width + 10, 'y': 90,
                'width': width - sidebar_width - 20,
                'height': height - 180
            }
            
            input_box = {
                'x': sidebar_width + 30, 'y': height - 100,
                'width': width - sidebar_width - 120,
                'height': 60
            }
            
            send_button = {
                'x': width - 80, 'y': height - 100,
                'width': 60, 'height': 60
            }
            
            self.log_message(f"� Layout: Sidebar {sidebar_width}px")
            
            return chat_list, message_area, input_box, send_button
            
        except Exception as e:
            self.log_message(f"❌ خطا در تشخیص layout: {e}")
            width, height = pyautogui.size()
            return (
                {'x': 10, 'y': 90, 'width': width//4, 'height': height-180},
                {'x': width//4+10, 'y': 90, 'width': width*3//4-20, 'height': height-180},
                {'x': width//4+30, 'y': height-100, 'width': width*3//4-120, 'height': 60},
                {'x': width-80, 'y': height-100, 'width': 60, 'height': 60}
            )
    
    def detect_chat_list_improved(self, screenshot, chat_region):
        """تشخیص بهبود یافته لیست چت‌ها"""
        try:
            chat_height = 65  # ارتفاع متوسط هر چت
            start_y = chat_region['y'] + 20
            max_chats = min(8, (chat_region['height'] - 40) // chat_height)
            
            chat_positions = []
            
            for i in range(max_chats):
                center_x = chat_region['x'] + chat_region['width'] // 2
                center_y = start_y + (i * chat_height)
                
                if center_y < chat_region['y'] + chat_region['height'] - 20:
                    chat_positions.append((center_x, center_y))
            
            self.log_message(f"🎯 {len(chat_positions)} موقعیت چت تعیین شد")
            return chat_positions
            
        except Exception as e:
            self.log_message(f"❌ خطا در تشخیص چت‌ها: {e}")
            return []
    
    def safe_click(self, x, y, description=""):
        """کلیک ایمن با بررسی محدوده"""
        try:
            screen_w, screen_h = pyautogui.size()
            
            if 0 <= x <= screen_w and 0 <= y <= screen_h:
                pyautogui.click(x, y)
                time.sleep(0.5)
                return True
            else:
                self.log_message(f"⚠️ موقعیت خارج از محدوده: ({x}, {y})")
                return False
        except Exception as e:
            self.log_message(f"❌ خطا در کلیک: {e}")
            return False
    
    def safe_read_messages(self, message_region=None):
        """خواندن پیشرفته و دقیق پیام‌ها"""
        try:
            self.log_message("📖 خواندن پیشرفته پیام‌ها...")
            
            # اگر message_region داده نشده، محاسبه کن
            if message_region is None:
                screenshot = pyautogui.screenshot()
                width, height = screenshot.size
                
                # محاسبه ناحیه پیام بر اساس layout
                sidebar_width = int(width * 0.28)  # 28% برای sidebar
                message_start_x = sidebar_width + 50
                message_start_y = 100
                message_end_x = width - 50
                message_end_y = height - 150
                
                message_region = {
                    'x': message_start_x,
                    'y': message_start_y,
                    'width': message_end_x - message_start_x,
                    'height': message_end_y - message_start_y
                }
                self.log_message(f"📍 ناحیه پیام محاسبه شد: {message_region}")
            
            # کلیک در ناحیه پیام‌ها
            center_x = message_region['x'] + message_region['width'] // 2
            center_y = message_region['y'] + message_region['height'] // 2
            
            if not self.safe_click(center_x, center_y, "ناحیه پیام"):
                return []
            
            # اسکرول به پایین‌ترین پیام‌ها
            for _ in range(5):
                pyautogui.scroll(-5, x=center_x, y=center_y)
                time.sleep(0.3)
            
            time.sleep(1)
            
            # روش 1: خواندن با انتخاب دقیق
            # شروع از پایین ناحیه پیام‌ها
            start_x = message_region['x'] + 100
            start_y = message_region['y'] + message_region['height'] - 200  # 200 پیکسل از پایین
            end_x = message_region['x'] + message_region['width'] - 100
            end_y = message_region['y'] + message_region['height'] - 50    # 50 پیکسل از پایین
            
            # کلیک و کشیدن برای انتخاب آخرین پیام‌ها
            pyautogui.click(start_x, start_y)
            time.sleep(0.3)
            pyautogui.drag(end_x, end_y, duration=0.8)
            time.sleep(0.5)
            
            # کپی محتوا
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            
            text1 = pyperclip.paste()
            
            # روش 2: خواندن با Ctrl+A در ناحیه محدود
            # انتخاب ناحیه کوچک‌تر برای پیام‌های اخیر
            small_x = message_region['x'] + 150
            small_y = message_region['y'] + message_region['height'] - 300
            small_w = min(600, message_region['width'] - 300)
            small_h = 200
            
            pyautogui.click(small_x, small_y)
            time.sleep(0.3)
            pyautogui.drag(small_x + small_w, small_y + small_h, duration=0.5)
            time.sleep(0.5)
            
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.8)
            
            text2 = pyperclip.paste()
            
            # ترکیب و پردازش متن‌ها
            all_texts = [text1, text2]
            all_messages = []
            
            for text in all_texts:
                if text and len(text) > 3:
                    # جدا کردن خطوط
                    lines = text.strip().split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        
                        # فیلتر کردن خطوط معتبر
                        if (line and 
                            len(line) > 3 and 
                            not line.isdigit() and 
                            not line.startswith('http') and
                            'python' not in line.lower() and
                            'smart_telegram' not in line.lower() and
                            'telegram_ai' not in line.lower() and
                            'online' not in line.lower() and
                            'last seen' not in line.lower() and
                            'typing' not in line.lower() and
                            'در حال تایپ' not in line and
                            'آنلاین' not in line and
                            len(line) < 500):  # حداکثر طول پیام
                            
                            # حذف timestamp ها
                            clean_line = re.sub(r'\d{2}:\d{2}', '', line).strip()
                            clean_line = re.sub(r'\d{1,2}/\d{1,2}', '', clean_line).strip()
                            
                            if clean_line and clean_line not in all_messages:
                                all_messages.append(clean_line)
            
            # انتخاب بهترین پیام‌ها
            valid_messages = []
            for msg in all_messages:
                # بررسی اینکه پیام واقعی باشد
                if (any(char.isalpha() for char in msg) and  # حداقل یک حرف
                    not msg.startswith('✅') and             # نه پیام سیستم
                    not msg.startswith('📱') and             # نه پیام سیستم
                    not msg.startswith('🔍') and             # نه پیام سیستم
                    len(msg.split()) > 1):                   # حداقل 2 کلمه
                    valid_messages.append(msg)
            
            # برگرداندن آخرین پیام‌های معتبر
            final_messages = list(dict.fromkeys(valid_messages))  # حذف تکراری
            result = final_messages[-3:] if final_messages else []  # 3 پیام آخر
            
            if result:
                self.log_message(f"📝 {len(result)} پیام معتبر خوانده شد")
                for i, msg in enumerate(result):
                    self.log_message(f"   {i+1}. {msg[:80]}...")
            else:
                self.log_message("⚠️ هیچ پیام معتبری یافت نشد")
            
            return result
            
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن پیشرفته: {e}")
            return []
    
    def safe_send_message(self, message, input_region):
        """ارسال ایمن پیام"""
        try:
            # کلیک روی input box
            center_x = input_region['x'] + input_region['width'] // 2
            center_y = input_region['y'] + input_region['height'] // 2
            
            if not self.safe_click(center_x, center_y, "input box"):
                return False
            
            # پاک کردن
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # تایپ پیام
            pyautogui.typewrite(message, interval=0.02)
            time.sleep(1)
            
            # ارسال
            pyautogui.press('enter')
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال: {e}")
            return False
    
    def generate_littlejoy_reply_improved(self, messages):
        """تولید پاسخ هوشمند بر اساس محتوای واقعی پیام‌ها"""
        try:
            if not messages:
                return "🐈 سلام! چطوری؟ 😊"
            
            # ترکیب پیام‌ها برای تحلیل
            full_context = " ".join(messages).lower()
            last_message = messages[-1].lower() if messages else ""
            
            # تحلیل محتوای پیام برای تولید پاسخ مناسب
            
            # 1. پاسخ به سلام و احوالپرسی
            if any(word in full_context for word in ['سلام', 'hi', 'hello', 'سلامت', 'درود']):
                responses = [
                    "🐈 سلام عزیزم! چطوری؟ خوش اومدی! 😊",
                    "� سلام گلم! حالت چطوره؟ خیلی دلم برات تنگ شده! 💕",
                    "🐾 سلام جونم! چه خبر؟ خوشحالم که پیام دادی! 😸"
                ]
                return random.choice(responses)
            
            # 2. پاسخ به سوال احوال
            if any(word in full_context for word in ['چطور', 'حال', 'خوب', 'چه خبر', 'چطوری']):
                responses = [
                    "� ممنون که پرسیدی! منم خوبم عزیزم! تو چطوری؟ 💕",
                    "🐈 خوبم گلم! خیلی خوشحالم که باهام حرف می‌زنی! تو چی؟ 😊",
                    "� عالیم دوست عزیزم! امیدوارم تو هم خوب باشی! 😻"
                ]
                return random.choice(responses)
            
            # 3. پاسخ به تشکر
            if any(word in full_context for word in ['ممنون', 'مرسی', 'thanks', 'تشکر', 'سپاس']):
                responses = [
                    "🐈 خواهش می‌کنم عزیزم! هر وقت کاری داشتی بگو! 😊",
                    "� قابل نداره گلم! همیشه در خدمتم! 💕",
                    "🐾 عزیزی که! خوشحالم کمکت کردم! 😻"
                ]
                return random.choice(responses)
            
            # 4. پاسخ به سوال
            if any(word in last_message for word in ['؟', 'چی', 'چه', 'کی', 'کجا', 'چرا', 'چطور']):
                if 'کار' in full_context or 'شغل' in full_context:
                    return "🐈 من یه ربات دوستانه‌ام! وظیفه‌ام کمک کردن به دوستانه! تو چی؟ 😊"
                elif 'اسم' in full_context or 'نام' in full_context:
                    return "😸 منم Littlejoy! خیلی خوشحالم آشناتون شدم! 🐾"
                elif 'وقت' in full_context or 'زمان' in full_context:
                    return "🐱 همیشه وقت دارم برای دوستای عزیزم مثل تو! 💕"
                else:
                    return "🐈 جالب سوال پرسیدی! بیشتر توضیح بده ببینم چطور کمکت کنم! 😊"
            
            # 5. پاسخ به احساسات
            if any(word in full_context for word in ['ناراحت', 'غمگین', 'خسته', 'بد']):
                responses = [
                    "🐾 عزیزم ناراحت نباش! همه چیز درست میشه! من کنارتم! 💕",
                    "😿 آخ دلم برات می‌سوزه! بگو چی شده تا کمکت کنم! 🤗",
                    "🐈 نگران نباش گلم! همیشه امیدوار باش! 😊"
                ]
                return random.choice(responses)
            
            if any(word in full_context for word in ['خوشحال', 'شاد', 'عالی', 'فوق‌العاده']):
                responses = [
                    "😻 وای چقدر خوشحالم که خوشحالی! منم خیلی شادم! 🎉",
                    "🐈 آفرین! عالیه که حالت خوبه! منم باهات شاد میشم! 😸",
                    "🐾 چه خوب! انرژی مثبتت رو احساس می‌کنم! 💕"
                ]
                return random.choice(responses)
            
            # 6. پاسخ به موضوعات خاص
            if any(word in full_context for word in ['کار', 'پروژه', 'تسک']):
                return "🐈 آه کار! امیدوارم پروژه‌هات عالی پیش بره! موفق باشی! ��😊"
            
            if any(word in full_context for word in ['غذا', 'نهار', 'شام', 'صبحانه']):
                return "😸 مم مم! غذا؟ من که گربه‌ام، عاشق ماهی و شیرم! تو چی دوست داری؟ 🐟🥛"
            
            if any(word in full_context for word in ['خواب', 'خسته', 'استراحت']):
                return "😴 خواب خوب چیز خوبیه! حتماً استراحت کن تا حالت بهتر بشه! شب بخیر! 🌙💤"
            
            if any(word in full_context for word in ['بازی', 'گیم', 'سرگرمی']):
                return "🎮 بازی؟ من عاشق بازی با نخ و توپم! تو چه بازی‌هایی دوست داری؟ 😸"
            
            # 7. پاسخ‌های عمومی بر اساس طول پیام
            if len(full_context) > 100:  # پیام طولانی
                responses = [
                    "🐈 وای چقدر حرف داری! دوست دارم باهات حرف بزنم! ادامه بده! 😊",
                    "😸 خیلی جالب بود! بیشتر بگو ببینم چی میشه! 🤗",
                    "🐾 چه داستان جالبی! من که گوش می‌دم عزیزم! 👂💕"
                ]
                return random.choice(responses)
            
            elif len(full_context) < 10:  # پیام خیلی کوتاه
                responses = [
                    "🐈 هی! یه چیز کوتاه گفتی! بیشتر حرف بزن که بدونم چی می‌خوای! 😊",
                    "😸 کمی کم حرف زدی! بیشتر توضیح بده! 🤗",
                    "🐾 خب؟ منتظرم بیشتر بگی! 😻"
                ]
                return random.choice(responses)
            
            # 8. پاسخ‌های پیش‌فرض Littlejoy
            default_responses = [
                "🐈 جالب بود! ممنون که باهام حرف زدی! چیز دیگه‌ای هم داری؟ 😊",
                "😸 آها! فهمیدم! خیلی خوشحالم که پیام دادی! 💕",
                "🐾 حرف قشنگی زدی! دوست دارم بیشتر باهات حرف بزنم! 😻",
                "🐱 ممنون از پیامت! همیشه خوشحالم که ازت می‌شنوم! 🤗",
                "😺 چه جالب! یه گربه کنجکاو مثل من همیشه سوال داره! بگو ببینم چی شده؟ �"
            ]
            
            return random.choice(default_responses)
            
        except Exception as e:
            self.log_message(f"❌ خطا در تولید پاسخ هوشمند: {e}")
            return "🐈 سلام! چطوری عزیزم؟ 😊"
    
    def find_real_telegram_window(self):
        """پیدا کردن پنجره تلگرام واقعی (نه برنامه Python)"""
        try:
            all_windows = gw.getAllWindows()
            telegram_windows = []
            
            for window in all_windows:
                window_title = window.title.lower()
                
                # فیلتر کردن پنجره‌هایی که احتمالاً تلگرام هستند
                if ('telegram' in window_title and 
                    'messenger' not in window_title and  # حذف برنامه Python ما
                    'ai' not in window_title and        # حذف برنامه Python ما
                    window.width > 300 and              # حداقل اندازه
                    window.height > 200):
                    telegram_windows.append(window)
                    self.log_message(f"🔍 پنجره تلگرام پیدا شد: '{window.title}' - {window.width}x{window.height}")
            
            # اگر چندین پنجره پیدا شد، بزرگترین را انتخاب کن
            if telegram_windows:
                largest_window = max(telegram_windows, key=lambda w: w.width * w.height)
                return largest_window
            
            # اگر پیدا نشد، سعی کن با جستجوی گسترده‌تر
            for window in all_windows:
                if ('telegram' in window.title.lower() and 
                    window.width > 200 and window.height > 150):
                    self.log_message(f"🔍 پنجره احتمالی تلگرام: '{window.title}'")
                    return window
            
            return None
            
        except Exception as e:
            self.log_message(f"❌ خطا در جستجوی پنجره تلگرام: {e}")
            return None
    
    def safe_activate_window(self, window):
        """فعال‌سازی ایمن پنجره"""
        try:
            # روش 1: استفاده از pygetwindow
            window.activate()
            time.sleep(1)
            self.log_message("✅ پنجره با pygetwindow فعال شد")
        except:
            try:
                # روش 2: استفاده از کلیک
                center_x = window.left + window.width // 2
                center_y = window.top + window.height // 2
                pyautogui.click(center_x, center_y)
                time.sleep(1)
                self.log_message("✅ پنجره با کلیک فعال شد")
            except:
                try:
                    # روش 3: استفاده از Alt+Tab
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(1)
                    self.log_message("✅ پنجره با Alt+Tab فعال شد")
                except:
                    self.log_message("⚠️ نتوانستم پنجره را فعال کنم")
    
    def safe_fullscreen_telegram(self, window):
        """تمام صفحه کردن ایمن تلگرام"""
        try:
            self.log_message("📺 در حال تمام صفحه کردن تلگرام...")
            
            # روش 1: maximize
            try:
                window.maximize()
                time.sleep(1)
                self.log_message("✅ پنجره maximize شد")
            except:
                self.log_message("⚠️ نتوانستم پنجره را maximize کنم")
            
            # روش 2: F11 برای fullscreen
            pyautogui.press('f11')
            time.sleep(2)
            self.log_message("✅ F11 فشرده شد برای fullscreen")
            
            # روش 3: کلیدهای Windows برای maximize
            pyautogui.hotkey('win', 'up')
            time.sleep(1)
            self.log_message("✅ Windows+Up فشرده شد")
            
        except Exception as e:
            self.log_message(f"⚠️ خطا در تمام صفحه کردن: {e}")
    
    def verify_telegram_screenshot(self, screenshot):
        """بررسی اینکه اسکرین‌شات از تلگرام است"""
        try:
            # تبدیل به آرایه numpy
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # جستجو برای نشانه‌های تلگرام
            # 1. رنگ آبی مشخصه تلگرام
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            blue_lower = np.array([100, 50, 50])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            blue_pixels = cv2.countNonZero(blue_mask)
            
            # 2. بررسی وجود ساختار UI مشابه تلگرام
            # تشخیص خطوط عمودی (جداکننده لیست چت‌ها)
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            vertical_pixels = cv2.countNonZero(vertical_lines)
            
            # اگر تعداد کافی پیکسل آبی یا خطوط عمودی وجود داشت
            if blue_pixels > 1000 or vertical_pixels > 500:
                self.log_message(f"✅ اسکرین‌شات از تلگرام تأیید شد (آبی: {blue_pixels}, خطوط: {vertical_pixels})")
                return True
            else:
                self.log_message(f"❌ اسکرین‌شات احتمالاً از تلگرام نیست (آبی: {blue_pixels}, خطوط: {vertical_pixels})")
                return False
                
        except Exception as e:
            self.log_message(f"❌ خطا در بررسی اسکرین‌شات: {e}")
            return False
    
    def manual_open_telegram(self):
        """باز کردن دستی تلگرام"""
        try:
            self.log_message("📱 باز کردن دستی تلگرام...")
            
            # روش 1: فشردن Win+R و تایپ telegram
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.typewrite('telegram')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(3)
            
            self.log_message("✅ تلگرام با Win+R باز شد")
            
        except Exception as e:
            self.log_message(f"❌ خطا در باز کردن دستی تلگرام: {e}")
    
    def open_telegram_with_path_safe(self, telegram_path):
        """باز کردن ایمن تلگرام با مسیر مشخص"""
        try:
            if telegram_path and os.path.exists(telegram_path):
                self.log_message(f"📱 باز کردن تلگرام از: {telegram_path}")
                
                # برای WindowsApps از روش مخصوص استفاده کن
                if "WindowsApps" in telegram_path:
                    # باز کردن از طریق Windows Store App
                    os.system('start ms-windows-store://pdp/?productid=9NZTWSQNTD0S')
                    time.sleep(3)
                    # یا استفاده از protocol
                    os.system('start telegram://')
                    time.sleep(2)
                else:
                    subprocess.Popen([telegram_path])
                    time.sleep(3)
            else:
                self.log_message("⚠️ مسیر تلگرام یافت نشد، از روش دستی استفاده می‌شود")
                self.manual_open_telegram()
                
        except Exception as e:
            self.log_message(f"❌ خطا در باز کردن تلگرام: {e}")
            self.manual_open_telegram()
    
    def open_telegram_with_path(self, telegram_path):
        """باز کردن تلگرام با مسیر مشخص"""
        try:
            if telegram_path and os.path.exists(telegram_path):
                self.log_message(f"📱 باز کردن تلگرام از: {telegram_path}")
                subprocess.Popen([telegram_path])
                time.sleep(3)
            else:
                self.log_message("⚠️ مسیر تلگرام یافت نشد، از تلگرام باز سیستم استفاده می‌شود")
                self.open_telegram()
        except Exception as e:
            self.log_message(f"❌ خطا در باز کردن تلگرام: {e}")
            self.open_telegram()
    
    def navigate_to_littlejoy_folder_improved(self):
        """هدایت بهبود یافته به فولدر Littlejoy🐈"""
        try:
            self.log_message("� در حال هدایت بهبود یافته به فولدر Littlejoy🐈...")
            
            # کلیک روی نوار جستجو (موقعیت تمام صفحه)
            search_x = self.ui_detector.screen_width // 4
            search_y = 60
            
            pyautogui.click(search_x, search_y)
            time.sleep(1)
            
            # پاک کردن نوار جستجو
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.5)
            
            # تایپ نام فولدر
            search_terms = ["Littlejoy", "littlejoy", "🐈", "گربه"]
            
            for term in search_terms:
                pyautogui.typewrite(term, interval=0.1)
                time.sleep(1.5)
                
                # بررسی نتایج
                pyautogui.press('enter')
                time.sleep(2)
                
                # اگر نتیجه‌ای پیدا شد، خروج از حلقه
                screenshot = pyautogui.screenshot()
                if self.check_search_results(screenshot):
                    self.log_message(f"✅ فولدر با کلیدواژه '{term}' پیدا شد")
                    break
                
                # پاک کردن برای تلاش بعدی
                pyautogui.click(search_x, search_y)
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyautogui.press('delete')
                time.sleep(0.5)
            
            self.log_message("✅ تلاش برای هدایت به فولدر Littlejoy تمام شد")
            
        except Exception as e:
            self.log_message(f"❌ خطا در هدایت بهبود یافته: {e}")
    
    def check_search_results(self, screenshot):
        """بررسی وجود نتایج جستجو"""
        try:
            # تبدیل اسکرین‌شات به آرایه numpy
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # بررسی وجود محتوا در ناحیه نتایج جستجو
            search_results_area = gray[150:400, 50:400]
            
            # اگر تنوع رنگی وجود داشت، احتمالاً نتایج جستجو هست
            if np.std(search_results_area) > 20:
                return True
            
            return False
        except:
            return False
    
    def detect_littlejoy_chats_improved(self, img):
        """تشخیص بهبود یافته چت‌های Littlejoy"""
        try:
            chat_positions = []
            
            # تعیین ناحیه لیست چت‌ها
            chat_list_x = 0
            chat_list_y = 150
            chat_list_width = int(self.ui_detector.screen_width * 0.25)
            chat_list_height = self.ui_detector.screen_height - 300
            
            # استخراج ناحیه چت‌ها
            chat_area = img[chat_list_y:chat_list_y + chat_list_height, 
                           chat_list_x:chat_list_x + chat_list_width]
            
            # تبدیل به grayscale
            gray = cv2.cvtColor(chat_area, cv2.COLOR_BGR2GRAY)
            
            # تشخیص نواحی با تغییرات نور (چت‌ها)
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # تحلیل contours برای یافتن چت‌ها
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # شرایط یک چت معتبر
                if (w > 150 and  # عرض مناسب
                    40 < h < 100 and  # ارتفاع مناسب
                    cv2.contourArea(contour) > 1000):  # حداقل مساحت
                    
                    # محاسبه موقعیت مرکز چت
                    center_x = chat_list_x + x + w // 2
                    center_y = chat_list_y + y + h // 2
                    
                    chat_positions.append((center_x, center_y))
            
            # اگر با contour چیزی پیدا نشد، از روش شبکه‌ای استفاده کن
            if not chat_positions:
                self.log_message("🔄 استفاده از روش شبکه‌ای برای تشخیص چت‌ها...")
                
                chat_height = 70  # ارتفاع متوسط هر چت
                chat_start_y = 180  # شروع لیست چت‌ها
                max_chats = min(10, (chat_list_height - 50) // chat_height)
                
                for i in range(max_chats):
                    center_x = chat_list_width // 2  # وسط لیست چت‌ها
                    center_y = chat_start_y + (i * chat_height)
                    
                    # بررسی اینکه در محدوده مجاز است
                    if center_y < self.ui_detector.screen_height - 200:
                        chat_positions.append((center_x, center_y))
            
            self.log_message(f"🎯 {len(chat_positions)} موقعیت چت تشخیص داده شد")
            return chat_positions
            
        except Exception as e:
            self.log_message(f"❌ خطا در تشخیص چت‌های Littlejoy: {e}")
            return []
    
    def process_single_chat(self):
        """پردازش یک چت منفرد"""
        try:
            # دریافت نام چت
            chat_name = self.get_current_chat_name_improved()
            
            if chat_name == "نامشخص":
                return False
            
            self.log_message(f"💬 پردازش چت: {chat_name}")
            
            # بررسی فیلتر Littlejoy
            if not self.filter_chats_for_littlejoy(chat_name):
                self.log_message(f"⏭️ چت {chat_name} در فولدر Littlejoy نیست")
                return False
            
            # خواندن پیام‌ها
            messages = self.safe_read_messages(None)  # None یعنی استفاده از کل ناحیه پیام
            
            if not messages:
                self.log_message("⚠️ پیامی یافت نشد")
                return False
            
            self.log_message(f"📖 {len(messages)} پیام خوانده شد")
            
            # تولید پاسخ مخصوص Littlejoy
            reply = self.generate_littlejoy_reply_improved(messages)
            
            # ارسال پاسخ
            if self.send_message_improved(reply):
                self.log_message(f"✅ پاسخ ارسال شد: {reply[:50]}...")
                return True
            else:
                self.log_message("❌ خطا در ارسال پاسخ")
                return False
                
        except Exception as e:
            self.log_message(f"❌ خطا در پردازش چت: {e}")
            return False
            
            left, top, width, height = target_window.left, target_window.top, target_window.width, target_window.height
            self.log_message(f"📏 ابعاد پنجره: {width}x{height} در موقعیت ({left}, {top})")
            
            # گرفتن اسکرین‌شات از پنجره تلگرام
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save('telegram_screenshot.png')
            self.log_message("✅ اسکرین‌شات از تلگرام ذخیره شد!")
            
            # تنظیم detector برای ابعاد جدید
            self.ui_detector.screen_width = width
            self.ui_detector.screen_height = height
            
            # تشخیص ساختار پنجره تلگرام
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.log_message("🔍 شروع تشخیص چت‌ها از اسکرین‌شات...")
            
            # تنظیم نواحی بر اساس ابعاد پنجره
            self.ui_detector.chat_list_region = (0, 80, int(width * 0.35), height - 160)
            self.ui_detector.message_area_region = (int(width * 0.35), 80, int(width * 0.65), height - 160)
            self.ui_detector.input_box_region = (int(width * 0.35), height - 80, int(width * 0.6), 40)
            self.ui_detector.send_button_region = (int(width * 0.95) - 50, height - 80, 50, 40)
            
            # تشخیص چت‌های خوانده نشده (اولویت)
            unread_chats = self.detect_unread_chats_from_screenshot(img)
            if unread_chats:
                self.log_message(f"📬 {len(unread_chats)} چت خوانده نشده تشخیص داده شد")
                
                for i, (chat_x, chat_y) in enumerate(unread_chats[:5]):  # حداکثر 5 چت خوانده نشده
                    if not self.is_running:
                        break
                    
                    # محاسبه موقعیت مطلق
                    abs_x = left + chat_x
                    abs_y = top + chat_y
                    
                    self.log_message(f"📨 کلیک روی چت خوانده نشده {i+1} در ({abs_x}, {abs_y})")
                    pyautogui.click(abs_x, abs_y)
                    time.sleep(2)
                    
                    # دریافت نام چت
                    chat_name = self.get_current_chat_name()
                    self.log_message(f"💬 پردازش چت خوانده نشده: {chat_name}")
                    
                    # خواندن پیام‌ها
                    last_messages = self.safe_read_messages(None)
                    
                    if last_messages:
                        self.log_message(f"📖 {len(last_messages)} پیام خوانده شد")
                        
                        # تولید پاسخ
                        smart_reply = self.generate_littlejoy_reply_improved(last_messages)
                        
                        # ارسال پاسخ
                        if self.smart_send_message(smart_reply):
                            self.log_message(f"✅ پاسخ ارسال شد به {chat_name}: {smart_reply[:50]}...")
                        else:
                            self.log_message(f"❌ خطا در ارسال پاسخ به {chat_name}")
                    else:
                        self.log_message(f"⚠️ پیامی در {chat_name} یافت نشد")
                    
                    time.sleep(2)
            
            # تشخیص چت‌های عادی در فولدر Littlejoy
            chat_positions = self.detect_chats_from_screenshot(img)
            if chat_positions:
                self.log_message(f"🐈 {len(chat_positions)} چت در فولدر Littlejoy تشخیص داده شد")
                
                for i, (chat_x, chat_y) in enumerate(chat_positions[:10]):  # حداکثر 10 چت
                    if not self.is_running:
                        break
                    
                    # محاسبه موقعیت مطلق
                    abs_x = left + chat_x
                    abs_y = top + chat_y
                    
                    self.log_message(f"🔍 کلیک روی چت Littlejoy {i+1} در ({abs_x}, {abs_y})")
                    pyautogui.click(abs_x, abs_y)
                    time.sleep(1.5)
                    
                    # دریافت نام چت
                    chat_name = self.get_current_chat_name()
                    
                    # بررسی اینکه این چت قبلاً پردازش نشده باشد
                    if chat_name == "نامشخص":
                        continue
                    
                    # فیلتر کردن چت‌ها - فقط چت‌های مربوط به Littlejoy
                    if not self.filter_chats_for_littlejoy(chat_name):
                        self.log_message(f"⏭️ چت {chat_name} در فولدر Littlejoy نیست، رد شد")
                        continue
                    
                    self.log_message(f"🐈 پردازش چت Littlejoy: {chat_name}")
                    
                    # خواندن پیام‌ها
                    last_messages = self.safe_read_messages(None)
                    
                    if last_messages:
                        # بررسی نیاز به پاسخ
                        needs_reply = self.analyze_need_for_reply(last_messages, chat_name)
                        
                        if needs_reply:
                            self.log_message(f"✅ چت Littlejoy {chat_name} نیاز به پاسخ دارد")
                            
                            # تولید پاسخ مناسب برای فولدر Littlejoy (ممکن است شامل مطالب مربوط به گربه باشد)
                            smart_reply = self.generate_littlejoy_reply_improved(last_messages)
                            
                            # ارسال پاسخ
                            if self.smart_send_message(smart_reply):
                                self.log_message(f"✅ پاسخ ارسال شد به {chat_name}: {smart_reply[:50]}...")
                            else:
                                self.log_message(f"❌ خطا در ارسال پاسخ به {chat_name}")
                        else:
                            self.log_message(f"⏭️ چت {chat_name} نیاز به پاسخ ندارد")
                    
                    time.sleep(2)
            else:
                self.log_message("❌ هیچ چتی در فولدر Littlejoy پیدا نشد!")
            
            self.log_message("✅ پردازش فولدر Littlejoy🐈 تمام شد")
            
        except Exception as e:
            self.log_message(f"❌ خطا در اسکرین گرفتن و پاسخ‌دهی: {e}")
            import traceback
            self.log_message(f"جزئیات خطا: {traceback.format_exc()}")

    def detect_unread_chats_from_screenshot(self, img):
        """تشخیص چت‌های خوانده نشده از اسکرین‌شات"""
        try:
            # تبدیل به HSV برای تشخیص رنگ آبی badge ها
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # رنگ آبی badge های خوانده نشده
            blue_lower = np.array([100, 100, 100])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # پیدا کردن دایره‌های کوچک (badge ها)
            circles = cv2.HoughCircles(blue_mask, cv2.HOUGH_GRADIENT, 1, 20,
                                     param1=30, param2=15, minRadius=5, maxRadius=20)
            
            unread_positions = []
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    # تخمین موقعیت چت بر اساس badge
                    chat_x = 175  # وسط لیست چت‌ها
                    chat_y = y
                    unread_positions.append((chat_x, chat_y))
            
            return unread_positions
            
        except Exception as e:
            self.log_message(f"❌ خطا در تشخیص چت‌های خوانده نشده: {e}")
            return []

    def detect_chats_from_screenshot(self, img):
        """
        تشخیص چت‌ها از اسکرین‌شات - فقط چت‌های فولدر Littlejoy🐈
        """
        try:
            # اول بررسی کن که آیا در فولدر Littlejoy هستیم یا نه
            if not self.check_if_in_littlejoy_folder(img):
                self.log_message("📁 در حال هدایت به فولدر Littlejoy🐈...")
                self.navigate_to_littlejoy_folder()
                time.sleep(2)
                return []
            
            self.log_message("✅ در فولدر Littlejoy🐈 هستیم، در حال تشخیص چت‌ها...")
            
            # تبدیل به grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # تشخیص خطوط افقی (جداکننده چت‌ها)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            detect_horizontal = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            
            chat_positions = []
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                if w > 200:  # عرض مناسب برای یک چت
                    chat_x = 175  # وسط لیست چت‌ها
                    chat_y = y + 30  # وسط آیتم چت
                    chat_positions.append((chat_x, chat_y))
            
            # اگر خط‌ها پیدا نشد، از روش تقسیم‌بندی یکنواخت استفاده کن
            if not chat_positions:
                chat_height = 70  # تقریبی ارتفاع هر چت
                num_chats = min(10, (self.ui_detector.screen_height - 160) // chat_height)  # کمتر چت برای فولدر خاص
                for i in range(num_chats):
                    chat_x = 175
                    chat_y = 115 + (i * chat_height)
                    chat_positions.append((chat_x, chat_y))
            
            self.log_message(f"🐈 {len(chat_positions)} چت در فولدر Littlejoy پیدا شد")
            return chat_positions[:10]  # حداکثر 10 چت برای فولدر خاص
            
        except Exception as e:
            self.log_message(f"❌ خطا در تشخیص چت‌ها: {e}")
            return []
    
    def check_if_in_littlejoy_folder(self, img):
        """بررسی اینکه آیا در فولدر Littlejoy🐈 هستیم یا نه"""
        try:
            # تبدیل تصویر به grayscale برای تشخیص متن
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # ناحیه بالای صفحه که عنوان فولدر نمایش داده می‌شود
            header_area = gray[0:100, 0:400]  # ناحیه هدر
            
            # تشخیص متن (این یک روش ساده است)
            # در اینجا باید OCR استفاده کرد ولی برای سادگی فرض می‌کنیم
            # که اگر در فولدر خاصی هستیم، رنگ خاصی در هدر وجود دارد
            
            # بررسی رنگ‌های خاص که ممکن است نشان‌دهنده فولدر باشد
            avg_brightness = np.mean(header_area)
            
            # اگر روشنایی متوسط در محدوده خاصی باشد، احتمالاً در فولدر هستیم
            # (این روش نیاز به تنظیم دقیق‌تر دارد)
            
            # برای الان، همیشه True برمی‌گردانیم تا سایر عملکردها را تست کنیم
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در بررسی فولدر: {e}")
            return False
    
    def navigate_to_littlejoy_folder(self):
        """هدایت به فولدر Littlejoy🐈"""
        try:
            self.log_message("📁 در حال هدایت به فولدر Littlejoy🐈...")
            
            # روش 1: استفاده از جستجو
            # کلیک روی نوار جستجو در بالای تلگرام
            search_x = self.ui_detector.screen_width // 4
            search_y = 50
            pyautogui.click(search_x, search_y)
            time.sleep(0.5)
            
            # پاک کردن نوار جستجو
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # تایپ نام فولدر
            pyautogui.typewrite("Littlejoy", interval=0.1)
            time.sleep(1)
            
            # فشردن Enter برای جستجو
            pyautogui.press('enter')
            time.sleep(2)
            
            # اگر نتایج جستجو نمایش داده شد، روی اولین نتیجه کلیک کن
            pyautogui.press('down')
            pyautogui.press('enter')
            time.sleep(1)
            
            self.log_message("✅ سعی شد به فولدر Littlejoy هدایت شود")
            
        except Exception as e:
            self.log_message(f"❌ خطا در هدایت به فولدر Littlejoy: {e}")
    
    def get_current_chat_name_improved(self):
        """دریافت بهبود یافته نام چت فعلی"""
        try:
            # موقعیت نام چت در تمام صفحه
            chat_name_x = self.ui_detector.screen_width // 2
            chat_name_y = 60
            
            # کلیک روی ناحیه نام چت
            pyautogui.click(chat_name_x, chat_name_y)
            time.sleep(0.5)
            
            # انتخاب نام با triple click
            pyautogui.click(chat_name_x, chat_name_y, clicks=3)
            time.sleep(0.3)
            
            # کپی نام
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            chat_name = pyperclip.paste().strip()
            
            # تمیز کردن نام چت
            chat_name = re.sub(r'[^\w\s🐈🐱😺😸😹😻🐾]', '', chat_name)
            
            return chat_name if chat_name else "نامشخص"
        except:
            return "نامشخص"
    
    def read_messages_improved(self):
        """خواندن بهبود یافته پیام‌ها"""
        try:
            messages = []
            
            # موقعیت ناحیه پیام‌ها در تمام صفحه
            message_area_x = int(self.ui_detector.screen_width * 0.25)
            message_area_y = 150
            message_area_width = int(self.ui_detector.screen_width * 0.75)
            message_area_height = self.ui_detector.screen_height - 250
            
            # کلیک در وسط ناحیه پیام‌ها
            center_x = message_area_x + message_area_width // 2
            center_y = message_area_y + message_area_height // 2
            
            pyautogui.click(center_x, center_y)
            time.sleep(0.5)
            
            # اسکرول به آخرین پیام‌ها
            for _ in range(5):
                pyautogui.scroll(-3, x=center_x, y=center_y)
                time.sleep(0.2)
            
            time.sleep(1)
            
            # انتخاب همه محتوا
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            
            # کپی محتوا
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            
            # دریافت متن
            all_text = pyperclip.paste()
            
            if all_text and len(all_text) > 10:
                # تمیز کردن و جدا کردن پیام‌ها
                lines = all_text.strip().split('\n')
                
                # فیلتر خطوط معتبر
                valid_lines = []
                for line in lines:
                    line = line.strip()
                    if (line and 
                        len(line) > 2 and 
                        not line.isdigit() and 
                        not line.startswith('http') and
                        not any(skip in line.lower() for skip in 
                               ['online', 'last seen', 'typing', 'در حال تایپ', 'آنلاین'])):
                        valid_lines.append(line)
                
                # گروه‌بندی پیام‌ها
                current_message = ""
                for line in valid_lines:
                    # اگر خط کوتاه است، احتمالاً نام کاربر یا زمان است
                    if len(line) < 30 and (any(char.isdigit() for char in line) or ':' in line):
                        if current_message:
                            messages.append(current_message.strip())
                        current_message = ""
                    else:
                        if current_message:
                            current_message += " " + line
                        else:
                            current_message = line
                
                # آخرین پیام
                if current_message:
                    messages.append(current_message.strip())
            
            # فیلتر نهایی
            filtered_messages = []
            for msg in messages:
                if (len(msg) > 5 and 
                    any(char.isalpha() for char in msg) and
                    not msg.lower().startswith('telegram')):
                    filtered_messages.append(msg)
            
            return filtered_messages[-5:] if filtered_messages else []  # 5 پیام آخر
            
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن پیام‌ها: {e}")
            return []
    
    def send_message_improved(self, message):
        """ارسال بهبود یافته پیام"""
        try:
            # موقعیت باکس پیام در تمام صفحه
            input_x = int(self.ui_detector.screen_width * 0.25) + 50
            input_y = self.ui_detector.screen_height - 100
            input_width = int(self.ui_detector.screen_width * 0.65)
            
            # کلیک روی باکس پیام
            pyautogui.click(input_x + input_width // 2, input_y)
            time.sleep(0.5)
            
            # پاک کردن محتوای قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # کپی پیام به کلیپ‌بورد
            pyperclip.copy(message)
            time.sleep(0.3)
            
            # پیست پیام
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            
            # ارسال با Enter
            pyautogui.press('enter')
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال پیام: {e}")
            return False

    def start_screenshot_and_reply(self):
        """شروع اسکرین گرفتن و پاسخ‌دهی"""
        if not self.is_running:
            self.is_running = True
            self.log_message("🖼️ شروع اسکرین گرفتن و پاسخ‌دهی...")
            threading.Thread(target=self.screenshot_telegram_and_reply, daemon=True).start()
        else:
            self.log_message("⚠️ عملیات قبلی هنوز در حال اجرا است")

    def read_and_reply_all_chats(self):
        """
        خواندن همه چت‌ها و پاسخ خودکار به پیام‌های جدید هر کاربر
        این تابع همه چت‌ها را اسکرول و پیام آخر هر کاربر را خوانده و با هوش مصنوعی پاسخ می‌دهد.
        توجه: این قابلیت نیازمند فعال بودن تلگرام و چیدمان استاندارد است.
        """
        self.log_message("🚦 شروع خواندن و پاسخ‌دهی خودکار به همه چت‌ها...")
        try:
            # فرض: لیست چت‌ها در سمت چپ تلگرام باز است
            for i in range(10):  # تعداد چت‌ها (برای تست)
                if not self.is_running:
                    break
                    
                # موقعیت تقریبی هر چت در لیست
                x = 200
                y = 150 + i * 60
                pyautogui.click(x, y)
                time.sleep(1.5)
                
                # تلاش برای خواندن آخرین پیام
                try:
                    # کلیک روی ناحیه چت برای انتخاب
                    pyautogui.click(x + 400, y + 100)
                    time.sleep(0.5)
                    
                    # انتخاب همه متن و کپی (روش جایگزین)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.3)
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(0.5)
                    
                    last_message = pyperclip.paste()
                    if last_message and len(last_message.strip()) > 0:
                        self.log_message(f"📨 پیام دریافت شده: {last_message[:50]}...")
                        
                        # تولید پاسخ هوشمند
                        reply = self.generate_ai_message("", f"پاسخ به: {last_message}")
                        
                        # ارسال پاسخ
                        if self.send_message(reply):
                            self.log_message(f"✅ پاسخ ارسال شد: {reply[:50]}...")
                        else:
                            self.log_message("❌ خطا در ارسال پاسخ")
                    else:
                        self.log_message(f"⚠️ چت {i+1}: پیامی یافت نشد")
                        
                except Exception as e:
                    self.log_message(f"❌ خطا در پردازش چت {i+1}: {e}")
                
                time.sleep(2)  # انتظار بین چت‌ها
                
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن چت‌ها: {e}")
        
        self.log_message("✅ خواندن و پاسخ‌دهی به همه چت‌ها تمام شد.")

    def auto_detect_telegram_accounts(self):
        """تشخیص خودکار تمام اکانت‌های تلگرام نصب شده"""
        self.detected_accounts = []
        print("🔍 در حال تشخیص اکانت‌های تلگرام...")
        
        # مسیرهای احتمالی تلگرام
        possible_paths = [
            # Windows Store version
            "C:\\Program Files\\WindowsApps\\TelegramMessengerLLP.TelegramDesktop_*\\Telegram.exe",
            # Portable versions
            "C:\\Users\\*\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe",
            "C:\\Users\\*\\Desktop\\Telegram\\Telegram.exe",
            "D:\\Apps\\Telegram\\Telegram.exe",
            "C:\\Program Files\\Telegram Desktop\\Telegram.exe",
            "C:\\Program Files (x86)\\Telegram Desktop\\Telegram.exe",
        ]
        
        # جستجو در Registry برای نسخه‌های نصب شده
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    if "telegram" in display_name.lower():
                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        telegram_exe = os.path.join(install_location, "Telegram.exe")
                        if os.path.exists(telegram_exe):
                            self.detected_accounts.append({
                                "username": f"Telegram ({display_name})",
                                "telegram_path": telegram_exe
                            })
                except:
                    pass
        except:
            pass
        
        # جستجو در مسیرهای معمول
        import glob
        for pattern in possible_paths:
            try:
                for path in glob.glob(pattern):
                    if os.path.exists(path):
                        account_name = self.extract_account_name_from_path(path)
                        self.detected_accounts.append({
                            "username": account_name,
                            "telegram_path": path
                        })
            except:
                pass
        
        # حذف تکراری‌ها
        seen_paths = set()
        unique_accounts = []
        for account in self.detected_accounts:
            if account["telegram_path"] not in seen_paths:
                seen_paths.add(account["telegram_path"])
                unique_accounts.append(account)
        
        self.detected_accounts = unique_accounts
        print(f"✅ {len(self.detected_accounts)} اکانت تلگرام پیدا شد")
        
        # ادغام با تنظیمات موجود
        existing_accounts = self.config.get("telegram_accounts", [])
        for detected in self.detected_accounts:
            if not any(acc["telegram_path"] == detected["telegram_path"] for acc in existing_accounts):
                existing_accounts.append(detected)
        
        self.config["telegram_accounts"] = existing_accounts

    def extract_account_name_from_path(self, path):
        """استخراج نام اکانت از مسیر فایل"""
        if "WindowsApps" in path:
            return "Telegram Desktop (Windows Store)"
        elif "AppData\\Roaming" in path:
            username = path.split("\\")[2] if len(path.split("\\")) > 2 else "User"
            return f"Telegram Desktop ({username})"
        elif "Desktop" in path:
            return "Telegram Portable (Desktop)"
        elif "Program Files" in path:
            return "Telegram Desktop (System)"
        else:
            folder_name = os.path.dirname(path).split("\\")[-1]
            return f"Telegram ({folder_name})"

    def improved_read_and_reply_all_chats(self):
        """
        نسخه بهبود یافته خواندن و پاسخ‌دهی به همه چت‌ها
        با تشخیص دقیق‌تر پیام‌ها و پاسخ‌دهی هوشمند
        """
        self.log_message("🚦 شروع خواندن پیشرفته و پاسخ‌دهی به همه چت‌ها...")
        
        try:
            # اطمینان از باز بودن تلگرام
            time.sleep(2)
            
            # ابتدا همه گروه‌ها و چت‌های خصوصی تعریف شده را بررسی کن
            groups = self.config.get("groups", [])
            private_chats = self.config.get("private_chats", [])
            
            all_chats = []
            
            # اضافه کردن گروه‌ها
            for group in groups:
                all_chats.append({
                    "name": group["group_name"],
                    "chat_id": group["chat_id"],
                    "type": "group"
                })
            
            # اضافه کردن چت‌های خصوصی
            for pv in private_chats:
                all_chats.append({
                    "name": pv["user_name"],
                    "chat_id": pv["chat_id"],
                    "type": "private"
                })
            
            self.log_message(f"📋 {len(all_chats)} چت برای بررسی پیدا شد")
            
            # بررسی هر چت تعریف شده
            for chat_info in all_chats:
                if not self.is_running:
                    break
                
                chat_name = chat_info["name"]
                chat_id = chat_info["chat_id"]
                chat_type = "گروه" if chat_info["type"] == "group" else "چت خصوصی"
                
                self.log_message(f"🔍 بررسی {chat_type}: {chat_name} ({chat_id})")
                
                # جستجو و باز کردن چت با Chat ID
                if self.find_specific_chat_by_id(chat_id, chat_name):
                    time.sleep(2)
                    
                    # خواندن آخرین پیام‌ها
                    last_messages = self.read_recent_messages()
                    
                    if last_messages:
                        self.log_message(f"� {len(last_messages)} پیام در {chat_name} پیدا شد")
                        
                        # تولید پاسخ هوشمند بر اساس کل مکالمه
                        context = f"نام {chat_type}: {chat_name}\nپیام‌های اخیر:\n" + "\n".join(last_messages[-3:])
                        smart_reply = self.generate_contextual_reply(context)
                        
                        # ارسال پاسخ
                        if self.send_message_to_current_chat(smart_reply):
                            self.log_message(f"✅ پاسخ ارسال شد به {chat_name}: {smart_reply[:60]}...")
                        else:
                            self.log_message(f"❌ خطا در ارسال پاسخ به {chat_name}")
                    else:
                        self.log_message(f"⚠️ {chat_name}: پیام جدیدی یافت نشد")
                else:
                    self.log_message(f"❌ نتوانستم {chat_name} را پیدا کنم")
                
                time.sleep(3)  # انتظار بین چت‌ها
            
            # بررسی اضافی چت‌های دیگر که در لیست نیستند
            self.log_message("🔄 بررسی چت‌های اضافی...")
            self.scan_additional_chats()
                
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن چت‌ها: {e}")
        
        self.log_message("✅ خواندن پیشرفته و پاسخ‌دهی تمام شد.")

    def find_specific_chat_by_id(self, chat_id, chat_name):
        """پیدا کردن چت مشخص با Chat ID"""
        try:
            # باز کردن جستجو
            pyautogui.hotkey('ctrl', 'k')
            time.sleep(1.5)
            
            # پاک کردن جستجوی قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            # جستجو با Chat ID (اولویت اول)
            search_term = chat_id
            pyperclip.copy(search_term)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2.5)
            
            # انتخاب اولین نتیجه
            pyautogui.press('enter')
            time.sleep(2)
            
            self.log_message(f"✅ چت باز شد: {chat_name}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در یافتن چت {chat_name}: {e}")
            
            # تلاش مجدد با نام چت
            try:
                pyautogui.hotkey('ctrl', 'k')
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                
                pyperclip.copy(chat_name)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(2)
                pyautogui.press('enter')
                time.sleep(2)
                
                self.log_message(f"✅ چت باز شد با نام: {chat_name}")
                return True
            except:
                return False

    def scan_additional_chats(self):
        """بررسی چت‌های اضافی که در لیست نیستند"""
        try:
            max_additional_chats = 10
            
            for chat_index in range(max_additional_chats):
                if not self.is_running:
                    break
                
                # موقعیت چت در لیست
                chat_x = 150
                chat_y = 100 + (chat_index * 70)
                
                # کلیک روی چت
                pyautogui.click(chat_x, chat_y)
                time.sleep(1.5)
                
                # خواندن نام چت
                chat_name = self.get_current_chat_name()
                
                # بررسی اینکه آیا این چت در لیست تعریف شده است یا نه
                is_defined = any(
                    chat_name in group["group_name"] or chat_name in pv["user_name"]
                    for group in self.config.get("groups", [])
                    for pv in self.config.get("private_chats", [])
                )
                
                if not is_defined and chat_name != "نامشخص":
                    self.log_message(f"🆕 چت جدید پیدا شد: {chat_name}")
                    
                    # خواندن پیام‌ها
                    last_messages = self.read_recent_messages()
                    
                    if last_messages:
                        # تولید پاسخ
                        context = f"چت جدید: {chat_name}\nپیام‌های اخیر:\n" + "\n".join(last_messages[-2:])
                        smart_reply = self.generate_contextual_reply(context)
                        
                        # ارسال پاسخ
                        if self.send_message_to_current_chat(smart_reply):
                            self.log_message(f"✅ پاسخ ارسال شد به چت جدید {chat_name}")
                
                time.sleep(2)
                
        except Exception as e:
            self.log_message(f"❌ خطا در بررسی چت‌های اضافی: {e}")

    def get_current_chat_name(self):
        """دریافت نام چت/کاربر فعلی"""
        try:
            # کلیک روی نام چت در بالای صفحه
            pyautogui.click(400, 50)
            time.sleep(0.5)
            
            # انتخاب و کپی نام
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            chat_name = pyperclip.paste().strip()
            return chat_name if chat_name else "نامشخص"
        except:
            return "نامشخص"

    def smart_read_recent_messages(self):
        """خواندن پیام‌های اخیر با تشخیص هوشمند ناحیه چت"""
        messages = []
        try:
            # تشخیص ناحیه پیام‌ها
            if self.ui_detector.message_area_region:
                # اسکرول به آخرین پیام‌ها در ناحیه تشخیص داده شده
                center_x = self.ui_detector.message_area_region[0] + self.ui_detector.message_area_region[2] // 2
                center_y = self.ui_detector.message_area_region[1] + self.ui_detector.message_area_region[3] // 2
                
                pyautogui.scroll(-10, x=center_x, y=center_y)
                time.sleep(1.5)
                
                # کلیک در ناحیه پیام‌ها
                pyautogui.click(center_x, center_y)
                time.sleep(0.5)
            else:
                # fallback به روش قدیمی
                pyautogui.scroll(-10, x=500, y=400)
                time.sleep(1.5)
                pyautogui.click(500, 400)
                time.sleep(0.5)
            
            # انتخاب همه و کپی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.8)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.8)
            
            all_text = pyperclip.paste()
            
            if all_text and len(all_text) > 10:
                # تمیز کردن متن و جدا کردن پیام‌ها
                lines = all_text.strip().split('\n')
                
                current_message = ""
                for line in lines:
                    line = line.strip()
                    
                    # فیلتر کردن خطوط غیرضروری
                    if (line and 
                        not line.isdigit() and 
                        len(line) > 3 and
                        not line.startswith('http') and
                        not line.startswith('@') and
                        not any(skip in line.lower() for skip in ['online', 'last seen', 'typing', 'در حال تایپ', 'آنلاین', 'آخرین بازدید'])):
                        
                        # تشخیص شروع پیام جدید (معمولاً با نام کاربر یا زمان)
                        if (line.replace(':', '').replace(' ', '').isalnum() or 
                            re.match(r'^\d{1,2}:\d{2}', line) or 
                            any(time_pattern in line for time_pattern in ['AM', 'PM', 'ص', 'ع']) or
                            len(line) < 20):
                            
                            # ذخیره پیام قبلی
                            if current_message:
                                messages.append(current_message.strip())
                            current_message = line
                        else:
                            # ادامه پیام فعلی
                            if current_message:
                                current_message += " " + line
                            else:
                                current_message = line
                
                # ذخیره آخرین پیام
                if current_message:
                    messages.append(current_message.strip())
            
            # فیلتر نهایی پیام‌ها
            filtered_messages = []
            for msg in messages:
                if (len(msg) > 10 and 
                    not msg.isdigit() and 
                    not msg.startswith('http') and
                    any(char.isalpha() for char in msg)):  # باید حداقل یک حرف داشته باشد
                    filtered_messages.append(msg)
            
            # حذف تکراری‌ها
            unique_messages = []
            for msg in filtered_messages:
                if msg not in unique_messages:
                    unique_messages.append(msg)
            
            return unique_messages[-7:] if unique_messages else []  # 7 پیام آخر
            
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن پیام‌ها: {e}")
            return []

    def smart_send_message(self, message):
        """ارسال پیام با تشخیص هوشمند باکس ورودی و دکمه ارسال"""
        try:
            message_sent = False
            
            # تشخیص موقعیت باکس ورودی
            input_position = self.ui_detector.find_message_input_box()
            
            if input_position:
                self.log_message(f"🎯 باکس ورودی در موقعیت {input_position} تشخیص داده شد")
                
                # کلیک روی باکس ورودی
                pyautogui.click(input_position[0], input_position[1])
                time.sleep(0.5)
                
                # پاک کردن محتوای قبلی
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.2)
                
                # کپی پیام به کلیپ‌بورد
                pyperclip.copy(message)
                time.sleep(0.3)
                
                # پیست پیام
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.8)
                
                # تشخیص دکمه ارسال
                send_button_position = self.ui_detector.find_send_button()
                
                if send_button_position:
                    self.log_message(f"🎯 دکمه ارسال در موقعیت {send_button_position} تشخیص داده شد")
                    # کلیک روی دکمه ارسال
                    pyautogui.click(send_button_position[0], send_button_position[1])
                    time.sleep(1)
                    message_sent = True
                else:
                    # استفاده از Enter به عنوان جایگزین
                    pyautogui.press('enter')
                    time.sleep(1)
                    message_sent = True
                    
            else:
                self.log_message("⚠️ نتوانستم باکس ورودی را تشخیص دهم، از روش‌های جایگزین استفاده می‌کنم")
                # fallback به روش‌های قدیمی
                message_sent = self.fallback_send_message(message)
            
            return message_sent
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال هوشمند پیام: {e}")
            # fallback به روش قدیمی
            return self.fallback_send_message(message)

    def fallback_send_message(self, message):
        """روش جایگزین برای ارسال پیام"""
        try:
            # کلیک روی باکس تایپ پیام (متعدد موقعیت)
            message_box_positions = [
                (500, 650),  # موقعیت معمولی
                (500, 680),  # موقعیت جایگزین 1
                (400, 650),  # موقعیت جایگزین 2
                (600, 650),  # موقعیت جایگزین 3
            ]
            
            for x, y in message_box_positions:
                try:
                    # کلیک روی باکس پیام
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    
                    # پاک کردن محتوای قبلی
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    
                    # کپی پیام به کلیپ‌بورد
                    pyperclip.copy(message)
                    time.sleep(0.3)
                    
                    # پیست پیام
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.8)
                    
                    # ارسال با Enter
                    pyautogui.press('enter')
                    time.sleep(1)
                    
                    return True
                    
                except Exception as e:
                    self.log_message(f"⚠️ تلاش {x},{y} ناموفق: {e}")
                    continue
            
            # روش نهایی: استفاده از Tab
            try:
                pyautogui.press('tab')
                time.sleep(0.5)
                
                pyperclip.copy(message)
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(1)
                
                return True
                
            except Exception as e:
                self.log_message(f"❌ همه روش‌های جایگزین ناموفق: {e}")
                return False
            
        except Exception as e:
            self.log_message(f"❌ خطا در روش جایگزین ارسال: {e}")
            return False

    def read_recent_messages(self):
        """خواندن پیام‌های اخیر در چت فعلی با بهبود تشخیص"""
        # استفاده از تابع هوشمند جدید
    def send_message_to_current_chat(self, message):
        """ارسال پیام به چت فعلی با بهبود دقت"""
        # استفاده از تابع هوشمند جدید
        return self.smart_send_message(message)

    def enhanced_chat_detection_and_response(self):
        """تشخیص پیشرفته چت‌ها و پاسخ‌دهی هوشمند"""
        self.log_message("🤖 شروع تشخیص پیشرفته چت‌ها و پاسخ‌دهی هوشمند...")
        
        try:
            # تشخیص ساختار کامل پنجره تلگرام
            if not self.ui_detector.detect_telegram_window():
                self.log_message("⚠️ ساختار پنجره تلگرام تشخیص داده نشد، تنظیمات پیش‌فرض اعمال شد")
            
            # تشخیص چت‌های خوانده نشده (اولویت بالا)
            unread_chats = self.ui_detector.detect_unread_chats()
            if unread_chats:
                self.log_message(f"📬 {len(unread_chats)} چت خوانده نشده تشخیص داده شد")
                
                for chat_pos in unread_chats[:5]:  # حداکثر 5 چت خوانده نشده
                    if not self.is_running:
                        break
                    
                    # کلیک دقیق روی چت خوانده نشده
                    pyautogui.click(chat_pos[0], chat_pos[1])
                    time.sleep(2)
                    
                    # دریافت نام چت
                    chat_name = self.get_current_chat_name()
                    self.log_message(f"📨 پردازش چت خوانده نشده: {chat_name}")
                    
                    # خواندن پیام‌ها با روش هوشمند
                    messages = self.smart_read_recent_messages()
                    
                    if messages:
                        # تولید پاسخ متناسب
                        context = f"چت خوانده نشده: {chat_name}\nپیام‌های جدید:\n" + "\n".join(messages[-3:])
                        reply = self.generate_contextual_reply(context)
                        
                        # ارسال پاسخ با تشخیص هوشمند
                        if self.smart_send_message(reply):
                            self.log_message(f"✅ پاسخ هوشمند ارسال شد: {reply[:50]}...")
                        else:
                            self.log_message(f"❌ خطا در ارسال پاسخ به {chat_name}")
                    
                    time.sleep(2)
            
            # تشخیص و پردازش چت‌های عادی
            chat_positions = self.ui_detector.find_chat_items()
            if chat_positions:
                self.log_message(f"🎯 {len(chat_positions)} موقعیت چت تشخیص داده شد")
                
                for i, chat_pos in enumerate(chat_positions[:10]):  # حداکثر 10 چت
                    if not self.is_running:
                        break
                    
                    # کلیک دقیق روی چت
                    pyautogui.click(chat_pos[0], chat_pos[1])
                    time.sleep(1.5)
                    
                    # دریافت نام چت
                    chat_name = self.get_current_chat_name()
                    
                    # بررسی وجود در لیست تعریف شده
                    is_configured = any(
                        chat_name in group["group_name"] or chat_name in pv["user_name"]
                        for group in self.config.get("groups", [])
                        for pv in self.config.get("private_chats", [])
                    )
                    
                    if is_configured or chat_name == "نامشخص":
                        continue  # رد کردن چت‌های تعریف شده یا نامشخص
                    
                    self.log_message(f"🔍 بررسی چت: {chat_name}")
                    
                    # خواندن پیام‌ها
                    messages = self.smart_read_recent_messages()
                    
                    if messages:
                        # بررسی نیاز به پاسخ (پیام‌های جدید یا سوال‌ها)
                        needs_reply = self.analyze_need_for_reply(messages, chat_name)
                        
                        if needs_reply:
                            # تولید پاسخ هوشمند
                            context = f"چت: {chat_name}\nپیام‌های اخیر:\n" + "\n".join(messages[-3:])
                            reply = self.generate_contextual_reply(context)
                            
                            # ارسال پاسخ
                            if self.smart_send_message(reply):
                                self.log_message(f"✅ پاسخ هوشمند ارسال شد به {chat_name}")
                            else:
                                self.log_message(f"❌ خطا در ارسال پاسخ به {chat_name}")
                    
                    time.sleep(2)
            
            self.log_message("✅ تشخیص پیشرفته چت‌ها و پاسخ‌دهی تمام شد")
            
        except Exception as e:
            self.log_message(f"❌ خطا در تشخیص پیشرفته چت‌ها: {e}")

    def analyze_need_for_reply(self, messages, chat_name):
        """تحلیل نیاز به پاسخ بر اساس محتوای پیام‌ها"""
        try:
            if not messages:
                return False
            
            last_message = messages[-1].lower()
            
            # نشانه‌های نیاز به پاسخ
            question_indicators = ['؟', '?', 'چی', 'چه', 'کی', 'کجا', 'چرا', 'چطور', 'آیا']
            urgent_keywords = ['فوری', 'مهم', 'ضروری', 'سریع', 'urgent', 'important']
            greeting_keywords = ['سلام', 'hi', 'hello', 'صبح بخیر', 'ظهر بخیر', 'عصر بخیر', 'شب بخیر']
            
            # بررسی وجود سوال
            has_question = any(indicator in last_message for indicator in question_indicators)
            
            # بررسی کلمات فوری
            is_urgent = any(keyword in last_message for keyword in urgent_keywords)
            
            # بررسی سلام و احوال‌پرسی
            is_greeting = any(keyword in last_message for keyword in greeting_keywords)
            
            # بررسی طول پیام (پیام‌های کوتاه معمولاً نیاز به پاسخ دارند)
            is_short_message = len(last_message.split()) <= 5
            
            # تصمیم‌گیری
            if has_question or is_urgent or is_greeting or is_short_message:
                return True
            
            return False
            
        except Exception as e:
            self.log_message(f"❌ خطا در تحلیل نیاز به پاسخ: {e}")
            return True  # در صورت خطا، فرض بر پاسخ‌دهی
        """خواندن پیام‌های اخیر در چت فعلی با بهبود تشخیص"""
        messages = []
        try:
            # اسکرول به آخرین پیام‌ها
            pyautogui.scroll(-10, x=500, y=400)
            time.sleep(1.5)
            
            # انتخاب ناحیه چت
            chat_area_x, chat_area_y = 500, 400
            pyautogui.click(chat_area_x, chat_area_y)
            time.sleep(0.5)
            
            # روش 1: انتخاب همه و کپی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.8)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.8)
            
            all_text = pyperclip.paste()
            
            if all_text and len(all_text) > 10:
                # تمیز کردن متن و جدا کردن پیام‌ها
                lines = all_text.strip().split('\n')
                
                current_message = ""
                for line in lines:
                    line = line.strip()
                    
                    # فیلتر کردن خطوط غیرضروری
                    if (line and 
                        not line.isdigit() and 
                        len(line) > 3 and
                        not line.startswith('http') and
                        not line.startswith('@') and
                        not any(skip in line.lower() for skip in ['online', 'last seen', 'typing', 'در حال تایپ', 'آنلاین', 'آخرین بازدید'])):
                        
                        # تشخیص شروع پیام جدید (معمولاً با نام کاربر یا زمان)
                        if (line.replace(':', '').replace(' ', '').isalnum() or 
                            re.match(r'^\d{1,2}:\d{2}', line) or 
                            any(time_pattern in line for time_pattern in ['AM', 'PM', 'ص', 'ع']) or
                            len(line) < 20):
                            
                            # ذخیره پیام قبلی
                            if current_message:
                                messages.append(current_message.strip())
                            current_message = line
                        else:
                            # ادامه پیام فعلی
                            if current_message:
                                current_message += " " + line
                            else:
                                current_message = line
                
                # ذخیره آخرین پیام
                if current_message:
                    messages.append(current_message.strip())
            
            # روش 2: اسکرول و خواندن متعدد (در صورت عدم موفقیت روش اول)
            if not messages:
                self.log_message("🔄 تلاش دوباره برای خواندن پیام‌ها...")
                
                # چندین اسکرول و کپی
                for i in range(3):
                    pyautogui.scroll(-5, x=500, y=400)
                    time.sleep(0.5)
                    
                    # انتخاب ناحیه کوچکتر
                    pyautogui.drag(300, 300, 700, 500, duration=0.5)
                    time.sleep(0.3)
                    
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(0.5)
                    
                    text_chunk = pyperclip.paste()
                    if text_chunk and len(text_chunk) > 5:
                        messages.extend([line.strip() for line in text_chunk.split('\n') if line.strip() and len(line.strip()) > 5])
            
            # فیلتر نهایی پیام‌ها
            filtered_messages = []
            for msg in messages:
                if (len(msg) > 10 and 
                    not msg.isdigit() and 
                    not msg.startswith('http') and
                    any(char.isalpha() for char in msg)):  # باید حداقل یک حرف داشته باشد
                    filtered_messages.append(msg)
            
            # حذف تکراری‌ها
            unique_messages = []
            for msg in filtered_messages:
                if msg not in unique_messages:
                    unique_messages.append(msg)
            
            return unique_messages[-7:] if unique_messages else []  # 7 پیام آخر
            
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن پیام‌ها: {e}")
            return []

    def generate_contextual_reply(self, context):
        """تولید پاسخ هوشمند بر اساس کنتکست کامل مکالمه"""
        if not self.ai_enabled_var.get():
            return self.base_message_text.get('1.0', tk.END).strip()
        
        try:
            url = self.ollama_url_var.get()
            model = self.ollama_model_var.get()
            personality = self.personality_var.get()
            use_variety = self.message_variety_var.get()
            use_emojis = self.use_emojis_var.get()
            
            # تعریف شخصیت‌ها
            personality_descriptions = {
                'دوستانه و صمیمی': 'دوستانه، گرم، صمیمی و نزدیک',
                'رسمی و حرفه‌ای': 'رسمی، حرفه‌ای، مؤدب و دقیق',
                'شوخ و سرگرم‌کننده': 'شوخ، بامزه، خنده‌دار و سرگرم‌کننده',
                'آموزشی و مفید': 'آموزشی، مفید، اطلاعاتی و کاربردی',
                'انگیزشی و مثبت': 'انگیزشی، مثبت، امیدوار و پرانرژی',
                'خلاق و هنری': 'خلاق، هنری، زیبا و الهام‌بخش'
            }
            
            # ایجاد prompt پیشرفته
            emoji_instruction = "از ایموجی‌های مناسب استفاده کن." if use_emojis else "از ایموجی استفاده نکن."
            variety_instruction = "پاسخ را خلاقانه و متفاوت بنویس." if use_variety else ""
            
            prompt = f"""
تو یک دستیار هوشمند برای پاسخ به پیام‌های تلگرام هستی.

شخصیت تو: {personality_descriptions.get(personality, 'معمولی')}

کنتکست مکالمه:
{context}

دستورالعمل:
- پاسخ کوتاه و مناسب باشد (حداکثر 2-3 خط)
- به آخرین پیام مستقیماً پاسخ بده
- زبان فارسی و طبیعی استفاده کن
- {variety_instruction}
- {emoji_instruction}
- مناسب چت خصوصی یا گروهی باشد
- اگر سوالی پرسیده شده، مستقیماً جواب بده

پاسخ مناسب:
"""
            
            response = requests.post(f"{url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 150
                    }
                },
                timeout=25)
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result.get('response', '').strip()
                
                # پاک‌سازی پاسخ
                ai_reply = ai_reply.replace('\n\n', '\n').strip()
                
                # اضافه کردن تنوع اضافی
                if use_variety and use_emojis:
                    random_emojis = ['✨', '🌟', '💫', '🎯', '💡', '🔥', '⚡', '🌈', '🎨', '❤️']
                    if ai_reply and not any(emoji in ai_reply for emoji in random_emojis):
                        ai_reply += f" {random.choice(random_emojis)}"
                
                return ai_reply if ai_reply else "سلام! چطورید؟ 😊"
            else:
                self.log_message(f"خطا در تولید پاسخ AI: {response.status_code}")
                return "سلام! چطورید؟ 😊"
                
        except Exception as e:
            self.log_message(f"خطا در تولید پاسخ AI: {e}")
            return "سلام! چطورید؟ 😊"

    def generate_littlejoy_reply(self, context):
        """تولید پاسخ مخصوص فولدر Littlejoy🐈 (مطالب مربوط به گربه)"""
        if not self.ai_enabled_var.get():
            return "🐈 سلام! Littlejoy چطوره؟"
        
        try:
            url = self.ollama_url_var.get()
            model = self.ollama_model_var.get()
            personality = self.personality_var.get()
            use_variety = self.message_variety_var.get()
            use_emojis = self.use_emojis_var.get()
            
            # تعریف شخصیت‌ها
            personality_descriptions = {
                'دوستانه و صمیمی': 'دوستانه، گرم، صمیمی و عاشق گربه‌ها',
                'رسمی و حرفه‌ای': 'رسمی ولی مهربان در مورد گربه‌ها',
                'شوخ و سرگرم‌کننده': 'شوخ، بامزه، خنده‌دار و عاشق گربه‌ها',
                'آموزشی و مفید': 'آموزشی در مورد نگهداری و مراقبت از گربه‌ها',
                'انگیزشی و مثبت': 'مثبت و پرانرژی در مورد گربه‌ها',
                'خلاق و هنری': 'خلاق و زیبا در توصیف گربه‌ها'
            }
            
            # ایجاد prompt مخصوص گربه‌ها
            emoji_instruction = "از ایموجی‌های گربه و حیوانات استفاده کن: 🐈 🐱 😺 😸 😹 😻 🐾 ❤️ 💕" if use_emojis else "از ایموجی استفاده نکن."
            variety_instruction = "پاسخ را خلاقانه و متفاوت بنویس." if use_variety else ""
            
            prompt = f"""
تو یک دستیار هوشمند هستی که عاشق گربه‌هاست و برای فولدر Littlejoy🐈 پاسخ می‌دهی.

شخصیت تو: {personality_descriptions.get(personality, 'عاشق گربه‌ها')}

کنتکست مکالمه در فولدر Littlejoy:
{context}

دستورالعمل:
- پاسخ کوتاه و مناسب باشد (حداکثر 2-3 خط)
- به آخرین پیام مستقیماً پاسخ بده
- زبان فارسی و طبیعی استفاده کن
- مخصوص مطالب گربه، Littlejoy و حیوانات خانگی
- اگر در مورد گربه صحبت شده، اطلاعات مفید بده
- اگر عکس گربه یا صدای نیو نیو باشه، واکنش مناسب نشان بده
- {variety_instruction}
- {emoji_instruction}
- مهربان و دوست‌دار حیوانات باش

پاسخ مناسب برای فولدر Littlejoy:
"""
            
            response = requests.post(f"{url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # کمی خلاقانه‌تر برای مطالب گربه
                        "max_tokens": 150
                    }
                },
                timeout=25)
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result.get('response', '').strip()
                
                # پاک‌سازی پاسخ
                ai_reply = ai_reply.replace('\n\n', '\n').strip()
                
                # اضافه کردن ایموجی‌های گربه
                if use_variety and use_emojis:
                    cat_emojis = ['🐈', '🐱', '😺', '😸', '😹', '😻', '🐾', '💕', '❤️']
                    if ai_reply and not any(emoji in ai_reply for emoji in cat_emojis):
                        ai_reply += f" {random.choice(cat_emojis)}"
                
                return ai_reply if ai_reply else "🐈 سلام! Littlejoy چطوره؟ 😺"
            else:
                self.log_message(f"خطا در تولید پاسخ AI برای Littlejoy: {response.status_code}")
                return "🐈 سلام! Littlejoy چطوره؟ 😺"
                
        except Exception as e:
            self.log_message(f"خطا در تولید پاسخ AI برای Littlejoy: {e}")
    def filter_chats_for_littlejoy(self, chat_name):
        """فیلتر کردن چت‌ها برای فولدر Littlejoy🐈"""
        # کلیدواژه‌هایی که نشان می‌دهد چت در فولدر Littlejoy است
        littlejoy_indicators = [
            "littlejoy", "little joy", "🐈", "گربه", "cat", "کت",
            "joy", "جوی", "بچه گربه", "kitten", "meow", "نیو"
        ]
        
        chat_name_lower = chat_name.lower()
        for indicator in littlejoy_indicators:
            if indicator.lower() in chat_name_lower:
                return True
        
        # اگر نام شامل کلیدواژه نبود، همه چت‌ها را قبول کن (چون در فولدر Littlejoy هستیم)
        return True
        """ارسال پیام به چت فعلی با بهبود دقت"""
        try:
            # کلیک روی باکس تایپ پیام (متعدد موقعیت)
            message_box_positions = [
                (500, 650),  # موقعیت معمولی
                (500, 680),  # موقعیت جایگزین 1
                (400, 650),  # موقعیت جایگزین 2
                (600, 650),  # موقعیت جایگزین 3
            ]
            
            message_sent = False
            
            for x, y in message_box_positions:
                try:
                    # کلیک روی باکس پیام
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    
                    # پاک کردن محتوای قبلی
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    
                    # کپی پیام به کلیپ‌بورد
                    pyperclip.copy(message)
                    time.sleep(0.3)
                    
                    # پیست پیام
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.8)
                    
                    # ارسال با Enter
                    pyautogui.press('enter')
                    time.sleep(1)
                    
                    message_sent = True
                    break
                    
                except Exception as e:
                    self.log_message(f"⚠️ تلاش {x},{y} ناموفق: {e}")
                    continue
            
            if not message_sent:
                # روش جایگزین: استفاده از کلیدهای ترکیبی
                try:
                    # فشار دادن Tab برای رفتن به باکس پیام
                    pyautogui.press('tab')
                    time.sleep(0.5)
                    
                    pyperclip.copy(message)
                    time.sleep(0.3)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(1)
                    
                    message_sent = True
                    
                except Exception as e:
                    self.log_message(f"❌ روش جایگزین نیز ناموفق: {e}")
            
            return message_sent
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال پیام: {e}")
            return False

    def start_enhanced_detection(self):
        """شروع تشخیص هوشمند چت‌ها و پاسخ‌دهی"""
        if not self.is_running:
            self.is_running = True
            self.log_message("🤖 شروع تشخیص هوشمند چت‌ها...")
            threading.Thread(target=self.enhanced_chat_detection_and_response, daemon=True).start()
        else:
            self.log_message("⚠️ عملیات قبلی هنوز در حال اجرا است")

    def start_read_and_reply(self):
        """شروع خواندن و پاسخ‌دهی خودکار به همه چت‌ها"""
        if not self.is_running:
            self.is_running = True
            self.log_message("🚀 شروع خواندن پیشرفته و پاسخ‌دهی خودکار...")
            threading.Thread(target=self.improved_read_and_reply_all_chats, daemon=True).start()
        else:
            self.log_message("⚠️ عملیات قبلی هنوز در حال اجرا است")

    def refresh_accounts(self):
        """تشخیص مجدد اکانت‌های تلگرام"""
        self.auto_detect_telegram_accounts()
        
        # بروزرسانی لیست اکانت‌ها در رابط کاربری
        all_accounts = self.config.get("telegram_accounts", [])
        unique_accounts = []
        seen_paths = set()
        for acc in all_accounts:
            if acc["telegram_path"] not in seen_paths:
                seen_paths.add(acc["telegram_path"])
                unique_accounts.append(acc)
        
        self.account_list = [acc["username"] for acc in unique_accounts]
        if hasattr(self, 'account_combo'):
            self.account_combo['values'] = self.account_list
            
            if self.account_list:
                self.account_var.set(self.account_list[0])
        
        if hasattr(self, 'log_message'):
            self.log_message(f"🔄 {len(self.account_list)} اکانت تشخیص داده شد و به‌روزرسانی شد")
        else:
            print(f"🔄 {len(self.account_list)} اکانت تشخیص داده شد و به‌روزرسانی شد")

    def load_config(self):
        """بارگذاری تنظیمات از فایل کانفیگ"""
        default_config = {
            "telegram_accounts": [
                {
                    "username": "account1",
                    "telegram_path": "C:\\Program Files\\WindowsApps\\TelegramMessengerLLP.TelegramDesktop_5.16.5.0_x64__t4vj0pshhgkwm\\Telegram.exe"
                }
            ],
            "groups": [
                {
                    "group_name": "getharemmeow",
                    "chat_id": "-4973474959"
                }
            ],
            "private_chats": [
                {
                    "user_name": "دوست مهم",
                    "chat_id": "8028348127"
                }
            ],
            "base_message": "سلام! این یک پیام هوشمند است",
            "interval_seconds": 30.0,
            "ollama_url": "http://127.0.0.1:11500",
            "ollama_model": "llama3.1:8b",
            "ai_enabled": True,
            "personality": "دوستانه و صمیمی",
            "message_variety": True,
            "use_emojis": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # اضافه کردن کلیدهای جدید در صورت عدم وجود
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            else:
                self.config = default_config
        except Exception as e:
            print(f"خطا در بارگذاری کانفیگ: {e}")
            self.config = default_config
    
    def save_config(self):
        """ذخیره تنظیمات در فایل کانفیگ"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطا در ذخیره کانفیگ: {e}")
    
    def setup_gui(self):
        """ایجاد رابط کاربری گرافیکی"""
        self.root = tk.Tk()
        self.root.title("Telegram AI Messenger - نسخه هوشمند")
        self.root.geometry("800x700")
        self.root.configure(bg='#2c3e50')
        
        # استایل
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook برای تب‌ها
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تب تنظیمات اصلی
        main_frame = ttk.Frame(notebook, padding="15")
        notebook.add(main_frame, text="تنظیمات اصلی")
        
        # تب AI
        ai_frame = ttk.Frame(notebook, padding="15")
        notebook.add(ai_frame, text="تنظیمات هوش مصنوعی")
        
        self.setup_main_tab(main_frame)
        self.setup_ai_tab(ai_frame)
        
        # بخش کنترل
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="🚀 شروع ارسال هوشمند", command=self.start_messaging)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ توقف", command=self.stop_messaging, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="💾 ذخیره تنظیمات", command=self.save_settings).pack(side='left', padx=5)
        ttk.Button(control_frame, text="📱 باز کردن تلگرام", command=self.open_telegram).pack(side='left', padx=5)
        ttk.Button(control_frame, text="🤖 تست AI", command=self.test_ai).pack(side='left', padx=5)
        ttk.Button(control_frame, text="👁️ خواندن پیشرفته چت‌ها", command=self.start_read_and_reply).pack(side='left', padx=5)
        ttk.Button(control_frame, text="🤖 تشخیص هوشمند چت‌ها", command=self.start_enhanced_detection).pack(side='left', padx=5)
        ttk.Button(control_frame, text="�️ اسکرین تلگرام + پاسخ", command=self.start_screenshot_and_reply).pack(side='left', padx=5)
        ttk.Button(control_frame, text="�🔄 تشخیص اکانت‌ها", command=self.refresh_accounts).pack(side='left', padx=5)
        
        # وضعیت
        self.status_label = tk.Label(self.root, text="آماده", bg='#2c3e50', fg='#2ecc71', font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)
        
        # لاگ
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        ttk.Label(log_frame, text="📋 لاگ عملیات:").pack(anchor='w')
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.pack(fill='both', expand=True)
        
        # تنظیم ریسایز
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_main_tab(self, parent):
        """تنظیم تب اصلی"""
        # انتخاب اکانت تلگرام
        ttk.Label(parent, text="� انتخاب اکانت تلگرام:").grid(row=0, column=0, sticky='w', pady=5)
        self.account_list = [acc["username"] for acc in self.config.get("telegram_accounts", [])]
        self.account_var = tk.StringVar(value=self.account_list[0] if self.account_list else "")
        self.account_combo = ttk.Combobox(parent, textvariable=self.account_var, values=self.account_list, width=67)
        self.account_combo.grid(row=0, column=1, pady=5, sticky='ew')

        # انتخاب گروه یا چت خصوصی
        ttk.Label(parent, text="👥 انتخاب گروه/چت:").grid(row=1, column=0, sticky='w', pady=5)
        
        # ترکیب گروه‌ها و چت‌های خصوصی
        groups = self.config.get("groups", [])
        private_chats = self.config.get("private_chats", [])
        
        self.chat_list = []
        for group in groups:
            self.chat_list.append(f"📢 {group['group_name']} ({group['chat_id']})")
        for pv in private_chats:
            self.chat_list.append(f"💬 {pv['user_name']} ({pv['chat_id']})")
        
        # اگر هیچ گروه/چت تعریف نشده، از تنظیمات قدیمی استفاده کن
        if not self.chat_list and "group_name" in self.config:
            self.chat_list.append(f"📢 {self.config['group_name']}")
        
        self.group_var = tk.StringVar(value=self.chat_list[0] if self.chat_list else "")
        self.group_combo = ttk.Combobox(parent, textvariable=self.group_var, values=self.chat_list, width=67)
        self.group_combo.grid(row=1, column=1, pady=5, sticky='ew')

        # پیام پایه
        ttk.Label(parent, text="💬 پیام پایه:").grid(row=2, column=0, sticky='w', pady=5)
        self.base_message_text = tk.Text(parent, height=4, width=70)
        self.base_message_text.insert('1.0', self.config["base_message"])
        self.base_message_text.grid(row=2, column=1, pady=5, sticky='ew')

        # فاصله زمانی
        ttk.Label(parent, text="⏰ فاصله زمانی (ثانیه):").grid(row=3, column=0, sticky='w', pady=5)
        self.interval_var = tk.DoubleVar(value=self.config["interval_seconds"])
        ttk.Spinbox(parent, from_=10, to=3600, textvariable=self.interval_var, width=20).grid(row=3, column=1, sticky='w', pady=5)

        # توضیح جدید:
        ttk.Label(parent, text="اکانت و گروه را انتخاب کنید. برای افزودن/ویرایش، فایل ai_config.json را ویرایش کنید.", foreground="#2980b9").grid(row=4, column=0, columnspan=2, sticky='w', pady=5)

        parent.columnconfigure(1, weight=1)
    
    def setup_ai_tab(self, parent):
        """تنظیم تب هوش مصنوعی"""
        # فعال‌سازی AI
        self.ai_enabled_var = tk.BooleanVar(value=self.config["ai_enabled"])
        ttk.Checkbutton(parent, text="🤖 فعال‌سازی هوش مصنوعی", variable=self.ai_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=10)
        
        # آدرس Ollama
        ttk.Label(parent, text="🌐 آدرس Ollama:").grid(row=1, column=0, sticky='w', pady=5)
        self.ollama_url_var = tk.StringVar(value=self.config["ollama_url"])
        ttk.Entry(parent, textvariable=self.ollama_url_var, width=60).grid(row=1, column=1, pady=5, sticky='ew')
        
        # مدل
        ttk.Label(parent, text="🧠 مدل:").grid(row=2, column=0, sticky='w', pady=5)
        self.ollama_model_var = tk.StringVar(value=self.config["ollama_model"])
        model_combo = ttk.Combobox(parent, textvariable=self.ollama_model_var, width=57)
        model_combo['values'] = ('llama3.1:8b', 'llama3.2', 'llama3.1', 'mistral', 'codellama', 'phi3')
        model_combo.grid(row=2, column=1, pady=5, sticky='ew')
        
        # شخصیت
        ttk.Label(parent, text="🎭 شخصیت AI:").grid(row=3, column=0, sticky='w', pady=5)
        self.personality_var = tk.StringVar(value=self.config["personality"])
        personality_combo = ttk.Combobox(parent, textvariable=self.personality_var, width=57)
        personality_combo['values'] = (
            'دوستانه و صمیمی', 
            'رسمی و حرفه‌ای', 
            'شوخ و سرگرم‌کننده', 
            'آموزشی و مفید',
            'انگیزشی و مثبت',
            'خلاق و هنری'
        )
        personality_combo.grid(row=3, column=1, pady=5, sticky='ew')
        
        # گزینه‌های اضافی
        options_frame = ttk.LabelFrame(parent, text="⚙️ گزینه‌های پیشرفته", padding="10")
        options_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=15)
        
        self.message_variety_var = tk.BooleanVar(value=self.config.get("message_variety", True))
        ttk.Checkbutton(options_frame, text="🎲 تنوع در پیام‌ها", variable=self.message_variety_var).pack(anchor='w', pady=2)
        
        self.use_emojis_var = tk.BooleanVar(value=self.config.get("use_emojis", True))
        ttk.Checkbutton(options_frame, text="😊 استفاده از ایموجی", variable=self.use_emojis_var).pack(anchor='w', pady=2)
        
        # تست پیام
        test_frame = ttk.LabelFrame(parent, text="🧪 تست تولید پیام", padding="10")
        test_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=15)
        
        ttk.Button(test_frame, text="🎯 تولید پیام تست", command=self.generate_test_message).pack(pady=5)
        
        self.test_message_text = scrolledtext.ScrolledText(test_frame, height=6, width=70)
        self.test_message_text.pack(fill='both', expand=True, pady=5)
        
        # تنظیم ستون‌ها
        parent.columnconfigure(1, weight=1)
    
    def log_message(self, message):
        """اضافه کردن پیام به لاگ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(log_entry.strip())
    
    def test_ai(self):
        """تست اتصال به Ollama"""
        try:
            url = self.ollama_url_var.get()
            model = self.ollama_model_var.get()
            
            self.log_message("🔍 در حال تست اتصال به Ollama...")
            
            response = requests.post(f"{url}/api/generate", 
                json={
                    "model": model,
                    "prompt": "سلام! یک پیام کوتاه و دوستانه بنویس",
                    "stream": False
                }, 
                timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                self.log_message(f"✅ Ollama کار می‌کند: {ai_response[:100]}...")
                messagebox.showinfo("موفقیت! 🎉", f"اتصال به Ollama برقرار است!\n\nپاسخ نمونه:\n{ai_response[:150]}...")
            else:
                self.log_message(f"❌ خطا در Ollama: کد {response.status_code}")
                messagebox.showerror("خطا", f"پاسخ نامعتبر از Ollama\nکد خطا: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ خطا در تست Ollama: {e}")
            messagebox.showerror("خطا در اتصال", f"نمی‌توان به Ollama متصل شد:\n\n{str(e)}\n\nمطمئن شوید که:\n• Ollama در حال اجرا است\n• آدرس صحیح است\n• مدل نصب شده")
    
    def generate_ai_message(self, base_message="", context=""):
        """تولید پیام هوشمند با Ollama"""
        if not self.ai_enabled_var.get():
            return base_message or self.base_message_text.get('1.0', tk.END).strip()
        
        try:
            url = self.ollama_url_var.get()
            model = self.ollama_model_var.get()
            personality = self.personality_var.get()
            use_variety = self.message_variety_var.get()
            use_emojis = self.use_emojis_var.get()
            
            # تعریف شخصیت‌ها
            personality_descriptions = {
                'دوستانه و صمیمی': 'دوستانه، گرم، صمیمی و نزدیک',
                'رسمی و حرفه‌ای': 'رسمی، حرفه‌ای، مؤدب و دقیق',
                'شوخ و سرگرم‌کننده': 'شوخ، بامزه، خنده‌دار و سرگرم‌کننده',
                'آموزشی و مفید': 'آموزشی، مفید، اطلاعاتی و کاربردی',
                'انگیزشی و مثبت': 'انگیزشی، مثبت، امیدوار و پرانرژی',
                'خلاق و هنری': 'خلاق، هنری، زیبا و الهام‌بخش'
            }
            
            # ایجاد prompt
            variety_instruction = "پیام را هر بار متفاوت و خلاقانه بنویس." if use_variety else ""
            emoji_instruction = "از ایموجی‌های مناسب استفاده کن." if use_emojis else "از ایموجی استفاده نکن."
            
            prompt = f"""
تو یک دستیار هوشمند برای تولید پیام در تلگرام هستی.

شخصیت تو: {personality_descriptions.get(personality, 'معمولی')}

پیام پایه: {base_message}
{context}

دستورالعمل:
- پیام کوتاه باشد (حداکثر 2-3 خط)
- زبان فارسی استفاده کن
- {variety_instruction}
- {emoji_instruction}
- مناسب گروه چت باشد
- طبیعی و انسانی باشد

پیام جدید:
"""
            
            response = requests.post(f"{url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8 if use_variety else 0.3,
                        "max_tokens": 100
                    }
                },
                timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result.get('response', '').strip()
                
                # پاک‌سازی پیام
                ai_message = ai_message.replace('\n\n', '\n').strip()
                
                # اضافه کردن تنوع اضافی
                if use_variety and use_emojis:
                    random_emojis = ['✨', '🌟', '💫', '🎯', '💡', '🔥', '⚡', '🌈', '🎨', '🎪']
                    if not any(emoji in ai_message for emoji in random_emojis):
                        ai_message += f" {random.choice(random_emojis)}"
                
                return ai_message if ai_message else base_message
            else:
                self.log_message(f"خطا در تولید پیام AI: {response.status_code}")
                return base_message
                
        except Exception as e:
            self.log_message(f"خطا در تولید پیام AI: {e}")
            return base_message or "سلام! پیام خودکار 🤖"
    
    def generate_test_message(self):
        """تولید پیام تست"""
        base_message = self.base_message_text.get('1.0', tk.END).strip()
        self.log_message("🧪 در حال تولید پیام تست...")
        
        test_message = self.generate_ai_message(base_message, "این یک تست است.")
        
        self.test_message_text.delete('1.0', tk.END)
        self.test_message_text.insert('1.0', test_message)
        
        self.log_message(f"✅ پیام تست: {test_message[:50]}...")
    
    def open_telegram(self):
        """باز کردن تلگرام دسکتاپ با استفاده از اکانت انتخاب شده"""
        try:
            # دریافت اطلاعات اکانت انتخاب شده
            selected_account = self.account_var.get().strip()
            account_info = next((acc for acc in self.config.get("telegram_accounts", []) if acc["username"] == selected_account), None)
            
            if account_info:
                telegram_path = account_info.get("telegram_path", "")
            else:
                # fallback به تنظیمات قدیمی
                telegram_path = self.config.get("telegram_path", "")
            
            self.log_message(f"📱 در حال باز کردن تلگرام برای اکانت: {selected_account}...")
            
            if "WindowsApps" in telegram_path:
                try:
                    subprocess.Popen([telegram_path])
                    self.log_message("✅ تلگرام (Windows Store) باز شد")
                except:
                    subprocess.Popen(["start", "tg://"], shell=True)
                    self.log_message("✅ تلگرام از طریق protocol باز شد")
            else:
                if os.path.exists(telegram_path):
                    subprocess.Popen([telegram_path])
                    self.log_message("✅ تلگرام باز شد")
                else:
                    subprocess.Popen(["start", "tg://"], shell=True)
                    self.log_message("✅ تلگرام از طریق protocol باز شد")
            
            time.sleep(3)
            
        except Exception as e:
            error_msg = f"خطا در باز کردن تلگرام: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("خطا", error_msg)
    
    def find_and_open_group(self):
        """یافتن و باز کردن گروه یا چت خصوصی با استفاده از تنظیمات جدید"""
        try:
            # دریافت انتخاب کاربر
            selected_chat = self.group_var.get().strip()
            
            chat_id = ""
            chat_name = ""
            
            # تشخیص نوع چت (گروه یا خصوصی) با پشتیبانی از فرمت جدید
            if selected_chat.startswith("📢 "):  # گروه
                # استخراج نام گروه و Chat ID از فرمت: "📢 نام گروه (chat_id)"
                if "(" in selected_chat and ")" in selected_chat:
                    group_name = selected_chat[2:selected_chat.rfind("(")].strip()
                    chat_id = selected_chat[selected_chat.rfind("(") + 1:selected_chat.rfind(")")].strip()
                else:
                    group_name = selected_chat[2:]  # فرمت قدیمی
                
                # یافتن اطلاعات گروه
                group_info = next((g for g in self.config.get("groups", []) 
                                 if g["group_name"] == group_name or g["chat_id"] == chat_id), None)
                if group_info:
                    chat_id = group_info.get("chat_id", chat_id)
                    chat_name = group_info.get("group_name", group_name)
                    
            elif selected_chat.startswith("💬 "):  # چت خصوصی
                # استخراج نام کاربر و Chat ID از فرمت: "💬 نام کاربر (chat_id)"
                if "(" in selected_chat and ")" in selected_chat:
                    user_name = selected_chat[2:selected_chat.rfind("(")].strip()
                    chat_id = selected_chat[selected_chat.rfind("(") + 1:selected_chat.rfind(")")].strip()
                else:
                    user_name = selected_chat[2:]  # فرمت قدیمی
                
                # یافتن اطلاعات چت خصوصی
                pv_info = next((p for p in self.config.get("private_chats", []) 
                              if p["user_name"] == user_name or p["chat_id"] == chat_id), None)
                if pv_info:
                    chat_id = pv_info.get("chat_id", chat_id)
                    chat_name = pv_info.get("user_name", user_name)
            else:
                # fallback به روش قدیمی
                if hasattr(self, 'chat_id_var') and hasattr(self, 'group_name_var'):
                    chat_id = self.chat_id_var.get().strip()
                    chat_name = self.group_name_var.get().strip()
                else:
                    raise ValueError("چت انتخاب نشده یا وجود ندارد")

            if not chat_id and not chat_name:
                raise ValueError("نام چت یا Chat ID وارد نشده")

            self.log_message(f"🔍 جستجو برای چت: {chat_name} / {chat_id}")
            
            # باز کردن جستجو
            pyautogui.hotkey('ctrl', 'k')
            time.sleep(1.5)
            
            # پاک کردن جستجوی قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            # جستجو (اولویت با Chat ID)
            search_term = chat_id if chat_id else chat_name
            pyperclip.copy(search_term)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2.5)
            
            # انتخاب اولین نتیجه
            pyautogui.press('enter')
            time.sleep(2)
            
            # تشخیص نوع چت برای لاگ
            chat_type = "گروه" if selected_chat.startswith("📢") else "چت خصوصی"
            self.log_message(f"✅ {chat_type} باز شد: {chat_name} ({chat_id})")
            return True
            
        except Exception as e:
            error_msg = f"خطا در یافتن چت: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            return False
    
    def send_message(self, message):
        """ارسال پیام"""
        try:
            # کپی پیام
            pyperclip.copy(message)
            time.sleep(0.3)
            
            # پیست و ارسال
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال پیام: {e}")
            
            # تلاش مجدد با کلیک
            try:
                screen_width, screen_height = pyautogui.size()
                pyautogui.click(screen_width // 2, screen_height - 60)
                time.sleep(0.5)
                
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
                
                return True
            except:
                return False
    
    def messaging_loop(self):
        """حلقه ارسال پیام"""
        try:
            # پیدا کردن گروه
            if not self.find_and_open_group():
                self.log_message("❌ نتوانستم گروه را پیدا کنم")
                return
            
            time.sleep(2)  # صبر برای باز شدن کامل گروه
            self.log_message("🚀 شروع ارسال پیام‌های هوشمند...")
            
            message_count = 0
            base_message = self.base_message_text.get('1.0', tk.END).strip()
            
            while self.is_running:
                # تولید پیام جدید
                if self.ai_enabled_var.get():
                    context = f"این پیام شماره {message_count + 1} است."
                    message = self.generate_ai_message(base_message, context)
                else:
                    message = f"{base_message} #{message_count + 1}"
                
                # ارسال پیام
                if self.send_message(message):
                    message_count += 1
                    self.log_message(f"✅ پیام {message_count} ارسال شد: {message[:60]}...")
                    self.status_label.config(text=f"ارسال شده: {message_count} پیام", fg='#27ae60')
                else:
                    self.log_message("❌ خطا در ارسال پیام")
                    self.status_label.config(text="خطا در ارسال", fg='#e74c3c')
                
                # انتظار
                interval = self.interval_var.get()
                for i in range(int(interval * 10)):
                    if not self.is_running:
                        break
                    remaining = (int(interval * 10) - i) / 10
                    if i % 10 == 0:  # هر ثانیه آپدیت کن
                        self.status_label.config(text=f"انتظار... {remaining:.0f}s", fg='#f39c12')
                    time.sleep(0.1)
                    
        except Exception as e:
            error_msg = f"خطا در حلقه پیام‌رسانی: {str(e)}"
            self.log_message(f"❌ {error_msg}")
        finally:
            self.stop_messaging()
    
    def start_messaging(self):
        """شروع ارسال خودکار پیام"""
        if self.is_running:
            return
        
        # بررسی ورودی‌ها
        if not self.group_var.get().strip():
            messagebox.showerror("خطا", "لطفاً گروه یا چت خصوصی را انتخاب کنید")
            return
        
        if not self.base_message_text.get('1.0', tk.END).strip():
            messagebox.showerror("خطا", "لطفاً پیام پایه را وارد کنید")
            return
        
        # ذخیره تنظیمات
        self.save_settings()
        
        # شروع
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="در حال اجرا...", fg='#e74c3c')
        
        # تشخیص نوع چت برای لاگ
        selected_chat = self.group_var.get().strip()
        chat_type = "گروه" if selected_chat.startswith("📢") else "چت خصوصی"
        self.log_message(f"🚀 شروع ارسال خودکار پیام‌های هوشمند به {chat_type}")
        
        # اجرا در thread جداگانه
        self.message_thread = threading.Thread(target=self.messaging_loop, daemon=True)
        self.message_thread.start()
    
    def stop_messaging(self):
        """توقف ارسال خودکار پیام"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="متوقف شده", fg='#f39c12')
        
        self.log_message("⏹️ ارسال خودکار پیام متوقف شد")
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        # بروزرسانی تنظیمات با مقادیر جدید
        self.config["base_message"] = self.base_message_text.get('1.0', tk.END).strip()
        self.config["interval_seconds"] = self.interval_var.get()
        self.config["ollama_url"] = self.ollama_url_var.get()
        self.config["ollama_model"] = self.ollama_model_var.get()
        self.config["ai_enabled"] = self.ai_enabled_var.get()
        self.config["personality"] = self.personality_var.get()
        self.config["message_variety"] = self.message_variety_var.get()
        self.config["use_emojis"] = self.use_emojis_var.get()
        
        # ذخیره انتخاب‌های فعلی اکانت و گروه
        if hasattr(self, 'account_var'):
            self.config["selected_account"] = self.account_var.get()
        if hasattr(self, 'group_var'):
            self.config["selected_group"] = self.group_var.get()
        
        self.save_config()
        self.log_message("💾 تنظیمات ذخیره شد")
    
    def run(self):
        """اجرای برنامه"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("برنامه توسط کاربر متوقف شد")
    
    def on_closing(self):
        """وقتی پنجره بسته می‌شود"""
        if self.is_running:
            self.stop_messaging()
        self.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    try:
        app = TelegramAIMessenger()
        app.run()
    except Exception as e:
        print(f"خطای کلی: {e}")
        input("برای خروج Enter را فشار دهید...")
