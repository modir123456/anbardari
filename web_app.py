#!/usr/bin/env python3
"""
Persian File Copier Pro - Web UI Version
HTML/CSS/JavaScript frontend with Python backend using Eel
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
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Initialize Eel
eel.init('web')

class ConfigManager:
    """مدیریت تنظیمات برنامه"""
    
    def __init__(self, config_file='config_web.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """بارگذاری تنظیمات"""
        default_config = {
            'ui_settings': {
                'theme': 'dark',
                'font_family': 'B Nazanin',
                'font_size': 14,
                'language': 'fa',
                'startup_maximized': True,
                'toast_duration': 10000
            },
            'file_operations': {
                'max_concurrent_tasks': 3,
                'chunk_size': 65536,
                'verify_copy': True,
                'auto_retry': True,
                'max_scan_depth': 10
            },
            'license': {
                'key': '',
                'type': 'trial',
                'status': 'active'
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for section, settings in default_config.items():
                        if section not in loaded_config:
                            loaded_config[section] = settings
                        else:
                            for key, value in settings.items():
                                if key not in loaded_config[section]:
                                    loaded_config[section][key] = value
                    return loaded_config
            else:
                return default_config
        except:
            return default_config
    
    def save_config(self):
        """ذخیره تنظیمات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, section, key, default=None):
        """دریافت تنظیم"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """تنظیم مقدار"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

