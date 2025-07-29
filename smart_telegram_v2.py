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

def load_config():
    """بارگذاری کانفیگ"""
    try:
        with open("ai_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"telegram_accounts": []}

def find_telegram_window():
    """پیدا کردن پنجره تلگرام"""
    print("🔍 جستجوی پنجره تلگرام...")
    
    all_windows = gw.getAllWindows()
    telegram_windows = []
    
    for window in all_windows:
        window_title = window.title.lower()
        if ('telegram' in window_title and 
            'messenger' not in window_title and
            'ai' not in window_title and
            window.width > 300):
            telegram_windows.append(window)
            print(f"📱 پنجره: '{window.title}' - {window.width}x{window.height} - موقعیت: ({window.left}, {window.top})")
    
    # انتخاب بزرگترین پنجره
    if telegram_windows:
        largest = max(telegram_windows, key=lambda w: w.width * w.height)
        return largest
    
    return None

def smart_fullscreen_telegram(window):
    """روش هوشمند fullscreen"""
    print("🎯 روش هوشمند fullscreen...")
    
    try:
        # گام 1: فعال‌سازی
        print("1️⃣ فعال‌سازی پنجره...")
        window.activate()
        time.sleep(1)
        
        # گام 2: کلیک برای اطمینان
        center_x = window.left + window.width // 2
        center_y = window.top + window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # گام 3: بررسی اندازه فعلی
        print(f"اندازه فعلی: {window.width}x{window.height}")
        screen_width, screen_height = pyautogui.size()
        print(f"اندازه صفحه: {screen_width}x{screen_height}")
        
        # گام 4: اگر قبلاً fullscreen نیست
        if window.width < screen_width * 0.9 or window.height < screen_height * 0.9:
            print("2️⃣ پنجره fullscreen نیست، در حال تغییر...")
            
            # روش 1: F11
            pyautogui.press('f11')
            time.sleep(2)
            print("   F11 فشرده شد")
            
            # بررسی نتیجه
            window_refreshed = find_telegram_window()
            if window_refreshed:
                print(f"   اندازه جدید: {window_refreshed.width}x{window_refreshed.height}")
                
                # اگر هنوز کوچک است
                if window_refreshed.width < screen_width * 0.9:
                    print("3️⃣ هنوز کوچک است، روش‌های بیشتر...")
                    
                    # روش 2: Alt+Enter
                    pyautogui.hotkey('alt', 'enter')
                    time.sleep(1)
                    print("   Alt+Enter فشرده شد")
                    
                    # روش 3: دوبار F11
                    pyautogui.press('f11')
                    time.sleep(1)
                    pyautogui.press('f11')
                    time.sleep(2)
                    print("   دوبار F11 فشرده شد")
                    
                    # روش 4: maximize سپس F11
                    try:
                        window_refreshed.maximize()
                        time.sleep(1)
                        pyautogui.press('f11')
                        time.sleep(2)
                        print("   maximize + F11 انجام شد")
                    except:
                        pass
        
        # گام 5: بررسی نهایی
        final_window = find_telegram_window()
        if final_window:
            print(f"✅ اندازه نهایی: {final_window.width}x{final_window.height}")
            
            # اگر هنوز کوچک است، از روش اجباری استفاده کن
            if final_window.width < screen_width * 0.8:
                print("4️⃣ استفاده از روش اجباری...")
                
                # کلیک و drag برای تغییر اندازه
                pyautogui.hotkey('win', 'up')  # maximize
                time.sleep(1)
                
                # F11 مجدد
                pyautogui.press('f11')
                time.sleep(2)
                
                print("   روش اجباری اعمال شد")
        
        print("✅ فرآیند fullscreen تمام شد")
        return True
        
    except Exception as e:
        print(f"❌ خطا در fullscreen: {e}")
        return False

def prevent_window_minimize():
    """جلوگیری از کوچک شدن پنجره"""
    print("🔒 اعمال تنظیمات ضد کوچک شدن...")
    
    try:
        # غیرفعال کردن Windows key shortcuts که ممکن است مزاحم باشند
        # (این کد فقط برای جلوگیری از تداخل است)
        
        # فشردن Escape برای لغو هر عملیات جاری
        pyautogui.press('escape')
        time.sleep(0.5)
        
        # کلیک روی وسط صفحه برای اطمینان
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(screen_width // 2, screen_height // 2)
        time.sleep(0.5)
        
        print("✅ تنظیمات اعمال شد")
        
    except Exception as e:
        print(f"⚠️ خطا در تنظیمات: {e}")

def take_multiple_screenshots():
    """گرفتن چندین اسکرین‌شات برای اطمینان"""
    print("📸 گرفتن اسکرین‌شات‌های متعدد...")
    
    screenshots = []
    
    for i in range(3):
        try:
            print(f"📷 اسکرین‌شات {i+1}/3...")
            
            # انتظار کوتاه
            time.sleep(1)
            
            # اسکرین‌شات
            screenshot = pyautogui.screenshot()
            timestamp = int(time.time())
            path = f"telegram_shot_{timestamp}_{i+1}.png"
            screenshot.save(path)
            
            screenshots.append((screenshot, path))
            print(f"   ذخیره شد: {path}")
            
        except Exception as e:
            print(f"❌ خطا در اسکرین‌شات {i+1}: {e}")
    
    # انتخاب بهترین اسکرین‌شات
    best_screenshot = None
    best_score = 0
    
    for screenshot, path in screenshots:
        try:
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # امتیازدهی بر اساس تنوع رنگی
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            variance = np.var(gray)
            
            # امتیازدهی بر اساس اندازه
            height, width = img.shape[:2]
            size_score = width * height
            
            total_score = variance + (size_score / 10000)
            
            print(f"📊 امتیاز {path}: {total_score:.1f}")
            
            if total_score > best_score:
                best_score = total_score
                best_screenshot = (screenshot, path)
                
        except:
            continue
    
    if best_screenshot:
        print(f"🏆 بهترین اسکرین‌شات: {best_screenshot[1]}")
        return best_screenshot
    
    return screenshots[0] if screenshots else (None, None)

def analyze_telegram_layout(screenshot):
    """تحلیل دقیق layout تلگرام"""
    try:
        print("🔍 تحلیل دقیق layout...")
        
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        
        # تقسیم‌بندی صفحه
        # سمت چپ: لیست چت‌ها (معمولاً 25-30% عرض)
        # سمت راست: ناحیه پیام‌ها
        
        # تشخیص جداکننده عمودی
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # تشخیص خطوط عمودی
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, height//4))
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        
        # پیدا کردن موقعیت جداکننده
        separator_x = width // 4  # موقعیت پیش‌فرض
        
        # جستجو برای جداکننده واقعی
        for x in range(width//6, width//2, 10):
            column = vertical_lines[:, x]
            if np.sum(column) > height * 20:  # اگر خط قوی پیدا شد
                separator_x = x
                break
        
        print(f"📐 جداکننده در x={separator_x} (عرض کل: {width})")
        
        # تعیین نواحی
        chat_list_region = {
            'x': 0,
            'y': 80,
            'width': separator_x,
            'height': height - 160
        }
        
        message_region = {
            'x': separator_x + 10,
            'y': 80,
            'width': width - separator_x - 10,
            'height': height - 160
        }
        
        input_region = {
            'x': separator_x + 20,
            'y': height - 100,
            'width': width - separator_x - 100,
            'height': 50
        }
        
        print(f"📊 نواحی تشخیص داده شده:")
        print(f"   لیست چت: {chat_list_region}")
        print(f"   پیام‌ها: {message_region}")
        print(f"   ورودی: {input_region}")
        
        return chat_list_region, message_region, input_region
        
    except Exception as e:
        print(f"❌ خطا در تحلیل layout: {e}")
        
        # نواحی پیش‌فرض
        width, height = pyautogui.size()
        return (
            {'x': 0, 'y': 80, 'width': width//4, 'height': height-160},
            {'x': width//4, 'y': 80, 'width': width*3//4, 'height': height-160},
            {'x': width//4+20, 'y': height-100, 'width': width*3//4-100, 'height': 50}
        )

def detect_chats_in_region(screenshot, chat_region):
    """تشخیص چت‌ها در ناحیه مشخص"""
    try:
        print("🔍 تشخیص چت‌ها در ناحیه لیست...")
        
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # استخراج ناحیه چت‌ها
        x, y = chat_region['x'], chat_region['y']
        w, h = chat_region['width'], chat_region['height']
        
        chat_area = img[y:y+h, x:x+w]
        
        # تبدیل به grayscale
        gray = cv2.cvtColor(chat_area, cv2.COLOR_BGR2GRAY)
        
        # روش 1: تشخیص contours
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        chat_positions = []
        
        for contour in contours:
            cx, cy, cw, ch = cv2.boundingRect(contour)
            
            # شرایط یک چت معتبر
            if (cw > w * 0.5 and           # عرض حداقل 50% ناحیه
                25 < ch < 80 and          # ارتفاع مناسب
                cv2.contourArea(contour) > 800):  # مساحت کافی
                
                # موقعیت مطلق
                abs_x = x + cx + cw // 2
                abs_y = y + cy + ch // 2
                
                chat_positions.append((abs_x, abs_y))
        
        # روش 2: تقسیم‌بندی یکنواخت (اگر contour کمک نکرد)
        if len(chat_positions) < 3:
            print("🔄 استفاده از تقسیم‌بندی یکنواخت...")
            chat_positions = []
            
            chat_height = 60
            start_y = y + 20
            max_chats = min(12, (h - 40) // chat_height)
            
            for i in range(max_chats):
                center_x = x + w // 2
                center_y = start_y + (i * chat_height)
                chat_positions.append((center_x, center_y))
        
        print(f"🎯 {len(chat_positions)} موقعیت چت تشخیص داده شد")
        return chat_positions
        
    except Exception as e:
        print(f"❌ خطا در تشخیص چت‌ها: {e}")
        return []

def smart_read_messages(message_region):
    """خواندن هوشمند پیام‌ها"""
    try:
        print("📖 خواندن هوشمند پیام‌ها...")
        
        x, y = message_region['x'], message_region['y']
        w, h = message_region['width'], message_region['height']
        
        # کلیک در وسط ناحیه پیام‌ها
        center_x = x + w // 2
        center_y = y + h // 2
        
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # اسکرول به پایین برای آخرین پیام‌ها
        for _ in range(3):
            pyautogui.scroll(-5, x=center_x, y=center_y)
            time.sleep(0.3)
        
        time.sleep(1)
        
        # انتخاب ناحیه پیام‌ها
        # شروع از گوشه بالا چپ ناحیه
        pyautogui.click(x + 20, y + 20)
        time.sleep(0.3)
        
        # کشیدن تا گوشه پایین راست
        pyautogui.drag(x + w - 20, y + h - 20, duration=1)
        time.sleep(0.5)
        
        # کپی متن انتخاب شده
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)
        
        # دریافت متن
        text = pyperclip.paste()
        
        if text and len(text) > 5:
            # پردازش متن
            lines = text.strip().split('\n')
            messages = []
            
            for line in lines:
                line = line.strip()
                if (line and 
                    len(line) > 2 and 
                    not line.isdigit() and 
                    not line.startswith('http') and
                    'online' not in line.lower() and
                    'typing' not in line.lower()):
                    messages.append(line)
            
            # حذف تکراری‌ها
            unique_messages = []
            for msg in messages:
                if msg not in unique_messages:
                    unique_messages.append(msg)
            
            print(f"📝 {len(unique_messages)} پیام منحصر به فرد خوانده شد")
            return unique_messages[-3:]  # 3 پیام آخر
        
        return []
        
    except Exception as e:
        print(f"❌ خطا در خواندن پیام‌ها: {e}")
        return []

def smart_send_message(message, input_region):
    """ارسال هوشمند پیام"""
    try:
        print(f"📤 ارسال: {message[:40]}...")
        
        x, y = input_region['x'], input_region['y']
        w, h = input_region['width'], input_region['height']
        
        # کلیک روی ناحیه ورودی
        center_x = x + w // 2
        center_y = y + h // 2
        
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # پاک کردن محتوای قبلی
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # کپی پیام جدید
        pyperclip.copy(message)
        time.sleep(0.3)
        
        # پیست
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)
        
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
    print("🚀 شروع برنامه تلگرام بهبود یافته v2")
    print("=" * 70)
    
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
    
    print(f"📱 باز کردن تلگرام: {telegram_path}")
    
    # باز کردن تلگرام
    try:
        subprocess.Popen([telegram_path])
        time.sleep(4)
    except Exception as e:
        print(f"❌ خطا در باز کردن: {e}")
        return
    
    # پیدا کردن پنجره
    window = find_telegram_window()
    if not window:
        print("❌ پنجره تلگرام پیدا نشد")
        return
    
    print(f"✅ پنجره پیدا شد: '{window.title}' - {window.width}x{window.height}")
    
    # fullscreen هوشمند
    smart_fullscreen_telegram(window)
    
    # جلوگیری از کوچک شدن
    prevent_window_minimize()
    
    # انتظار برای تثبیت
    print("⏳ انتظار برای تثبیت پنجره...")
    time.sleep(3)
    
    # اسکرین‌شات‌های متعدد
    screenshot, screenshot_path = take_multiple_screenshots()
    if not screenshot:
        print("❌ مشکل در اسکرین‌شات")
        return
    
    print(f"✅ اسکرین‌شات نهایی: {screenshot_path}")
    
    # تحلیل layout
    chat_region, message_region, input_region = analyze_telegram_layout(screenshot)
    
    # تشخیص چت‌ها
    chat_positions = detect_chats_in_region(screenshot, chat_region)
    
    if not chat_positions:
        print("❌ چتی پیدا نشد")
        return
    
    # پردازش چت‌ها
    print(f"\n🔄 شروع پردازش {len(chat_positions)} چت...")
    
    for i, (chat_x, chat_y) in enumerate(chat_positions[:3]):  # فقط 3 چت اول
        print(f"\n--- پردازش چت {i+1} ---")
        print(f"📍 کلیک در موقعیت: ({chat_x}, {chat_y})")
        
        # کلیک روی چت
        pyautogui.click(chat_x, chat_y)
        time.sleep(2)
        
        # خواندن پیام‌ها
        messages = smart_read_messages(message_region)
        
        if messages:
            print(f"📖 پیام‌های خوانده شده:")
            for j, msg in enumerate(messages):
                print(f"   {j+1}. {msg[:60]}...")
            
            # تولید پاسخ
            reply = f"🐈 سلام! {len(messages)} پیام دریافت شد. وقت شما بخیر!"
            
            # ارسال پاسخ
            if smart_send_message(reply, input_region):
                print(f"✅ پاسخ ارسال شد: {reply}")
            else:
                print("❌ مشکل در ارسال پاسخ")
        else:
            print("⚠️ پیامی یافت نشد")
        
        time.sleep(2)
    
    print("\n" + "=" * 70)
    print("✅ پردازش کامل شد!")
    print("📊 خلاصه:")
    print(f"   - چت‌های پردازش شده: {min(len(chat_positions), 3)}")
    print(f"   - اسکرین‌شات ذخیره شده: {screenshot_path}")
    print("   - عملیات تمام شد")

if __name__ == "__main__":
    main()
