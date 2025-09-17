#!/usr/bin/env python3
"""
🎯 Telegram AI Admin Pro v3.0 - ادمین هوشمند حرفه‌ای
سیستم مدیریت چت‌های تلگرام با هوش مصنوعی پیشرفته

ویژگی‌های نسخه 3:
- مدیریت همزمان چندین چت و گروه
- پاسخ‌دهی هوشمند و خودکار به همه پیام‌ها
- پردازش موازی و اسکن خودکار چت‌ها
- ارسال مستقیم پیام (نه کپی به کلیپ‌بورد)
- اجرا و کنترل خودکار تلگرام
- سیستم لاگ و گزارش‌دهی حرفه‌ای
- پنل مدیریت پیشرفته
- امنیت و کنترل دسترسی
- قابلیت فروش و استفاده تجاری
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from dotenv import load_dotenv
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

# ایمپورت ماژول‌های جدید
from telegram_auto_manager import TelegramAutoManager
from chat_scanner import ChatScanner
from smart_response_generator import SmartResponseGenerator
from parallel_processor import ParallelProcessor

class TelegramAdminPro:
    """کلاس اصلی ادمین هوشمند تلگرام"""
    
    def __init__(self):
        """مقداردهی اولیه سیستم"""
        self.version = "3.0.0"
        self.product_name = "Telegram AI Admin Pro"
        
        # بارگذاری تنظیمات از .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # اگر dotenv نصب نیست، از روش دستی استفاده می‌کنیم
            self.load_env_manually()
        
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
        self.setup_logging()  # ابتدا logging را تنظیم کنیم
        self.setup_system()
        self.setup_database()
        
        # مقداردهی ماژول‌های جدید
        self.setup_new_modules()
        self.create_gui()
    
    def load_env_manually(self):
        """بارگذاری دستی فایل .env"""
        try:
            env_file = self.base_dir / '.env'
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"خطا در بارگذاری .env: {e}")
    
    def get_env_license(self):
        """دریافت لایسنس از متغیر محیطی"""
        return os.getenv('ADMIN_PRO_LICENSE', '')
    
    def is_unlimited_license(self):
        """بررسی لایسنس نامحدود"""
        return os.getenv('ADMIN_PRO_UNLIMITED', 'false').lower() == 'true'
    
    def is_commercial_license(self):
        """بررسی لایسنس تجاری"""
        return os.getenv('ADMIN_PRO_COMMERCIAL', 'false').lower() == 'true'
    
    def get_ollama_settings(self):
        """دریافت تنظیمات Ollama از .env"""
        return {
            'url': os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434'),
            'text_model': os.getenv('OLLAMA_TEXT_MODEL', 'llama3.1:8b'),
            'vision_model': os.getenv('OLLAMA_VISION_MODEL', 'llava'),
            'timeout': int(os.getenv('OLLAMA_TIMEOUT', '45')),
            'vision_timeout': int(os.getenv('VISION_TIMEOUT', '60')),
            'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', '3'))
        }
    
    def get_performance_settings(self):
        """دریافت تنظیمات عملکرد از .env"""
        return {
            'max_chats': int(os.getenv('MAX_CONCURRENT_CHATS', '50')),
            'response_delay': float(os.getenv('RESPONSE_DELAY', '0.5')),
            'professional_mode': os.getenv('PROFESSIONAL_MODE', 'true').lower() == 'true',
            'vision_enabled': os.getenv('VISION_ENABLED', 'true').lower() == 'true'
        }
        
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
            # تنظیم logger ساده برای خطاهای اولیه
            import logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """راه‌اندازی پایگاه داده"""
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.create_tables()
        except Exception as e:
            print(f"خطا در راه‌اندازی دیتابیس: {e}")
    
    def setup_new_modules(self):
        """راه‌اندازی ماژول‌های جدید"""
        try:
            self.log_message("🔧 راه‌اندازی ماژول‌های جدید...")
            
            # تنظیمات کانفیگ
            config = {
                'telegram_path': os.getenv('TELEGRAM_PORTABLE_PATH', 'C:/Telegram/Telegram.exe'),
                'auto_start': os.getenv('TELEGRAM_AUTO_START', 'true').lower() == 'true',
                'fullscreen': os.getenv('TELEGRAM_FULLSCREEN', 'true').lower() == 'true',
                'send_delay': float(os.getenv('MESSAGE_SEND_DELAY', '1.5')),
                'typing_speed': float(os.getenv('TYPING_SPEED', '0.05')),
                'scan_interval': int(os.getenv('SCAN_INTERVAL', '30')),
                'max_chats_per_scan': int(os.getenv('MAX_CHATS_PER_SCAN', '20')),
                'max_worker_threads': int(os.getenv('MAX_WORKER_THREADS', '3')),
                'queue_size': int(os.getenv('QUEUE_SIZE', '100')),
                'batch_size': int(os.getenv('BATCH_SIZE', '5')),
                'ollama_url': os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434'),
                'text_model': os.getenv('OLLAMA_TEXT_MODEL', 'llama3.1:8b'),
                'vision_model': os.getenv('OLLAMA_VISION_MODEL', 'llava'),
                'vision_timeout': int(os.getenv('VISION_TIMEOUT', '180')),
                'text_timeout': int(os.getenv('OLLAMA_TIMEOUT', '120'))
            }
            
            # مقداردهی ماژول‌ها
            self.telegram_manager = TelegramAutoManager(config)
            self.response_generator = SmartResponseGenerator(config)
            self.chat_scanner = ChatScanner(config, self.telegram_manager)
            self.parallel_processor = ParallelProcessor(
                config, self.telegram_manager, self.chat_scanner, self.response_generator
            )
            
            self.log_message("✅ ماژول‌های جدید راه‌اندازی شدند")
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطا در راه‌اندازی ماژول‌ها: {e}")
            return False
    
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
        # تنظیم پیش‌فرض logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'admin.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # بروزرسانی بر اساس تنظیمات config اگر موجود باشد
        try:
            if hasattr(self, 'config'):
                log_level = getattr(logging, self.config.get('admin_settings', {}).get('log_level', 'INFO'))
                self.logger.setLevel(log_level)
        except:
            pass
    
    def check_license(self):
        """بررسی اعتبار لایسنس"""
        try:
            # اول از .env بررسی کنیم
            env_license = self.get_env_license()
            if env_license and self.validate_license(env_license):
                self.is_licensed = True
                self.logger.info(f"✅ لایسنس معتبر از .env: {env_license[:15]}...")
                return
            
            # بعد از فایل لایسنس
            if self.license_file.exists():
                with open(self.license_file, 'r') as f:
                    license_data = f.read().strip()
                
                if self.validate_license(license_data):
                    self.is_licensed = True
                    self.logger.info("✅ لایسنس معتبر از فایل")
                else:
                    self.is_licensed = False
                    self.logger.warning("❌ لایسنس نامعتبر")
            else:
                self.is_licensed = False
                self.logger.warning("⚠️ فایل لایسنس پیدا نشد")
                
        except Exception as e:
            self.is_licensed = False
            self.logger.error(f"❌ خطا در بررسی لایسنس: {e}")
    
    def validate_license(self, license_key):
        """اعتبارسنجی کلید لایسنس"""
        # بررسی لایسنس از .env
        env_license = self.get_env_license()
        if env_license and license_key == env_license:
            return True
        
        # لایسنس‌های معتبر برای تست
        valid_licenses = [
            "ADMIN_PRO_DEMO_2025",  # لایسنس دمو
            "FREE_TRIAL_LICENSE",    # لایسنس آزمایشی
            "PERMANENT_ACTIVE_LICENSE_2025",  # لایسنس همیشه فعال
            "UNLIMITED_COMMERCIAL_LICENSE",   # لایسنس تجاری نامحدود
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
            'light': '#ecf0f1',
            'secondary': '#95a5a6',
            'info': '#16a085'
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
        
        self.fallback_btn = ttk.Button(btn_frame, text="🔄 تست Fallback", 
                                     style='Warning.TButton',
                                     command=self.test_fallback_mode)
        self.fallback_btn.pack(side='left', padx=5)
        
        # دکمه‌های کنترل تلگرام
        telegram_control_frame = tk.Frame(control_frame, bg='#ecf0f1')
        telegram_control_frame.pack(fill='x', pady=5)
        
        tk.Label(telegram_control_frame, text="🔧 کنترل تلگرام:", 
                font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        
        self.telegram_start_btn = ttk.Button(telegram_control_frame, text="📱 شروع تلگرام", 
                                           command=self.start_telegram_manually)
        self.telegram_start_btn.pack(side='left', padx=5)
        
        self.telegram_focus_btn = ttk.Button(telegram_control_frame, text="🎯 فوکوس", 
                                           command=self.focus_telegram_manually)
        self.telegram_focus_btn.pack(side='left', padx=5)
        
        self.scan_chats_btn = ttk.Button(telegram_control_frame, text="🔍 اسکن چت‌ها", 
                                       command=self.manual_scan_chats)
        self.scan_chats_btn.pack(side='left', padx=5)
        
        # دکمه‌های تست اتصال
        test_frame = tk.Frame(control_frame, bg='#ecf0f1')
        test_frame.pack(fill='x', pady=5)
        
        tk.Label(test_frame, text="🧪 تست‌ها:", 
                font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        
        self.test_ollama_btn = ttk.Button(test_frame, text="🤖 تست Vision AI", 
                                        command=self.test_vision_ai_connection)
        self.test_ollama_btn.pack(side='left', padx=5)
        
        self.test_telegram_btn = ttk.Button(test_frame, text="📱 تست تلگرام", 
                                          command=self.test_telegram_connection)
        self.test_telegram_btn.pack(side='left', padx=5)
        
        self.test_scan_btn = ttk.Button(test_frame, text="🔍 تست اسکن", 
                                      command=self.test_chat_scanning)
        self.test_scan_btn.pack(side='left', padx=5)
        
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
        self.fallback_status_var = tk.StringVar(value="Vision AI")
        
        # متغیرهای آمار جدید
        self.unread_chats_var = tk.StringVar(value="0")
        self.sent_messages_var = tk.StringVar(value="0")
        self.scan_success_rate_var = tk.StringVar(value="0%")
        self.last_scan_time_var = tk.StringVar(value="هرگز")
        self.scan_method_var = tk.StringVar(value="هیچ")
        
        # نمایش آمار
        stats_grid = tk.Frame(stats_frame, bg='#ecf0f1')
        stats_grid.pack(fill='x')
        
        # ردیف اول
        tk.Label(stats_grid, text="چت‌های فعال:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5)
        tk.Label(stats_grid, textvariable=self.active_chats_var, fg=self.colors['primary']).grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="چت‌های خوانده نشده:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=20)
        tk.Label(stats_grid, textvariable=self.unread_chats_var, fg=self.colors['warning']).grid(row=0, column=3, sticky='w', padx=5)
        
        # ردیف دوم
        tk.Label(stats_grid, text="کل پیام‌ها:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5)
        tk.Label(stats_grid, textvariable=self.total_messages_var, fg=self.colors['primary']).grid(row=1, column=1, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="پیام‌های ارسالی:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='w', padx=20)
        tk.Label(stats_grid, textvariable=self.sent_messages_var, fg=self.colors['success']).grid(row=1, column=3, sticky='w', padx=5)
        
        # ردیف سوم
        tk.Label(stats_grid, text="حالت فعلی:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5)
        self.fallback_status_label = tk.Label(stats_grid, textvariable=self.fallback_status_var, fg=self.colors['success'])
        self.fallback_status_label.grid(row=2, column=1, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="درصد موفقیت اسکن:", font=('Arial', 10, 'bold')).grid(row=2, column=2, sticky='w', padx=20)
        tk.Label(stats_grid, textvariable=self.scan_success_rate_var, fg=self.colors['primary']).grid(row=2, column=3, sticky='w', padx=5)
        
        # ردیف چهارم
        tk.Label(stats_grid, text="آخرین اسکن:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5)
        tk.Label(stats_grid, textvariable=self.last_scan_time_var, fg=self.colors['secondary']).grid(row=3, column=1, sticky='w', padx=5)
        
        tk.Label(stats_grid, text="روش اسکن:", font=('Arial', 10, 'bold')).grid(row=3, column=2, sticky='w', padx=20)
        tk.Label(stats_grid, textvariable=self.scan_method_var, fg=self.colors['info']).grid(row=3, column=3, sticky='w', padx=5)
        
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
        
        try:
            self.log_message("🚀 شروع سیستم ادمین هوشمند...")
            
            # راه‌اندازی تلگرام خودکار
            auto_start = os.getenv('TELEGRAM_AUTO_START', 'true').lower() == 'true'
            if auto_start:
                self.log_message("📱 راه‌اندازی تلگرام خودکار...")
                if self.telegram_manager.start_telegram():
                    self.telegram_manager.maximize_telegram()
                    self.log_message("✅ تلگرام با موفقیت راه‌اندازی شد")
                else:
                    self.log_message("⚠️ خطا در راه‌اندازی تلگرام، ادامه با حالت دستی")
            
            # شروع پردازش موازی
            if self.parallel_processor.start():
                self.log_message("⚡ پردازش موازی شروع شد")
            else:
                self.log_message("⚠️ خطا در شروع پردازش موازی")
            
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="🟢 فعال", fg='#27ae60')
            
            # شروع thread اصلی
            self.admin_thread = threading.Thread(target=self.run_admin_system, daemon=True)
            self.admin_thread.start()
            
            self.log_message("✅ سیستم ادمین هوشمند شروع شد")
            
        except Exception as e:
            self.log_message(f"❌ خطا در شروع سیستم: {e}")
            self.is_running = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.status_label.config(text="🔴 خطا", fg='#e74c3c')
    
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
• PERMANENT_ACTIVE_LICENSE_2025 (همیشه فعال)
• ADMIN_PRO_DEMO_2025 (نسخه دمو)
• FREE_TRIAL_LICENSE (آزمایشی رایگان)
• UNLIMITED_COMMERCIAL_LICENSE (تجاری نامحدود)

💡 لایسنس همیشه فعال در فایل .env موجود است."""
        
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
        
        def try_permanent():
            license_entry.delete(0, tk.END)
            license_entry.insert(0, "PERMANENT_ACTIVE_LICENSE_2025")
            activate_license()
        
        def try_unlimited():
            license_entry.delete(0, tk.END)
            license_entry.insert(0, "UNLIMITED_COMMERCIAL_LICENSE")
            activate_license()
        
        ttk.Button(button_frame, text="فعال‌سازی", command=activate_license, style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="همیشه فعال", command=try_permanent, style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="دمو رایگان", command=try_demo, style='Primary.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="لغو", command=license_window.destroy, style='Danger.TButton').pack(side='left', padx=5)
        
        # بایند کلید Enter
        license_entry.bind('<Return>', lambda e: activate_license())
    
    def stop_admin_system(self):
        """توقف سیستم ادمین"""
        try:
            self.log_message("🛑 توقف سیستم ادمین...")
            
            self.is_running = False
            
            # توقف پردازش موازی
            if hasattr(self, 'parallel_processor'):
                self.parallel_processor.stop()
            
            # بستن تلگرام (اختیاری)
            # if hasattr(self, 'telegram_manager'):
            #     self.telegram_manager.close_telegram()
            
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.status_label.config(text="🔴 غیرفعال", fg='#e74c3c')
            
            self.log_message("✅ سیستم ادمین متوقف شد")
            
        except Exception as e:
            self.log_message(f"❌ خطا در توقف سیستم: {e}")
    
    def test_fallback_mode(self):
        """تست حالت fallback"""
        try:
            self.log_message("🧪 شروع تست حالت Fallback...")
            
            # تنظیمات چت فیک برای تست
            test_chat_config = {
                'name': 'Test Chat',
                'type': 'private',
                'admin_style': 'friendly',
                'auto_response': True
            }
            
            # اجرای fallback
            self.process_chat_fallback(test_chat_config)
            
            messagebox.showinfo("تست Fallback", 
                              "✅ تست حالت Fallback با موفقیت انجام شد!\n"
                              "پیام تست در لاگ مشاهده کنید.")
                              
        except Exception as e:
            self.log_message(f"❌ خطا در تست fallback: {e}")
            messagebox.showerror("خطا", f"خطا در تست fallback:\n{e}")
    
    def test_vision_ai_connection(self):
        """تست اتصال Vision AI"""
        try:
            self.log_message("🧪 شروع تست اتصال Vision AI...")
            
            settings = self.get_ollama_settings()
            
            # تست اتصال به Ollama
            response = requests.get(f"{settings['url']}/api/tags", timeout=10)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                vision_model = settings['vision_model']
                
                # بررسی وجود مدل Vision
                vision_available = any(model.get('name', '').startswith(vision_model) for model in models)
                
                if vision_available:
                    # تست تولید پاسخ ساده
                    test_response = requests.post(
                        f"{settings['url']}/api/generate",
                        json={
                            "model": vision_model,
                            "prompt": "سلام! این یک تست است.",
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        self.log_message("✅ Vision AI کاملاً آماده است")
                        messagebox.showinfo("تست Vision AI", 
                                          f"✅ اتصال موفق!\n"
                                          f"🤖 مدل: {vision_model}\n"
                                          f"🌐 سرور: {settings['url']}\n"
                                          f"📊 تعداد مدل‌ها: {len(models)}")
                    else:
                        self.log_message("⚠️ مدل Vision در دسترس نیست")
                        messagebox.showwarning("تست Vision AI", 
                                             f"⚠️ مدل {vision_model} پاسخ نمی‌دهد")
                else:
                    self.log_message(f"❌ مدل {vision_model} یافت نشد")
                    messagebox.showerror("تست Vision AI", 
                                       f"❌ مدل {vision_model} نصب نیست\n"
                                       f"💡 دستور نصب: ollama pull {vision_model}")
            else:
                self.log_message("❌ سرور Ollama در دسترس نیست")
                messagebox.showerror("تست Vision AI", 
                                   f"❌ سرور Ollama در دسترس نیست\n"
                                   f"🌐 آدرس: {settings['url']}\n"
                                   f"💡 لطفاً Ollama را راه‌اندازی کنید")
                
        except requests.exceptions.ConnectionError:
            self.log_message("❌ خطا در اتصال به Ollama")
            messagebox.showerror("تست Vision AI", 
                               "❌ خطا در اتصال به Ollama\n"
                               "💡 مطمئن شوید Ollama در حال اجرا است")
        except Exception as e:
            self.log_message(f"❌ خطا در تست Vision AI: {e}")
            messagebox.showerror("خطا", f"خطا در تست:\n{e}")
    
    def test_telegram_connection(self):
        """تست اتصال و کنترل تلگرام"""
        try:
            self.log_message("🧪 شروع تست اتصال تلگرام...")
            
            # بررسی وجود فایل تلگرام
            telegram_path = os.getenv('TELEGRAM_PORTABLE_PATH', 'C:/Telegram/Telegram.exe')
            
            if not Path(telegram_path).exists():
                self.log_message(f"❌ فایل تلگرام پیدا نشد: {telegram_path}")
                messagebox.showerror("تست تلگرام", 
                                   f"❌ فایل تلگرام پیدا نشد:\n{telegram_path}\n"
                                   f"💡 مسیر را در فایل .env تنظیم کنید")
                return
            
            # بررسی اجرا بودن تلگرام
            telegram_running = self.telegram_manager.is_telegram_running()
            
            # تست پیدا کردن پنجره
            window_found = self.telegram_manager.find_telegram_window()
            
            # گزارش نتایج
            results = []
            results.append(f"📱 فایل تلگرام: {'✅ موجود' if Path(telegram_path).exists() else '❌ موجود نیست'}")
            results.append(f"🔄 وضعیت اجرا: {'✅ در حال اجرا' if telegram_running else '❌ اجرا نیست'}")
            results.append(f"🖼️ پنجره: {'✅ پیدا شد' if window_found else '❌ پیدا نشد'}")
            
            if telegram_running and window_found:
                # تست فوکوس
                focus_success = self.telegram_manager.focus_telegram()
                results.append(f"🎯 فوکوس: {'✅ موفق' if focus_success else '❌ ناموفق'}")
                
                self.log_message("✅ تلگرام کاملاً آماده است")
                messagebox.showinfo("تست تلگرام", "\n".join(results))
            else:
                self.log_message("⚠️ تلگرام آماده نیست")
                messagebox.showwarning("تست تلگرام", 
                                     "\n".join(results) + 
                                     "\n\n💡 از دکمه 'شروع تلگرام' استفاده کنید")
                
        except Exception as e:
            self.log_message(f"❌ خطا در تست تلگرام: {e}")
            messagebox.showerror("خطا", f"خطا در تست:\n{e}")
    
    def test_chat_scanning(self):
        """تست قابلیت اسکن چت‌ها"""
        try:
            self.log_message("🧪 شروع تست اسکن چت‌ها...")
            
            # بررسی آماده بودن تلگرام
            if not self.telegram_manager.is_telegram_running():
                messagebox.showwarning("تست اسکن", 
                                     "⚠️ ابتدا تلگرام را راه‌اندازی کنید")
                return
            
            # اسکن تستی
            chat_data = self.chat_scanner.scan_chat_list()
            scan_stats = self.chat_scanner.get_scan_statistics()
            
            # نمایش نتایج
            if chat_data and chat_data.get('chats'):
                total_chats = len(chat_data['chats'])
                unread_chats = chat_data.get('unread_chats', 0)
                scan_method = scan_stats.get('scan_method_used', 'نامشخص')
                
                results = [
                    f"✅ اسکن موفق!",
                    f"📊 کل چت‌ها: {total_chats}",
                    f"📨 خوانده نشده: {unread_chats}",
                    f"🔍 روش اسکن: {scan_method}",
                    f"📈 نرخ موفقیت: {scan_stats.get('successful_scans', 0)}/{scan_stats.get('total_scans', 0)}"
                ]
                
                self.log_message(f"✅ تست اسکن موفق: {total_chats} چت، {unread_chats} خوانده نشده")
                messagebox.showinfo("تست اسکن چت‌ها", "\n".join(results))
                
                # آپدیت آمار در GUI
                self.update_live_stats()
            else:
                self.log_message("⚠️ هیچ چتی شناسایی نشد")
                messagebox.showwarning("تست اسکن چت‌ها", 
                                     "⚠️ هیچ چتی شناسایی نشد\n"
                                     "💡 مطمئن شوید:\n"
                                     "- تلگرام باز است\n"
                                     "- در صفحه چت‌ها هستید\n"
                                     "- چت‌های خوانده نشده دارید")
                
        except Exception as e:
            self.log_message(f"❌ خطا در تست اسکن: {e}")
            messagebox.showerror("خطا", f"خطا در تست اسکن:\n{e}")
    
    def start_telegram_manually(self):
        """راه‌اندازی دستی تلگرام"""
        try:
            self.log_message("📱 راه‌اندازی دستی تلگرام...")
            
            if self.telegram_manager.start_telegram():
                self.telegram_manager.maximize_telegram()
                self.log_message("✅ تلگرام با موفقیت راه‌اندازی شد")
                messagebox.showinfo("تلگرام", "✅ تلگرام با موفقیت راه‌اندازی شد")
            else:
                self.log_message("❌ خطا در راه‌اندازی تلگرام")
                messagebox.showerror("خطا", "❌ خطا در راه‌اندازی تلگرام")
                
        except Exception as e:
            self.log_message(f"❌ خطا: {e}")
            messagebox.showerror("خطا", f"خطا در راه‌اندازی:\n{e}")
    
    def focus_telegram_manually(self):
        """فوکوس دستی روی تلگرام"""
        try:
            if self.telegram_manager.focus_telegram():
                self.log_message("✅ فوکوس روی تلگرام")
                messagebox.showinfo("تلگرام", "✅ فوکوس روی تلگرام")
            else:
                self.log_message("❌ نتوانستیم فوکوس کنیم")
                messagebox.showerror("خطا", "❌ نتوانستیم روی تلگرام فوکوس کنیم")
                
        except Exception as e:
            self.log_message(f"❌ خطا: {e}")
            messagebox.showerror("خطا", f"خطا در فوکوس:\n{e}")
    
    def manual_scan_chats(self):
        """اسکن دستی چت‌ها"""
        try:
            self.log_message("🔍 شروع اسکن دستی چت‌ها...")
            
            # اسکن چت‌ها
            unread_chats = self.chat_scanner.find_unread_chats()
            
            if unread_chats:
                self.log_message(f"📨 {len(unread_chats)} چت خوانده نشده پیدا شد")
                
                # نمایش لیست چت‌ها
                chat_names = [chat.get('name', 'نامشخص') for chat in unread_chats[:5]]
                if len(unread_chats) > 5:
                    chat_names.append(f"... و {len(unread_chats) - 5} چت دیگر")
                
                messagebox.showinfo("اسکن چت‌ها", 
                                  f"📨 {len(unread_chats)} چت خوانده نشده:\n\n" + 
                                  "\n".join(f"• {name}" for name in chat_names))
            else:
                self.log_message("📭 هیچ چت خوانده نشده‌ای پیدا نشد")
                messagebox.showinfo("اسکن چت‌ها", 
                                  "📭 هیچ چت خوانده نشده‌ای پیدا نشد\n\n"
                                  "💡 نکات:\n"
                                  "• مطمئن شوید در صفحه چت‌ها هستید\n"
                                  "• چت‌های خوانده نشده داشته باشید\n"
                                  "• تلگرام کاملاً بارگذاری شده باشد")
            
            # آپدیت آمار
            self.update_live_stats()
            
        except Exception as e:
            self.log_message(f"❌ خطا در اسکن دستی: {e}")
            messagebox.showerror("خطا", f"خطا در اسکن:\n{e}")
    
    def start_telegram_manually(self):
        """راه‌اندازی دستی تلگرام"""
        try:
            self.log_message("📱 راه‌اندازی دستی تلگرام...")
            
            if hasattr(self, 'telegram_manager'):
                if self.telegram_manager.start_telegram():
                    self.telegram_manager.maximize_telegram()
                    self.log_message("✅ تلگرام راه‌اندازی شد")
                    messagebox.showinfo("موفق", "✅ تلگرام با موفقیت راه‌اندازی شد!")
                else:
                    self.log_message("❌ خطا در راه‌اندازی تلگرام")
                    messagebox.showerror("خطا", "❌ خطا در راه‌اندازی تلگرام")
            else:
                messagebox.showerror("خطا", "ماژول تلگرام مقداردهی نشده")
                
        except Exception as e:
            self.log_message(f"❌ خطا در راه‌اندازی دستی: {e}")
            messagebox.showerror("خطا", f"خطا در راه‌اندازی:\n{e}")
    
    def focus_telegram_manually(self):
        """فوکوس دستی روی تلگرام"""
        try:
            if hasattr(self, 'telegram_manager'):
                if self.telegram_manager.focus_telegram():
                    self.log_message("✅ فوکوس روی تلگرام")
                    messagebox.showinfo("موفق", "✅ فوکوس روی تلگرام انجام شد")
                else:
                    self.log_message("❌ خطا در فوکوس")
                    messagebox.showerror("خطا", "❌ خطا در فوکوس روی تلگرام")
            else:
                messagebox.showerror("خطا", "ماژول تلگرام مقداردهی نشده")
                
        except Exception as e:
            self.log_message(f"❌ خطا در فوکوس: {e}")
            messagebox.showerror("خطا", f"خطا در فوکوس:\n{e}")
    
    def manual_scan_chats(self):
        """اسکن دستی چت‌ها"""
        try:
            self.log_message("🔍 شروع اسکن دستی چت‌ها...")
            
            if hasattr(self, 'chat_scanner'):
                # اجرای اسکن در thread جداگانه
                def scan_thread():
                    try:
                        unread_chats = self.chat_scanner.find_unread_chats()
                        
                        # نمایش نتایج در GUI thread
                        def show_results():
                            if unread_chats:
                                self.log_message(f"✅ {len(unread_chats)} چت خوانده نشده پیدا شد")
                                
                                # نمایش جزئیات
                                details = "چت‌های خوانده نشده:\n\n"
                                for i, chat in enumerate(unread_chats[:10]):  # نمایش 10 تای اول
                                    details += f"{i+1}. {chat.get('name', 'نامشخص')}\n"
                                
                                if len(unread_chats) > 10:
                                    details += f"\n... و {len(unread_chats) - 10} چت دیگر"
                                
                                messagebox.showinfo("نتیجه اسکن", details)
                            else:
                                self.log_message("📭 هیچ چت خوانده نشده‌ای پیدا نشد")
                                messagebox.showinfo("نتیجه اسکن", "📭 هیچ چت خوانده نشده‌ای پیدا نشد")
                        
                        # اجرای در GUI thread
                        self.root.after(0, show_results)
                        
                    except Exception as e:
                        self.log_message(f"❌ خطا در اسکن: {e}")
                        self.root.after(0, lambda: messagebox.showerror("خطا", f"خطا در اسکن:\n{e}"))
                
                # شروع thread اسکن
                threading.Thread(target=scan_thread, daemon=True).start()
                
            else:
                messagebox.showerror("خطا", "ماژول اسکن مقداردهی نشده")
                
        except Exception as e:
            self.log_message(f"❌ خطا در اسکن دستی: {e}")
            messagebox.showerror("خطا", f"خطا در اسکن:\n{e}")
    
    def run_admin_system(self):
        """حلقه اصلی سیستم ادمین"""
        try:
            self.log_message("🔄 شروع حلقه مدیریت چت‌ها...")
            
            scan_interval = int(os.getenv('SCAN_INTERVAL', '30'))
            
            while self.is_running:
                # اسکن خودکار چت‌ها
                self.auto_scan_and_process_chats()
                
                # بروزرسانی آمار
                self.update_live_stats()
                
                # انتظار
                self.log_message(f"⏳ انتظار {scan_interval} ثانیه تا اسکن بعدی...")
                time.sleep(scan_interval)
                
        except Exception as e:
            self.log_message(f"❌ خطا در سیستم ادمین: {e}")
            self.logger.error(f"خطا در run_admin_system: {e}")
    
    def auto_scan_and_process_chats(self):
        """اسکن خودکار و پردازش چت‌ها"""
        try:
            self.log_message("🔍 شروع اسکن خودکار چت‌ها...")
            
            # اسکن چت‌های خوانده نشده
            unread_chats = self.chat_scanner.find_unread_chats()
            
            if not unread_chats:
                self.log_message("📭 هیچ چت خوانده نشده‌ای پیدا نشد")
                return
            
            self.log_message(f"📨 {len(unread_chats)} چت خوانده نشده پیدا شد")
            
            # محدود کردن تعداد چت‌ها در هر اسکن
            max_chats = int(os.getenv('MAX_CHATS_PER_SCAN', '20'))
            if len(unread_chats) > max_chats:
                unread_chats = unread_chats[:max_chats]
                self.log_message(f"⚡ محدود شده به {max_chats} چت برای بهینه‌سازی")
            
            # پردازش موازی یا sequential
            parallel_enabled = os.getenv('PARALLEL_PROCESSING', 'true').lower() == 'true'
            
            if parallel_enabled:
                self.process_chats_parallel(unread_chats)
            else:
                self.process_chats_sequential(unread_chats)
                
        except Exception as e:
            self.log_message(f"❌ خطا در اسکن خودکار: {e}")
    
    def process_chats_parallel(self, chat_list):
        """پردازش موازی چت‌ها"""
        try:
            self.log_message(f"⚡ شروع پردازش موازی {len(chat_list)} چت")
            
            results = self.parallel_processor.process_chat_batch(chat_list)
            
            # گزارش نتایج
            successful = sum(1 for r in results if r.get('success', False))
            self.log_message(f"✅ پردازش موازی تکمیل: {successful}/{len(results)} موفق")
            
        except Exception as e:
            self.log_message(f"❌ خطا در پردازش موازی: {e}")
    
    def process_chats_sequential(self, chat_list):
        """پردازش ترتیبی چت‌ها"""
        try:
            self.log_message(f"🔄 شروع پردازش ترتیبی {len(chat_list)} چت")
            
            for i, chat in enumerate(chat_list):
                if not self.is_running:
                    break
                
                self.log_message(f"📝 پردازش چت {i+1}/{len(chat_list)}: {chat.get('name', 'نامشخص')}")
                
                # اسکن و پردازش چت
                chat_position = (
                    chat.get('position', {}).get('x', 100),
                    chat.get('position', {}).get('y', 100)
                )
                
                chat_data = self.chat_scanner.scan_single_chat(chat_position)
                
                if chat_data and chat_data.get('unread_messages'):
                    for message in chat_data['unread_messages']:
                        if message.get('needs_response', False):
                            # تولید پاسخ
                            response = self.response_generator.generate_response(
                                message, chat_data['chat_info']
                            )
                            
                            if response:
                                # ارسال پاسخ
                                success = self.telegram_manager.send_message(response)
                                
                                if success:
                                    self.log_message(f"✅ پاسخ ارسال شد: {response[:50]}...")
                                    # ثبت در دیتابیس
                                    self.log_chat_interaction(chat, message, response)
                                else:
                                    self.log_message(f"❌ خطا در ارسال پاسخ")
                                
                                # تاخیر بین پیام‌ها
                                send_delay = float(os.getenv('MESSAGE_SEND_DELAY', '1.5'))
                                time.sleep(send_delay)
                
                # تاخیر بین چت‌ها
                time.sleep(1)
                
        except Exception as e:
            self.log_message(f"❌ خطا در پردازش ترتیبی: {e}")
    
    def process_chat(self, chat_config):
        """پردازش یک چت با قابلیت fallback"""
        screenshot = None
        try:
            # تصویربرداری از چت
            screenshot = self.capture_chat_screen()
            if not screenshot:
                self.log_message("⚠️ خطا در تصویربرداری - استفاده از حالت fallback")
                self.process_chat_fallback(chat_config)
                return
            
            # تحلیل پیام‌ها با Vision AI
            messages = self.analyze_chat_messages(screenshot, chat_config)
            
            # اگر Vision AI ناموفق بود، از حالت fallback استفاده کن
            if not messages:
                self.log_message("🔄 Vision AI ناموفق - تغییر به حالت fallback")
                self.process_chat_fallback(chat_config)
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
            self.log_message("🔄 تغییر به حالت fallback")
            self.process_chat_fallback(chat_config)
        finally:
            # پاک کردن فایل موقت
            if screenshot:
                self.cleanup_screenshot(screenshot)
    
    def process_chat_fallback(self, chat_config):
        """حالت fallback برای زمانی که Vision AI کار نمی‌کند"""
        try:
            # آپدیت وضعیت GUI
            self.fallback_status_var.set("🔄 Fallback Mode")
            self.fallback_status_label.config(fg=self.colors['warning'])
            
            # بررسی فعال بودن fallback
            fallback_enabled = os.getenv('FALLBACK_ENABLED', 'true').lower() == 'true'
            if not fallback_enabled:
                self.log_message("⚠️ Fallback غیرفعال است")
                return
                
            self.log_message("🔄 حالت Fallback فعال - پاسخ‌دهی ساده")
            
            # تولید پاسخ کلی بر اساس تنظیمات چت
            fallback_message = {
                "content": "پیام عمومی در چت",
                "type": "general",
                "priority": "متوسط", 
                "sender": "unknown"
            }
            
            # پاسخ‌های از پیش تعریف شده
            fallback_responses = [
                "سلام دوست عزیز! 👋 در خدمت شما هستم",
                "ممنون که با ما در ارتباط هستید 🙏",
                "سوال یا درخواستی دارید؟ خوشحال می‌شوم کمکتان کنم 😊",
                "در صورت نیاز به راهنمایی، در خدمت شما هستیم ✨",
                "امیدوارم روز خوبی داشته باشید! 🌟",
                "چطور می‌تونم بهتون کمک کنم؟ 🤝",
                "سلام! آماده پاسخگویی به سوالات شما هستم 💬"
            ]
            
            import random
            response = random.choice(fallback_responses)
            
            # تاخیر طبیعی بر اساس تنظیمات
            delay_min = float(os.getenv('FALLBACK_DELAY_MIN', '2'))
            delay_max = float(os.getenv('FALLBACK_DELAY_MAX', '5'))
            time.sleep(random.uniform(delay_min, delay_max))
            
            self.send_response(response, chat_config)
            self.log_chat_interaction(chat_config, fallback_message, response)
            
            self.log_message("✅ پاسخ fallback ارسال شد")
            
            # بازگشت به حالت عادی
            self.fallback_status_var.set("✅ Vision AI")
            self.fallback_status_label.config(fg=self.colors['success'])
            
        except Exception as e:
            self.log_message(f"❌ خطا در حالت fallback: {e}")
            self.fallback_status_var.set("❌ خطا")
            self.fallback_status_label.config(fg=self.colors['danger'])
    
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
        settings = self.get_ollama_settings()
        
        for attempt in range(settings['retry_attempts']):
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

                self.log_message(f"🔍 تحلیل Vision - تلاش {attempt + 1}/{settings['retry_attempts']}")
                
                response = requests.post(
                    f"{settings['url']}/api/generate",
                    json={
                        "model": settings['vision_model'],
                        "prompt": prompt,
                        "images": [image_data],
                        "stream": False,
                        "options": {"temperature": 0.3}
                    },
                    timeout=settings['vision_timeout']
                )
                
                if response.status_code == 200:
                    result = response.json().get('response', '').strip()
                    self.log_message(f"✅ Vision تحلیل موفق - تلاش {attempt + 1}")
                    if result != "NO_NEW_MESSAGES":
                        try:
                            return json.loads(result).get('new_messages', [])
                        except:
                            return [{"content": result, "type": "unknown", "priority": "متوسط", "sender": "unknown"}]
                    return []
                else:
                    self.log_message(f"⚠️ خطا در Vision API - کد {response.status_code}")
                    
            except requests.exceptions.Timeout:
                wait_time = 2 ** attempt  # Exponential backoff
                self.log_message(f"⏰ Timeout در Vision - تلاش {attempt + 1}, انتظار {wait_time}s")
                if attempt < settings['retry_attempts'] - 1:
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.log_message(f"❌ خطا در تحلیل Vision تلاش {attempt + 1}: {e}")
                if attempt < settings['retry_attempts'] - 1:
                    time.sleep(1)
        
        self.log_message(f"❌ Vision ناموفق پس از {settings['retry_attempts']} تلاش")
        return []
    
    def cleanup_screenshot(self, screenshot_path):
        """پاک کردن فایل موقت اسکرین‌شات"""
        try:
            if screenshot_path and screenshot_path.exists():
                screenshot_path.unlink()
        except Exception as e:
            self.log_message(f"⚠️ خطا در پاک کردن فایل موقت: {e}")
    
    def generate_intelligent_response(self, message, chat_config):
        """تولید پاسخ هوشمند با قابلیت تلاش مجدد"""
        settings = self.get_ollama_settings()
        
        for attempt in range(settings['retry_attempts']):
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

                self.log_message(f"🤖 تولید پاسخ - تلاش {attempt + 1}/{settings['retry_attempts']}")
                
                response = requests.post(
                    f"{settings['url']}/api/generate",
                    json={
                        "model": settings['text_model'],
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": self.config['response_settings']['max_message_length']
                        }
                    },
                    timeout=settings['timeout']
                )
                
                if response.status_code == 200:
                    result = response.json().get('response', '').strip()
                    self.log_message(f"✅ پاسخ تولید شد - تلاش {attempt + 1}")
                    return result
                else:
                    self.log_message(f"⚠️ خطا در Text API - کد {response.status_code}")
                    
            except requests.exceptions.Timeout:
                wait_time = 2 ** attempt
                self.log_message(f"⏰ Timeout در تولید پاسخ - تلاش {attempt + 1}, انتظار {wait_time}s")
                if attempt < settings['retry_attempts'] - 1:
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.log_message(f"❌ خطا در تولید پاسخ تلاش {attempt + 1}: {e}")
                if attempt < settings['retry_attempts'] - 1:
                    time.sleep(1)
        
        self.log_message(f"❌ تولید پاسخ ناموفق پس از {settings['retry_attempts']} تلاش")
        return "متأسفانه در حال حاضر امکان پاسخ‌دهی وجود ندارد"
    
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
            active_chats = len(self.active_sessions) if hasattr(self, 'active_sessions') else 0
            self.active_chats_var.set(str(active_chats))
            
            # کل پیام‌های امروز
            cursor.execute('''
                SELECT COUNT(*) FROM message_logs 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            total_messages = cursor.fetchone()[0]
            self.total_messages_var.set(str(total_messages))
            
            # پیام‌های ارسالی موفق امروز
            cursor.execute('''
                SELECT COUNT(*) FROM message_logs 
                WHERE DATE(timestamp) = DATE('now') AND success = 1
            ''')
            sent_messages = cursor.fetchone()[0]
            self.sent_messages_var.set(str(sent_messages))
            
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
            
            # آمار اسکن چت‌ها
            if hasattr(self, 'chat_scanner'):
                scan_stats = self.chat_scanner.get_scan_statistics()
                
                # چت‌های خوانده نشده
                self.unread_chats_var.set(str(scan_stats.get('unread_chats', 0)))
                
                # نرخ موفقیت اسکن
                total_scans = scan_stats.get('total_scans', 0)
                successful_scans = scan_stats.get('successful_scans', 0)
                if total_scans > 0:
                    scan_success_rate = (successful_scans / total_scans) * 100
                    self.scan_success_rate_var.set(f"{scan_success_rate:.1f}%")
                else:
                    self.scan_success_rate_var.set("0%")
                
                # آخرین زمان اسکن
                last_scan = scan_stats.get('last_scan_time')
                if last_scan:
                    import datetime
                    last_time = datetime.datetime.fromtimestamp(last_scan)
                    self.last_scan_time_var.set(last_time.strftime("%H:%M:%S"))
                else:
                    self.last_scan_time_var.set("هرگز")
                
                # روش اسکن
                scan_method = scan_stats.get('scan_method_used', 'none')
                method_display = {
                    'vision_ai': '🤖 Vision AI',
                    'ocr': '👁️ OCR',
                    'failed': '❌ ناموفق',
                    'none': '⏸️ هیچ'
                }.get(scan_method, scan_method)
                self.scan_method_var.set(method_display)
            
            # آمار پردازش موازی
            if hasattr(self, 'parallel_processor'):
                parallel_stats = self.parallel_processor.get_statistics()
                
                # میانگین زمان پاسخ
                avg_time = parallel_stats.get('avg_response_time', 0)
                self.avg_response_time_var.set(f"{avg_time:.1f}s")
            
        except Exception as e:
            self.logger.error(f"خطا در بروزرسانی آمار: {e}")
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
