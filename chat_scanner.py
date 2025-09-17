#!/usr/bin/env python3
"""
🔍 Chat Scanner & Analyzer - اسکنر و تحلیلگر چت‌ها
ماژول تحلیل خودکار چت‌های تلگرام با Vision AI
"""

import json
import time
import base64
import requests
from pathlib import Path
import logging
from PIL import Image
import cv2
import numpy as np

# اضافه کردن OCR
try:
    import pytesseract
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class ChatScanner:
    """اسکنر خودکار چت‌ها"""
    
    def __init__(self, config, telegram_manager):
        self.config = config
        self.telegram_manager = telegram_manager
        self.detected_chats = []
        self.processed_chats = set()
        
        # لاگ
        self.logger = logging.getLogger("ChatScanner")
        
        # آمار اسکن
        self.scan_stats = {
            'total_scans': 0,
            'successful_scans': 0,
            'chats_found': 0,
            'unread_chats': 0,
            'last_scan_time': None,
            'scan_method_used': 'none'
        }
        
        # تنظیمات OCR
        self.ocr_reader = None
        if OCR_AVAILABLE:
            try:
                self.ocr_reader = easyocr.Reader(['en', 'fa'])  # انگلیسی و فارسی
                self.logger.info("✅ OCR Reader آماده شد")
            except Exception as e:
                self.logger.warning(f"⚠️ خطا در آماده‌سازی OCR: {e}")
    
    def scan_chat_list(self):
        """اسکن کامل لیست چت‌ها"""
        try:
            self.logger.info("🔍 شروع اسکن لیست چت‌ها...")
            self.scan_stats['total_scans'] += 1
            self.scan_stats['last_scan_time'] = time.time()
            
            # رفتن به لیست چت‌ها
            if not self.telegram_manager.navigate_to_chat_list():
                self.logger.error("❌ نتوانستیم به لیست چت‌ها برویم")
                return []
            
            # گرفتن اسکرین‌شات از لیست چت‌ها
            chat_region = self.telegram_manager.get_chat_list_region()
            screenshot = self.telegram_manager.take_screenshot(region=chat_region)
            
            if not screenshot:
                self.logger.error("❌ نتوانستیم اسکرین‌شات بگیریم")
                return []
            
            # ذخیره اسکرین‌شات برای تحلیل
            screenshot_path = self.save_screenshot(screenshot, "chat_list")
            
            # تحلیل ترکیبی: Vision AI + OCR
            chat_data = self.analyze_chat_list_hybrid(screenshot_path)
            
            # آپدیت آمار
            if chat_data and chat_data.get('chats'):
                self.scan_stats['successful_scans'] += 1
                self.scan_stats['chats_found'] = len(chat_data['chats'])
                self.scan_stats['unread_chats'] = chat_data.get('unread_chats', 0)
            
            self.logger.info(f"✅ {len(chat_data.get('chats', []))} چت شناسایی شد")
            return chat_data
            
        except Exception as e:
            self.logger.error(f"❌ خطا در اسکن چت‌ها: {e}")
            return []
    
    def analyze_chat_list_with_vision(self, screenshot_path):
        """تحلیل لیست چت‌ها با Vision AI"""
        try:
            with open(screenshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = """تو یک تحلیلگر هوشمند تلگرام هستی. این تصویر از لیست چت‌های تلگرام است.

وظایف:
1. همه چت‌ها و گروه‌های موجود را شناسایی کن
2. وضعیت هر چت را مشخص کن (خوانده نشده، آنلاین، آفلاین)
3. موقعیت تقریبی هر چت در صفحه را تشخیص بده
4. نوع چت (شخصی، گروه، کانال) را مشخص کن

فرمت پاسخ JSON:
{
  "chats": [
    {
      "name": "نام چت",
      "type": "private/group/channel", 
      "status": "unread/read/online/offline",
      "position": {"x": 100, "y": 200},
      "has_unread": true/false,
      "unread_count": عدد یا null,
      "last_message_preview": "پیش‌نمایش آخرین پیام"
    }
  ],
  "total_chats": عدد,
  "unread_chats": عدد
}

فقط JSON برگردان، هیچ توضیح اضافی نیاز نیست."""

            settings = self._get_ollama_settings()
            
            response = requests.post(
                f"{settings['url']}/api/generate",
                json={
                    "model": settings['vision_model'],
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=settings['vision_timeout']
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    self.logger.warning("⚠️ پاسخ Vision AI قابل parse نیست")
                    return {"chats": [], "total_chats": 0, "unread_chats": 0}
            else:
                self.logger.error(f"❌ خطا در Vision API: {response.status_code}")
                return {"chats": [], "total_chats": 0, "unread_chats": 0}
                
        except Exception as e:
            self.logger.error(f"❌ خطا در تحلیل Vision: {e}")
            return {"chats": [], "total_chats": 0, "unread_chats": 0}
    
    def analyze_chat_list_hybrid(self, screenshot_path):
        """تحلیل ترکیبی لیست چت‌ها: Vision AI + OCR"""
        try:
            self.logger.info("🧠 شروع تحلیل ترکیبی چت‌ها...")
            
            # ابتدا سعی با Vision AI
            self.logger.info("🔮 تلاش با Vision AI...")
            self.scan_stats['scan_method_used'] = 'vision_ai'
            vision_result = self.analyze_chat_list_with_vision(screenshot_path)
            
            # اگر Vision AI موفق بود و چت پیدا کرد
            if vision_result and vision_result.get('chats') and len(vision_result['chats']) > 0:
                self.logger.info(f"✅ Vision AI موفق: {len(vision_result['chats'])} چت")
                return vision_result
            
            # اگر Vision AI ناموفق بود، از OCR استفاده کن
            self.logger.info("🔄 Vision AI ناموفق، تلاش با OCR...")
            self.scan_stats['scan_method_used'] = 'ocr'
            ocr_result = self.analyze_chat_list_with_ocr(screenshot_path)
            
            if ocr_result and ocr_result.get('chats') and len(ocr_result['chats']) > 0:
                self.logger.info(f"✅ OCR موفق: {len(ocr_result['chats'])} چت")
                return ocr_result
            
            # اگر هیچکدام موفق نبود
            self.logger.warning("⚠️ هیچ چتی با هیچ روشی شناسایی نشد")
            self.scan_stats['scan_method_used'] = 'failed'
            return {"chats": [], "total_chats": 0, "unread_chats": 0}
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تحلیل ترکیبی: {e}")
            return {"chats": [], "total_chats": 0, "unread_chats": 0}
    
    def scan_single_chat(self, chat_position):
        """اسکن یک چت خاص"""
        try:
            # کلیک روی چت
            if not self.telegram_manager.click_on_chat(chat_position):
                return None
            
            # کمی صبر تا چت بارگذاری شود
            time.sleep(2)
            
            # گرفتن اسکرین‌شات از چت
            screenshot = self.telegram_manager.take_screenshot()
            if not screenshot:
                return None
            
            # ذخیره و تحلیل
            screenshot_path = self.save_screenshot(screenshot, "single_chat")
            return self.analyze_single_chat_with_vision(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"❌ خطا در اسکن چت: {e}")
            return None
    
    def analyze_single_chat_with_vision(self, screenshot_path):
        """تحلیل یک چت با Vision AI"""
        try:
            with open(screenshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = """تو یک ادمین هوشمند تلگرام هستی. این تصویر از یک چت باز شده است.

وظایف:
1. آخرین پیام‌های چت را بخوان
2. پیام‌های خوانده نشده را شناسایی کن
3. نوع پیام‌ها را تشخیص بده (سوال، درخواست، شکایت، تشکر، عادی)
4. اولویت پاسخ‌دهی را مشخص کن
5. وضعیت چت (آنلاین/آفلاین کاربر) را بگو

فرمت پاسخ JSON:
{
  "chat_info": {
    "name": "نام چت",
    "type": "private/group",
    "user_status": "online/offline/last_seen",
    "is_typing": true/false
  },
  "unread_messages": [
    {
      "content": "متن پیام",
      "sender": "نام فرستنده",
      "type": "question/request/complaint/thanks/normal",
      "priority": "high/medium/low",
      "timestamp": "زمان تقریبی",
      "needs_response": true/false
    }
  ],
  "message_input_ready": true/false,
  "can_type": true/false
}

فقط JSON برگردان."""

            settings = self._get_ollama_settings()
            
            response = requests.post(
                f"{settings['url']}/api/generate",
                json={
                    "model": settings['vision_model'],
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=settings['vision_timeout']
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تحلیل چت: {e}")
            return None
    
    def find_unread_chats(self):
        """پیدا کردن چت‌های خوانده نشده"""
        try:
            chat_data = self.scan_chat_list()
            if not chat_data:
                return []

            unread_chats = []
            for chat in chat_data.get('chats', []):
                if chat.get('has_unread', False):
                    unread_chats.append(chat)

            self.logger.info(f"📨 {len(unread_chats)} چت خوانده نشده پیدا شد")
            return unread_chats
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پیدا کردن چت‌های خوانده نشده: {e}")
            return []
    
    def analyze_chat_list_with_ocr(self, screenshot_path):
        """تحلیل لیست چت‌ها با OCR"""
        try:
            if not OCR_AVAILABLE or not self.ocr_reader:
                self.logger.warning("⚠️ OCR در دسترس نیست")
                return {"chats": [], "total_chats": 0, "unread_chats": 0}
            
            self.logger.info("👁️ تحلیل با OCR...")
            
            # خواندن تصویر
            image = cv2.imread(str(screenshot_path))
            if image is None:
                return {"chats": [], "total_chats": 0, "unread_chats": 0}
            
            # استخراج متن با EasyOCR
            results = self.ocr_reader.readtext(image)
            
            # پردازش نتایج OCR
            detected_chats = []
            unread_count = 0
            
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # اطمینان بالا
                    # تشخیص نشانه‌های چت خوانده نشده
                    has_unread = self._detect_unread_indicators(text, bbox, image)
                    
                    if self._is_likely_chat_name(text):
                        chat_info = {
                            "name": text.strip(),
                            "type": "private",  # پیش‌فرض
                            "status": "unread" if has_unread else "read",
                            "position": {
                                "x": int((bbox[0][0] + bbox[2][0]) / 2),
                                "y": int((bbox[0][1] + bbox[2][1]) / 2)
                            },
                            "has_unread": has_unread,
                            "unread_count": 1 if has_unread else 0,
                            "last_message_preview": "",
                            "confidence": confidence
                        }
                        detected_chats.append(chat_info)
                        
                        if has_unread:
                            unread_count += 1
            
            self.logger.info(f"📊 OCR یافت: {len(detected_chats)} چت، {unread_count} خوانده نشده")
            
            return {
                "chats": detected_chats,
                "total_chats": len(detected_chats),
                "unread_chats": unread_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطا در OCR: {e}")
            return {"chats": [], "total_chats": 0, "unread_chats": 0}
    
    def _detect_unread_indicators(self, text, bbox, image):
        """تشخیص نشانه‌های پیام خوانده نشده"""
        try:
            # بررسی متنی
            unread_keywords = ['unread', 'new', 'جدید', 'خوانده نشده']
            if any(keyword in text.lower() for keyword in unread_keywords):
                return True
            
            # بررسی رنگی (نقطه سبز یا آبی)
            x1, y1 = int(bbox[0][0]), int(bbox[0][1])
            x2, y2 = int(bbox[2][0]), int(bbox[2][1])
            
            # منطقه کوچک کنار متن برای چک کردن نقطه رنگی
            region = image[max(0, y1-10):min(image.shape[0], y2+10), 
                          max(0, x1-30):min(image.shape[1], x2+30)]
            
            # تبدیل به HSV برای تشخیص رنگ
            hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            
            # ماسک برای رنگ سبز (نشانه خوانده نشده)
            green_lower = np.array([40, 50, 50])
            green_upper = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            # ماسک برای رنگ آبی
            blue_lower = np.array([100, 50, 50])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # اگر نقطه رنگی پیدا شد
            if cv2.countNonZero(green_mask) > 5 or cv2.countNonZero(blue_mask) > 5:
                return True
                
            return False
            
        except Exception as e:
            return False
    
    def _is_likely_chat_name(self, text):
        """تشخیص اینکه متن احتمالاً نام چت است"""
        # فیلتر کردن متن‌های غیرمرتبط
        if len(text.strip()) < 2:
            return False
        
        # حذف متن‌هایی که احتمالاً UI هستند
        ui_elements = ['telegram', 'search', 'settings', 'menu', 'chat', 'جستجو', 'تنظیمات', 'منو']
        if any(element in text.lower() for element in ui_elements):
            return False
        
        # بررسی طول مناسب
        if len(text) > 50:  # اسم چت خیلی طولانی
            return False
        
        return True
    
    def scroll_and_scan(self, max_scrolls=5):
        """اسکرول و اسکن کامل لیست چت‌ها"""
        try:
            all_chats = []
            
            for scroll_count in range(max_scrolls):
                self.logger.info(f"🔄 اسکرول {scroll_count + 1}/{max_scrolls}")
                
                # اسکن صفحه فعلی
                current_chats = self.scan_chat_list()
                if current_chats and current_chats.get('chats'):
                    all_chats.extend(current_chats['chats'])
                
                # اسکرول به پایین
                if scroll_count < max_scrolls - 1:
                    self.telegram_manager.scroll_chat_list('down', 3)
                    time.sleep(1)
            
            # حذف تکراری‌ها
            unique_chats = self._remove_duplicate_chats(all_chats)
            
            self.logger.info(f"✅ در کل {len(unique_chats)} چت یکتا پیدا شد")
            return unique_chats
            
        except Exception as e:
            self.logger.error(f"❌ خطا در اسکرول و اسکن: {e}")
            return []
    
    def _remove_duplicate_chats(self, chats):
        """حذف چت‌های تکراری"""
        seen_names = set()
        unique_chats = []
        
        for chat in chats:
            name = chat.get('name', '').strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_chats.append(chat)
        
        return unique_chats
    
    def save_screenshot(self, screenshot, prefix="screenshot"):
        """ذخیره اسکرین‌شات"""
        try:
            timestamp = int(time.time())
            filename = f"{prefix}_{timestamp}.png"
            filepath = Path(__file__).parent / filename
            
            screenshot.save(filepath)
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ خطا در ذخیره اسکرین‌شات: {e}")
            return None
    
    def _get_ollama_settings(self):
        """تنظیمات Ollama"""
        return {
            'url': self.config.get('ollama_url', 'http://127.0.0.1:11434'),
            'vision_model': self.config.get('vision_model', 'llava'),
            'vision_timeout': self.config.get('vision_timeout', 180)
        }
    
    def detect_chat_regions(self, screenshot_path):
        """تشخیص مناطق چت با پردازش تصویر"""
        try:
            # خواندن تصویر
            image = cv2.imread(str(screenshot_path))
            if image is None:
                return []
            
            # تبدیل به grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # تشخیص لبه‌ها
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # پیدا کردن contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # فیلتر کردن contours مناسب برای چت‌ها
            chat_regions = []
            height, width = gray.shape
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # فیلتر اندازه (چت‌ها باید عرض و ارتفاع مناسب داشته باشند)
                if w > width * 0.15 and h > 30 and h < 150:
                    chat_regions.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    })
            
            return chat_regions
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تشخیص مناطق چت: {e}")
            return []
    
    def get_scan_statistics(self):
        """گرفتن آمار اسکن"""
        return self.scan_stats.copy()
    
    def reset_statistics(self):
        """ریست کردن آمار"""
        self.scan_stats = {
            'total_scans': 0,
            'successful_scans': 0,
            'chats_found': 0,
            'unread_chats': 0,
            'last_scan_time': None,
            'scan_method_used': 'none'
        }
