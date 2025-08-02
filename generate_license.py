#!/usr/bin/env python3
"""
🔐 تولید کننده لایسنس برای Telegram Admin Pro
License Generator for Telegram Admin Pro
"""

import hashlib
import datetime
import secrets
import os

def generate_permanent_license():
    """تولید لایسنس دائمی"""
    return "ADMIN_PRO_PERMANENT_2025_UNLIMITED"

def generate_trial_license():
    """تولید لایسنس آزمایشی"""
    return "FREE_TRIAL_LICENSE"

def generate_demo_license():
    """تولید لایسنس دمو"""
    return "ADMIN_PRO_DEMO_2025"

def generate_developer_license():
    """تولید لایسنس توسعه‌دهندگان"""
    return "DEV_LICENSE"

def generate_master_key():
    """تولید Master Key"""
    return "7f4c8b9e2d1a3f6c5e8d9b2a4c7f1e6d"

def generate_custom_license(name="CUSTOM"):
    """تولید لایسنس سفارشی"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()
    return f"{name}_LICENSE_{timestamp}_{random_part}"

def create_license_file(license_key, filename="license.key"):
    """ساخت فایل لایسنس"""
    with open(filename, 'w') as f:
        f.write(license_key)
    print(f"✅ فایل لایسنس ساخته شد: {filename}")
    print(f"🔑 کلید لایسنس: {license_key}")

def main():
    """منوی اصلی"""
    print("🔐 تولید کننده لایسنس Telegram Admin Pro")
    print("=" * 50)
    print("1. لایسنس دائمی (نامحدود)")
    print("2. لایسنس آزمایشی") 
    print("3. لایسنس دمو")
    print("4. لایسنس توسعه‌دهندگان")
    print("5. Master Key")
    print("6. لایسنس سفارشی")
    print("7. همه لایسنس‌ها")
    print()
    
    choice = input("انتخاب کنید (1-7): ").strip()
    
    licenses = {
        "1": ("دائمی", generate_permanent_license()),
        "2": ("آزمایشی", generate_trial_license()),
        "3": ("دمو", generate_demo_license()),
        "4": ("توسعه‌دهندگان", generate_developer_license()),
        "5": ("Master Key", generate_master_key()),
        "6": ("سفارشی", generate_custom_license())
    }
    
    if choice == "7":
        print("\n🎯 همه لایسنس‌های معتبر:")
        print("-" * 40)
        for key, (name, license_key) in licenses.items():
            print(f"{name}: {license_key}")
        
        # ساخت فایل .env کامل
        env_content = f"""# 🔐 تنظیمات محیط برای Telegram Admin Pro
ADMIN_PRO_LICENSE={generate_demo_license()}
TRIAL_LICENSE={generate_trial_license()}
PERMANENT_LICENSE={generate_permanent_license()}
MASTER_KEY={generate_master_key()}
DEV_LICENSE={generate_developer_license()}

# تنظیمات اضافی
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_TEXT_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava
DEV_MODE=true
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n✅ فایل .env کامل ساخته شد!")
        
    elif choice in licenses:
        name, license_key = licenses[choice]
        print(f"\n🔑 لایسنس {name}: {license_key}")
        
        save = input("\nآیا می‌خواهید در فایل ذخیره شود؟ (y/n): ").lower()
        if save == 'y':
            create_license_file(license_key)
    
    else:
        print("❌ انتخاب نامعتبر!")

if __name__ == "__main__":
    main()
