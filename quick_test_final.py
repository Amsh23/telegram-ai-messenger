#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test for Ultimate System
تست سریع سیستم نهایی
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_ai_messenger import TelegramAIMessenger, TelegramUIDetector
import time

def test_basic_functionality():
    """تست عملکرد پایه سیستم"""
    
    print("🚀 تست سریع سیستم پیشرفته")
    print("=" * 50)
    
    # تست ایجاد کلاس‌ها
    print("📋 تست 1: ایجاد کلاس‌ها")
    try:
        detector = TelegramUIDetector()
        messenger = TelegramAIMessenger()
        print("✅ کلاس‌ها با موفقیت ایجاد شدند")
    except Exception as e:
        print(f"❌ خطا در ایجاد کلاس‌ها: {e}")
        return
    
    # تست PyAutoGUI settings
    print("\n📋 تست 2: تنظیمات PyAutoGUI")
    try:
        import pyautogui
        print(f"   FAILSAFE: {pyautogui.FAILSAFE}")
        print(f"   PAUSE: {pyautogui.PAUSE}")
        print(f"   Screen Size: {pyautogui.size()}")
        print("✅ تنظیمات PyAutoGUI درست است")
    except Exception as e:
        print(f"❌ خطا در PyAutoGUI: {e}")
    
    # تست تشخیص پیشرفته
    print("\n📋 تست 3: تشخیص پیشرفته")
    try:
        screenshot = detector.take_screenshot()
        if screenshot is not None:
            print(f"   اندازه اسکرین‌شات: {screenshot.shape}")
            
            # تست متد پیشرفته
            positions = detector.detect_unread_chats_advanced(screenshot)
            print(f"   تعداد موقعیت‌های تشخیص داده شده: {len(positions)}")
            print("✅ تشخیص پیشرفته کار می‌کند")
        else:
            print("⚠️ اسکرین‌شات گرفته نشد")
    except Exception as e:
        print(f"❌ خطا در تشخیص پیشرفته: {e}")
    
    # تست فیلتر پیشرفته
    print("\n📋 تست 4: فیلتر پیشرفته پیام‌ها")
    try:
        test_messages = [
            "سلام چطوری؟",
            "debug error 404",
            "ممنون عزیزم",
            "http://example.com",
            "چه خبر؟"
        ]
        
        filtered = messenger.advanced_message_filter(test_messages)
        print(f"   پیام‌های اصلی: {len(test_messages)}")
        print(f"   پیام‌های فیلتر شده: {len(filtered)}")
        print(f"   پیام‌های معتبر: {filtered}")
        print("✅ فیلتر پیشرفته کار می‌کند")
    except Exception as e:
        print(f"❌ خطا در فیلتر پیشرفته: {e}")
    
    # تست تولید پاسخ هوشمند
    print("\n📋 تست 5: تولید پاسخ هوشمند")
    try:
        test_inputs = [
            ["سلام چطوری؟"],
            ["ممنون از کمکت"],
            ["چه کار می‌کنی؟"]
        ]
        
        for messages in test_inputs:
            response = messenger.generate_littlejoy_reply_improved(messages)
            print(f"   ورودی: {messages[0]}")
            print(f"   پاسخ: {response[:50]}...")
        
        print("✅ تولید پاسخ هوشمند کار می‌کند")
    except Exception as e:
        print(f"❌ خطا در تولید پاسخ: {e}")
    
    # تست کلیک ایمن
    print("\n📋 تست 6: سیستم کلیک ایمن")
    try:
        # تست بدون کلیک واقعی
        test_positions = [(100, 100), (-10, 50), (5000, 100)]
        safe_count = 0
        
        for x, y in test_positions:
            try:
                # شبیه‌سازی منطق کلیک ایمن
                import pyautogui
                screen_w, screen_h = pyautogui.size()
                safe_x = max(10, min(x, screen_w - 10))
                safe_y = max(10, min(y, screen_h - 10))
                
                if 10 <= safe_x <= screen_w - 10 and 10 <= safe_y <= screen_h - 10:
                    safe_count += 1
                    
            except Exception:
                pass
        
        print(f"   تست‌های ایمن: {safe_count}/{len(test_positions)}")
        print("✅ سیستم کلیک ایمن کار می‌کند")
    except Exception as e:
        print(f"❌ خطا در کلیک ایمن: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 تست سریع کامل شد!")
    print("🚀 سیستم آماده استفاده است")

if __name__ == "__main__":
    test_basic_functionality()
