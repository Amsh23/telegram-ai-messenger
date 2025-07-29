#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Desktop Auto Messenger
Automatically opens Telegram Desktop, selects account, and sends messages to a group
"""

import time
import subprocess
import pyautogui
import pyperclip
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
import json
import os
from datetime import datetime

class TelegramAutoMessenger:
    def __init__(self):
        self.is_running = False
        self.message_thread = None
        self.config_file = "config.json"
        self.load_config()
        
        # پیکربندی pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        self.setup_gui()
    
    def load_config(self):
        """بارگذاری تنظیمات از فایل کانفیگ"""
        default_config = {
            "telegram_path": "C:\\Program Files\\WindowsApps\\TelegramMessengerLLP.TelegramDesktop_5.16.5.0_x64__t4vj0pshhgkwm\\Telegram.exe",
            "group_name": "",
            "message_text": "سلام! این یک پیام خودکار است.",
            "interval_seconds": 1.0,
            "account_number": 1
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
        self.root.title("Telegram Auto Messenger")
        self.root.geometry("500x600")
        self.root.configure(bg='#2c3e50')
        
        # استایل
        style = ttk.Style()
        style.theme_use('clam')
        
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # عنوان
        title_label = tk.Label(main_frame, text="تلگرام مسنجر خودکار", 
                              font=("Arial", 16, "bold"), bg='#2c3e50', fg='white')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # مسیر تلگرام
        ttk.Label(main_frame, text="مسیر تلگرام:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.telegram_path_var = tk.StringVar(value=self.config["telegram_path"])
        telegram_entry = ttk.Entry(main_frame, textvariable=self.telegram_path_var, width=50)
        telegram_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # نام گروه
        ttk.Label(main_frame, text="نام گروه:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.group_name_var = tk.StringVar(value=self.config["group_name"])
        group_entry = ttk.Entry(main_frame, textvariable=self.group_name_var, width=50)
        group_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Chat ID گروه (اختیاری)
        ttk.Label(main_frame, text="Chat ID گروه (اختیاری):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.chat_id_var = tk.StringVar(value=self.config.get("chat_id", ""))
        chat_id_entry = ttk.Entry(main_frame, textvariable=self.chat_id_var, width=50)
        chat_id_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # متن پیام
        ttk.Label(main_frame, text="متن پیام:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.message_text = tk.Text(main_frame, height=5, width=50)
        self.message_text.insert('1.0', self.config["message_text"])
        self.message_text.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # فاصله زمانی
        ttk.Label(main_frame, text="فاصله زمانی (ثانیه):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.DoubleVar(value=self.config["interval_seconds"])
        interval_spinbox = ttk.Spinbox(main_frame, from_=0.1, to=3600, increment=0.1, 
                                      textvariable=self.interval_var, width=20)
        interval_spinbox.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # شماره اکانت
        ttk.Label(main_frame, text="شماره اکانت:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.account_var = tk.IntVar(value=self.config["account_number"])
        account_spinbox = ttk.Spinbox(main_frame, from_=1, to=10, 
                                     textvariable=self.account_var, width=20)
        account_spinbox.grid(row=6, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # دکمه‌ها
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="شروع", command=self.start_messaging)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="توقف", command=self.stop_messaging, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="ذخیره تنظیمات", command=self.save_settings).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="باز کردن تلگرام", command=self.open_telegram).grid(row=0, column=3, padx=5)
        
        # نمایش وضعیت
        self.status_label = tk.Label(main_frame, text="آماده", bg='#2c3e50', fg='#2ecc71')
        self.status_label.grid(row=8, column=0, columnspan=2, pady=10)
        
        # لاگ
        ttk.Label(main_frame, text="لاگ:").grid(row=9, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = tk.Text(main_frame, height=10, width=60)
        log_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=10, column=0, columnspan=2, pady=5)
        log_scrollbar.grid(row=10, column=2, sticky='ns')
        
        # تنظیم ریسایز
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def log_message(self, message):
        """اضافه کردن پیام به لاگ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(log_entry.strip())
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        self.config["telegram_path"] = self.telegram_path_var.get()
        self.config["group_name"] = self.group_name_var.get()
        self.config["chat_id"] = self.chat_id_var.get()
        self.config["message_text"] = self.message_text.get('1.0', tk.END).strip()
        self.config["interval_seconds"] = self.interval_var.get()
        self.config["account_number"] = self.account_var.get()
        
        self.save_config()
        self.log_message("تنظیمات ذخیره شد")
        messagebox.showinfo("موفقیت", "تنظیمات با موفقیت ذخیره شد")
    
    def open_telegram(self):
        """باز کردن تلگرام دسکتاپ"""
        try:
            telegram_path = self.telegram_path_var.get()
            
            # جایگزینی متغیر USERNAME
            if "%USERNAME%" in telegram_path:
                import getpass
                username = getpass.getuser()
                telegram_path = telegram_path.replace("%USERNAME%", username)
            
            self.log_message("در حال باز کردن تلگرام...")
            
            # بررسی اگر مسیر Windows Store app است
            if "WindowsApps" in telegram_path:
                try:
                    # روش اول: استفاده از مسیر مستقیم
                    subprocess.Popen([telegram_path])
                    self.log_message("تلگرام (Windows Store) باز شد")
                except Exception as store_error:
                    self.log_message(f"خطا در باز کردن از مسیر Store: {store_error}")
                    # روش دوم: استفاده از protocol handler
                    try:
                        subprocess.Popen(["start", "tg://"], shell=True)
                        self.log_message("تلگرام از طریق protocol باز شد")
                    except Exception as protocol_error:
                        # روش سوم: استفاده از PowerShell
                        powershell_cmd = 'Start-Process -FilePath "shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!App"'
                        subprocess.Popen(["powershell", "-Command", powershell_cmd])
                        self.log_message("تلگرام از طریق PowerShell باز شد")
            else:
                # مسیر معمولی
                if not os.path.exists(telegram_path):
                    # جستجو در مسیرهای معمول
                    import getpass
                    possible_paths = [
                        f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe",
                        "C:\\Program Files\\Telegram Desktop\\Telegram.exe",
                        "C:\\Program Files (x86)\\Telegram Desktop\\Telegram.exe"
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            telegram_path = path
                            self.telegram_path_var.set(path)
                            break
                    else:
                        # اگر هیچ مسیری پیدا نشد، سعی کن از طریق protocol باز کنی
                        try:
                            subprocess.Popen(["start", "tg://"], shell=True)
                            self.log_message("تلگرام از طریق protocol باز شد")
                        except:
                            raise FileNotFoundError("تلگرام پیدا نشد")
                
                if os.path.exists(telegram_path):
                    subprocess.Popen([telegram_path])
                    self.log_message("تلگرام باز شد")
            
            # صبر برای بارگذاری
            time.sleep(5)  # زمان بیشتری برای Windows Store apps
            
            # انتخاب اکانت
            self.select_account()
            
        except Exception as e:
            error_msg = f"خطا در باز کردن تلگرام: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("خطا", error_msg)
    
    def select_account(self):
        """انتخاب اکانت"""
        try:
            account_num = self.account_var.get()
            self.log_message(f"انتخاب اکانت شماره {account_num}")
            
            # اگر چند اکانت وجود دارد، کلیک روی اکانت مورد نظر
            if account_num > 1:
                # فرض می‌کنیم اکانت‌ها در سمت چپ نمایش داده می‌شوند
                # این بخش ممکن است نیاز به تنظیم داشته باشد
                time.sleep(2)
                # کلیک روی منطقه اکانت‌ها
                pyautogui.click(50, 100 + (account_num - 1) * 70)
                time.sleep(1)
            
            self.log_message("اکانت انتخاب شد")
            
        except Exception as e:
            error_msg = f"خطا در انتخاب اکانت: {str(e)}"
            self.log_message(error_msg)
    
    def find_and_open_group(self):
        """یافتن و باز کردن گروه"""
        try:
            group_name = self.group_name_var.get().strip()
            chat_id = self.chat_id_var.get().strip()
            
            if not group_name and not chat_id:
                raise ValueError("نام گروه یا Chat ID وارد نشده")
            
            self.log_message(f"جستجو برای گروه: {group_name} (ID: {chat_id})")
            
            # مطمئن شوید که تلگرام فعال است
            time.sleep(1)
            
            # روش ساده: جستجو با Ctrl+K
            self.log_message("استفاده از جستجوی سراسری...")
            pyautogui.hotkey('ctrl', 'k')
            time.sleep(1.5)
            
            # پاک کردن جستجوی قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            # ابتدا سعی کن با Chat ID
            search_term = chat_id if chat_id else group_name
            self.log_message(f"جستجو برای: {search_term}")
            
            pyperclip.copy(search_term)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)
            
            # انتخاب اولین نتیجه
            pyautogui.press('enter')
            time.sleep(2)
            
            # تأیید که چت باز شد
            self.log_message("گروه انتخاب شد")
            return True
            
        except Exception as e:
            error_msg = f"خطا در یافتن گروه: {str(e)}"
            self.log_message(error_msg)
            return False
    
    def check_if_chat_opened(self):
        """بررسی اینکه آیا چتی باز شده است"""
        try:
            # بررسی وجود نوار پیام در پایین صفحه
            screen_width, screen_height = pyautogui.size()
            # اگر چتی باز باشد، معمولاً نوار پیام در پایین وجود دارد
            return True  # فعلاً همیشه True برمی‌گرداند
        except:
            return False
    
    def verify_correct_chat(self, group_name, chat_id):
        """تأیید اینکه چت باز شده درست است"""
        try:
            # این تابع می‌تواند عنوان چت را بررسی کند
            # فعلاً ساده پیاده‌سازی شده
            time.sleep(1)
            return True  # فعلاً همیشه True برمی‌گرداند
        except:
            return False
    
    def send_message(self):
        """ارسال پیام به صورت ساده"""
        try:
            message = self.message_text.get('1.0', tk.END).strip()
            if not message:
                raise ValueError("متن پیام خالی است")
            
            self.log_message("در حال ارسال پیام...")
            
            # روش ساده: کپی پیام و پیست در جای فعال
            pyperclip.copy(message)
            time.sleep(0.2)
            
            # پیست پیام
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # ارسال با Enter
            pyautogui.press('enter')
            time.sleep(0.3)
            
            self.log_message("پیام ارسال شد")
            return True
            
        except Exception as e:
            error_msg = f"خطا در ارسال پیام: {str(e)}"
            self.log_message(error_msg)
            
            # تلاش مجدد با کلیک
            try:
                self.log_message("تلاش مجدد با کلیک...")
                screen_width, screen_height = pyautogui.size()
                
                # کلیک در پایین وسط صفحه (جایی که معمولاً نوار پیام است)
                pyautogui.click(screen_width // 2, screen_height - 60)
                time.sleep(0.5)
                
                # دوباره پیست و ارسال
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
                
                self.log_message("پیام در تلاش دوم ارسال شد")
                return True
                
            except Exception as retry_error:
                self.log_message(f"خطا در تلاش مجدد: {retry_error}")
                return False
    
    def messaging_loop(self):
        """حلقه ارسال پیام"""
        try:
            # ابتدا گروه را باز کن
            if not self.find_and_open_group():
                self.stop_messaging()
                return
            
            # صبر کمی تا گروه کاملاً باز شود
            time.sleep(2)
            self.log_message("شروع ارسال پیام‌ها...")
            
            message_count = 0
            while self.is_running:
                if self.send_message():
                    message_count += 1
                    self.log_message(f"پیام {message_count} ارسال شد")
                else:
                    self.log_message("خطا در ارسال پیام")
                
                # صبر برای فاصله زمانی تعیین شده
                interval = self.interval_var.get()
                for _ in range(int(interval * 10)):  # تقسیم به دهم ثانیه برای بررسی توقف
                    if not self.is_running:
                        break
                    time.sleep(0.1)
                
        except Exception as e:
            error_msg = f"خطا در حلقه پیام‌رسانی: {str(e)}"
            self.log_message(error_msg)
        finally:
            self.stop_messaging()
    
    def start_messaging(self):
        """شروع ارسال خودکار پیام"""
        if self.is_running:
            return
        
        # بررسی ورودی‌ها
        if not self.group_name_var.get().strip():
            messagebox.showerror("خطا", "لطفاً نام گروه را وارد کنید")
            return
        
        if not self.message_text.get('1.0', tk.END).strip():
            messagebox.showerror("خطا", "لطفاً متن پیام را وارد کنید")
            return
        
        # ذخیره تنظیمات
        self.save_settings()
        
        # شروع
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="در حال اجرا...", fg='#e74c3c')
        
        self.log_message("شروع ارسال خودکار پیام")
        
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
        
        self.log_message("ارسال خودکار پیام متوقف شد")
    
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
        app = TelegramAutoMessenger()
        app.run()
    except Exception as e:
        print(f"خطای کلی: {e}")
        input("برای خروج Enter را فشار دهید...")