class LicenseManager:
    """مدیریت لایسنس"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def get_license_info(self):
        """دریافت اطلاعات لایسنس"""
        return {
            'type': self.config.get('license', 'type', 'trial'),
            'status': self.config.get('license', 'status', 'active'),
            'key': self.config.get('license', 'key', '')
        }
    
    def check_file_limit(self, file_count):
        """بررسی محدودیت فایل"""
        license_type = self.config.get('license', 'type', 'trial')
        if license_type == 'trial':
            return file_count <= 100
        return True

class FileManager:
    """مدیریت فایل‌ها و عملیات کپی"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.file_cache = {}
        self.active_tasks = {}
        self.task_counter = 0
    
    def scan_drives(self):
        """اسکن درایوهای سیستم"""
        drives = []
        try:
            for partition in psutil.disk_partitions():
                if partition.mountpoint:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        drive_info = {
                            'path': partition.mountpoint,
                            'free_space': self.format_size(usage.free),
                            'total_space': self.format_size(usage.total),
                            'icon': self.get_drive_icon(partition),
                            'type': 'drive'
                        }
                        drives.append(drive_info)
                        
                        # Add common folders
                        drives.extend(self.get_common_folders(partition.mountpoint))
                        
                    except (PermissionError, OSError):
                        continue
            
            # Add MTP devices
            drives.extend(self.scan_mtp_devices())
            
        except Exception as e:
            print(f"Error scanning drives: {e}")
        
        return drives
    
    def get_drive_icon(self, partition):
        """تشخیص آیکون درایو"""
        try:
            drive_type = partition.fstype.lower() if partition.fstype else ""
            device = partition.device.lower() if partition.device else ""
            
            if "usb" in device or "removable" in str(partition.opts).lower():
                return "🔌"
            elif "cdrom" in str(partition.opts).lower():
                return "💿"
            elif "network" in str(partition.opts).lower():
                return "🌐"
            else:
                return "💾"
        except:
            return "💿"
    
    def get_common_folders(self, drive_path):
        """دریافت پوشه‌های رایج"""
        common_folders = []
        if platform.system() == "Windows" and drive_path.startswith('C:'):
            folders = [
                ('Users', '👥'),
                ('Program Files', '📦'),
                ('Windows', '⚙️')
            ]
            for folder_name, icon in folders:
                folder_path = os.path.join(drive_path, folder_name)
                if os.path.exists(folder_path):
                    common_folders.append({
                        'path': folder_path,
                        'name': f"{icon} {folder_name}",
                        'type': 'folder'
                    })
        return common_folders
    
    def scan_mtp_devices(self):
        """اسکن دستگاه‌های MTP"""
        devices = []
        try:
            if platform.system() == "Windows":
                # Enhanced Windows MTP detection
                result = subprocess.run([
                    "wmic", "logicaldisk", "get", "deviceid,drivetype,volumename"
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    for line in lines:
                        if line.strip():
                            parts = line.strip().split(None, 2)
                            if len(parts) >= 2:
                                device_id = parts[0]
                                drive_type = parts[1]
                                volume_name = parts[2] if len(parts) > 2 else "دستگاه"
                                
                                if device_id and ':' in device_id:
                                    try:
                                        test_path = device_id + "\\"
                                        if os.path.exists(test_path):
                                            contents = os.listdir(test_path)
                                            content_upper = [name.upper() for name in contents]
                                            
                                            if any(folder in content_upper for folder in ['DCIM', 'ANDROID']):
                                                devices.append({
                                                    'path': test_path,
                                                    'name': f"📱 {volume_name}",
                                                    'type': 'mtp_device'
                                                })
                                            elif drive_type == "2":
                                                devices.append({
                                                    'path': test_path,
                                                    'name': f"🔌 {volume_name}",
                                                    'type': 'usb_device'
                                                })
                                    except:
                                        continue
        except Exception as e:
            print(f"Error scanning MTP devices: {e}")
        
        return devices
    
    def scan_files(self, directory_path, search_term="", format_filter="همه فرمت‌ها", size_filter="همه اندازه‌ها"):
        """اسکن فایل‌ها در دایرکتوری"""
        files = []
        try:
            max_files = 1000  # Limit for web performance
            count = 0
            
            for root, dirs, filenames in os.walk(directory_path):
                if count >= max_files:
                    break
                
                for filename in filenames:
                    if count >= max_files:
                        break
                    
                    file_path = os.path.join(root, filename)
                    
                    # Apply filters
                    if search_term and search_term.lower() not in filename.lower():
                        continue
                    
                    if not self.matches_format_filter(filename, format_filter):
                        continue
                    
                    try:
                        stat = os.stat(file_path)
                        file_info = {
                            'name': filename,
                            'path': file_path,
                            'size': self.format_size(stat.st_size),
                            'raw_size': stat.st_size,
                            'type': self.get_file_type(filename),
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'selected': False
                        }
                        
                        if self.matches_size_filter(stat.st_size, size_filter):
                            files.append(file_info)
                            count += 1
                            
                    except (PermissionError, OSError):
                        continue
            
            # Also scan folders
            for item in os.listdir(directory_path):
                if count >= max_files:
                    break
                
                item_path = os.path.join(directory_path, item)
                if os.path.isdir(item_path):
                    try:
                        stat = os.stat(item_path)
                        files.append({
                            'name': item,
                            'path': item_path,
                            'size': "پوشه",
                            'raw_size': 0,
                            'type': "📁 پوشه",
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'selected': False
                        })
                        count += 1
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error scanning files: {e}")
        
        return files
    
    def matches_format_filter(self, filename, filter_type):
        """بررسی فیلتر فرمت"""
        if filter_type == "همه فرمت‌ها":
            return True
        
        ext = os.path.splitext(filename.lower())[1]
        filter_map = {
            "📷 تصاویر": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            "🎬 ویدیوها": ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            "🎵 صوتی": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            "📄 اسناد": ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            "📊 جداول": ['.xls', '.xlsx', '.csv', '.ods'],
            "📋 ارائه": ['.ppt', '.pptx', '.odp'],
            "📦 آرشیو": ['.zip', '.rar', '.7z', '.tar', '.gz'],
            "⚙️ برنامه": ['.exe', '.msi', '.deb', '.dmg', '.app'],
            "💻 کد": ['.py', '.js', '.html', '.css', '.php', '.cpp', '.java'],
            "🔤 فونت": ['.ttf', '.otf', '.woff', '.woff2'],
            "🗄️ دیتابیس": ['.db', '.sqlite', '.sql', '.mdb']
        }
        
        return ext in filter_map.get(filter_type, [])
    
    def matches_size_filter(self, size, filter_type):
        """بررسی فیلتر اندازه"""
        if filter_type == "همه اندازه‌ها":
            return True
        
        if filter_type == "🟢 کوچک":
            return size < 1024 * 1024  # < 1MB
        elif filter_type == "🟡 متوسط":
            return 1024 * 1024 <= size < 100 * 1024 * 1024  # 1MB - 100MB
        elif filter_type == "🟠 بزرگ":
            return 100 * 1024 * 1024 <= size < 1024 * 1024 * 1024  # 100MB - 1GB
        elif filter_type == "🔴 خیلی بزرگ":
            return size >= 1024 * 1024 * 1024  # > 1GB
        
        return True
    
    def get_file_type(self, filename):
        """تشخیص نوع فایل"""
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return '🖼️ تصویر'
        elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
            return '🎬 ویدیو'
        elif ext in ['.mp3', '.wav', '.flac']:
            return '🎵 صوتی'
        elif ext in ['.pdf', '.doc', '.docx', '.txt']:
            return '📄 سند'
        elif ext in ['.zip', '.rar', '.7z']:
            return '📦 آرشیو'
        else:
            return '📄 فایل'
    
    def format_size(self, size_bytes):
        """فرمت اندازه فایل"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def start_copy_task(self, source_files, destination):
        """شروع تسک کپی"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        # Create task
        task = {
            'id': task_id,
            'source_files': source_files,
            'destination': destination,
            'status': 'running',
            'progress': 0,
            'speed': '0 MB/s',
            'eta': 'محاسبه...',
            'copied_size': '0 B',
            'total_size': '0 B'
        }
        
        self.active_tasks[task_id] = task
        
        # Start copy in background thread
        copy_thread = threading.Thread(
            target=self._copy_files_thread,
            args=(task_id, source_files, destination),
            daemon=True
        )
        copy_thread.start()
        
        return task_id
    
    def _copy_files_thread(self, task_id, source_files, destination):
        """Thread برای کپی فایل‌ها"""
        try:
            task = self.active_tasks[task_id]
            
            # Calculate total size
            total_size = 0
            for file_path in source_files:
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
            
            task['total_size'] = self.format_size(total_size)
            copied_size = 0
            start_time = time.time()
            
            for i, source_path in enumerate(source_files):
                if task['status'] == 'cancelled':
                    break
                
                # Pause handling
                while task['status'] == 'paused':
                    time.sleep(0.1)
                
                try:
                    if os.path.isfile(source_path):
                        dest_path = os.path.join(destination, os.path.basename(source_path))
                        shutil.copy2(source_path, dest_path)
                        copied_size += os.path.getsize(source_path)
                    elif os.path.isdir(source_path):
                        dest_path = os.path.join(destination, os.path.basename(source_path))
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        # Add directory size to copied_size
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                fp = os.path.join(root, file)
                                try:
                                    copied_size += os.path.getsize(fp)
                                except:
                                    continue
                    
                    # Update progress
                    progress = int((i + 1) / len(source_files) * 100)
                    elapsed_time = time.time() - start_time
                    
                    if elapsed_time > 0:
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
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error copying {source_path}: {e}")
                    continue
            
            if task['status'] != 'cancelled':
                task.update({
                    'status': 'completed',
                    'progress': 100,
                    'eta': '00:00'
                })
            
        except Exception as e:
            print(f"Copy task error: {e}")
            task['status'] = 'failed'
    
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
config_manager = ConfigManager()
license_manager = LicenseManager(config_manager)
file_manager = FileManager(config_manager)

# Eel exposed functions
@eel.expose
def get_drives():
    """دریافت لیست درایوها"""
    return file_manager.scan_drives()

@eel.expose
def scan_directory(path, search="", format_filter="همه فرمت‌ها", size_filter="همه اندازه‌ها"):
    """اسکن دایرکتوری"""
    return file_manager.scan_files(path, search, format_filter, size_filter)

@eel.expose
def start_copy(source_files, destination):
    """شروع کپی"""
    # Check license
    if not license_manager.check_file_limit(len(source_files)):
        return {'error': 'محدودیت نسخه آزمایشی', 'limit': 100}
    
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
            task['status'] = 'paused'
        elif action == 'resume':
            task['status'] = 'running'
        elif action == 'cancel':
            task['status'] = 'cancelled'
        return True
    return False

@eel.expose
def get_config():
    """دریافت تنظیمات"""
    return config_manager.config

@eel.expose
def save_config(config):
    """ذخیره تنظیمات"""
    config_manager.config = config
    config_manager.save_config()
    return True

@eel.expose
def get_license_info():
    """دریافت اطلاعات لایسنس"""
    return license_manager.get_license_info()

@eel.expose
def activate_license(license_key):
    """فعال‌سازی لایسنس"""
    # Simple validation (در نسخه واقعی باید پیچیده‌تر باشد)
    if license_key and len(license_key) > 10:
        config_manager.set('license', 'key', license_key)
        config_manager.set('license', 'type', 'professional')
        config_manager.set('license', 'status', 'active')
        return {'success': True, 'message': 'لایسنس با موفقیت فعال شد'}
    else:
        return {'success': False, 'message': 'کلید لایسنس نامعتبر است'}

@eel.expose
def open_payment_gateway():
    """باز کردن درگاه پرداخت"""
    import webbrowser
    webbrowser.open('https://zarinp.al/735413')
    return True

def main():
    """تابع اصلی"""
    try:
        # Start the web app
        eel.start('index.html', size=(1200, 800), port=8080, host='localhost')
    except Exception as e:
        print(f"Error starting web app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()