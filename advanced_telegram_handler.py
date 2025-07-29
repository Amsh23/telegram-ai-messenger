#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyautogui
import pygetwindow as gw
import subprocess
import time
import os
import cv2
import numpy as np
import json
import win32gui
import win32con
import win32api
from ctypes import windll

def load_config():
    """بارگذاری کانفیگ"""
    try:
        with open("ai_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"telegram_accounts": []}

def find_telegram_portable():
    """پیدا کردن پنجره تلگرام portable با روش‌های مختلف"""
    print("🔍 جستجوی پیشرفته پنجره تلگرام...")
    
    # روش 1: pygetwindow
    all_windows = gw.getAllWindows()
    telegram_windows = []
    
    for window in all_windows:
        window_title = window.title.lower()
        if ('telegram' in window_title and 
            'messenger' not in window_title and
            'ai' not in window_title and
            window.width > 300):
            telegram_windows.append(window)
            print(f"📱 پنجره پیدا شد: '{window.title}' - {window.width}x{window.height}")
    
    if telegram_windows:
        return telegram_windows[0]
    
    # روش 2: win32gui
    telegram_hwnd = None
    
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if ('telegram' in window_title.lower() and 
                'messenger' not in window_title.lower() and
                'ai' not in window_title.lower()):
                windows.append(hwnd)
                print(f"🔍 Win32 پنجره: '{window_title}'")
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        telegram_hwnd = windows[0]
        # تبدیل به pygetwindow object
        window_title = win32gui.GetWindowText(telegram_hwnd)
        try:
            return gw.getWindowsWithTitle(window_title)[0]
        except:
            pass
    
    return None

def aggressive_fullscreen_telegram(window):
    """fullscreen کردن قدرتمند تلگرام"""
    print("🚀 شروع fullscreen کردن قدرتمند...")
    
    try:
        # مرحله 1: فعال‌سازی پنجره
        print("1️⃣ فعال‌سازی پنجره...")
        window.activate()
        time.sleep(1)
        
        # کلیک برای اطمینان
        center_x = window.left + window.width // 2
        center_y = window.top + window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # مرحله 2: maximize قدرتمند
        print("2️⃣ Maximize قدرتمند...")
        window.maximize()
        time.sleep(1)
        
        # استفاده از Win32 API برای maximize
        if hasattr(window, '_hWnd'):
            hwnd = window._hWnd
        else:
            hwnd = win32gui.FindWindow(None, window.title)
        
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            time.sleep(1)
        
        # مرحله 3: کلیدهای مختلف fullscreen
        print("3️⃣ تلاش‌های fullscreen...")
        
        # F11 چندین بار
        for i in range(3):
            pyautogui.press('f11')
            time.sleep(1)
            if i < 2:
                print(f"   F11 تلاش {i+1}")
        
        # Alt+Enter برای fullscreen
        pyautogui.hotkey('alt', 'enter')
        time.sleep(1)
        print("   Alt+Enter فشرده شد")
        
        # Windows+Up
        pyautogui.hotkey('win', 'up')
        time.sleep(1)
        print("   Windows+Up فشرده شد")
        
        # مرحله 4: کنترل اندازه با ctypes
        print("4️⃣ کنترل اندازه با Win32...")
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        if hwnd:
            # تنظیم اندازه به کل صفحه
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 
                                screen_width, screen_height, 
                                win32con.SWP_SHOWWINDOW)
            time.sleep(1)
        
        print(f"✅ Fullscreen تمام شد - ابعاد هدف: {screen_width}x{screen_height}")
        return True
        
    except Exception as e:
        print(f"❌ خطا در fullscreen: {e}")
        return False

def wait_for_stable_window(window, timeout=10):
    """انتظار برای تثبیت پنجره"""
    print("⏳ انتظار برای تثبیت پنجره...")
    
    start_time = time.time()
    last_size = (0, 0)
    stable_count = 0
    
    while time.time() - start_time < timeout:
        try:
            window.resizable()  # refresh window info
            current_size = (window.width, window.height)
            
            if current_size == last_size:
                stable_count += 1
                if stable_count >= 3:  # 3 بررسی ثابت
                    print(f"✅ پنجره تثبیت شد: {current_size}")
                    return True
            else:
                stable_count = 0
                last_size = current_size
                print(f"🔄 اندازه پنجره: {current_size}")
            
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    
    print("⚠️ پنجره کاملاً تثبیت نشد")
    return False

def take_smart_screenshot():
    """گرفتن اسکرین‌شات هوشمند"""
    print("📸 گرفتن اسکرین‌شات هوشمند...")
    
    try:
        # انتظار کوتاه برای تثبیت
        time.sleep(2)
        
        # ابعاد صفحه
        screen_width, screen_height = pyautogui.size()
        print(f"📏 ابعاد صفحه: {screen_width}x{screen_height}")
        
        # اسکرین‌شات کامل
        screenshot = pyautogui.screenshot()
        
        # ذخیره با timestamp
        timestamp = int(time.time())
        screenshot_path = f"telegram_fullscreen_{timestamp}.png"
        screenshot.save(screenshot_path)
        
        print(f"✅ اسکرین‌شات ذخیره شد: {screenshot_path}")
        return screenshot, screenshot_path
        
    except Exception as e:
        print(f"❌ خطا در اسکرین‌شات: {e}")
        return None, None

