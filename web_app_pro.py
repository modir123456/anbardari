#!/usr/bin/env python3
"""
Persian File Copier Pro - Professional Web UI Version
Enhanced with background services, real-time indexing, and complete feature set
شرکت فناوری نوآئران مثبت سبز
"""

import eel
import os
import sys
import json
import time
import threading
import shutil
import psutil
import platform
import subprocess
import glob
import sqlite3
import hashlib
import uuid
import base64
import queue
import watchdog
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Eel
eel.init('web')

class DatabaseManager:
    """مدیریت پایگاه داده برای cache فایل‌ها"""
    
    def __init__(self, db_file='file_cache.db'):
        self.db_file = db_file
        self.init_database()
    
    @property
    def db_path(self):
        """دریافت مسیر فایل پایگاه داده"""
        return self.db_file
    
    def init_database(self):
        """ایجاد جداول پایگاه داده"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER NOT NULL,
                modified INTEGER NOT NULL,
                drive TEXT NOT NULL,
                extension TEXT,
                type TEXT,
                is_directory BOOLEAN DEFAULT 0,
                indexed_at INTEGER DEFAULT (strftime('%s', 'now')),
                hash TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT,
                total_space INTEGER,
                free_space INTEGER,
                drive_type TEXT,
                last_scan INTEGER DEFAULT (strftime('%s', 'now')),
                auto_index BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_drive ON files(drive)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified)')
        
        conn.commit()
        conn.close()
    
    def add_file(self, file_info: Dict):
        """اضافه کردن فایل به دیتابیس"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO files 
                (path, name, size, modified, drive, extension, type, is_directory, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_info['path'],
                file_info['name'],
                file_info['size'],
                file_info['modified'],
                file_info['drive'],
                file_info.get('extension', ''),
                file_info.get('type', ''),
                file_info.get('is_directory', False),
                file_info.get('hash', '')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding file to database: {e}")
        finally:
            conn.close()
    
    def get_files(self, drive=None, search_term="", format_filter="همه فرمت‌ها", 
                  size_filter="همه اندازه‌ها", limit=2000, offset=0):
        """دریافت فایل‌ها از دیتابیس با فیلتر"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = "SELECT * FROM files WHERE 1=1"
        params = []
        
        if drive and drive != "all":
            query += " AND drive = ?"
            params.append(drive)
        
        if search_term:
            query += " AND name LIKE ?"
            params.append(f"%{search_term}%")
        
        if format_filter != "همه فرمت‌ها":
            extensions = self.get_format_extensions(format_filter)
            if extensions:
                placeholders = ','.join('?' * len(extensions))
                query += f" AND extension IN ({placeholders})"
                params.extend(extensions)
        
        if size_filter != "همه اندازه‌ها":
            size_range = self.get_size_range(size_filter)
            if size_range:
                query += " AND size BETWEEN ? AND ?"
                params.extend(size_range)
        
        query += " ORDER BY is_directory DESC, name COLLATE NOCASE"
        query += f" LIMIT {limit} OFFSET {offset}"
        
        try:
            cursor.execute(query, params)
            files = cursor.fetchall()
            
            # Convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            result = []
            for file_row in files:
                file_dict = dict(zip(columns, file_row))
                file_dict['selected'] = False
                result.append(file_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error querying files: {e}")
            return []
        finally:
            conn.close()
    
    def get_format_extensions(self, format_filter):
        """دریافت پسوندهای مربوط به فیلتر فرمت"""
        format_map = {
            "📷 تصاویر": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
            "🎬 ویدیوها": ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            "🎵 صوتی": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            "📄 اسناد": ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
            "📊 جداول": ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
            "📋 ارائه": ['.ppt', '.pptx', '.odp', '.key'],
            "📦 آرشیو": ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            "⚙️ برنامه": ['.exe', '.msi', '.deb', '.dmg', '.app', '.apk'],
            "💻 کد": ['.py', '.js', '.html', '.css', '.php', '.cpp', '.java', '.c'],
            "🔤 فونت": ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
            "🗄️ دیتابیس": ['.db', '.sqlite', '.sql', '.mdb', '.accdb']
        }
        return format_map.get(format_filter, [])
    
    def get_size_range(self, size_filter):
        """دریافت محدوده اندازه بر اساس فیلتر"""
        if size_filter == "🟢 کوچک":
            return (0, 1024 * 1024)  # < 1MB
        elif size_filter == "🟡 متوسط":
            return (1024 * 1024, 100 * 1024 * 1024)  # 1MB - 100MB
        elif size_filter == "🟠 بزرگ":
            return (100 * 1024 * 1024, 1024 * 1024 * 1024)  # 100MB - 1GB
        elif size_filter == "🔴 خیلی بزرگ":
            return (1024 * 1024 * 1024, 999999999999999)  # > 1GB
        return None
    
    def remove_file(self, file_path):
        """حذف فایل از دیتابیس"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM files WHERE path = ?", (file_path,))
            conn.commit()
        finally:
            conn.close()
    
    def update_drive_info(self, drive_info):
        """بروزرسانی اطلاعات درایو"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO drives 
                (path, name, total_space, free_space, drive_type, auto_index)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                drive_info['path'],
                drive_info.get('name', ''),
                drive_info.get('total_space', 0),
                drive_info.get('free_space', 0),
                drive_info.get('drive_type', ''),
                drive_info.get('auto_index', True)
            ))
            conn.commit()
        finally:
            conn.close()
    
    def get_drive_settings(self, drive_path):
        """دریافت تنظیمات درایو"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT auto_index FROM drives WHERE path = ?", (drive_path,))
            result = cursor.fetchone()
            return result[0] if result else True
        finally:
            conn.close()
    
    def set_drive_auto_index(self, drive_path, auto_index):
        """تنظیم ایندکس خودکار درایو"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO drives (path, auto_index, last_scan)
                VALUES (?, ?, ?)
            ''', (drive_path, auto_index, int(time.time())))
            conn.commit()
        finally:
            conn.close()
    
    def reset_database(self):
        """بازنشانی کامل پایگاه داده"""
        try:
            import os
            # Close any existing connections
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
            
            # Recreate database
            self.init_database()
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise

class FileSystemWatcher(FileSystemEventHandler):
    """نظارت بر تغییرات فایل سیستم"""
    
    def __init__(self, db_manager, file_manager):
        self.db_manager = db_manager
        self.file_manager = file_manager
        self.update_queue = queue.Queue()
        
    def on_created(self, event):
        if not event.is_directory:
            self.update_queue.put(('created', event.src_path))
    
    def on_deleted(self, event):
        self.update_queue.put(('deleted', event.src_path))
    
    def on_modified(self, event):
        if not event.is_directory:
            self.update_queue.put(('modified', event.src_path))
    
    def on_moved(self, event):
        self.update_queue.put(('moved', event.src_path, event.dest_path))

class BackgroundIndexer:
    """سرویس پس‌زمینه برای ایندکس فایل‌ها"""
    
    def __init__(self, db_manager, file_manager):
        self.db_manager = db_manager
        self.file_manager = file_manager
        self.is_running = False
        self.observer = Observer()
        self.watcher = FileSystemWatcher(db_manager, file_manager)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def start(self):
        """شروع سرویس پس‌زمینه"""
        self.is_running = True
        
        # Start file system monitoring
        self.start_filesystem_monitoring()
        
        # Start drive monitoring
        self.start_drive_monitoring()
        
        # Start update processing
        self.start_update_processing()
        
        logger.info("Background indexer started")
    
    def stop(self):
        """توقف سرویس پس‌زمینه"""
        self.is_running = False
        self.observer.stop()
        self.observer.join()
        self.executor.shutdown(wait=True)
        logger.info("Background indexer stopped")
    
    def start_filesystem_monitoring(self):
        """شروع نظارت بر فایل سیستم"""
        try:
            for partition in psutil.disk_partitions():
                if self.db_manager.get_drive_settings(partition.mountpoint):
                    self.observer.schedule(self.watcher, partition.mountpoint, recursive=True)
            self.observer.start()
        except Exception as e:
            logger.error(f"Error starting filesystem monitoring: {e}")
    
    def start_drive_monitoring(self):
        """شروع نظارت بر درایوها"""
        def monitor_drives():
            last_drives = set()
            while self.is_running:
                try:
                    current_drives = set()
                    for partition in psutil.disk_partitions():
                        current_drives.add(partition.mountpoint)
                    
                    # Check for new drives
                    new_drives = current_drives - last_drives
                    for drive in new_drives:
                        self.on_drive_connected(drive)
                    
                    # Check for removed drives
                    removed_drives = last_drives - current_drives
                    for drive in removed_drives:
                        self.on_drive_disconnected(drive)
                    
                    last_drives = current_drives
                    time.sleep(3)  # Check every 3 seconds
                    
                except Exception as e:
                    logger.error(f"Error in drive monitoring: {e}")
                    time.sleep(5)
        
        threading.Thread(target=monitor_drives, daemon=True).start()
    
    def start_update_processing(self):
        """شروع پردازش بروزرسانی‌ها"""
        def process_updates():
            while self.is_running:
                try:
                    if not self.watcher.update_queue.empty():
                        update = self.watcher.update_queue.get(timeout=1)
                        self.process_file_update(update)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing updates: {e}")
        
        threading.Thread(target=process_updates, daemon=True).start()
    
    def on_drive_connected(self, drive_path):
        """رویداد اتصال درایو جدید"""
        logger.info(f"New drive connected: {drive_path}")
        
        # Auto-index if enabled
        if self.db_manager.get_drive_settings(drive_path):
            self.executor.submit(self.index_drive, drive_path)
        
        # Notify frontend
        try:
            eel.on_drive_connected(drive_path)
        except AttributeError:
            pass  # Function not exposed yet
    
    def on_drive_disconnected(self, drive_path):
        """رویداد قطع اتصال درایو"""
        logger.info(f"Drive disconnected: {drive_path}")
        try:
            eel.on_drive_disconnected(drive_path)
        except AttributeError:
            pass  # Function not exposed yet
    
    def process_file_update(self, update):
        """پردازش بروزرسانی فایل"""
        try:
            if update[0] == 'created':
                file_info = self.file_manager.get_file_info(update[1])
                if file_info:
                    self.db_manager.add_file(file_info)
                    try:
                        eel.on_file_added(file_info)
                    except AttributeError:
                        pass  # Function not exposed yet
            
            elif update[0] == 'deleted':
                self.db_manager.remove_file(update[1])
                try:
                    eel.on_file_removed(update[1])
                except AttributeError:
                    pass  # Function not exposed yet
            
            elif update[0] == 'modified':
                file_info = self.file_manager.get_file_info(update[1])
                if file_info:
                    self.db_manager.add_file(file_info)
                    try:
                        eel.on_file_modified(file_info)
                    except AttributeError:
                        pass  # Function not exposed yet
            
            elif update[0] == 'moved':
                self.db_manager.remove_file(update[1])
                file_info = self.file_manager.get_file_info(update[2])
                if file_info:
                    self.db_manager.add_file(file_info)
                    try:
                        eel.on_file_moved(update[1], file_info)
                    except AttributeError:
                        pass  # Function not exposed yet
        
        except Exception as e:
            logger.error(f"Error processing file update: {e}")
    
    def index_drive(self, drive_path):
        """ایندکس کردن کامل درایو"""
        logger.info(f"Starting full index of drive: {drive_path}")
        try:
            for root, dirs, files in os.walk(drive_path):
                if not self.is_running:
                    break
                
                # Index directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        stat = os.stat(dir_path)
                        file_info = {
                            'path': dir_path,
                            'name': dir_name,
                            'size': 0,
                            'modified': int(stat.st_mtime),
                            'drive': drive_path,
                            'extension': '',
                            'type': '📁 پوشه',
                            'is_directory': True
                        }
                        self.db_manager.add_file(file_info)
                    except (PermissionError, OSError):
                        continue
                
                # Index files
                for file_name in files:
                    if not self.is_running:
                        break
                    
                    file_path = os.path.join(root, file_name)
                    file_info = self.file_manager.get_file_info(file_path)
                    if file_info:
                        self.db_manager.add_file(file_info)
            
            logger.info(f"Completed indexing drive: {drive_path}")
            try:
                eel.on_drive_indexed(drive_path)
            except AttributeError:
                pass  # Function not exposed yet
            
        except Exception as e:
            logger.error(f"Error indexing drive {drive_path}: {e}")

class ConfigManager:
    """مدیریت پیکربندی پیشرفته"""
    
    def __init__(self, config_file='config_web_pro.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """بارگذاری تنظیمات"""
        default_config = {
            'ui_settings': {
                'theme': 'dark',
                'font_family': 'Vazirmatn',
                'font_size': 14,
                'font_weight': 'normal',
                'language': 'fa',
                'direction': 'rtl',
                'startup_maximized': True,
                'toast_duration': 10000,
                'animation_speed': 'normal',
                'show_tooltips': True,
                'compact_mode': False
            },
            'file_operations': {
                'max_concurrent_tasks': 5,
                'chunk_size': 65536,
                'verify_copy': True,
                'auto_retry': True,
                'max_retry_attempts': 3,
                'skip_existing': False,
                'preserve_timestamps': True,
                'show_hidden_files': False,
                'follow_symlinks': False
            },
            'indexing': {
                'auto_index_new_drives': True,
                'index_system_drives': False,
                'max_file_cache': 1000000,
                'scan_depth': 10,
                'exclude_extensions': ['.tmp', '.cache', '.log'],
                'exclude_folders': ['$Recycle.Bin', 'System Volume Information'],
                'background_indexing': True
            },
            'notifications': {
                'toast_duration': 10000,
                'sound_enabled': True,
                'system_tray': True,
                'progress_notifications': True,
                'completion_sound': True
            },
            'advanced': {
                'debug_logging': False,
                'auto_save_settings': True,
                'memory_optimization': True,
                'performance_mode': 'balanced',
                'database_cleanup_days': 30
            },
            'drives': {
                'auto_index_settings': {}
            },
            'license': {
                'key': '',
                'type': 'trial',
                'status': 'active',
                'machine_id': '',
                'trial_start': None
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self.merge_configs(default_config, loaded_config)
                    return loaded_config
            else:
                return default_config
        except:
            return default_config
    
    def merge_configs(self, default, loaded):
        """ادغام تنظیمات پیش‌فرض با بارگذاری شده"""
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                self.merge_configs(value, loaded[key])
    
    def save_config(self):
        """ذخیره تنظیمات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, section, key, default=None):
        """دریافت تنظیم"""
        return self.config.get(section, {}).get(key, default)
    
    def get_section(self, section):
        """دریافت کل بخش"""
        return self.config.get(section, {})
    
    def set(self, section, key, value):
        """تنظیم مقدار"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        if self.get('advanced', 'auto_save_settings', True):
            self.save_config()
    
class LicenseManager:
    """مدیریت لایسنس پیشرفته"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        
        # Set machine_id if not exists
        if not self.config.get('license', 'machine_id', ''):
            self.config.set('license', 'machine_id', self.get_machine_id())
        
        # Check if already has valid license
        current_key = self.config.get('license', 'key', '')
        if current_key and self.validate_license(current_key):
            self.config.set('license', 'type', 'professional')
            self.config.set('license', 'status', 'active')
    
    def get_license_info(self):
        """دریافت اطلاعات کامل لایسنس"""
        license_type = self.config.get('license', 'type', 'trial')
        return {
            'type': license_type,
            'status': self.config.get('license', 'status', 'active'),
            'key': self.config.get('license', 'key', ''),
            'machine_id': self.config.get('license', 'machine_id', ''),
            'trial_files_limit': 100 if license_type == 'trial' else None,
            'professional_files_limit': None,
            'trial_days_left': self.get_trial_days_left() if license_type == 'trial' else None
        }
    
    def get_trial_days_left(self):
        """محاسبه روزهای باقی‌مانده از نسخه آزمایشی"""
        # Check if trial start date is set
        trial_start = self.config.get('license', 'trial_start', None)
        if not trial_start:
            # Set trial start date
            from datetime import datetime
            trial_start = datetime.now().timestamp()
            self.config.set('license', 'trial_start', trial_start)
        
        # Calculate days left (30 day trial)
        from datetime import datetime, timedelta
        start_date = datetime.fromtimestamp(trial_start)
        end_date = start_date + timedelta(days=30)
        days_left = (end_date - datetime.now()).days
        return max(0, days_left)
    
    def check_file_limit(self, file_count):
        """بررسی محدودیت تعداد فایل"""
        license_type = self.config.get('license', 'type', 'trial')
        if license_type == 'trial':
            trial_days = self.get_trial_days_left()
            if trial_days <= 0:
                return False  # Trial expired
            return file_count <= 100  # Trial limit: 100 files
        return True  # Professional: unlimited
    
    def validate_license(self, license_key):
        """اعتبارسنجی کلید لایسنس"""
        if not license_key or len(license_key) < 10:
            return False
        
        # Valid license keys (you can add more)
        valid_keys = [
            'PFC-PRO-2024-FULL',
            'PFC-PRO-UNLIMITED',
            'PERSIAN-FILE-COPIER-PRO',
            'PFC-PREMIUM-2024',
            'PFC-PRO-UNLIMITED-1754433649983-N6103H22'  # User's generated key
        ]
        
        return license_key in valid_keys
    
    def activate_license(self, license_key):
        """فعال‌سازی لایسنس"""
        if self.validate_license(license_key):
            self.config.set('license', 'key', license_key)
            self.config.set('license', 'type', 'professional')
            self.config.set('license', 'status', 'active')
            return {'success': True, 'message': 'لایسنس با موفقیت فعال شد! تمام امکانات آزاد شدند.'}
        else:
            return {'success': False, 'message': 'کلید لایسنس نامعتبر است. لطفاً کلید صحیح را وارد کنید.'}
    
    def get_machine_id(self):
        """دریافت شناسه منحصر به فرد دستگاه"""
        try:
            # Try to get existing machine_id first
            existing_id = self.config.get('license', 'machine_id', None)
            if existing_id and existing_id != 'default-pro-machine':
                return existing_id
            
            # Generate based on stable system info
            import hashlib
            machine_info = f"{platform.node()}-{platform.machine()}"
            if not machine_info or machine_info == "-":
                machine_info = "default-pro-machine"
            return hashlib.md5(machine_info.encode()).hexdigest()
        except:
            return "default-pro-machine"

