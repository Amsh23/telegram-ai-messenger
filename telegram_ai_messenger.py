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

class TelegramAIMessenger:
    def __init__(self):
        self.is_running = False
        self.message_thread = None
        self.config_file = "ai_config.json"
        self.load_config()
        
        # پیکربندی pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        self.setup_gui()
    
    def load_config(self):
        """بارگذاری تنظیمات از فایل کانفیگ"""
        default_config = {
            "telegram_path": "C:\\Program Files\\WindowsApps\\TelegramMessengerLLP.TelegramDesktop_5.16.5.0_x64__t4vj0pshhgkwm\\Telegram.exe",
            "group_name": "getharemmeow",
            "chat_id": "-4973474959",
            "base_message": "سلام! این یک پیام هوشمند است",
            "interval_seconds": 30.0,
            "account_number": 1,
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
        # مسیر تلگرام
        ttk.Label(parent, text="📁 مسیر تلگرام:").grid(row=0, column=0, sticky='w', pady=5)
        self.telegram_path_var = tk.StringVar(value=self.config["telegram_path"])
        ttk.Entry(parent, textvariable=self.telegram_path_var, width=70).grid(row=0, column=1, pady=5, sticky='ew')
        
        # نام گروه
        ttk.Label(parent, text="👥 نام گروه:").grid(row=1, column=0, sticky='w', pady=5)
        self.group_name_var = tk.StringVar(value=self.config["group_name"])
        ttk.Entry(parent, textvariable=self.group_name_var, width=70).grid(row=1, column=1, pady=5, sticky='ew')
        
        # Chat ID
        ttk.Label(parent, text="🆔 Chat ID:").grid(row=2, column=0, sticky='w', pady=5)
        self.chat_id_var = tk.StringVar(value=self.config["chat_id"])
        ttk.Entry(parent, textvariable=self.chat_id_var, width=70).grid(row=2, column=1, pady=5, sticky='ew')
        
        # پیام پایه
        ttk.Label(parent, text="💬 پیام پایه:").grid(row=3, column=0, sticky='w', pady=5)
        self.base_message_text = tk.Text(parent, height=4, width=70)
        self.base_message_text.insert('1.0', self.config["base_message"])
        self.base_message_text.grid(row=3, column=1, pady=5, sticky='ew')
        
        # فاصله زمانی
        ttk.Label(parent, text="⏰ فاصله زمانی (ثانیه):").grid(row=4, column=0, sticky='w', pady=5)
        self.interval_var = tk.DoubleVar(value=self.config["interval_seconds"])
        ttk.Spinbox(parent, from_=10, to=3600, textvariable=self.interval_var, width=20).grid(row=4, column=1, sticky='w', pady=5)
        
        # تنظیم ستون‌ها
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
        """باز کردن تلگرام دسکتاپ"""
        try:
            telegram_path = self.telegram_path_var.get()
            self.log_message("📱 در حال باز کردن تلگرام...")
            
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
        """یافتن و باز کردن گروه"""
        try:
            chat_id = self.chat_id_var.get().strip()
            group_name = self.group_name_var.get().strip()
            
            if not chat_id and not group_name:
                raise ValueError("نام گروه یا Chat ID وارد نشده")
            
            self.log_message("🔍 جستجو برای گروه...")
            
            # باز کردن جستجو
            pyautogui.hotkey('ctrl', 'k')
            time.sleep(1)
            
            # پاک کردن جستجوی قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            # جستجو (اولویت با Chat ID)
            search_term = chat_id if chat_id else group_name
            self.log_message(f"🔎 جستجو برای: {search_term}")
            
            pyperclip.copy(search_term)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)
            
            # انتخاب اولین نتیجه
            pyautogui.press('enter')
            time.sleep(2)
            
            self.log_message("✅ گروه باز شد")
            return True
            
        except Exception as e:
            error_msg = f"خطا در یافتن گروه: {str(e)}"
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
        if not self.group_name_var.get().strip() and not self.chat_id_var.get().strip():
            messagebox.showerror("خطا", "لطفاً نام گروه یا Chat ID را وارد کنید")
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
        
        self.log_message("🚀 شروع ارسال خودکار پیام‌های هوشمند")
        
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
        self.config["telegram_path"] = self.telegram_path_var.get()
        self.config["group_name"] = self.group_name_var.get()
        self.config["chat_id"] = self.chat_id_var.get()
        self.config["base_message"] = self.base_message_text.get('1.0', tk.END).strip()
        self.config["interval_seconds"] = self.interval_var.get()
        self.config["ollama_url"] = self.ollama_url_var.get()
        self.config["ollama_model"] = self.ollama_model_var.get()
        self.config["ai_enabled"] = self.ai_enabled_var.get()
        self.config["personality"] = self.personality_var.get()
        self.config["message_variety"] = self.message_variety_var.get()
        self.config["use_emojis"] = self.use_emojis_var.get()
        
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