def advanced_telegram_verification(screenshot):
    """تأیید پیشرفته تلگرام"""
    try:
        print("🔍 تحلیل پیشرفته اسکرین‌شات...")
        
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        
        # 1. تشخیص رنگ آبی تلگرام
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        blue_pixels = cv2.countNonZero(blue_mask)
        
        # 2. تشخیص خطوط عمودی (sidebar)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # خطوط عمودی
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        vertical_pixels = cv2.countNonZero(vertical_lines)
        
        # خطوط افقی
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        horizontal_pixels = cv2.countNonZero(horizontal_lines)
        
        # 3. تشخیص ناحیه سمت چپ (chat list)
        left_quarter = img[:, :width//4]
        left_gray = cv2.cvtColor(left_quarter, cv2.COLOR_BGR2GRAY)
        left_variance = np.var(left_gray)
        
        # 4. تشخیص ناحیه سمت راست (messages)
        right_three_quarters = img[:, width//4:]
        right_gray = cv2.cvtColor(right_three_quarters, cv2.COLOR_BGR2GRAY)
        right_variance = np.var(right_gray)
        
        print(f"📊 آمار تحلیل:")
        print(f"   آبی: {blue_pixels} پیکسل")
        print(f"   خطوط عمودی: {vertical_pixels}")
        print(f"   خطوط افقی: {horizontal_pixels}")
        print(f"   تنوع چپ: {left_variance:.1f}")
        print(f"   تنوع راست: {right_variance:.1f}")
        
        # شرایط تلگرام
        is_telegram = (
            blue_pixels > 1000 and              # حداقل رنگ آبی
            vertical_pixels > 100 and           # حداقل خطوط عمودی
            left_variance > 500 and             # تنوع در لیست چت‌ها
            right_variance > 300 and            # تنوع در ناحیه پیام‌ها
            width > 1000 and height > 600      # حداقل اندازه
        )
        
        if is_telegram:
            print("✅ اسکرین‌شات از تلگرام تأیید شد")
            return True
        else:
            print("❌ اسکرین‌شات احتمالاً از تلگرام نیست")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تأیید: {e}")
        return False

def detect_chat_structure(screenshot):
    """تشخیص ساختار چت‌ها"""
    try:
        print("🔍 تشخیص ساختار چت‌ها...")
        
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        
        # تعیین نواحی
        chat_list_width = width // 4  # 25% سمت چپ
        
        # استخراج ناحیه لیست چت‌ها
        chat_area = img[100:height-100, 0:chat_list_width]
        
        # تبدیل به grayscale
        gray = cv2.cvtColor(chat_area, cv2.COLOR_BGR2GRAY)
        
        # تشخیص contours
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        chat_positions = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # شرایط یک چت معتبر
            if (w > chat_list_width * 0.6 and        # عرض مناسب
                30 < h < 100 and                     # ارتفاع مناسب
                cv2.contourArea(contour) > 1000):    # حداقل مساحت
                
                # موقعیت مرکز چت
                center_x = x + w // 2
                center_y = 100 + y + h // 2  # اضافه کردن offset
                
                chat_positions.append((center_x, center_y))
        
        # اگر contour کمک نکرد، از روش تقسیم‌بندی استفاده کن
        if len(chat_positions) < 3:
            print("🔄 استفاده از روش تقسیم‌بندی...")
            chat_positions = []
            
            chat_height = 65  # ارتفاع متوسط چت
            start_y = 150
            max_chats = min(15, (height - 250) // chat_height)
            
            for i in range(max_chats):
                center_x = chat_list_width // 2
                center_y = start_y + (i * chat_height)
                chat_positions.append((center_x, center_y))
        
        print(f"🎯 {len(chat_positions)} موقعیت چت تشخیص داده شد")
        
        # تعیین نواحی مختلف
        regions = {
            'chat_list': (0, 100, chat_list_width, height - 200),
            'message_area': (chat_list_width, 100, width - chat_list_width, height - 200),
            'input_box': (chat_list_width + 20, height - 100, width - chat_list_width - 100, 50),
            'send_button': (width - 80, height - 100, 60, 50)
        }
        
        return chat_positions, regions
        
    except Exception as e:
        print(f"❌ خطا در تشخیص ساختار: {e}")
        return [], {}

def read_messages_advanced(regions):
    """خواندن پیشرفته پیام‌ها"""
    try:
        print("📖 خواندن پیشرفته پیام‌ها...")
        
        if 'message_area' not in regions:
            return []
        
        # ناحیه پیام‌ها
        msg_x, msg_y, msg_w, msg_h = regions['message_area']
        center_x = msg_x + msg_w // 2
        center_y = msg_y + msg_h // 2
        
        # کلیک در ناحیه پیام‌ها
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # اسکرول به آخر
        for _ in range(5):
            pyautogui.scroll(-3, x=center_x, y=center_y)
            time.sleep(0.2)
        
        time.sleep(1)
        
        # انتخاب محتوا در ناحیه پیام‌ها
        pyautogui.click(msg_x + 50, msg_y + 50)  # گوشه بالا چپ
        pyautogui.drag(msg_x + msg_w - 50, msg_y + msg_h - 50, duration=1)  # به گوشه پایین راست
        time.sleep(1)
        
        # کپی
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)
        
        # دریافت متن
        import pyperclip
        text = pyperclip.paste()
        
        if text and len(text) > 10:
            # پردازش متن
            lines = text.strip().split('\n')
            messages = []
            
            for line in lines:
                line = line.strip()
                if (line and len(line) > 3 and 
                    not line.isdigit() and 
                    not line.startswith('http')):
                    messages.append(line)
            
            print(f"📝 {len(messages)} پیام خوانده شد")
            return messages[-5:]  # 5 پیام آخر
        
        return []
        
    except Exception as e:
        print(f"❌ خطا در خواندن پیام‌ها: {e}")
        return []

def send_message_advanced(message, regions):
    """ارسال پیشرفته پیام"""
    try:
        print(f"📤 ارسال پیام: {message[:30]}...")
        
        if 'input_box' not in regions:
            return False
        
        # ناحیه input box
        input_x, input_y, input_w, input_h = regions['input_box']
        center_x = input_x + input_w // 2
        center_y = input_y + input_h // 2
        
        # کلیک روی input box
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # پاک کردن محتوای قبلی
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # کپی پیام
        import pyperclip
        pyperclip.copy(message)
        time.sleep(0.3)
        
        # پیست
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        
        # ارسال
        pyautogui.press('enter')
        time.sleep(1)
        
        print("✅ پیام ارسال شد")
        return True
        
    except Exception as e:
        print(f"❌ خطا در ارسال: {e}")
        return False

def main():
    """تابع اصلی بهبود یافته"""
    print("🚀 شروع برنامه بهبود یافته تلگرام")
    print("=" * 60)
    
    # بارگذاری کانفیگ
    config = load_config()
    
    # انتخاب اکانت portable
    telegram_path = None
    for account in config.get("telegram_accounts", []):
        if "Portable" in account.get("username", ""):
            telegram_path = account.get("telegram_path")
            break
    
    if not telegram_path:
        print("❌ اکانت Portable پیدا نشد")
        return
    
    print(f"📱 باز کردن تلگرام: {telegram_path}")
    
    # باز کردن تلگرام
    try:
        subprocess.Popen([telegram_path])
        time.sleep(5)
    except Exception as e:
        print(f"❌ خطا در باز کردن: {e}")
        return
    
    # پیدا کردن پنجره
    window = find_telegram_portable()
    if not window:
        print("❌ پنجره تلگرام پیدا نشد")
        return
    
    print(f"✅ پنجره پیدا شد: '{window.title}'")
    
    # fullscreen قدرتمند
    if not aggressive_fullscreen_telegram(window):
        print("❌ مشکل در fullscreen")
        return
    
    # انتظار برای تثبیت
    wait_for_stable_window(window)
    
    # اسکرین‌شات هوشمند
    screenshot, screenshot_path = take_smart_screenshot()
    if not screenshot:
        print("❌ مشکل در اسکرین‌شات")
        return
    
    # تأیید تلگرام
    if not advanced_telegram_verification(screenshot):
        print("⚠️ ممکن است اسکرین‌شات از تلگرام نباشد")
    
    # تشخیص ساختار
    chat_positions, regions = detect_chat_structure(screenshot)
    
    if not chat_positions:
        print("❌ چتی پیدا نشد")
        return
    
    # پردازش چت‌ها
    print(f"🔄 شروع پردازش {len(chat_positions)} چت...")
    
    for i, (chat_x, chat_y) in enumerate(chat_positions[:5]):
        print(f"\n--- چت {i+1} ---")
        
        # کلیک روی چت
        pyautogui.click(chat_x, chat_y)
        time.sleep(2)
        
        # خواندن پیام‌ها
        messages = read_messages_advanced(regions)
        
        if messages:
            print(f"📖 پیام‌ها: {messages[-1][:50]}...")
            
            # تولید پاسخ ساده
            reply = f"🐈 سلام! دریافت شد: {len(messages)} پیام"
            
            # ارسال پاسخ
            if send_message_advanced(reply, regions):
                print(f"✅ پاسخ ارسال شد")
            else:
                print(f"❌ مشکل در ارسال")
        else:
            print("⚠️ پیامی یافت نشد")
        
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ پردازش تمام شد")

if __name__ == "__main__":
    main()