class FileManager:
    """مدیریت پیشرفته فایل‌ها"""
    
    def __init__(self, config: ConfigManager, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.active_tasks = {}
        self.task_counter = 0
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def scan_drives(self):
        """اسکن پیشرفته درایوها"""
        drives = []
        try:
            for partition in psutil.disk_partitions():
                if partition.mountpoint and self.is_valid_drive(partition):
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        drive_info = {
                            'path': partition.mountpoint,
                            'name': self.get_drive_name(partition),
                            'free_space': self.format_size(usage.free),
                            'total_space': self.format_size(usage.total),
                            'free_space_bytes': usage.free,
                            'total_space_bytes': usage.total,
                            'usage_percent': round((usage.used / usage.total) * 100, 1),
                            'icon': self.get_drive_icon(partition),
                            'type': 'drive',
                            'file_system': partition.fstype,
                            'auto_index': self.db_manager.get_drive_settings(partition.mountpoint)
                        }
                        drives.append(drive_info)
                        
                        # Update database
                        self.db_manager.update_drive_info(drive_info)
                        
                    except (PermissionError, OSError):
                        continue
            
            # If no main drives found, add essential directories
            if not drives:
                essential_dirs = [
                    ('/workspace', '💼 ورک‌اسپیس', '📁'),
                    (os.path.expanduser('~'), '🏠 خانه', '🏠'),
                ]
                
                for dir_path, name, icon in essential_dirs:
                    if os.path.exists(dir_path) and os.access(dir_path, os.R_OK):
                        try:
                            usage = psutil.disk_usage(dir_path)
                            drives.append({
                                'path': dir_path,
                                'name': name,
                                'free_space': self.format_size(usage.free),
                                'total_space': self.format_size(usage.total),
                                'free_space_bytes': usage.free,
                                'total_space_bytes': usage.total,
                                'usage_percent': round((usage.used / usage.total) * 100, 1),
                                'icon': icon,
                                'type': 'directory',
                                'file_system': 'directory',
                                'auto_index': True
                            })
                        except:
                            pass
            
            # Add MTP devices only
            drives.extend(self.scan_mtp_devices())
            
        except Exception as e:
            logger.error(f"Error scanning drives: {e}")
        
        return drives
    
    def is_valid_drive(self, partition):
        """بررسی معتبر بودن درایو برای نمایش"""
        mountpoint = partition.mountpoint
        fstype = partition.fstype.lower() if partition.fstype else ""
        
        # System-specific filters
        if platform.system() == "Windows":
            # Skip system reserved partitions
            if len(mountpoint) < 3 or not mountpoint.endswith('\\'):
                return False
            # Skip network drives and virtual drives
            if mountpoint.startswith('\\\\'):
                return False
        else:  # Linux/Unix
            # Skip system and virtual filesystems
            system_mounts = {
                '/dev', '/proc', '/sys', '/run', '/tmp', '/var/run',
                '/dev/pts', '/dev/shm', '/dev/mqueue', '/sys/fs',
                '/proc/sys/fs/binfmt_misc', '/sys/kernel/debug',
                '/sys/kernel/security', '/sys/fs/cgroup', '/sys/fs/pstore',
                '/sys/fs/fuse/connections', '/sys/kernel/config'
            }
            
            # Skip if it's a system mount
            if any(mountpoint.startswith(sm) for sm in system_mounts):
                return False
            
            # Skip virtual filesystems
            virtual_fs = {
                'proc', 'sysfs', 'devtmpfs', 'tmpfs', 'devpts', 
                'securityfs', 'cgroup', 'pstore', 'configfs',
                'debugfs', 'tracefs', 'fusectl', 'fuse.gvfsd-fuse'
            }
            if fstype in virtual_fs:
                return False
            
            # Skip small temporary filesystems (less than 100MB)
            try:
                usage = psutil.disk_usage(mountpoint)
                if usage.total < 100 * 1024 * 1024:  # 100MB
                    return False
            except:
                return False
        
        # Check if mountpoint is accessible
        try:
            os.listdir(mountpoint)
            return True
        except (PermissionError, OSError, FileNotFoundError):
            return False
    
    def get_drive_name(self, partition):
        """دریافت نام درایو"""
        try:
            if platform.system() == "Windows":
                try:
                    # Use subprocess to get drive label on Windows
                    import subprocess
                    drive_letter = partition.mountpoint.rstrip('\\/')
                    if ':' in drive_letter:
                        result = subprocess.run(
                            ['vol', drive_letter], 
                            capture_output=True, 
                            text=True, 
                            shell=True
                        )
                        if result.returncode == 0 and result.stdout:
                            lines = result.stdout.strip().split('\n')
                            for line in lines:
                                if 'is' in line and drive_letter in line:
                                    parts = line.split('is')
                                    if len(parts) > 1:
                                        label = parts[1].strip()
                                        return label if label else f"Drive {partition.mountpoint}"
                    return f"Drive {partition.mountpoint}"
                except (OSError, subprocess.SubprocessError):
                    # Fallback if subprocess fails
                    return f"Drive {partition.mountpoint}"
            else:
                return partition.mountpoint
        except Exception:
            return partition.mountpoint
    
    def get_drive_icon(self, partition):
        """تشخیص آیکون درایو بهبود یافته"""
        try:
            device = partition.device.lower() if partition.device else ""
            opts = str(partition.opts).lower() if partition.opts else ""
            
            if "usb" in device or "removable" in opts:
                return "🔌"
            elif "cdrom" in opts or "dvd" in device:
                return "💿"
            elif "network" in opts or "cifs" in opts or "nfs" in opts:
                return "🌐"
            elif partition.mountpoint == "/" or partition.mountpoint.startswith("C:"):
                return "🖥️"
            else:
                return "💾"
        except:
            return "💾"
    
    def scan_mtp_devices(self):
        """اسکن دستگاه‌های MTP (موبایل، دوربین، و...)"""
        devices = []
        try:
            # Only detect actual MTP/mobile devices, not regular drives
            if platform.system() == "Windows":
                # Check for mobile devices using WMI
                try:
                    result = subprocess.run([
                        "wmic", "logicaldisk", "where", "drivetype=2", "get", "deviceid,volumename"
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]
                        for line in lines:
                            line = line.strip()
                            if line and ':' in line:
                                parts = line.split(None, 1)
                                if parts:
                                    device_id = parts[0]
                                    volume_name = parts[1] if len(parts) > 1 else "USB Device"
                                    
                                    try:
                                        test_path = device_id + "\\"
                                        if os.path.exists(test_path):
                                            contents = os.listdir(test_path)
                                            content_upper = [name.upper() for name in contents]
                                            
                                            # Only add if it looks like a mobile device
                                            if any(folder in content_upper for folder in ['DCIM', 'ANDROID', 'IPHONE_INTERNAL']):
                                                devices.append({
                                                    'path': test_path,
                                                    'name': f"📱 {volume_name}",
                                                    'icon': '📱',
                                                    'type': 'mobile',
                                                    'auto_index': True
                                                })
                                    except:
                                        continue
                except:
                    pass
            
            elif platform.system() == "Linux":
                # Linux MTP detection - only mobile devices
                possible_paths = glob.glob("/run/user/*/gvfs/*")
                
                for path in possible_paths:
                    if os.path.isdir(path) and any(x in path.lower() for x in ['mtp', 'android', 'phone']):
                        try:
                            devices.append({
                                'path': path,
                                'name': f"📱 {os.path.basename(path)}",
                                'icon': '📱',
                                'type': 'mobile',
                                'auto_index': True
                            })
                        except:
                            continue
        
        except Exception as e:
            logger.error(f"Error scanning MTP devices: {e}")
        
        return devices
    
    def get_quick_access_folders(self):
        """دریافت پوشه‌های دسترسی سریع"""
        folders = []
        try:
            import os
            
            if platform.system() == "Windows":
                user_profile = os.environ.get('USERPROFILE', '')
                if user_profile:
                    quick_folders = [
                        ('Desktop', '🖥️'),
                        ('Documents', '📄'),
                        ('Downloads', '📥'),
                        ('Pictures', '🖼️'),
                        ('Music', '🎵'),
                        ('Videos', '🎬')
                    ]
                    
                    for folder_name, icon in quick_folders:
                        folder_path = os.path.join(user_profile, folder_name)
                        if os.path.exists(folder_path):
                            folders.append({
                                'path': folder_path,
                                'name': f"{icon} {folder_name}",
                                'icon': icon,
                                'type': 'quick_folder',
                                'auto_index': True
                            })
            
            elif platform.system() == "Linux":
                home = os.path.expanduser("~")
                quick_folders = [
                    ('Desktop', '🖥️'),
                    ('Documents', '📄'),
                    ('Downloads', '📥'),
                    ('Pictures', '🖼️'),
                    ('Music', '🎵'),
                    ('Videos', '🎬')
                ]
                
                for folder_name, icon in quick_folders:
                    folder_path = os.path.join(home, folder_name)
                    if os.path.exists(folder_path):
                        folders.append({
                            'path': folder_path,
                            'name': f"{icon} {folder_name}",
                            'icon': icon,
                            'type': 'quick_folder',
                            'auto_index': True
                        })
                        
        except Exception as e:
            logger.error(f"Error getting quick access folders: {e}")
        
        return folders
    
    def scan_directory_direct(self, path, search="", format_filter="همه فرمت‌ها", size_filter="همه اندازه‌ها", limit=2000, offset=0):
        """اسکن مستقیم دایرکتوری از سیستم فایل"""
        files = []
        
        try:
            # If path is 'all', scan common directories
            if path == 'all':
                # Add current workspace files as example
                scan_paths = ['/workspace', os.path.expanduser('~')]
            else:
                scan_paths = [path] if os.path.isdir(path) else []
            
            for scan_path in scan_paths:
                if not os.path.exists(scan_path):
                    continue
                    
                try:
                    for root, dirs, filenames in os.walk(scan_path):
                        # Limit depth to avoid too deep scanning
                        depth = root.replace(scan_path, '').count(os.sep)
                        if depth > 3:
                            dirs[:] = []  # Don't recurse deeper
                            continue
                        
                        for filename in filenames:
                            if len(files) >= limit:
                                break
                                
                            file_path = os.path.join(root, filename)
                            
                            # Apply search filter
                            if search and search.lower() not in filename.lower():
                                continue
                            
                            try:
                                stat = os.stat(file_path)
                                file_info = {
                                    'path': file_path,
                                    'name': filename,
                                    'size': stat.st_size,
                                    'modified': int(stat.st_mtime),
                                    'drive': scan_path,
                                    'extension': os.path.splitext(filename)[1].lower(),
                                    'type': self.get_file_type(filename),
                                    'is_directory': False,
                                    'selected': False
                                }
                                
                                # Apply format filter
                                if format_filter != "همه فرمت‌ها":
                                    extensions = self.db_manager.get_format_extensions(format_filter)
                                    if extensions and file_info['extension'] not in extensions:
                                        continue
                                
                                # Apply size filter
                                if size_filter != "همه اندازه‌ها":
                                    size_range = self.db_manager.get_size_range(size_filter)
                                    if size_range and not (size_range[0] <= stat.st_size <= size_range[1]):
                                        continue
                                
                                files.append(file_info)
                                
                            except (OSError, PermissionError):
                                continue
                        
                        if len(files) >= limit:
                            break
                            
                except (OSError, PermissionError):
                    continue
                    
        except Exception as e:
            logger.error(f"Error in direct directory scan: {e}")
        
        # Apply offset
        return files[offset:offset + limit]
    
    def get_file_type(self, filename):
        """تشخیص نوع فایل"""
        ext = os.path.splitext(filename)[1].lower()
        
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        audio_exts = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'}
        doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.md'}
        archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz'}
        code_exts = {'.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml'}
        
        if ext in image_exts:
            return '🖼️ تصویر'
        elif ext in video_exts:
            return '🎬 ویدیو'
        elif ext in audio_exts:
            return '🎵 صوتی'
        elif ext in doc_exts:
            return '📄 سند'
        elif ext in archive_exts:
            return '📦 فشرده'
        elif ext in code_exts:
            return '💻 کد'
        else:
            return '📄 فایل'
    
    def get_file_info(self, file_path):
        """دریافت اطلاعات کامل فایل"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            is_directory = os.path.isdir(file_path)
            name = os.path.basename(file_path)
            extension = os.path.splitext(name.lower())[1] if not is_directory else ""
            
            # Determine drive
            drive = os.path.splitdrive(file_path)[0] + "\\" if platform.system() == "Windows" else "/"
            
            file_info = {
                'path': file_path,
                'name': name,
                'size': 0 if is_directory else stat.st_size,
                'modified': int(stat.st_mtime),
                'drive': drive,
                'extension': extension,
                'type': self.get_file_type(name, is_directory),
                'is_directory': is_directory
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def get_file_type(self, filename, is_directory=False):
        """تشخیص نوع فایل بهبود یافته"""
        if is_directory:
            return '📁 پوشه'
        
        ext = os.path.splitext(filename.lower())[1]
        
        type_map = {
            # Images
            **dict.fromkeys(['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'], '🖼️ تصویر'),
            # Videos
            **dict.fromkeys(['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'], '🎬 ویدیو'),
            # Audio
            **dict.fromkeys(['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'], '🎵 صوتی'),
            # Documents
            **dict.fromkeys(['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'], '📄 سند'),
            # Spreadsheets
            **dict.fromkeys(['.xls', '.xlsx', '.csv', '.ods'], '📊 جدول'),
            # Presentations
            **dict.fromkeys(['.ppt', '.pptx', '.odp'], '📋 ارائه'),
            # Archives
            **dict.fromkeys(['.zip', '.rar', '.7z', '.tar', '.gz'], '📦 آرشیو'),
            # Executables
            **dict.fromkeys(['.exe', '.msi', '.deb', '.dmg', '.app'], '⚙️ برنامه'),
            # Code
            **dict.fromkeys(['.py', '.js', '.html', '.css', '.php', '.cpp', '.java'], '💻 کد'),
            # Fonts
            **dict.fromkeys(['.ttf', '.otf', '.woff', '.woff2'], '🔤 فونت')
        }
        
        return type_map.get(ext, '📄 فایل')
    
    def format_size(self, size_bytes):
        """فرمت اندازه فایل"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def start_copy_task(self, source_files, destination):
        """شروع تسک کپی پیشرفته"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        task = {
            'id': task_id,
            'source_files': source_files,
            'destination': destination,
            'status': 'running',
            'progress': 0,
            'speed': '0 MB/s',
            'eta': 'محاسبه...',
            'copied_size': '0 B',
            'total_size': '0 B',
            'files_copied': 0,
            'total_files': len(source_files),
            'current_file': '',
            'start_time': time.time(),
            'paused': False,
            'cancelled': False
        }
        
        self.active_tasks[task_id] = task
        
        # Start copy in background
        future = self.executor.submit(self._copy_files_thread, task_id, source_files, destination)
        task['future'] = future
        
        return task_id
    
    def _copy_files_thread(self, task_id, source_files, destination):
        """Thread پیشرفته برای کپی فایل‌ها"""
        try:
            task = self.active_tasks[task_id]
            
            # Calculate total size
            total_size = 0
            for file_path in source_files:
                if task['cancelled']:
                    break
                try:
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
                    elif os.path.isdir(file_path):
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                fp = os.path.join(root, file)
                                try:
                                    total_size += os.path.getsize(fp)
                                except:
                                    continue
                except:
                    continue
            
            task['total_size'] = self.format_size(total_size)
            copied_size = 0
            start_time = time.time()
            
            for i, source_path in enumerate(source_files):
                if task['cancelled']:
                    break
                
                # Handle pause
                while task['paused'] and not task['cancelled']:
                    time.sleep(0.1)
                
                task['current_file'] = os.path.basename(source_path)
                
                try:
                    if os.path.isfile(source_path):
                        dest_path = os.path.join(destination, os.path.basename(source_path))
                        
                        # Copy with progress tracking
                        file_size = os.path.getsize(source_path)
                        copied_size += self._copy_file_with_progress(source_path, dest_path, task)
                        
                    elif os.path.isdir(source_path):
                        dest_path = os.path.join(destination, os.path.basename(source_path))
                        copied_size += self._copy_directory_with_progress(source_path, dest_path, task)
                    
                    task['files_copied'] = i + 1
                    
                    # Update progress
                    if total_size > 0:
                        progress = int((copied_size / total_size) * 100)
                    else:
                        progress = int(((i + 1) / len(source_files)) * 100)
                    
                    elapsed_time = time.time() - start_time
                    
                    if elapsed_time > 0 and copied_size > 0:
                        speed = copied_size / elapsed_time / 1024 / 1024  # MB/s
                        remaining_size = total_size - copied_size
                        eta_seconds = remaining_size / (speed * 1024 * 1024) if speed > 0 else 0
                        eta = self.format_time(eta_seconds)
                        speed_str = f"{speed:.1f} MB/s"
                    else:
                        speed_str = "0 MB/s"
                        eta = "محاسبه..."
                    
                    task.update({
                        'progress': progress,
                        'speed': speed_str,
                        'eta': eta,
                        'copied_size': self.format_size(copied_size)
                    })
                    
                    # Small delay to prevent UI flooding
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error copying {source_path}: {e}")
                    continue
            
            if not task['cancelled']:
                task.update({
                    'status': 'completed',
                    'progress': 100,
                    'eta': '00:00',
                    'current_file': 'تکمیل شد'
                })
            else:
                task['status'] = 'cancelled'
            
        except Exception as e:
            logger.error(f"Copy task error: {e}")
            task['status'] = 'failed'
    
    def _copy_file_with_progress(self, src, dst, task):
        """کپی فایل با نمایش پیشرفت"""
        try:
            file_size = os.path.getsize(src)
            copied = 0
            
            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                while True:
                    if task['cancelled']:
                        break
                    
                    while task['paused'] and not task['cancelled']:
                        time.sleep(0.1)
                    
                    chunk = fsrc.read(self.config.get('file_operations', 'chunk_size', 65536))
                    if not chunk:
                        break
                    
                    fdst.write(chunk)
                    copied += len(chunk)
            
            # Preserve timestamps if enabled
            if self.config.get('file_operations', 'preserve_timestamps', True):
                stat = os.stat(src)
                os.utime(dst, (stat.st_atime, stat.st_mtime))
            
            return file_size
            
        except Exception as e:
            logger.error(f"Error copying file {src}: {e}")
            return 0
    
    def _copy_directory_with_progress(self, src, dst, task):
        """کپی پوشه با نمایش پیشرفت"""
        try:
            if not os.path.exists(dst):
                os.makedirs(dst)
            
            total_copied = 0
            
            for root, dirs, files in os.walk(src):
                if task['cancelled']:
                    break
                
                # Create subdirectories
                for dir_name in dirs:
                    src_dir = os.path.join(root, dir_name)
                    dst_dir = os.path.join(dst, os.path.relpath(src_dir, src))
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                
                # Copy files
                for file_name in files:
                    if task['cancelled']:
                        break
                    
                    src_file = os.path.join(root, file_name)
                    dst_file = os.path.join(dst, os.path.relpath(src_file, src))
                    
                    total_copied += self._copy_file_with_progress(src_file, dst_file, task)
            
            return total_copied
            
        except Exception as e:
            logger.error(f"Error copying directory {src}: {e}")
            return 0
    
    def format_time(self, seconds):
        """فرمت زمان"""
        if seconds < 60:
            return f"{int(seconds)} ثانیه"
        elif seconds < 3600:
            return f"{int(seconds // 60)} دقیقه"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} ساعت {minutes} دقیقه"

# Initialize managers
db_manager = DatabaseManager()
config_manager = ConfigManager()
license_manager = LicenseManager(config_manager)
file_manager = FileManager(config_manager, db_manager)
background_indexer = BackgroundIndexer(db_manager, file_manager)

# Eel exposed functions
@eel.expose
def get_drives():
    """دریافت لیست درایوها"""
    return file_manager.scan_drives()

@eel.expose
def scan_directory(path, search="", format_filter="همه فرمت‌ها", size_filter="همه اندازه‌ها", limit=2000, offset=0):
    """اسکن دایرکتوری از دیتابیس یا مستقیم از سیستم فایل"""
    # First try from database
    db_files = db_manager.get_files(path, search, format_filter, size_filter, limit, offset)
    
    # If database is empty or path is specific directory, try direct file system scan
    if not db_files or (path != 'all' and os.path.isdir(path)):
        return file_manager.scan_directory_direct(path, search, format_filter, size_filter, limit, offset)
    
    return db_files

@eel.expose
def start_copy(source_files, destination):
    """شروع کپی"""
    # Check license limitations
    if not license_manager.check_file_limit(len(source_files)):
        license_info = license_manager.get_license_info()
        if license_info['type'] == 'trial':
            if license_info['trial_days_left'] <= 0:
                return {'error': 'نسخه آزمایشی منقضی شده است. لطفاً لایسنس تهیه کنید.', 'expired': True}
            else:
                return {'error': f'محدودیت نسخه آزمایشی: حداکثر {license_info["trial_files_limit"]} فایل', 'limit': license_info["trial_files_limit"]}
        return {'error': 'خطا در بررسی لایسنس', 'limit': 0}
    
    task_id = file_manager.start_copy_task(source_files, destination)
    return {'task_id': task_id, 'success': True}

@eel.expose
def get_tasks():
    """دریافت لیست تسک‌ها"""
    return list(file_manager.active_tasks.values())

@eel.expose
def control_task(task_id, action):
    """کنترل تسک (pause/resume/cancel)"""
    if task_id in file_manager.active_tasks:
        task = file_manager.active_tasks[task_id]
        if action == 'pause':
            task['paused'] = True
            task['status'] = 'paused'
        elif action == 'resume':
            task['paused'] = False
            task['status'] = 'running'
        elif action == 'cancel':
            task['cancelled'] = True
            task['status'] = 'cancelled'
        return True
    return False

@eel.expose
def get_config(section=None):
    """دریافت تنظیمات"""
    if section:
        return config_manager.get_section(section)
    return config_manager.config

@eel.expose
def save_config(config):
    """ذخیره تنظیمات"""
    config_manager.config = config
    config_manager.save_config()
    return True

@eel.expose
def get_database_status():
    """دریافت وضعیت پایگاه داده"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Get files count
        cursor.execute("SELECT COUNT(*) FROM files")
        files_count = cursor.fetchone()[0]
        
        # Get database size
        import os
        db_size = os.path.getsize(db_manager.db_path) if os.path.exists(db_manager.db_path) else 0
        
        # Get last cleanup (dummy for now)
        last_cleanup = config_manager.get('advanced', 'last_cleanup', None)
        
        conn.close()
        
        return {
            'files_count': files_count,
            'size': db_size,
            'last_cleanup': last_cleanup
        }
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return {'files_count': 0, 'size': 0, 'last_cleanup': None}

@eel.expose
def optimize_database():
    """بهینه‌سازی پایگاه داده"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Vacuum database
        cursor.execute("VACUUM")
        
        # Analyze database
        cursor.execute("ANALYZE")
        
        # Reindex
        cursor.execute("REINDEX")
        
        conn.close()
        
        # Update last optimization time
        import datetime
        config_manager.set('advanced', 'last_optimization', datetime.datetime.now().isoformat())
        
        return {'success': True, 'message': 'پایگاه داده بهینه‌سازی شد'}
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose  
def reset_database():
    """بازنشانی کامل پایگاه داده"""
    try:
        # Stop background indexer
        background_indexer.stop()
        
        # Reset database
        db_manager.reset_database()
        
        # Restart background indexer
        background_indexer.start()
        
        return {'success': True, 'message': 'پایگاه داده بازنشانی شد'}
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def save_advanced_settings(settings):
    """ذخیره تنظیمات پیشرفته"""
    try:
        # Save each setting
        for key, value in settings.items():
            config_manager.set('advanced', key, value)
        
        return {'success': True, 'message': 'تنظیمات ذخیره شد'}
    except Exception as e:
        logger.error(f"Error saving advanced settings: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose
def save_file_operation_settings(settings):
    """ذخیره تنظیمات عملیات فایل"""
    try:
        for key, value in settings.items():
            config_manager.set('file_operations', key, value)
        
        return {'success': True, 'message': 'تنظیمات عملیات فایل ذخیره شد'}
    except Exception as e:
        logger.error(f"Error saving file operation settings: {e}")
        return {'success': False, 'message': str(e)}

@eel.expose  
def save_ui_settings(settings):
    """ذخیره تنظیمات رابط کاربری"""
    try:
        for key, value in settings.items():
            config_manager.set('ui_settings', key, value)
        
        return {'success': True, 'message': 'تنظیمات رابط کاربری ذخیره شد'}
    except Exception as e:
        logger.error(f"Error saving UI settings: {e}")
        return {'success': False, 'message': str(e)}



@eel.expose
def get_license_info():
    """دریافت اطلاعات لایسنس"""
    return license_manager.get_license_info()

@eel.expose
def activate_license(license_key):
    """فعال‌سازی لایسنس"""
    return license_manager.activate_license(license_key)

@eel.expose
def open_payment_gateway():
    """باز کردن درگاه پرداخت"""
    import webbrowser
    webbrowser.open('https://zarinp.al/735413')
    return True

@eel.expose
def set_drive_auto_index(drive_path, auto_index):
    """تنظیم ایندکس خودکار درایو"""
    db_manager.set_drive_auto_index(drive_path, auto_index)
    
    # Start/stop indexing for this drive
    if auto_index:
        background_indexer.executor.submit(background_indexer.index_drive, drive_path)
    
    return True

@eel.expose
def start_drive_index(drive_path):
    """شروع ایندکس دستی درایو"""
    background_indexer.executor.submit(background_indexer.index_drive, drive_path)
    return True

@eel.expose
def get_file_count(drive_path):
    """دریافت تعداد فایل‌های ایندکس شده در درایو"""
    conn = sqlite3.connect(db_manager.db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM files WHERE drive = ?", (drive_path,))
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()

@eel.expose
def clear_drive_cache(drive_path):
    """پاک کردن کش درایو"""
    conn = sqlite3.connect(db_manager.db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM files WHERE drive = ?", (drive_path,))
        conn.commit()
        return True
    finally:
        conn.close()

@eel.expose
def save_setting(key, value):
    """ذخیره تنظیمات"""
    try:
        config_manager.set_by_key(key, value)
        config_manager.save()
        return {'success': True}
    except Exception as e:
        logger.error(f"Error saving setting {key}: {e}")
        return {'success': False, 'error': str(e)}

@eel.expose
def load_setting(key, default_value=None):
    """بارگیری تنظیمات"""
    try:
        return config_manager.get_by_key(key, default_value)
    except Exception as e:
        logger.error(f"Error loading setting {key}: {e}")
        return default_value

@eel.expose
def save_all_settings(settings_data):
    """ذخیره همه تنظیمات"""
    try:
        for key, value in settings_data.items():
            config_manager.set_by_key(key, value)
        config_manager.save()
        return {'success': True}
    except Exception as e:
        logger.error(f"Error saving all settings: {e}")
        return {'success': False, 'error': str(e)}

@eel.expose
def load_all_settings():
    """بارگیری همه تنظیمات"""
    try:
        return {
            'ui_settings': {
                'theme': config_manager.get('ui', 'theme', 'dark'),
                'language': config_manager.get('ui', 'language', 'fa'),
                'notifications': config_manager.get('ui', 'notifications', True),
                'show_hidden_files': config_manager.get('ui', 'show_hidden_files', False),
                'compact_view': config_manager.get('ui', 'compact_view', False)
            },
            'file_operation_settings': {
                'auto_resume': config_manager.get('file_operations', 'auto_resume', True),
                'verify_copy': config_manager.get('file_operations', 'verify_copy', True),
                'preserve_timestamps': config_manager.get('file_operations', 'preserve_timestamps', True),
                'skip_existing': config_manager.get('file_operations', 'skip_existing', False),
                'create_log': config_manager.get('file_operations', 'create_log', True)
            },
            'advanced_settings': {
                'max_parallel_copies': config_manager.get('advanced', 'max_parallel_copies', 3),
                'buffer_size': config_manager.get('advanced', 'buffer_size', 1048576),
                'auto_index': config_manager.get('advanced', 'auto_index', True),
                'cache_enabled': config_manager.get('advanced', 'cache_enabled', True),
                'auto_save_settings': config_manager.get('advanced', 'auto_save_settings', True)
            },
            'license_info': license_manager.get_license_info()
        }
    except Exception as e:
        logger.error(f"Error loading all settings: {e}")
        return {}

# JavaScript callback functions (called from Python)
def on_drive_connected(drive_path):
    """Callback for new drive connection"""
    pass

def on_drive_disconnected(drive_path):
    """Callback for drive disconnection"""
    pass

def on_file_added(file_info):
    """Callback for file added"""
    pass

def on_file_removed(file_path):
    """Callback for file removed"""
    pass

def on_file_modified(file_info):
    """Callback for file modified"""
    pass

def on_file_moved(old_path, new_file_info):
    """Callback for file moved"""
    pass

def on_drive_indexed(drive_path):
    """Callback for drive indexing completed"""
    pass

def main():
    """تابع اصلی"""
    try:
        # Start background services
        background_indexer.start()
        
        # Start the web app
        print("🚀 سرور وب در حال اجرا...")
        print("🌐 برای دسترسی به برنامه به آدرس زیر بروید:")
        print("   http://localhost:8080")
        print("⏹️ برای خروج Ctrl+C را فشار دهید")
        
        try:
            # Try to start with browser if available
            eel.start('index_pro.html', size=(1400, 900), port=8080, host='localhost', 
                     close_callback=lambda page, sockets: background_indexer.stop(),
                     block=True)
        except Exception as browser_error:
            print(f"⚠️ مرورگر به طور خودکار باز نشد: {browser_error}")
            print("🌐 لطفاً دستی به آدرس http://localhost:8080 بروید")
            
            # Start without browser (headless mode)
            import bottle
            bottle.run(host='localhost', port=8080, debug=False, quiet=True)
        
    except Exception as e:
        logger.error(f"Error starting web app: {e}")
        sys.exit(1)
    finally:
        background_indexer.stop()

if __name__ == '__main__':
    main()