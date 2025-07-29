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

class TelegramAIMessenger:
    def __init__(self):
        self.is_running = False
        self.message_thread = None
        self.config_file = "ai_config.json"
        self.detected_accounts = []
        self.load_config()
        
        # پیکربندی pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        # تشخیص خودکار اکانت‌های تلگرام
        self.auto_detect_telegram_accounts()
        
        self.setup_gui()
    
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
            
            # تعداد چت‌هایی که بررسی شوند
            max_chats = 15
            
            for chat_index in range(max_chats):
                if not self.is_running:
                    break
                
                self.log_message(f"📋 بررسی چت {chat_index + 1}...")
                
                # موقعیت چت در لیست (تنظیم شده برای رزولوشن‌های مختلف)
                chat_x = 150
                chat_y = 100 + (chat_index * 70)
                
                # کلیک روی چت
                pyautogui.click(chat_x, chat_y)
                time.sleep(1.5)
                
                # خواندن نام چت/کاربر
                chat_name = self.get_current_chat_name()
                
                # خواندن آخرین پیام‌ها
                last_messages = self.read_recent_messages()
                
                if last_messages:
                    self.log_message(f"👤 چت: {chat_name}")
                    for i, msg in enumerate(last_messages[-3:]):  # نمایش 3 پیام آخر
                        self.log_message(f"📨 پیام {i+1}: {msg[:100]}...")
                    
                    # تولید پاسخ هوشمند بر اساس کل مکالمه
                    context = f"نام چت: {chat_name}\nپیام‌های اخیر:\n" + "\n".join(last_messages[-3:])
                    smart_reply = self.generate_contextual_reply(context)
                    
                    # ارسال پاسخ
                    if self.send_message_to_current_chat(smart_reply):
                        self.log_message(f"✅ پاسخ ارسال شد: {smart_reply[:80]}...")
                    else:
                        self.log_message("❌ خطا در ارسال پاسخ")
                else:
                    self.log_message(f"⚠️ چت {chat_index + 1}: پیامی یافت نشد")
                
                time.sleep(2)  # انتظار بین چت‌ها
                
        except Exception as e:
            self.log_message(f"❌ خطا در خواندن چت‌ها: {e}")
        
        self.log_message("✅ خواندن پیشرفته و پاسخ‌دهی تمام شد.")

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

    def read_recent_messages(self):
        """خواندن پیام‌های اخیر در چت فعلی"""
        messages = []
        try:
            # اسکرول به آخرین پیام‌ها
            pyautogui.scroll(-5, x=500, y=400)
            time.sleep(1)
            
            # انتخاب ناحیه چت
            chat_area_x, chat_area_y = 500, 400
            pyautogui.click(chat_area_x, chat_area_y)
            time.sleep(0.5)
            
            # روش‌های مختلف برای خواندن پیام‌ها
            
            # روش 1: انتخاب همه و کپی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            all_text = pyperclip.paste()
            
            # تجزیه متن به پیام‌های جداگانه
            if all_text:
                # تمیز کردن و تقسیم متن
                lines = all_text.split('\n')
                current_message = ""
                
                for line in lines:
                    line = line.strip()
                    if line:
                        # تشخیص شروع پیام جدید (معمولاً با زمان یا نام کاربر)
                        if re.match(r'^\d{1,2}:\d{2}', line) or len(current_message) > 200:
                            if current_message:
                                messages.append(current_message.strip())
                            current_message = line
                        else:
                            current_message += " " + line
                
                # اضافه کردن آخرین پیام
                if current_message:
                    messages.append(current_message.strip())
            
            # فیلتر کردن پیام‌های خالی و کوتاه
            filtered_messages = []
            for msg in messages:
                if len(msg) > 5 and not msg.isdigit():  # حذف پیام‌های خیلی کوتاه و اعداد
                    filtered_messages.append(msg)
            
            return filtered_messages[-5:] if filtered_messages else []  # 5 پیام آخر
            
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

    def send_message_to_current_chat(self, message):
        """ارسال پیام به چت فعلی"""
        try:
            # پیدا کردن باکس تایپ پیام
            message_box_x, message_box_y = 500, 650
            pyautogui.click(message_box_x, message_box_y)
            time.sleep(0.5)
            
            # پاک کردن محتوای قبلی (در صورت وجود)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # کپی و ارسال پیام
            pyperclip.copy(message)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.8)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال پیام: {e}")
            return False

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
        ttk.Button(control_frame, text="🔄 تشخیص اکانت‌ها", command=self.refresh_accounts).pack(side='left', padx=5)
        
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
            self.chat_list.append(f"📢 {group['group_name']}")
        for pv in private_chats:
            self.chat_list.append(f"💬 {pv['user_name']}")
        
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
            
            # تشخیص نوع چت (گروه یا خصوصی)
            if selected_chat.startswith("📢 "):  # گروه
                group_name = selected_chat[2:]  # حذف ایموجی
                group_info = next((g for g in self.config.get("groups", []) if g["group_name"] == group_name), None)
                if group_info:
                    chat_id = group_info.get("chat_id", "")
                    chat_name = group_info.get("group_name", "")
            elif selected_chat.startswith("💬 "):  # چت خصوصی
                user_name = selected_chat[2:]  # حذف ایموجی
                pv_info = next((p for p in self.config.get("private_chats", []) if p["user_name"] == user_name), None)
                if pv_info:
                    chat_id = pv_info.get("chat_id", "")
                    chat_name = pv_info.get("user_name", "")
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
            time.sleep(1)
            
            # پاک کردن جستجوی قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            # جستجو (اولویت با Chat ID)
            search_term = chat_id if chat_id else chat_name
            pyperclip.copy(search_term)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)
            
            # انتخاب اولین نتیجه
            pyautogui.press('enter')
            time.sleep(2)
            
            # تشخیص نوع چت برای لاگ
            chat_type = "گروه" if selected_chat.startswith("📢") else "چت خصوصی"
            self.log_message(f"✅ {chat_type} باز شد: {chat_name}")
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
