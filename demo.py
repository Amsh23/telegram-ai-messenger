#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Script for Telegram AI Auto Messenger
نمایش سریع ویژگی‌های کلیدی
"""

import json
import requests
import time

def test_ollama_connection():
    """تست اتصال به Ollama"""
    print("🤖 تست اتصال به Ollama...")
    
    try:
        response = requests.get("http://127.0.0.1:11500/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama متصل است! تعداد مدل‌ها: {len(models)}")
            for model in models:
                print(f"   📦 {model.get('name', 'نامشخص')}")
            return True
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطا در اتصال به Ollama: {e}")
        print("💡 اطمینان حاصل کنید که Ollama در حال اجرا است:")
        print("   ollama serve")
        return False

def generate_sample_message():
    """تولید پیام نمونه با AI"""
    print("\n🎯 تولید پیام نمونه...")
    
    prompt = """شما یک دستیار دوستانه هستید. یک پیام کوتاه و صمیمی برای گروه دوستان بنویسید.
پیام باید:
- فارسی باشد
- حداکثر 50 کلمه
- شامل یک ایموجی مناسب
- مثبت و انرژی‌بخش باشد"""

    try:
        response = requests.post(
            "http://127.0.0.1:11500/api/generate",
            json={
                "model": "llama3.1:8b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result.get('response', '').strip()
            print(f"✨ پیام تولید شده:")
            print(f"   {message}")
            return message
        else:
            print(f"❌ خطا در تولید پیام: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ خطا در تولید پیام: {e}")
        return None

def show_config_info():
    """نمایش اطلاعات کانفیگ"""
    print("\n📋 اطلاعات کانفیگ:")
    
    try:
        with open("ai_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            
        print(f"   🎯 گروه هدف: {config.get('group_name', 'نامشخص')}")
        print(f"   🆔 Chat ID: {config.get('chat_id', 'نامشخص')}")
        print(f"   ⏱️ فاصله زمانی: {config.get('interval_seconds', 30)} ثانیه")
        print(f"   🤖 مدل AI: {config.get('ollama_model', 'نامشخص')}")
        print(f"   🎭 شخصیت: {config.get('personality', 'نامشخص')}")
        print(f"   📱 تلگرام: {config.get('telegram_path', 'نامشخص')}")
        
    except FileNotFoundError:
        print("   ⚠️ فایل کانفیگ یافت نشد")
    except Exception as e:
        print(f"   ❌ خطا در خواندن کانفیگ: {e}")

def main():
    """اجرای تست‌های اصلی"""
    print("🚀 Telegram AI Auto Messenger - Demo")
    print("=" * 50)
    
    # نمایش اطلاعات کانفیگ
    show_config_info()
    
    # تست اتصال Ollama
    if test_ollama_connection():
        # تولید پیام نمونه
        generate_sample_message()
    
    print("\n" + "=" * 50)
    print("✅ Demo تکمیل شد!")
    print("💡 برای اجرای برنامه اصلی:")
    print("   python telegram_ai_messenger.py")

if __name__ == "__main__":
    main()
