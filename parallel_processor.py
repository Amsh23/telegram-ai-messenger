#!/usr/bin/env python3
"""
⚡ Parallel Processor - پردازشگر موازی
ماژول پردازش همزمان چندین چت با کارایی بالا
"""

import threading
import queue
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ChatTask:
    """وظیفه پردازش چت"""
    chat_info: Dict[str, Any]
    message_data: Dict[str, Any]
    priority: str = 'medium'
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class ParallelProcessor:
    """پردازشگر موازی چت‌ها"""
    
    def __init__(self, config, telegram_manager, chat_scanner, response_generator):
        self.config = config
        self.telegram_manager = telegram_manager
        self.chat_scanner = chat_scanner
        self.response_generator = response_generator
        
        # تنظیمات پردازش موازی
        self.max_workers = int(config.get('max_worker_threads', 3))
        self.queue_size = int(config.get('queue_size', 100))
        self.batch_size = int(config.get('batch_size', 5))
        
        # صف‌های کاری
        self.high_priority_queue = queue.PriorityQueue(maxsize=self.queue_size)
        self.medium_priority_queue = queue.PriorityQueue(maxsize=self.queue_size)
        self.low_priority_queue = queue.PriorityQueue(maxsize=self.queue_size)
        
        # کنترل thread ها
        self.is_running = False
        self.worker_threads = []
        self.stats_lock = threading.Lock()
        
        # آمارها
        self.stats = {
            'processed_chats': 0,
            'sent_messages': 0,
            'failed_tasks': 0,
            'avg_response_time': 0,
            'active_workers': 0
        }
        
        # لاگ
        self.logger = logging.getLogger("ParallelProcessor")
    
    def start(self):
        """شروع پردازش موازی"""
        try:
            self.is_running = True
            self.logger.info(f"🚀 شروع پردازش موازی با {self.max_workers} worker")
            
            # ایجاد worker threads
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    name=f"Worker-{i+1}",
                    daemon=True
                )
                worker.start()
                self.worker_threads.append(worker)
            
            # Thread مانیتورینگ
            monitor_thread = threading.Thread(
                target=self._monitor_loop,
                name="Monitor",
                daemon=True
            )
            monitor_thread.start()
            
            self.logger.info("✅ پردازش موازی شروع شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در شروع پردازش موازی: {e}")
            return False
    
    def stop(self):
        """توقف پردازش موازی"""
        try:
            self.is_running = False
            self.logger.info("🛑 توقف پردازش موازی...")
            
            # انتظار برای اتمام worker ها
            for worker in self.worker_threads:
                worker.join(timeout=5)
            
            self.logger.info("✅ پردازش موازی متوقف شد")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در توقف: {e}")
            return False
    
    def add_chat_task(self, chat_info, message_data, priority='medium'):
        """اضافه کردن وظیفه چت"""
        try:
            task = ChatTask(
                chat_info=chat_info,
                message_data=message_data,
                priority=priority
            )
            
            # انتخاب صف بر اساس اولویت
            if priority == 'high':
                queue_obj = self.high_priority_queue
            elif priority == 'low':
                queue_obj = self.low_priority_queue
            else:
                queue_obj = self.medium_priority_queue
            
            # اضافه کردن به صف
            priority_value = self._get_priority_value(priority)
            queue_obj.put((priority_value, task.timestamp, task), timeout=1)
            
            self.logger.debug(f"📝 وظیفه اضافه شد: {chat_info.get('name', 'Unknown')} - {priority}")
            return True
            
        except queue.Full:
            self.logger.warning("⚠️ صف پر است، وظیفه رد شد")
            return False
        except Exception as e:
            self.logger.error(f"❌ خطا در اضافه کردن وظیفه: {e}")
            return False
    
    def process_chat_batch(self, chat_list):
        """پردازش دسته‌ای چت‌ها"""
        try:
            self.logger.info(f"📦 شروع پردازش دسته‌ای {len(chat_list)} چت")
            
            # تقسیم به batch ها
            batches = [chat_list[i:i + self.batch_size] 
                      for i in range(0, len(chat_list), self.batch_size)]
            
            results = []
            
            # پردازش موازی batch ها
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch = {
                    executor.submit(self._process_single_batch, batch): batch 
                    for batch in batches
                }
                
                for future in as_completed(future_to_batch):
                    batch = future_to_batch[future]
                    try:
                        batch_results = future.result(timeout=30)
                        results.extend(batch_results)
                        self.logger.info(f"✅ Batch تکمیل شد: {len(batch)} چت")
                    except Exception as e:
                        self.logger.error(f"❌ خطا در batch: {e}")
            
            self.logger.info(f"🎯 پردازش دسته‌ای تکمیل: {len(results)} نتیجه")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پردازش دسته‌ای: {e}")
            return []
    
    def _process_single_batch(self, chat_batch):
        """پردازش یک batch از چت‌ها"""
        results = []
        
        for chat in chat_batch:
            try:
                if not self.is_running:
                    break
                
                # اسکن چت
                chat_data = self.chat_scanner.scan_single_chat(
                    (chat.get('position', {}).get('x', 100),
                     chat.get('position', {}).get('y', 100))
                )
                
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
                                
                                results.append({
                                    'chat': chat.get('name'),
                                    'message': message.get('content', '')[:50],
                                    'response': response[:50],
                                    'success': success
                                })
                                
                                # تاخیر بین پیام‌ها
                                time.sleep(float(self.config.get('send_delay', 1.5)))
                
            except Exception as e:
                self.logger.error(f"❌ خطا در پردازش چت {chat.get('name', 'Unknown')}: {e}")
                results.append({
                    'chat': chat.get('name'),
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def _worker_loop(self):
        """حلقه اصلی worker"""
        worker_name = threading.current_thread().name
        self.logger.info(f"👷 {worker_name} شروع به کار کرد")
        
        with self.stats_lock:
            self.stats['active_workers'] += 1
        
        try:
            while self.is_running:
                task = self._get_next_task()
                
                if task:
                    start_time = time.time()
                    success = self._process_task(task)
                    processing_time = time.time() - start_time
                    
                    # آپدیت آمار
                    with self.stats_lock:
                        self.stats['processed_chats'] += 1
                        if success:
                            self.stats['sent_messages'] += 1
                        else:
                            self.stats['failed_tasks'] += 1
                        
                        # محاسبه میانگین زمان پاسخ
                        current_avg = self.stats['avg_response_time']
                        total_processed = self.stats['processed_chats']
                        self.stats['avg_response_time'] = (
                            (current_avg * (total_processed - 1) + processing_time) / total_processed
                        )
                
                else:
                    # کمی استراحت اگر وظیفه‌ای نیست
                    time.sleep(0.5)
                    
        except Exception as e:
            self.logger.error(f"❌ خطا در worker {worker_name}: {e}")
        finally:
            with self.stats_lock:
                self.stats['active_workers'] -= 1
            self.logger.info(f"👋 {worker_name} متوقف شد")
    
    def _get_next_task(self):
        """گرفتن وظیفه بعدی از صف"""
        try:
            # اولویت: high -> medium -> low
            for queue_obj in [self.high_priority_queue, self.medium_priority_queue, self.low_priority_queue]:
                try:
                    _, _, task = queue_obj.get(timeout=1)
                    return task
                except queue.Empty:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطا در گرفتن وظیفه: {e}")
            return None
    
    def _process_task(self, task):
        """پردازش یک وظیفه"""
        try:
            chat_info = task.chat_info
            message_data = task.message_data
            
            self.logger.debug(f"⚙️ پردازش: {chat_info.get('name', 'Unknown')}")
            
            # تولید پاسخ
            response = self.response_generator.generate_response(message_data, chat_info)
            
            if response:
                # ارسال پاسخ
                success = self.telegram_manager.send_message(response)
                
                if success:
                    self.logger.info(f"✅ پاسخ ارسال شد: {chat_info.get('name', 'Unknown')}")
                    return True
                else:
                    self.logger.warning(f"⚠️ خطا در ارسال: {chat_info.get('name', 'Unknown')}")
                    return False
            else:
                self.logger.warning(f"⚠️ پاسخ تولید نشد: {chat_info.get('name', 'Unknown')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ خطا در پردازش وظیفه: {e}")
            return False
    
    def _monitor_loop(self):
        """حلقه مانیتورینگ"""
        self.logger.info("📊 مانیتور شروع شد")
        
        while self.is_running:
            try:
                # چاپ آمار هر 30 ثانیه
                time.sleep(30)
                
                with self.stats_lock:
                    stats_copy = self.stats.copy()
                
                self.logger.info(
                    f"📈 آمار: "
                    f"پردازش شده: {stats_copy['processed_chats']}, "
                    f"ارسال شده: {stats_copy['sent_messages']}, "
                    f"خطا: {stats_copy['failed_tasks']}, "
                    f"میانگین زمان: {stats_copy['avg_response_time']:.2f}s, "
                    f"Worker فعال: {stats_copy['active_workers']}"
                )
                
            except Exception as e:
                self.logger.error(f"❌ خطا در مانیتور: {e}")
    
    def _get_priority_value(self, priority):
        """تبدیل اولویت به عدد"""
        priority_map = {
            'high': 1,
            'medium': 2,
            'low': 3
        }
        return priority_map.get(priority, 2)
    
    def get_queue_status(self):
        """وضعیت صف‌ها"""
        return {
            'high_priority': self.high_priority_queue.qsize(),
            'medium_priority': self.medium_priority_queue.qsize(),
            'low_priority': self.low_priority_queue.qsize(),
            'total_queued': (
                self.high_priority_queue.qsize() +
                self.medium_priority_queue.qsize() +
                self.low_priority_queue.qsize()
            )
        }
    
    def get_statistics(self):
        """گرفتن آمار کامل"""
        with self.stats_lock:
            stats_copy = self.stats.copy()
        
        stats_copy['queue_status'] = self.get_queue_status()
        return stats_copy
    
    def clear_queues(self):
        """پاک کردن همه صف‌ها"""
        try:
            while not self.high_priority_queue.empty():
                self.high_priority_queue.get_nowait()
            
            while not self.medium_priority_queue.empty():
                self.medium_priority_queue.get_nowait()
            
            while not self.low_priority_queue.empty():
                self.low_priority_queue.get_nowait()
            
            self.logger.info("🧹 صف‌ها پاک شدند")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطا در پاک کردن صف‌ها: {e}")
            return False
