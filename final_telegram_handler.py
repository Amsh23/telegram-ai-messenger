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
import pyperclip

# غیرفعال کردن failsafe برای عملیات طولانی
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.2

def load_config():
    """بارگذاری کانفیگ"""
    try:
        with open("ai_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"telegram_accounts": []}

def find_main_telegram_window():
    """پیدا کردن پنجره اصلی تلگرام (بزرگترین پنجره)"""
    print("🔍 جستجوی پنجره اصلی تلگرام...")
    
    all_windows = gw.getAllWindows()
    telegram_windows = []
    
    for window in all_windows:
        window_title = window.title.lower()
        if ('telegram' in window_title and 
            'messenger' not in window_title and
            'ai' not in window_title and
            window.width > 400 and window.height > 300):  # حداقل اندازه معقول
            telegram_windows.append(window)
            print(f"📱 پنجره: '{window.title}' - {window.width}x{window.height}")
    
    if not telegram_windows:
        print("❌ هیچ پنجره تلگرام مناسب پیدا نشد")
        return None
    
    # انتخاب بزرگترین پنجره
    main_window = max(telegram_windows, key=lambda w: w.width * w.height)
    print(f"✅ پنجره اصلی انتخاب شد: '{main_window.title}' - {main_window.width}x{main_window.height}")
    
    return main_window

def force_maximize_telegram():
    """اجبار برای maximize کردن تلگرام"""
    print("💪 اجبار برای maximize کردن...")
    
    try:
        # روش 1: تلاش چندگانه F11
        for i in range(5):
            print(f"🔄 تلاش F11 شماره {i+1}")
            pyautogui.press('f11')
            time.sleep(1.5)
            
            # بررسی اندازه پنجره
            window = find_main_telegram_window()
            if window and window.width > 2000:  # اگر کافی بزرگ شد
                print(f"✅ موفق! اندازه: {window.width}x{window.height}")
                return True
        
        # روش 2: ترکیب کلیدها
        combinations = [
            ['alt', 'enter'],
            ['win', 'up'],
            ['alt', 'space', 'x'],  # Alt+Space سپس X برای maximize
        ]
        
        for combo in combinations:
            print(f"🔄 تلاش ترکیب: {'+'.join(combo)}")
            pyautogui.hotkey(*combo)
            time.sleep(2)
            pyautogui.press('f11')
            time.sleep(2)
            
            window = find_main_telegram_window()
            if window and window.width > 2000:
                print(f"✅ موفق با ترکیب! اندازه: {window.width}x{window.height}")
                return True
        
        # روش 3: دوبل کلیک روی title bar
        window = find_main_telegram_window()
        if window:
            print("🔄 دوبل کلیک روی title bar...")
            title_x = window.left + window.width // 2
            title_y = window.top + 15  # ناحیه title bar
            
            pyautogui.doubleClick(title_x, title_y)
            time.sleep(2)
            pyautogui.press('f11')
            time.sleep(2)
            
            window_after = find_main_telegram_window()
            if window_after and window_after.width > 2000:
                print(f"✅ موفق با double click! اندازه: {window_after.width}x{window_after.height}")
                return True
        
        print("⚠️ نتوانستیم به طور کامل maximize کنیم")
        return False
        
    except Exception as e:
        print(f"❌ خطا در maximize: {e}")
        return False

def manual_fullscreen_steps():
    """مراحل دستی fullscreen"""
    print("🎯 اجرای مراحل دستی fullscreen...")
    
    # مرحله 1: فشردن Escape برای لغو حالت‌های جانبی
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # مرحله 2: کلیک در وسط صفحه
    screen_width, screen_height = pyautogui.size()
    pyautogui.click(screen_width // 2, screen_height // 2)
    time.sleep(0.5)
    
    # مرحله 3: تلاش‌های متعدد F11
    for attempt in range(3):
        print(f"🔄 F11 تلاش {attempt + 1}/3")
        pyautogui.press('f11')
        time.sleep(2)
        
        # بررسی که آیا fullscreen شد
        window = find_main_telegram_window()
        if window:
            coverage = (window.width * window.height) / (screen_width * screen_height)
            print(f"📊 پوشش صفحه: {coverage:.1%}")
            
            if coverage > 0.8:  # اگر 80% صفحه را پوشانده
                print("✅ Fullscreen موفقیت‌آمیز!")
                return True
    
    return False

def take_verified_screenshot():
    """گرفتن اسکرین‌شات تأیید شده"""
    print("📸 گرفتن اسکرین‌شات تأیید شده...")
    
    try:
        # انتظار برای تثبیت
        time.sleep(3)
        
        # گرفتن اسکرین‌شات
        screenshot = pyautogui.screenshot()
        
        # ذخیره با timestamp
        timestamp = int(time.time())
        path = f"telegram_verified_{timestamp}.png"
        screenshot.save(path)
        
        # تحلیل برای تأیید
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        
        # بررسی اندازه
        screen_w, screen_h = pyautogui.size()
        coverage = (width * height) / (screen_w * screen_h)
        
        # تحلیل محتوا
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        
        print(f"📊 تحلیل اسکرین‌شات:")
        print(f"   اندازه: {width}x{height}")
        print(f"   پوشش: {coverage:.1%}")
        print(f"   تنوع: {variance:.1f}")
        
        # بررسی کیفیت
        is_good = (coverage > 0.7 and variance > 100 and width > 2000)
        
        if is_good:
            print(f"✅ اسکرین‌شات خوب: {path}")
            return screenshot, path
        else:
            print(f"⚠️ اسکرین‌شات ممکن است مشکل داشته باشد: {path}")
            return screenshot, path
            
    except Exception as e:
        print(f"❌ خطا در اسکرین‌شات: {e}")
        return None, None

def smart_layout_detection(screenshot):
    """تشخیص هوشمند layout"""
    try:
        print("🧠 تشخیص هوشمند layout...")
        
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        
        # تقسیم‌بندی بر اساس نسبت طلایی تلگرام
        # معمولاً sidebar حدود 25-30% عرض صفحه است
        
        sidebar_width = int(width * 0.28)  # 28% عرض
        
        # تعریف نواحی
        chat_list = {
            'x': 10,
            'y': 90,
            'width': sidebar_width - 20,
            'height': height - 180
        }
        
        message_area = {
            'x': sidebar_width + 10,
            'y': 90,
            'width': width - sidebar_width - 20,
            'height': height - 180
        }
        
        input_box = {
            'x': sidebar_width + 30,
            'y': height - 100,
            'width': width - sidebar_width - 120,
            'height': 60
        }
        
        send_button = {
            'x': width - 80,
            'y': height - 100,
            'width': 60,
            'height': 60
        }
        
        print(f"📐 Layout تشخیص داده شده:")
        print(f"   Sidebar: {sidebar_width}px عرض")
        print(f"   لیست چت: {chat_list}")
        print(f"   ناحیه پیام: {message_area}")
        print(f"   Input: {input_box}")
        
        return chat_list, message_area, input_box, send_button
        
    except Exception as e:
        print(f"❌ خطا در تشخیص layout: {e}")
        
        # fallback layout
        width, height = pyautogui.size()
        return (
            {'x': 10, 'y': 90, 'width': width//4, 'height': height-180},
            {'x': width//4+10, 'y': 90, 'width': width*3//4-20, 'height': height-180},
            {'x': width//4+30, 'y': height-100, 'width': width*3//4-120, 'height': 60},
            {'x': width-80, 'y': height-100, 'width': 60, 'height': 60}
        )

def detect_chat_list(screenshot, chat_region):
    """تشخیص لیست چت‌ها"""
    try:
        print("📋 تشخیص لیست چت‌ها...")
        
        # تعیین موقعیت‌های چت بر اساس فاصله یکنواخت
        chat_height = 65  # ارتفاع متوسط هر چت
        start_y = chat_region['y'] + 20
        max_chats = min(8, (chat_region['height'] - 40) // chat_height)
        
        chat_positions = []
        
        for i in range(max_chats):
            center_x = chat_region['x'] + chat_region['width'] // 2
            center_y = start_y + (i * chat_height)
            
            # اطمینان از اینکه در محدوده قابل قبول است
            if center_y < chat_region['y'] + chat_region['height'] - 20:
                chat_positions.append((center_x, center_y))
        
        print(f"🎯 {len(chat_positions)} موقعیت چت تعیین شد")
        
        # نمایش موقعیت‌ها برای debug
        for i, (x, y) in enumerate(chat_positions):
            print(f"   چت {i+1}: ({x}, {y})")
        
        return chat_positions
        
    except Exception as e:
        print(f"❌ خطا در تشخیص چت‌ها: {e}")
        return []

def safe_click(x, y, description=""):
    """کلیک ایمن با بررسی محدوده"""
    try:
        screen_w, screen_h = pyautogui.size()
        
        # بررسی محدوده
        if 0 <= x <= screen_w and 0 <= y <= screen_h:
            print(f"🖱️ کلیک {description}: ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(0.5)
            return True
        else:
            print(f"⚠️ موقعیت خارج از محدوده: ({x}, {y})")
            return False
    except Exception as e:
        print(f"❌ خطا در کلیک: {e}")
        return False

def safe_read_messages(message_region):
    """خواندن ایمن پیام‌ها"""
    try:
        print("📖 خواندن ایمن پیام‌ها...")
        
        # کلیک در ناحیه پیام‌ها
        center_x = message_region['x'] + message_region['width'] // 2
        center_y = message_region['y'] + message_region['height'] // 2
        
        if not safe_click(center_x, center_y, "ناحیه پیام"):
            return []
        
        # اسکرول کمی به پایین
        pyautogui.scroll(-3, x=center_x, y=center_y)
        time.sleep(1)
        
        # انتخاب یک ناحیه کوچک برای تست
        test_x = message_region['x'] + 50
        test_y = message_region['y'] + 50
        test_w = min(400, message_region['width'] - 100)
        test_h = min(300, message_region['height'] - 100)
        
        # انتخاب ناحیه تست
        pyautogui.click(test_x, test_y)
        time.sleep(0.3)
        pyautogui.drag(test_x + test_w, test_y + test_h, duration=0.5)
        time.sleep(0.5)
        
        # کپی
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.8)
        
        # دریافت متن
        text = pyperclip.paste()
        
        if text and len(text) > 3:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            messages = [line for line in lines if len(line) > 2 and not line.isdigit()]
            
            print(f"📝 {len(messages)} پیام خوانده شد")
            if messages:
                print(f"   نمونه: {messages[-1][:50]}...")
            
            return messages[-2:] if messages else []
        
        return []
        
    except Exception as e:
        print(f"❌ خطا در خواندن: {e}")
        return []

def safe_send_message(message, input_region):
    """ارسال ایمن پیام"""
    try:
        print(f"📤 ارسال ایمن: {message[:30]}...")
        
        # کلیک روی input box
        center_x = input_region['x'] + input_region['width'] // 2
        center_y = input_region['y'] + input_region['height'] // 2
        
        if not safe_click(center_x, center_y, "input box"):
            return False
        
        # پاک کردن
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # تایپ پیام (روش مستقیم)
        pyautogui.typewrite(message, interval=0.02)
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
    """تابع اصلی نهایی"""
    print("🚀 شروع برنامه نهایی تلگرام")
    print("=" * 80)
    
    # بارگذاری کانفیگ
    config = load_config()
    telegram_path = None
    
    for account in config.get("telegram_accounts", []):
        if "Portable" in account.get("username", ""):
            telegram_path = account.get("telegram_path")
            break
    
    if not telegram_path:
        print("❌ اکانت Portable پیدا نشد")
        return
    
    print(f"📱 باز کردن تلگرام: {os.path.basename(telegram_path)}")
    
    # باز کردن تلگرام
    try:
        subprocess.Popen([telegram_path])
        time.sleep(6)  # زمان بیشتر برای بارگذاری
    except Exception as e:
        print(f"❌ خطا در باز کردن: {e}")
        return
    
    # پیدا کردن پنجره اصلی
    window = find_main_telegram_window()
    if not window:
        print("❌ پنجره اصلی پیدا نشد")
        return
    
    # فعال‌سازی پنجره
    print("🎯 فعال‌سازی پنجره...")
    try:
        window.activate()
        time.sleep(1)
    except:
        safe_click(window.left + window.width//2, window.top + window.height//2, "وسط پنجره")
    
    # تلاش برای maximize
    if not force_maximize_telegram():
        print("⚠️ نتوانستیم کاملاً maximize کنیم، ادامه می‌دهیم...")
    
    # اجرای مراحل دستی
    manual_fullscreen_steps()
    
    # اسکرین‌شات نهایی
    screenshot, screenshot_path = take_verified_screenshot()
    if not screenshot:
        print("❌ مشکل در اسکرین‌شات")
        return
    
    # تشخیص layout
    chat_region, message_region, input_region, send_region = smart_layout_detection(screenshot)
    
    # تشخیص چت‌ها
    chat_positions = detect_chat_list(screenshot, chat_region)
    
    if not chat_positions:
        print("❌ چتی پیدا نشد")
        return
    
    # پردازش چت‌ها (فقط 2 چت اول برای تست)
    print(f"\n🔄 پردازش {min(len(chat_positions), 2)} چت...")
    
    for i, (chat_x, chat_y) in enumerate(chat_positions[:2]):
        print(f"\n--- چت {i+1} ---")
        
        # کلیک روی چت
        if not safe_click(chat_x, chat_y, f"چت {i+1}"):
            continue
        
        time.sleep(2)
        
        # خواندن پیام‌ها
        messages = safe_read_messages(message_region)
        
        if messages:
            print(f"📖 پیام‌ها دریافت شد:")
            for msg in messages:
                print(f"   • {msg[:60]}...")
            
            # تولید پاسخ
            reply = f"🐈 سلام! دریافت کردم {len(messages)} پیام. ممنون!"
            
            # ارسال پاسخ
            if safe_send_message(reply, input_region):
                print(f"✅ پاسخ ارسال شد")
            else:
                print("❌ مشکل در ارسال")
        else:
            print("⚠️ پیامی یافت نشد")
        
        time.sleep(3)  # فاصله بین چت‌ها
    
    print("\n" + "=" * 80)
    print("✅ پردازش کامل!")
    print(f"📊 خلاصه:")
    print(f"   - اسکرین‌شات: {screenshot_path}")
    print(f"   - چت‌های پردازش شده: {min(len(chat_positions), 2)}")
    print("🎉 تمام!")

if __name__ == "__main__":
    main()
