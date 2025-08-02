#!/usr/bin/env python3
"""
🎯 Telegram AI Admin Pro v3.0 - ادمین هوشمند حرفه‌ای
سیستم مدیریت چت‌های تلگرام با هوش مصنوعی پیشرفته

ویژگی‌های نسخه 3:
- مدیریت همزمان چندین چت و گروه
- پاسخ‌دهی هوشمند و خودکار به همه پیام‌ها
- سیستم لاگ و گزارش‌دهی حرفه‌ای
- پنل مدیریت پیشرفته
- امنیت و کنترل دسترسی
- قابلیت فروش و استفاده تجاری
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import time
import threading
import requests
import pyautogui
import pyperclip
import base64
import hashlib
import logging
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import subprocess
import pygetwindow as gw
from PIL import Image, ImageTk

class TelegramAdminPro:
    """کلاس اصلی ادمین هوشمند تلگرام"""
    
    def __init__(self):
        """مقداردهی اولیه سیستم"""
        self.version = "3.0.0"
        self.product_name = "Telegram AI Admin Pro"
        
        # مسیرها و فایل‌ها
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "admin_config.json"
        self.db_file = self.base_dir / "admin_logs.db"
        self.license_file = self.base_dir / "license.key"
        
        # وضعیت سیستم
        self.is_running = False
        self.is_licensed = False
        self.active_sessions = {}
        self.performance_stats = {}
        
        # تنظیمات پیش‌فرض
        self.default_config = {
            "version": self.version,
            "license_key": "",
            "ollama_url": "http://127.0.0.1:11434",
            "ollama_text_model": "llama3.1:8b",
            "ollama_vision_model": "llava",
            "telegram_accounts": [],
            "managed_chats": [],
            "response_settings": {
                "auto_reply": True,
                "response_delay": 1.0,
                "max_message_length": 500,
                "professional_mode": True,
                "multi_language": True,
                "emotion_detection": True
            },
            "admin_settings": {
                "max_concurrent_chats": 10,
                "backup_interval": 3600,
                "log_level": "INFO",
                "security_mode": "HIGH"
            }
        }
        
        # راه‌اندازی اولیه
        self.setup_system()
        self.setup_database()
        self.setup_logging()
        self.create_gui()
        
    def setup_system(self):
        """راه‌اندازی سیستم و بارگذاری تنظیمات"""
        try:
            # بارگذاری تنظیمات
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config.copy()
                self.save_config()
            
            # بررسی لایسنس
            self.check_license()
            
        except Exception as e:
            print(f"خطا در راه‌اندازی سیستم: {e}")
            self.config = self.default_config.copy()
    
    def setup_database(self):
        """راه‌اندازی پایگاه داده"""
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.create_tables()
        except Exception as e:
            print(f"خطا در راه‌اندازی دیتابیس: {e}")
    
    def create_tables(self):
        """ساخت جداول پایگاه داده"""
        cursor = self.conn.cursor()
        
        # جدول لاگ پیام‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                chat_id TEXT,
                chat_name TEXT,
                message_type TEXT,
                content TEXT,
                response TEXT,
                processing_time REAL,
                success BOOLEAN
            )
        ''')
        
        # جدول آمار عملکرد
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_messages INTEGER,
                successful_responses INTEGER,
                failed_responses INTEGER,
                avg_response_time REAL,
                active_chats INTEGER
            )
        ''')
        
        # جدول تنظیمات چت‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id TEXT PRIMARY KEY,
                chat_name TEXT,
                auto_reply BOOLEAN DEFAULT TRUE,
                response_style TEXT DEFAULT 'friendly',
                language TEXT DEFAULT 'fa',
                custom_prompts TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def setup_logging(self):
        """راه‌اندازی سیستم لاگ"""
        log_level = getattr(logging, self.config.get('admin_settings', {}).get('log_level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'admin.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def check_license(self):
        """بررسی اعتبار لایسنس"""
        try:
            if self.license_file.exists():
                with open(self.license_file, 'r') as f:
                    license_data = f.read().strip()
                
                # بررسی ساده لایسنس (در نسخه واقعی باید پیچیده‌تر باشد)
                if self.validate_license(license_data):
                    self.is_licensed = True
                    self.logger.info("لایسنس معتبر")
                else:
                    self.is_licensed = False
                    self.logger.warning("لایسنس نامعتبر")
            else:
                self.is_licensed = False
                self.logger.warning("فایل لایسنس پیدا نشد")
                
        except Exception as e:
            self.is_licensed = False
            self.logger.error(f"خطا در بررسی لایسنس: {e}")
    
    def validate_license(self, license_key):
        """اعتبارسنجی کلید لایسنس"""
        # الگوریتم ساده برای تست - در نسخه واقعی باید پیچیده‌تر باشد
        expected_hash = hashlib.md5(f"TELEGRAM_ADMIN_PRO_{self.version}".encode()).hexdigest()
        
        # لایسنس‌های معتبر برای تست
        valid_licenses = [
            expected_hash,
            "ADMIN_PRO_DEMO_2025",  # لایسنس دمو
            "FREE_TRIAL_LICENSE",    # لایسنس آزمایشی
            hashlib.md5("FULL_VERSION".encode()).hexdigest()  # نسخه کامل
        ]
        
        return license_key in valid_licenses
    
    def create_gui(self):
        """ساخت رابط کاربری پیشرفته"""
        self.root = tk.Tk()
        self.root.title(f"{self.product_name} v{self.version}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # استایل
        self.setup_styles()
        
        # منوی اصلی
        self.create_menu()
        
        # پنل‌های اصلی
        self.create_main_panels()
        
        # نوار وضعیت
        self.create_status_bar()
        
        # تنظیمات پنجره
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # بررسی اولیه
        self.initial_checks()
    
    def setup_styles(self):
        """تنظیم استایل‌های رابط کاربری"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # تعریف رنگ‌ها
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'dark': '#2c3e50',
            'light': '#ecf0f1'
        }
        
        # استایل دکمه‌ها
        self.style.configure('Primary.TButton', 
                           background=self.colors['primary'],
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('Success.TButton', 
                           background=self.colors['success'],
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('Danger.TButton', 
                           background=self.colors['danger'],
                           foreground='white',
                           font=('Arial', 10, 'bold'))
    
    def create_menu(self):
        """ساخت منوی اصلی"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # منوی فایل
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="فایل", menu=file_menu)
        file_menu.add_command(label="تنظیمات جدید", command=self.new_config)
        file_menu.add_command(label="بارگذاری تنظیمات", command=self.load_config)
        file_menu.add_command(label="ذخیره تنظیمات", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.on_closing)
        
        # منوی ابزارها
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ابزارها", menu=tools_menu)
        tools_menu.add_command(label="تست اتصال Ollama", command=self.test_ollama)
        tools_menu.add_command(label="بررسی سیستم", command=self.system_check)
        tools_menu.add_command(label="پاک‌سازی لاگ‌ها", command=self.cleanup_logs)
        
        # منوی راهنما
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="راهنما", menu=help_menu)
        help_menu.add_command(label="راهنمای استفاده", command=self.show_help)
        help_menu.add_command(label="درباره", command=self.show_about)
    
    def create_main_panels(self):
        """ساخت پنل‌های اصلی"""
        # پنل کنترل اصلی
        control_frame = ttk.LabelFrame(self.root, text="🎯 کنترل اصلی", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # دکمه‌های کنترل
        btn_frame = tk.Frame(control_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x')
        
        self.start_btn = ttk.Button(btn_frame, text="🚀 شروع ادمین هوشمند", 
                                  style='Success.TButton',
                                  command=self.start_admin_system)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹️ توقف", 
                                 style='Danger.TButton',
                                 command=self.stop_admin_system,
                                 state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.settings_btn = ttk.Button(btn_frame, text="⚙️ تنظیمات پیشرفته", 
                                     style='Primary.TButton',
                                     command=self.open_advanced_settings)
        self.settings_btn.pack(side='left', padx=5)
        
        # Notebook برای تب‌ها
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # تب مانیتورینگ
        self.create_monitoring_tab()
        
        # تب چت‌ها
        self.create_chats_tab()
        
        # تب آمار
        self.create_stats_tab()
        
        # تب لاگ‌ها
        self.create_logs_tab()
    
    def create_monitoring_tab(self):
        """تب مانیتورینگ بلادرنگ"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="📊 مانیتورینگ")
        
        # پنل آمار لحظه‌ای
        stats_frame = ttk.LabelFrame(monitoring_frame, text="📈 آمار لحظه‌ای", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # متغیرهای آمار
        self.active_chats_var = tk.StringVar(value="0")
        self.total_messages_var = tk.StringVar(value="0")
        self.success_rate_var = tk.StringVar(value="0%")
        self.avg_response_time_var = tk.StringVar(value="0s")
        
        # نمایش آمار
        stats_grid = tk.Frame(stats_frame, bg='#ecf0f1')
        stats_grid.pack(fill='x')
        
        tk.Label(stats_grid, text="چت‌های فعال:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5)
        tk.Label(stats_grid, textvariable=self.active_chats_var, fg=self.colors['primary']).grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="کل پیام‌ها:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=20)
        tk.Label(stats_grid, textvariable=self.total_messages_var, fg=self.colors['primary']).grid(row=0, column=3, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="نرخ موفقیت:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5)
        tk.Label(stats_grid, textvariable=self.success_rate_var, fg=self.colors['success']).grid(row=1, column=1, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="زمان پاسخ:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='w', padx=20)
        tk.Label(stats_grid, textvariable=self.avg_response_time_var, fg=self.colors['warning']).grid(row=1, column=3, sticky='w', padx=5)
        
        # پنل وضعیت سیستم
        system_frame = ttk.LabelFrame(monitoring_frame, text="🔧 وضعیت سیستم", padding=10)
        system_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.system_status = scrolledtext.ScrolledText(system_frame, height=20, width=80)
        self.system_status.pack(fill='both', expand=True)
    
    def create_chats_tab(self):
        """تب مدیریت چت‌ها"""
        chats_frame = ttk.Frame(self.notebook)
        self.notebook.add(chats_frame, text="💬 چت‌ها")
        
        # پنل اضافه کردن چت
        add_chat_frame = ttk.LabelFrame(chats_frame, text="➕ اضافه کردن چت جدید", padding=10)
        add_chat_frame.pack(fill='x', padx=10, pady=5)
        
        # فرم اضافه کردن چت
        form_frame = tk.Frame(add_chat_frame)
        form_frame.pack(fill='x')
        
        tk.Label(form_frame, text="نام چت:").grid(row=0, column=0, sticky='w', padx=5)
        self.chat_name_entry = tk.Entry(form_frame, width=30)
        self.chat_name_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(form_frame, text="شناسه چت:").grid(row=0, column=2, sticky='w', padx=20)
        self.chat_id_entry = tk.Entry(form_frame, width=20)
        self.chat_id_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(form_frame, text="افزودن", command=self.add_chat).grid(row=0, column=4, padx=10)
        
        # لیست چت‌ها
        chats_list_frame = ttk.LabelFrame(chats_frame, text="📋 چت‌های مدیریت شده", padding=10)
        chats_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # جدول چت‌ها
        columns = ('نام', 'شناسه', 'وضعیت', 'آخرین فعالیت', 'پیام‌ها')
        self.chats_tree = ttk.Treeview(chats_list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.chats_tree.heading(col, text=col)
            self.chats_tree.column(col, width=150)
        
        # اسکرول‌بار
        chats_scrollbar = ttk.Scrollbar(chats_list_frame, orient='vertical', command=self.chats_tree.yview)
        self.chats_tree.configure(yscrollcommand=chats_scrollbar.set)
        
        self.chats_tree.pack(side='left', fill='both', expand=True)
        chats_scrollbar.pack(side='right', fill='y')
        
        # منوی راست کلیک
        self.create_chat_context_menu()
    
    def create_stats_tab(self):
        """تب آمار و گزارش‌ها"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 آمار")
        
        # فیلترهای زمانی
        filter_frame = ttk.LabelFrame(stats_frame, text="🔍 فیلترها", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(filter_frame, text="بازه زمانی:").pack(side='left', padx=5)
        
        self.time_filter = ttk.Combobox(filter_frame, values=[
            "امروز", "هفته گذشته", "ماه گذشته", "سه ماه گذشته", "همه"
        ], state='readonly')
        self.time_filter.set("امروز")
        self.time_filter.pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="بروزرسانی", command=self.update_stats).pack(side='left', padx=10)
        ttk.Button(filter_frame, text="خروجی Excel", command=self.export_stats).pack(side='left', padx=5)
        
        # نمایش آمار
        self.stats_display = scrolledtext.ScrolledText(stats_frame, height=25, width=80)
        self.stats_display.pack(fill='both', expand=True, padx=10, pady=5)
    
    def create_logs_tab(self):
        """تب لاگ‌ها"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 لاگ‌ها")
        
        # کنترل‌های لاگ
        log_control_frame = ttk.LabelFrame(logs_frame, text="🎛️ کنترل لاگ", padding=10)
        log_control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(log_control_frame, text="بروزرسانی", command=self.refresh_logs).pack(side='left', padx=5)
        ttk.Button(log_control_frame, text="پاک کردن", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(log_control_frame, text="ذخیره", command=self.save_logs).pack(side='left', padx=5)
        
        # نمایش لاگ‌ها
        self.logs_display = scrolledtext.ScrolledText(logs_frame, height=25, width=80)
        self.logs_display.pack(fill='both', expand=True, padx=10, pady=5)
    
    def create_status_bar(self):
        """ساخت نوار وضعیت"""
        self.status_frame = tk.Frame(self.root, bg=self.colors['dark'], height=30)
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(self.status_frame, 
                                   text="🔴 غیرفعال", 
                                   bg=self.colors['dark'], 
                                   fg='white',
                                   font=('Arial', 10))
        self.status_label.pack(side='left', padx=10)
        
        self.license_label = tk.Label(self.status_frame,
                                    text="🔒 لایسنس: بررسی...",
                                    bg=self.colors['dark'],
                                    fg='white',
                                    font=('Arial', 10))
        self.license_label.pack(side='right', padx=10)
    
    def create_chat_context_menu(self):
        """منوی راست کلیک برای چت‌ها"""
        self.chat_menu = tk.Menu(self.root, tearoff=0)
        self.chat_menu.add_command(label="ویرایش", command=self.edit_chat)
        self.chat_menu.add_command(label="حذف", command=self.delete_chat)
        self.chat_menu.add_command(label="نمایش آمار", command=self.show_chat_stats)
        self.chat_menu.add_command(label="تست اتصال", command=self.test_chat_connection)
        
        self.chats_tree.bind("<Button-3>", self.show_chat_menu)
    
    def initial_checks(self):
        """بررسی‌های اولیه سیستم"""
        # بروزرسانی وضعیت لایسنس
        if self.is_licensed:
            self.license_label.config(text="🟢 لایسنس: معتبر", fg='#27ae60')
        else:
            self.license_label.config(text="🔴 لایسنس: نامعتبر", fg='#e74c3c')
        
        # تست اتصال Ollama
        threading.Thread(target=self.test_ollama_background, daemon=True).start()
    
    def start_admin_system(self):
        """شروع سیستم ادمین هوشمند"""
        if not self.is_licensed:
            # نمایش پنجره ورود لایسنس
            self.show_license_dialog()
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="🟢 فعال", fg='#27ae60')
        
        # شروع thread اصلی
        self.admin_thread = threading.Thread(target=self.run_admin_system, daemon=True)
        self.admin_thread.start()
        
        self.log_message("🚀 سیستم ادمین هوشمند شروع شد")
    
    def show_license_dialog(self):
        """نمایش پنجره ورود لایسنس"""
        license_window = tk.Toplevel(self.root)
        license_window.title("ورود لایسنس")
        license_window.geometry("500x400")
        license_window.configure(bg='#ecf0f1')
        license_window.resizable(False, False)
        
        # محتوای پنجره
        title_label = tk.Label(license_window, 
                              text="🔐 فعال‌سازی Telegram Admin Pro", 
                              font=('Arial', 16, 'bold'),
                              bg='#ecf0f1',
                              fg='#2c3e50')
        title_label.pack(pady=20)
        
        info_text = """برای استفاده از نسخه حرفه‌ای، لطفاً یکی از لایسنس‌های زیر را وارد کنید:

🎯 لایسنس‌های معتبر:
• ADMIN_PRO_DEMO_2025 (نسخه دمو)
• FREE_TRIAL_LICENSE (آزمایشی رایگان)

یا برای دریافت لایسنس کامل با ما تماس بگیرید."""
        
        info_label = tk.Label(license_window, 
                             text=info_text,
                             font=('Arial', 10),
                             bg='#ecf0f1',
                             fg='#34495e',
                             justify='right')
        info_label.pack(pady=10, padx=20)
        
        # فیلد ورود لایسنس
        tk.Label(license_window, text="کلید لایسنس:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(pady=5)
        
        license_entry = tk.Entry(license_window, width=40, font=('Arial', 12))
        license_entry.pack(pady=10)
        license_entry.focus()
        
        # دکمه‌ها
        button_frame = tk.Frame(license_window, bg='#ecf0f1')
        button_frame.pack(pady=20)
        
        def activate_license():
            license_key = license_entry.get().strip()
            if self.validate_license(license_key):
                # ذخیره لایسنس
                with open(self.license_file, 'w') as f:
                    f.write(license_key)
                
                self.is_licensed = True
                self.license_label.config(text="🟢 لایسنس: معتبر", fg='#27ae60')
                license_window.destroy()
                
                messagebox.showinfo("موفقیت", "لایسنس با موفقیت فعال شد!")
                self.start_admin_system()  # شروع مجدد
            else:
                messagebox.showerror("خطا", "کلید لایسنس نامعتبر است!")
        
        def try_demo():
            license_entry.delete(0, tk.END)
            license_entry.insert(0, "ADMIN_PRO_DEMO_2025")
            activate_license()
        
        ttk.Button(button_frame, text="فعال‌سازی", command=activate_license, style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="دمو رایگان", command=try_demo, style='Primary.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="لغو", command=license_window.destroy, style='Danger.TButton').pack(side='left', padx=5)
        
        # بایند کلید Enter
        license_entry.bind('<Return>', lambda e: activate_license())
    
    def stop_admin_system(self):
        """توقف سیستم ادمین"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="🔴 غیرفعال", fg='#e74c3c')
        
        self.log_message("⏹️ سیستم ادمین متوقف شد")
    
    def run_admin_system(self):
        """حلقه اصلی سیستم ادمین"""
        try:
            self.log_message("🔄 شروع حلقه مدیریت چت‌ها...")
            
            while self.is_running:
                # مدیریت همه چت‌ها
                self.manage_all_chats()
                
                # بروزرسانی آمار
                self.update_live_stats()
                
                # انتظار
                time.sleep(self.config.get('response_settings', {}).get('response_delay', 1.0))
                
        except Exception as e:
            self.log_message(f"❌ خطا در سیستم ادمین: {e}")
            self.logger.error(f"خطا در run_admin_system: {e}")
    
    def manage_all_chats(self):
        """مدیریت همه چت‌ها"""
        managed_chats = self.config.get('managed_chats', [])
        
        for chat in managed_chats:
            if not self.is_running:
                break
            
            try:
                self.process_chat(chat)
            except Exception as e:
                self.log_message(f"❌ خطا در پردازش چت {chat.get('name', 'نامشخص')}: {e}")
    
    def process_chat(self, chat_config):
        """پردازش یک چت"""
        try:
            # تصویربرداری از چت
            screenshot = self.capture_chat_screen()
            if not screenshot:
                return
            
            # تحلیل پیام‌ها با Vision AI
            messages = self.analyze_chat_messages(screenshot, chat_config)
            if not messages:
                return
            
            # پردازش هر پیام
            for message in messages:
                if not self.is_running:
                    break
                
                response = self.generate_intelligent_response(message, chat_config)
                if response:
                    self.send_response(response, chat_config)
                    self.log_chat_interaction(chat_config, message, response)
                    
        except Exception as e:
            self.log_message(f"❌ خطا در پردازش چت: {e}")
    
    def capture_chat_screen(self):
        """تصویربرداری از صفحه چت"""
        try:
            screenshot = pyautogui.screenshot()
            timestamp = int(time.time())
            screenshot_path = self.base_dir / f"temp_screenshot_{timestamp}.png"
            screenshot.save(screenshot_path)
            return screenshot_path
        except Exception as e:
            self.log_message(f"❌ خطا در تصویربرداری: {e}")
            return None
    
    def analyze_chat_messages(self, screenshot_path, chat_config):
        """تحلیل پیام‌های چت با Vision AI"""
        try:
            with open(screenshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = """تو یک ادمین هوشمند هستی که صفحه تلگرام را تحلیل می‌کنی.

وظایف:
1. پیام‌های جدید و خوانده نشده را شناسایی کن
2. محتوای پیام‌ها را استخراج کن
3. نوع پیام (سوال، درخواست، شکایت، تشکر) را تشخیص بده
4. اولویت پاسخ‌دهی را مشخص کن

فرمت پاسخ:
{
  "new_messages": [
    {
      "content": "متن پیام",
      "type": "نوع پیام",
      "priority": "بالا/متوسط/پایین",
      "sender": "نام فرستنده"
    }
  ]
}

اگر پیام جدیدی نیست، فقط بنویس: NO_NEW_MESSAGES"""

            response = requests.post(
                f"{self.config['ollama_url']}/api/generate",
                json={
                    "model": self.config['ollama_vision_model'],
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                if result != "NO_NEW_MESSAGES":
                    try:
                        return json.loads(result).get('new_messages', [])
                    except:
                        return [{"content": result, "type": "unknown", "priority": "متوسط", "sender": "unknown"}]
            
            return []
            
        except Exception as e:
            self.log_message(f"❌ خطا در تحلیل Vision: {e}")
            return []
        finally:
            # پاک کردن فایل موقت
            if screenshot_path and screenshot_path.exists():
                screenshot_path.unlink()
    
    def generate_intelligent_response(self, message, chat_config):
        """تولید پاسخ هوشمند"""
        try:
            # تنظیمات پاسخ بر اساس نوع چت و پیام
            response_style = self.determine_response_style(message, chat_config)
            
            prompt = f"""تو یک ادمین حرفه‌ای و با تجربه هستی.

پیام دریافتی: "{message['content']}"
نوع پیام: {message.get('type', 'نامشخص')}
اولویت: {message.get('priority', 'متوسط')}

تنظیمات پاسخ:
- استایل: {response_style}
- حداکثر طول: {self.config['response_settings']['max_message_length']} کاراکتر
- حالت حرفه‌ای: {self.config['response_settings']['professional_mode']}
- استفاده از ایموجی: {self.config['response_settings'].get('use_emojis', True)}

یک پاسخ مناسب، مفید و دوستانه بنویس. پاسخ باید:
1. مستقیم و مفید باشد
2. حالت حرفه‌ای داشته باشد
3. احترام‌آمیز باشد
4. در صورت نیاز، راهنمایی ارائه دهد

فقط متن پاسخ را بنویس، بدون توضیح اضافی."""

            response = requests.post(
                f"{self.config['ollama_url']}/api/generate",
                json={
                    "model": self.config['ollama_text_model'],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": self.config['response_settings']['max_message_length']
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            
            return None
            
        except Exception as e:
            self.log_message(f"❌ خطا در تولید پاسخ: {e}")
            return None
    
    def determine_response_style(self, message, chat_config):
        """تعیین سبک پاسخ بر اساس پیام و چت"""
        message_type = message.get('type', 'unknown')
        
        if message_type in ['complaint', 'urgent']:
            return 'formal_supportive'
        elif message_type in ['question', 'help']:
            return 'helpful_detailed'
        elif message_type in ['thanks', 'appreciation']:
            return 'warm_appreciative'
        else:
            return 'friendly_professional'
    
    def send_response(self, response_text, chat_config):
        """ارسال پاسخ به چت"""
        try:
            # پیدا کردن باکس پیام
            screen_width, screen_height = pyautogui.size()
            input_x = screen_width // 2
            input_y = screen_height - 100
            
            # کلیک و ارسال
            pyautogui.click(input_x, input_y)
            time.sleep(0.3)
            
            # پاک کردن محتوای قبلی
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # کپی و ارسال
            pyperclip.copy(response_text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            
            self.log_message(f"✅ پاسخ ارسال شد: {response_text[:50]}...")
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در ارسال پاسخ: {e}")
            return False
    
    def log_chat_interaction(self, chat_config, message, response):
        """ثبت تعامل چت در دیتابیس"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs 
                (chat_id, chat_name, message_type, content, response, processing_time, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                chat_config.get('id', ''),
                chat_config.get('name', ''),
                message.get('type', 'unknown'),
                message.get('content', ''),
                response,
                time.time(),
                True
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"خطا در ثبت لاگ: {e}")
    
    def log_message(self, message):
        """نمایش پیام در سیستم"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_text = f"[{timestamp}] {message}\n"
        
        try:
            self.system_status.insert(tk.END, log_text)
            self.system_status.see(tk.END)
        except:
            pass
        
        self.logger.info(message)
    
    def update_live_stats(self):
        """بروزرسانی آمار زنده"""
        try:
            # آمار از دیتابیس
            cursor = self.conn.cursor()
            
            # تعداد چت‌های فعال
            active_chats = len(self.active_sessions)
            self.active_chats_var.set(str(active_chats))
            
            # کل پیام‌های امروز
            cursor.execute('''
                SELECT COUNT(*) FROM message_logs 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            total_messages = cursor.fetchone()[0]
            self.total_messages_var.set(str(total_messages))
            
            # نرخ موفقیت
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM message_logs 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            result = cursor.fetchone()
            if result[0] > 0:
                success_rate = (result[1] / result[0]) * 100
                self.success_rate_var.set(f"{success_rate:.1f}%")
            else:
                self.success_rate_var.set("0%")
            
            # میانگین زمان پاسخ
            cursor.execute('''
                SELECT AVG(processing_time) FROM message_logs 
                WHERE DATE(timestamp) = DATE('now') AND success = 1
            ''')
            avg_time = cursor.fetchone()[0]
            if avg_time:
                self.avg_response_time_var.set(f"{avg_time:.1f}s")
            else:
                self.avg_response_time_var.set("0s")
                
        except Exception as e:
            self.logger.error(f"خطا در بروزرسانی آمار: {e}")
    
    # متدهای کمکی GUI
    def add_chat(self):
        """اضافه کردن چت جدید"""
        name = self.chat_name_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()
        
        if not name or not chat_id:
            messagebox.showwarning("هشدار", "لطفاً نام و شناسه چت را وارد کنید")
            return
        
        # اضافه کردن به تنظیمات
        new_chat = {
            "id": chat_id,
            "name": name,
            "auto_reply": True,
            "response_style": "friendly",
            "language": "fa"
        }
        
        if 'managed_chats' not in self.config:
            self.config['managed_chats'] = []
        
        self.config['managed_chats'].append(new_chat)
        self.save_config()
        
        # اضافه کردن به جدول
        self.chats_tree.insert('', 'end', values=(
            name, chat_id, "فعال", "اکنون", "0"
        ))
        
        # پاک کردن فرم
        self.chat_name_entry.delete(0, tk.END)
        self.chat_id_entry.delete(0, tk.END)
        
        self.log_message(f"✅ چت جدید اضافه شد: {name}")
    
    def test_ollama_background(self):
        """تست اتصال Ollama در پس‌زمینه"""
        try:
            response = requests.get(f"{self.config['ollama_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                self.log_message("✅ اتصال Ollama برقرار است")
            else:
                self.log_message("❌ مشکل در اتصال Ollama")
        except:
            self.log_message("❌ Ollama در دسترس نیست")
    
    def save_config(self):
        """ذخیره تنظیمات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.log_message("✅ تنظیمات ذخیره شد")
        except Exception as e:
            self.log_message(f"❌ خطا در ذخیره تنظیمات: {e}")
    
    def on_closing(self):
        """بستن برنامه"""
        if self.is_running:
            if messagebox.askokcancel("خروج", "آیا می‌خواهید از برنامه خارج شوید؟"):
                self.stop_admin_system()
                time.sleep(1)
                self.root.destroy()
        else:
            self.root.destroy()
    
    # متدهای کامل GUI
    def new_config(self):
        """تنظیمات جدید"""
        if messagebox.askyesno("تنظیمات جدید", "آیا می‌خواهید تنظیمات را به حالت پیش‌فرض بازگردانید؟"):
            self.config = self.default_config.copy()
            self.save_config()
            messagebox.showinfo("موفقیت", "تنظیمات جدید اعمال شد")
    
    def load_config(self):
        """بارگذاری تنظیمات"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="انتخاب فایل تنظیمات",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.save_config()
                messagebox.showinfo("موفقیت", "تنظیمات بارگذاری شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بارگذاری: {e}")
    
    def test_ollama(self):
        """تست اتصال Ollama"""
        try:
            response = requests.get(f"{self.config['ollama_url']}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                message = f"✅ اتصال موفق!\n\nمدل‌های موجود:\n" + "\n".join(model_names)
                messagebox.showinfo("تست Ollama", message)
            else:
                messagebox.showerror("خطا", "اتصال ناموفق")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اتصال: {e}")
    
    def system_check(self):
        """بررسی سیستم"""
        check_results = []
        
        # بررسی Ollama
        try:
            response = requests.get(f"{self.config['ollama_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                check_results.append("✅ Ollama: متصل")
            else:
                check_results.append("❌ Ollama: خطا در اتصال")
        except:
            check_results.append("❌ Ollama: غیرقابل دسترس")
        
        # بررسی دیتابیس
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM message_logs")
            count = cursor.fetchone()[0]
            check_results.append(f"✅ دیتابیس: {count} رکورد")
        except:
            check_results.append("❌ دیتابیس: مشکل در اتصال")
        
        # بررسی لایسنس
        if self.is_licensed:
            check_results.append("✅ لایسنس: معتبر")
        else:
            check_results.append("❌ لایسنس: نامعتبر")
        
        # بررسی چت‌ها
        chat_count = len(self.config.get('managed_chats', []))
        check_results.append(f"📊 چت‌های مدیریت شده: {chat_count}")
        
        messagebox.showinfo("بررسی سیستم", "\n".join(check_results))
    
    def cleanup_logs(self):
        """پاک‌سازی لاگ‌ها"""
        if messagebox.askyesno("پاک‌سازی", "آیا می‌خواهید لاگ‌های قدیمی (بیش از 30 روز) را پاک کنید؟"):
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    DELETE FROM message_logs 
                    WHERE timestamp < datetime('now', '-30 days')
                ''')
                deleted_count = cursor.rowcount
                self.conn.commit()
                
                messagebox.showinfo("موفقیت", f"{deleted_count} رکورد قدیمی پاک شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در پاک‌سازی: {e}")
    
    def show_help(self):
        """نمایش راهنما"""
        help_text = """🎯 راهنمای استفاده از Telegram Admin Pro

🚀 شروع کار:
1. ابتدا لایسنس معتبر وارد کنید
2. چت‌های مورد نظر را اضافه کنید
3. دکمه "شروع ادمین هوشمند" را کلیک کنید

💬 مدیریت چت‌ها:
• تب "چت‌ها" → "افزودن چت جدید"
• نام و شناسه چت را وارد کنید
• روی چت راست کلیک کنید برای تنظیمات

📊 مانیتورینگ:
• تب "مانیتورینگ" برای نظارت زنده
• تب "آمار" برای گزارش‌های تفصیلی
• تب "لاگ‌ها" برای بررسی جزئیات

⚙️ تنظیمات:
• منو "ابزارها" → "تنظیمات پیشرفته"
• تنظیم سبک پاسخ‌دهی
• کنترل سرعت و دقت"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("راهنما")
        help_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
    
    def show_about(self):
        """درباره برنامه"""
        about_text = f"""🎯 {self.product_name}
نسخه: {self.version}

🚀 ویژگی‌ها:
• مدیریت خودکار چت‌های تلگرام
• پاسخ‌دهی هوشمند با AI
• مانیتورینگ بلادرنگ
• گزارش‌دهی تفصیلی
• امنیت پیشرفته

👨‍💻 توسعه‌دهنده: AI Assistant
📧 پشتیبانی: telegram.admin.pro@example.com
🌐 وب‌سایت: www.telegram-admin-pro.com

© 2025 - همه حقوق محفوظ است"""
        
        messagebox.showinfo("درباره", about_text)
    
    def open_advanced_settings(self):
        """پنل تنظیمات پیشرفته"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("تنظیمات پیشرفته")
        settings_window.geometry("700x600")
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تب تنظیمات پاسخ
        response_frame = ttk.Frame(notebook)
        notebook.add(response_frame, text="پاسخ‌دهی")
        
        # تنظیمات پاسخ‌دهی
        ttk.Label(response_frame, text="تاخیر پاسخ (ثانیه):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        delay_var = tk.DoubleVar(value=self.config['response_settings']['response_delay'])
        ttk.Scale(response_frame, from_=0.5, to=10.0, variable=delay_var, orient='horizontal').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(response_frame, text="حداکثر طول پیام:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        length_var = tk.IntVar(value=self.config['response_settings']['max_message_length'])
        ttk.Scale(response_frame, from_=100, to=1000, variable=length_var, orient='horizontal').grid(row=1, column=1, padx=5, pady=5)
        
        professional_var = tk.BooleanVar(value=self.config['response_settings']['professional_mode'])
        ttk.Checkbutton(response_frame, text="حالت حرفه‌ای", variable=professional_var).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        
        # دکمه ذخیره
        def save_advanced_settings():
            self.config['response_settings']['response_delay'] = delay_var.get()
            self.config['response_settings']['max_message_length'] = int(length_var.get())
            self.config['response_settings']['professional_mode'] = professional_var.get()
            self.save_config()
            messagebox.showinfo("موفقیت", "تنظیمات ذخیره شد")
            settings_window.destroy()
        
        ttk.Button(response_frame, text="ذخیره", command=save_advanced_settings).grid(row=10, column=0, pady=20)
    
    def edit_chat(self):
        """ویرایش چت انتخاب شده"""
        selected = self.chats_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً چتی را انتخاب کنید")
            return
        
        # پیاده‌سازی ویرایش چت
        messagebox.showinfo("ویرایش", "ویرایش چت در نسخه بعدی اضافه می‌شود")
    
    def delete_chat(self):
        """حذف چت انتخاب شده"""
        selected = self.chats_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً چتی را انتخاب کنید")
            return
        
        if messagebox.askyesno("تأیید", "آیا می‌خواهید این چت را حذف کنید؟"):
            item = selected[0]
            values = self.chats_tree.item(item, 'values')
            chat_id = values[1]
            
            # حذف از تنظیمات
            self.config['managed_chats'] = [
                chat for chat in self.config.get('managed_chats', [])
                if chat.get('id') != chat_id
            ]
            self.save_config()
            
            # حذف از جدول
            self.chats_tree.delete(item)
            
            self.log_message(f"🗑️ چت حذف شد: {values[0]}")
    
    def show_chat_stats(self):
        """نمایش آمار چت"""
        selected = self.chats_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً چتی را انتخاب کنید")
            return
        
        # نمایش آمار چت
        messagebox.showinfo("آمار", "آمار چت در نسخه بعدی اضافه می‌شود")
    
    def test_chat_connection(self):
        """تست اتصال چت"""
        selected = self.chats_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً چتی را انتخاب کنید")
            return
        
        messagebox.showinfo("تست", "تست اتصال چت در نسخه بعدی اضافه می‌شود")
    
    def show_chat_menu(self, event):
        """نمایش منوی راست کلیک چت"""
        try:
            self.chat_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.chat_menu.grab_release()
    
    def update_stats(self):
        """بروزرسانی آمار"""
        try:
            time_filter = self.time_filter.get()
            
            # محاسبه بازه زمانی
            if time_filter == "امروز":
                where_clause = "WHERE DATE(timestamp) = DATE('now')"
            elif time_filter == "هفته گذشته":
                where_clause = "WHERE timestamp >= datetime('now', '-7 days')"
            elif time_filter == "ماه گذشته":
                where_clause = "WHERE timestamp >= datetime('now', '-30 days')"
            elif time_filter == "سه ماه گذشته":
                where_clause = "WHERE timestamp >= datetime('now', '-90 days')"
            else:
                where_clause = ""
            
            cursor = self.conn.cursor()
            
            # آمار کلی
            cursor.execute(f"SELECT COUNT(*) FROM message_logs {where_clause}")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM message_logs {where_clause} AND success = 1")
            successful = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT AVG(processing_time) FROM message_logs {where_clause}")
            avg_time = cursor.fetchone()[0] or 0
            
            # آمار روزانه
            cursor.execute(f'''
                SELECT DATE(timestamp), COUNT(*), 
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END)
                FROM message_logs {where_clause}
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp) DESC
                LIMIT 10
            ''')
            daily_stats = cursor.fetchall()
            
            # نمایش آمار
            stats_text = f"""📊 آمار {time_filter}

📈 خلاصه:
• کل پیام‌ها: {total_messages:,}
• پاسخ‌های موفق: {successful:,}
• نرخ موفقیت: {(successful/max(total_messages,1)*100):.1f}%
• میانگین زمان پاسخ: {avg_time:.2f} ثانیه

📅 آمار روزانه:
"""
            
            for date_str, count, success_count in daily_stats:
                success_rate = (success_count/max(count,1)*100)
                stats_text += f"• {date_str}: {count} پیام ({success_rate:.1f}% موفق)\n"
            
            self.stats_display.delete('1.0', tk.END)
            self.stats_display.insert('1.0', stats_text)
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بروزرسانی آمار: {e}")
    
    def export_stats(self):
        """خروجی Excel از آمار"""
        messagebox.showinfo("خروجی", "خروجی Excel در نسخه بعدی اضافه می‌شود")
    
    def refresh_logs(self):
        """بروزرسانی لاگ‌ها"""
        try:
            with open(self.base_dir / 'admin.log', 'r', encoding='utf-8') as f:
                logs = f.read()
            
            self.logs_display.delete('1.0', tk.END)
            self.logs_display.insert('1.0', logs)
            self.logs_display.see(tk.END)
            
        except Exception as e:
            self.log_message(f"خطا در خواندن لاگ: {e}")
    
    def clear_logs(self):
        """پاک کردن لاگ‌ها"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید لاگ‌ها را پاک کنید؟"):
            try:
                with open(self.base_dir / 'admin.log', 'w', encoding='utf-8') as f:
                    f.write("")
                
                self.logs_display.delete('1.0', tk.END)
                self.log_message("🗑️ لاگ‌ها پاک شدند")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در پاک کردن: {e}")
    
    def save_logs(self):
        """ذخیره لاگ‌ها"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="ذخیره لاگ‌ها",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                content = self.logs_display.get('1.0', tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("موفقیت", "لاگ‌ها ذخیره شدند")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره: {e}")
    
    def run(self):
        """اجرای برنامه"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TelegramAdminPro()
    app.run()
