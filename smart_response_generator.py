#!/usr/bin/env python3
"""
🧠 Smart Response Generator - تولیدکننده پاسخ هوشمند
ماژول تولید پاسخ‌های طبیعی و متناسب برای چت‌های مختلف
"""

import json
import time
import requests
import random
import logging
from datetime import datetime

class SmartResponseGenerator:
    """تولیدکننده پاسخ هوشمند"""
    
    def __init__(self, config):
        self.config = config
        self.response_history = {}
        self.user_profiles = {}
        
        # لاگ
        self.logger = logging.getLogger("SmartResponseGenerator")
        
        # قالب‌های پاسخ
        self.response_templates = self._load_response_templates()
    
    def generate_response(self, message_data, chat_info):
        """تولید پاسخ هوشمند"""
        try:
            message_content = message_data.get('content', '')
            message_type = message_data.get('type', 'normal')
            sender = message_data.get('sender', 'کاربر')
            
            self.logger.info(f"🧠 تولید پاسخ برای: {message_content[:50]}...")
            
            # تشخیص نوع پاسخ مورد نیاز
            response_type = self._determine_response_type(message_data, chat_info)
            
            # تولید پاسخ با AI
            ai_response = self._generate_ai_response(message_data, chat_info, response_type)
            
            if ai_response:
                # شخصی‌سازی پاسخ
                personalized_response = self._personalize_response(ai_response, chat_info, sender)
                
                # ذخیره در تاریخچه
                self._save_to_history(chat_info.get('name', ''), message_content, personalized_response)
                
                return personalized_response
            else:
                # استفاده از پاسخ fallback
                return self._get_fallback_response(message_type, sender)
                
        except Exception as e:
            self.logger.error(f"❌ خطا در تولید پاسخ: {e}")
            return self._get_emergency_response()
    
    def _determine_response_type(self, message_data, chat_info):
        """تشخیص نوع پاسخ"""
        message_type = message_data.get('type', 'normal')
        priority = message_data.get('priority', 'medium')
        
        if message_type == 'question':
            return 'informative'
        elif message_type == 'request':
            return 'helpful'
        elif message_type == 'complaint':
            return 'supportive'
        elif message_type == 'thanks':
            return 'appreciative'
        else:
            return 'friendly'
    
    def _generate_ai_response(self, message_data, chat_info, response_type):
        """تولید پاسخ با هوش مصنوعی"""
        try:
            # ساخت prompt پیشرفته
            prompt = self._build_advanced_prompt(message_data, chat_info, response_type)
            
            settings = self._get_ollama_settings()
            
            response = requests.post(
                f"{settings['url']}/api/generate",
                json={
                    "model": settings['text_model'],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                },
                timeout=settings['text_timeout']
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                
                # پردازش و بهبود پاسخ
                improved_response = self._improve_response(result)
                
                return improved_response
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تولید AI: {e}")
            return None
    
    def _build_advanced_prompt(self, message_data, chat_info, response_type):
        """ساخت prompt پیشرفته"""
        
        # اطلاعات پایه
        message_content = message_data.get('content', '')
        sender = message_data.get('sender', 'کاربر')
        chat_name = chat_info.get('name', 'چت')
        chat_type = chat_info.get('type', 'private')
        
        # تاریخچه چت
        history_context = self._get_chat_history_context(chat_name)
        
        # زمان فعلی
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""تو یک ادمین باهوش و دوستانه هستی که در {chat_name} فعالیت می‌کنی.

اطلاعات چت:
- نوع چت: {chat_type}
- فرستنده: {sender}
- زمان: {current_time}
- نوع پاسخ مورد نیاز: {response_type}

پیام دریافتی:
"{message_content}"

{history_context}

راهنمای پاسخ‌دهی:
- پاسخ کوتاه و مفید باشد (حداکثر 2 خط)
- لحن دوستانه و حرفه‌ای
- از ایموجی مناسب استفاده کن
- مستقیم به موضوع پاسخ بده
- اگر سوال فنی است، راهنمایی عملی بده
- اگر تشکر است، خوشحالی نشان بده
- اگر شکایت است، همدردی و حمایت کن

فقط متن پاسخ را بنویس، هیچ توضیح اضافی نداده."""

        return prompt
    
    def _get_chat_history_context(self, chat_name):
        """گرفتن زمینه تاریخچه چت"""
        if chat_name in self.response_history:
            recent_messages = self.response_history[chat_name][-3:]  # آخرین 3 پیام
            if recent_messages:
                context = "تاریخچه اخیر:\n"
                for msg in recent_messages:
                    context += f"- {msg['message'][:50]}... → {msg['response'][:50]}...\n"
                return context
        return ""
    
    def _improve_response(self, response):
        """بهبود و پالایش پاسخ"""
        # حذف کاراکترهای اضافی
        response = response.strip()
        
        # حذف نقل قول‌های اضافی
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        # اضافه کردن ایموجی اگر نداشت
        if not any(char in response for char in ['😊', '😄', '👍', '🙏', '❤️', '🌟', '✨']):
            response = self._add_appropriate_emoji(response)
        
        return response
    
    def _add_appropriate_emoji(self, response):
        """اضافه کردن ایموجی مناسب"""
        # ایموجی بر اساس محتوای پاسخ
        if any(word in response for word in ['ممنون', 'متشکر', 'سپاس']):
            return response + " 🙏"
        elif any(word in response for word in ['خوشحال', 'خوب', 'عالی']):
            return response + " 😊"
        elif any(word in response for word in ['کمک', 'راهنمایی']):
            return response + " 🤝"
        elif any(word in response for word in ['موفق', 'بهتر']):
            return response + " ✨"
        else:
            return response + " 😊"
    
    def _personalize_response(self, response, chat_info, sender):
        """شخصی‌سازی پاسخ"""
        try:
            chat_type = chat_info.get('type', 'private')
            
            # شخصی‌سازی بر اساس نوع چت
            if chat_type == 'group':
                # در گروه‌ها اسم فرد را اضافه کن
                if sender and sender != 'کاربر':
                    response = f"{sender.split()[0]} عزیز، {response}"
            
            # اضافه کردن تنوع
            response = self._add_variation(response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ خطا در شخصی‌سازی: {e}")
            return response
    
    def _add_variation(self, response):
        """اضافه کردن تنوع به پاسخ"""
        # واژه‌های مترادف
        variations = {
            'سلام': ['سلام', 'درود', 'احوال'],
            'ممنون': ['ممنون', 'متشکرم', 'سپاس'],
            'خوشحالم': ['خوشحالم', 'خوشوقتم', 'مسرورم'],
            'کمک': ['کمک', 'راهنمایی', 'یاری']
        }
        
        for original, alternatives in variations.items():
            if original in response:
                replacement = random.choice(alternatives)
                response = response.replace(original, replacement, 1)
                break
        
        return response
    
    def _get_fallback_response(self, message_type, sender):
        """پاسخ fallback"""
        responses = self.response_templates.get(message_type, self.response_templates['normal'])
        selected_response = random.choice(responses)
        
        # شخصی‌سازی ساده
        if '{sender}' in selected_response and sender:
            selected_response = selected_response.replace('{sender}', sender.split()[0])
        
        return selected_response
    
    def _get_emergency_response(self):
        """پاسخ اضطراری"""
        emergency_responses = [
            "سلام! 👋 در خدمت شما هستم",
            "ممنون که با ما در ارتباط هستید 🙏",
            "چطور می‌تونم کمکتان کنم؟ 😊"
        ]
        return random.choice(emergency_responses)
    
    def _save_to_history(self, chat_name, message, response):
        """ذخیره در تاریخچه"""
        try:
            if chat_name not in self.response_history:
                self.response_history[chat_name] = []
            
            self.response_history[chat_name].append({
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'response': response
            })
            
            # نگه داری فقط 50 پیام آخر
            if len(self.response_history[chat_name]) > 50:
                self.response_history[chat_name] = self.response_history[chat_name][-50:]
                
        except Exception as e:
            self.logger.error(f"❌ خطا در ذخیره تاریخچه: {e}")
    
    def _load_response_templates(self):
        """بارگذاری قالب‌های پاسخ"""
        return {
            'question': [
                "این سوال جالبی است! 🤔 بگذارید کمکتان کنم",
                "خوشحالم که سوال کردید 😊 پاسخ شما:",
                "سوال خوبی پرسیدید! 👍 اینطور فکر می‌کنم:",
            ],
            'request': [
                "حتماً! 😊 کمکتان می‌کنم",
                "البته که می‌تونم کمک کنم 🤝",
                "با کمال میل! ✨ این کار رو انجام می‌دم",
            ],
            'complaint': [
                "متأسفم که این مشکل پیش اومده 😔 کمکتان می‌کنم",
                "درک می‌کنم و همدردی می‌کنم 🙏 بیاید حلش کنیم",
                "ببخشید که ناراحت شدید 😞 سعی می‌کنم حل کنم",
            ],
            'thanks': [
                "قابل نداشت! 😊 همیشه در خدمتم",
                "خوشحالم که تونستم کمک کنم 🌟",
                "هر وقت نیاز داشتید در خدمتم 🙏",
            ],
            'normal': [
                "سلام! 👋 چطور می‌تونم کمکتان کنم؟",
                "در خدمت شما هستم 😊",
                "خوشحالم که با ما در ارتباط هستید 🌟",
            ]
        }
    
    def _get_ollama_settings(self):
        """تنظیمات Ollama"""
        return {
            'url': self.config.get('ollama_url', 'http://127.0.0.1:11434'),
            'text_model': self.config.get('text_model', 'llama3.1:8b'),
            'text_timeout': self.config.get('text_timeout', 60)
        }
    
    def get_response_statistics(self):
        """آمار پاسخ‌دهی"""
        total_chats = len(self.response_history)
        total_responses = sum(len(messages) for messages in self.response_history.values())
        
        return {
            'total_chats': total_chats,
            'total_responses': total_responses,
            'avg_responses_per_chat': total_responses / max(total_chats, 1)
        }
