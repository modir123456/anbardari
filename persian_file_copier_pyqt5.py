#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro v2.0 - PyQt5 Edition
نرم‌افزار کپی فایل ایرانی پیشرفته - نسخه PyQt5

شرکت فناوری نوآئران مثبت سبز
https://zarinp.al/735413
"""

import sys
import os
import json
import time
import threading
import psutil
import hashlib
import base64
import webbrowser
import shutil
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QPushButton, QLabel, QProgressBar, QStatusBar,
    QSplitter, QFrame, QScrollArea, QTextEdit, QCheckBox, QSpinBox,
    QGroupBox, QFileDialog, QMessageBox, QMenu, QMenuBar, QToolBar,
    QSystemTrayIcon, QDialog, QDialogButtonBox, QFormLayout
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings, QSize, QPoint,
    QPropertyAnimation, QEasingCurve, QRect, QMimeData, QUrl
)
from PyQt5.QtGui import (
    QFont, QIcon, QPixmap, QPalette, QColor, QMovie, QClipboard,
    QPainter, QBrush, QLinearGradient, QDrag, QCursor
)

# Configuration Management
class ConfigManager:
    """مدیریت تنظیمات برنامه"""
    
    def __init__(self):
        self.config_file = "config_pyqt5.json"
        self.default_config = {
            "app_settings": {
                "app_name": "Persian File Copier Pro",
                "version": "2.0",
                "company": "شرکت فناوری نوآئران مثبت سبز",
                "window_maximized": True,
                "window_geometry": [100, 100, 1600, 1000],
                "last_destination": "",
                "auto_scan_drives": True
            },
            "font_settings": {
                "primary_font": "B Nazanin",
                "fallback_font": "Tahoma",
                "font_size": 11,
                "apply_to_all": True
            },
            "ui_settings": {
                "theme": "dark",
                "language": "persian",
                "show_tooltips": True,
                "animation_speed": 300,
                "toast_duration": 10000,
                "status_update_interval": 1000,
                "auto_refresh": True
            },
            "file_operations": {
                "max_concurrent_tasks": 3,
                "chunk_size": 8192,
                "verify_copy": True,
                "auto_retry": True,
                "max_retries": 3,
                "timeout": 30,
                "show_hidden_files": False,
                "recursive_scan": True,
                "max_scan_depth": 10
            },
            "filters": {
                "file_categories": {
                    "تصاویر": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico"],
                    "ویدیوها": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp", ".mpg", ".mpeg"],
                    "صوتی": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".aiff"],
                    "اسناد": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages", ".tex", ".md"],
                    "جداول": [".xls", ".xlsx", ".csv", ".ods", ".numbers", ".tsv"],
                    "ارائه": [".ppt", ".pptx", ".odp", ".key"],
                    "آرشیو": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2"],
                    "برنامه": [".exe", ".msi", ".deb", ".dmg", ".app", ".pkg", ".rpm", ".apk"],
                    "کد": [".py", ".js", ".html", ".css", ".cpp", ".java", ".c", ".php", ".rb", ".go", ".rs", ".swift"],
                    "فونت": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
                    "دیتابیس": [".db", ".sqlite", ".mdb", ".sql", ".dbf"]
                },
                "size_categories": {
                    "کوچک": 1024 * 1024,  # < 1 MB
                    "متوسط": 10 * 1024 * 1024,  # 1-10 MB
                    "بزرگ": 100 * 1024 * 1024,  # 10-100 MB
                    "خیلی بزرگ": float('inf')  # > 100 MB
                }
            },
            "destinations": {
                "quick_destinations": {
                    "🖥️ دسکتاپ": "~/Desktop",
                    "📁 مستندات": "~/Documents", 
                    "📥 دانلودها": "~/Downloads",
                    "🎵 موزیک": "~/Music",
                    "🎬 ویدیوها": "~/Videos",
                    "📷 عکس‌ها": "~/Pictures"
                },
                "recent_destinations": [],
                "auto_create_folders": True
            },
            "license": {
                "license_key": "",
                "license_type": "trial",
                "license_status": "inactive",
                "max_files_trial": 100,
                "activation_date": "",
                "expiry_date": ""
            },
            "zarinpal": {
                "payment_url": "https://zarinp.al/735413",
                "support_telegram": "@PersianFileSupport",
                "company_phone": "+98 21 1234 5678",
                "company_email": "sales@persianfile.ir"
            },
            "logging": {
                "log_level": "INFO",
                "log_file": "persian_file_copier.log",
                "max_log_size": 10485760,  # 10 MB
                "backup_count": 5
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """بارگذاری تنظیمات از فایل"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self.merge_configs(self.default_config, loaded_config)
            else:
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def merge_configs(self, default: dict, loaded: dict) -> dict:
        """ادغام تنظیمات پیش‌فرض با بارگذاری شده"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def save_config(self, config: dict = None):
        """ذخیره تنظیمات در فایل"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, section: str, key: str = None, default=None):
        """دریافت مقدار تنظیمات"""
        try:
            if key is None:
                return self.config.get(section, default)
            return self.config.get(section, {}).get(key, default)
        except:
            return default
    
    def set(self, section: str, key: str, value):
        """تنظیم مقدار"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

# License Management System - Enhanced Security
class LicenseManager:
    """مدیریت لایسنس و احراز هویت - نسخه امن"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.company_key = "PERSIANFILECOPIER2024_SECURE"
        self.trial_days = 7
        self.trial_file_limit = 100
        self._machine_id = self._get_machine_id()
        
    def _get_machine_id(self) -> str:
        """دریافت شناسه منحصر به فرد دستگاه"""
        try:
            import platform
            
            # Combine multiple hardware identifiers
            machine_data = f"{platform.machine()}-{platform.processor()}-{platform.node()}"
            
            # Add network MAC address if available
            try:
                import uuid
                mac = hex(uuid.getnode())[2:]
                machine_data += f"-{mac}"
            except:
                pass
            
            # Create hash
            hash_obj = hashlib.sha256(machine_data.encode())
            return hash_obj.hexdigest()[:16].upper()
        except:
            return "DEFAULT-MACHINE"
    
    def generate_serial(self, customer_name: str, customer_email: str) -> str:
        """تولید سریال منحصربه‌فرد با machine binding"""
        timestamp = str(int(time.time()))
        machine_hash = self._machine_id[:8]
        data = f"{customer_name}{customer_email}{timestamp}{machine_hash}{self.company_key}"
        hash_obj = hashlib.sha256(data.encode())
        serial = base64.b64encode(hash_obj.digest()).decode()[:16].upper()
        checksum = self._calculate_checksum("PRO", machine_hash)
        return f"PFC-PRO-{machine_hash}-{checksum}"
    
    def _calculate_checksum(self, license_type: str, machine_hash: str) -> str:
        """محاسبه checksum برای لایسنس"""
        data = f"{license_type}-{machine_hash}-{self.company_key}"
        return hashlib.md5(data.encode()).hexdigest()[:8].upper()
    
    def validate_license(self, license_key: str) -> bool:
        """اعتبارسنجی کلید لایسنس با machine binding"""
        try:
            if not license_key or len(license_key) < 25:
                return False
            
            # Expected format: PFC-[TYPE]-[MACHINE]-[CHECKSUM]
            parts = license_key.split('-')
            if len(parts) != 4 or parts[0] != 'PFC':
                return False
            
            license_type = parts[1]
            machine_hash = parts[2]
            checksum = parts[3]
            
            # Validate license type
            if license_type not in ['PRO', 'ENT']:
                return False
            
            # Validate machine binding
            if machine_hash != self._machine_id[:8]:
                return False
            
            # Validate checksum
            expected_checksum = self._calculate_checksum(license_type, machine_hash)
            if checksum != expected_checksum:
                return False
            
            return True
            
        except:
            return False
    
    def activate_license(self, license_key: str) -> tuple:
        """فعال‌سازی لایسنس"""
        if self.validate_license(license_key):
            self.config.set('license', 'license_key', license_key)
            self.config.set('license', 'license_status', 'active')
            self.config.set('license', 'activation_date', datetime.now().isoformat())
            self.config.set('license', 'machine_id', self._machine_id)
            
            # Determine license type
            parts = license_key.split('-')
            license_type = parts[1] if len(parts) > 1 else 'PRO'
            
            self.config.set('license', 'license_type', license_type)
            return True, f"لایسنس {license_type} با موفقیت فعال شد"
        else:
            return False, "کلید لایسنس نامعتبر است یا متعلق به دستگاه دیگری است"
    
    def check_file_limit(self, file_count: int) -> bool:
        """بررسی محدودیت تعداد فایل"""
        license_info = self.get_license_info()
        
        # Check if license is valid and not expired
        if license_info['status'] == 'active' and license_info['type'] != 'trial':
            # Additional machine verification
            stored_machine = self.config.get('license', 'machine_id', '')
            if stored_machine and stored_machine != self._machine_id:
                return False
            return True
        
        # Trial version limitations
        if self._is_trial_expired():
            return False
            
        return file_count <= self.trial_file_limit
    
    def _is_trial_expired(self) -> bool:
        """بررسی انقضای نسخه آزمایشی"""
        try:
            install_date_str = self.config.get('license', 'install_date', '')
            if not install_date_str:
                # First run
                install_date = datetime.now().isoformat()
                self.config.set('license', 'install_date', install_date)
                self.config.set('license', 'trial_machine_id', self._machine_id)
                return False
            
            # Check machine binding for trial
            trial_machine = self.config.get('license', 'trial_machine_id', '')
            if trial_machine and trial_machine != self._machine_id:
                return True  # Trial expired if moved to different machine
            
            install_date = datetime.fromisoformat(install_date_str)
            days_passed = (datetime.now() - install_date).days
            return days_passed >= self.trial_days
        except:
            return True
    
    def get_license_info(self) -> dict:
        """دریافت اطلاعات لایسنس"""
        license_status = self.config.get('license', 'license_status', 'inactive')
        license_type = self.config.get('license', 'license_type', 'trial')
        license_key = self.config.get('license', 'license_key', '')
        
        if license_status == 'active' and license_key:
            # Verify license is still valid
            if not self.validate_license(license_key):
                license_status = 'invalid'
                license_type = 'trial'
        
        # Calculate trial info
        trial_info = ""
        if license_type == 'trial' or license_status != 'active':
            try:
                install_date_str = self.config.get('license', 'install_date', '')
                if install_date_str:
                    install_date = datetime.fromisoformat(install_date_str)
                    days_passed = (datetime.now() - install_date).days
                    remaining_days = max(0, self.trial_days - days_passed)
                    trial_info = f"{remaining_days} روز باقی‌مانده"
                else:
                    trial_info = f"{self.trial_days} روز آزمایشی"
            except:
                trial_info = "نامشخص"
        
        return {
            'status': trial_info if license_type == 'trial' else license_status,
            'type': 'نسخه کامل' if license_status == 'active' else 'آزمایشی',
            'key': license_key if license_status == 'active' else '',
            'activation_date': self.config.get('license', 'activation_date', ''),
            'max_files': 'نامحدود' if license_status == 'active' else self.trial_file_limit,
            'machine_id': self._machine_id[:8]  # Show partial ID for support
        }
    
    def get_machine_info_for_support(self) -> str:
        """تولید اطلاعات دستگاه برای پشتیبانی"""
        return f"Machine ID: {self._machine_id[:8]}\nFull Hash: {self._machine_id}\nPlatform: {platform.system()} {platform.release()}"

# Toast Notification System
class ToastNotification(QWidget):
    """سیستم اعلان Toast مشابه SweetAlert"""
    
    def __init__(self, parent, message: str, toast_type: str = "info", duration: int = 10000):
        super().__init__(parent)
        self.parent_widget = parent
        self.duration = duration
        self.setupUI(message, toast_type)
        self.show_animation()
        
        # Auto hide timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_animation)
        self.timer.start(duration)
    
    def setupUI(self, message: str, toast_type: str):
        """تنظیم رابط Toast"""
        self.setFixedSize(400, 80)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon based on type
        icons = {
            "success": "✅",
            "warning": "⚠️", 
            "error": "❌",
            "info": "ℹ️"
        }
        
        colors = {
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336", 
            "info": "#2196F3"
        }
        
        icon_label = QLabel(icons.get(toast_type, "ℹ️"))
        icon_label.setFont(QFont("Arial", 16))
        
        message_label = QLabel(message)
        message_label.setFont(QFont("B Nazanin", 11))
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white;")
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        
        # Styling
        color = colors.get(toast_type, "#2196F3")
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
        """)
        
        # Position at top-right of parent
        if self.parent_widget:
            parent_rect = self.parent_widget.geometry()
            x = parent_rect.x() + parent_rect.width() - self.width() - 20
            y = parent_rect.y() + 50
            self.move(x, y)
    
    def show_animation(self):
        """انیمیشن نمایش"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        
        start_rect = self.geometry()
        start_rect.moveRight(start_rect.right() + self.width())
        end_rect = self.geometry()
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.show()
        self.animation.start()
    
    def hide_animation(self):
        """انیمیشن مخفی کردن"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        
        start_rect = self.geometry()
        end_rect = start_rect
        end_rect.moveRight(end_rect.right() + self.width())
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()

# File Copy Worker Thread
class FileCopyWorker(QThread):
    """Worker thread برای کپی فایل‌ها"""
    
    progress_updated = pyqtSignal(str, int, str, str)  # task_id, progress, speed, eta
    task_completed = pyqtSignal(str, bool, str)  # task_id, success, message
    error_occurred = pyqtSignal(str, str)  # task_id, error_message
    
    def __init__(self, task_id: str, source_files: List[str], destination: str, config: ConfigManager):
        super().__init__()
        self.task_id = task_id
        self.source_files = source_files
        self.destination = destination
        self.config = config
        self.is_paused = False
        self.is_cancelled = False
        self.total_size = 0
        self.copied_size = 0
        
    def run(self):
        """اجرای کپی فایل‌ها"""
        try:
            # Calculate total size
            self.calculate_total_size()
            
            start_time = time.time()
            
            for i, source_file in enumerate(self.source_files):
                if self.is_cancelled:
                    break
                    
                # Wait if paused
                while self.is_paused and not self.is_cancelled:
                    self.msleep(100)
                
                if self.is_cancelled:
                    break
                    
                # Copy file
                success = self.copy_single_file(source_file)
                
                if not success and not self.is_cancelled:
                    self.error_occurred.emit(self.task_id, f"خطا در کپی فایل: {source_file}")
                
                # Update progress
                progress = int((i + 1) / len(self.source_files) * 100)
                elapsed_time = time.time() - start_time
                
                if elapsed_time > 0:
                    speed = self.copied_size / elapsed_time / 1024 / 1024  # MB/s
                    remaining_size = self.total_size - self.copied_size
                    eta_seconds = remaining_size / (speed * 1024 * 1024) if speed > 0 else 0
                    eta = self.format_time(eta_seconds)
                    speed_str = f"{speed:.1f} MB/s"
                else:
                    speed_str = "0 MB/s"
                    eta = "محاسبه..."
                
                self.progress_updated.emit(self.task_id, progress, speed_str, eta)
            
            if not self.is_cancelled:
                self.task_completed.emit(self.task_id, True, "کپی با موفقیت تکمیل شد")
            else:
                self.task_completed.emit(self.task_id, False, "کپی لغو شد")
                
        except Exception as e:
            self.error_occurred.emit(self.task_id, str(e))
    
    def calculate_total_size(self):
        """محاسبه حجم کل فایل‌ها"""
        self.total_size = 0
        for file_path in self.source_files:
            if os.path.isfile(file_path):
                self.total_size += os.path.getsize(file_path)
    
    def copy_single_file(self, source_file: str) -> bool:
        """کپی یک فایل"""
        try:
            if not os.path.exists(source_file):
                return False
                
            filename = os.path.basename(source_file)
            dest_file = os.path.join(self.destination, filename)
            
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            
            # Copy with progress tracking
            file_size = os.path.getsize(source_file)
            chunk_size = self.config.get('file_operations', 'chunk_size', 8192)
            
            with open(source_file, 'rb') as src, open(dest_file, 'wb') as dst:
                while True:
                    if self.is_cancelled:
                        return False
                        
                    while self.is_paused and not self.is_cancelled:
                        self.msleep(100)
                    
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                        
                    dst.write(chunk)
                    self.copied_size += len(chunk)
            
            return True
            
        except Exception as e:
            print(f"Error copying {source_file}: {e}")
            return False
    
    def pause(self):
        """مکث کپی"""
        self.is_paused = True
    
    def resume(self):
        """ادامه کپی"""
        self.is_paused = False
    
    def cancel(self):
        """لغو کپی"""
        self.is_cancelled = True
    
    def format_time(self, seconds: float) -> str:
        """فرمت زمان"""
        if seconds < 60:
            return f"{int(seconds)} ثانیه"
        elif seconds < 3600:
            return f"{int(seconds // 60)} دقیقه"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} ساعت {minutes} دقیقه"

# File Scanner Worker Thread
class FileScannerWorker(QThread):
    """Worker thread برای اسکن فایل‌ها"""
    
    file_found = pyqtSignal(dict)  # file_info dict
    scan_completed = pyqtSignal(int)  # total_files
    progress_updated = pyqtSignal(str)  # status_message
    
    def __init__(self, drives: List[str], config: ConfigManager):
        super().__init__()
        self.drives = drives
        self.config = config
        self.is_cancelled = False
        self.file_count = 0
        
    def run(self):
        """اسکن فایل‌ها از همه درایوها"""
        try:
            self.progress_updated.emit("شروع اسکن درایوها...")
            
            for drive in self.drives:
                if self.is_cancelled:
                    break
                    
                self.progress_updated.emit(f"اسکن {drive}...")
                self.scan_directory(drive)
            
            self.scan_completed.emit(self.file_count)
            
        except Exception as e:
            print(f"Scan error: {e}")
    
    def scan_directory(self, directory: str, depth: int = 0):
        """اسکن بازگشتی دایرکتوری"""
        max_depth = self.config.get('file_operations', 'max_scan_depth', 10)
        
        if depth > max_depth or self.is_cancelled:
            return
            
        try:
            for item in os.listdir(directory):
                if self.is_cancelled:
                    break
                    
                item_path = os.path.join(directory, item)
                
                try:
                    if os.path.isfile(item_path):
                        file_info = self.get_file_info(item_path)
                        if file_info:
                            self.file_found.emit(file_info)
                            self.file_count += 1
                            
                    elif os.path.isdir(item_path):
                        # Skip system directories
                        skip_dirs = {
                            'System Volume Information', '$RECYCLE.BIN',
                            'Windows', 'Program Files', 'Program Files (x86)',
                            '/proc', '/sys', '/dev'
                        }
                        
                        if not any(skip_dir in item_path for skip_dir in skip_dirs):
                            self.scan_directory(item_path, depth + 1)
                            
                except (PermissionError, OSError):
                    continue
                    
        except (PermissionError, OSError):
            pass
    
    def get_file_info(self, file_path: str) -> dict:
        """دریافت اطلاعات فایل"""
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': self.format_size(size),
                'raw_size': size,
                'type': self.get_file_type(file_path),
                'drive': os.path.splitdrive(file_path)[0],
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            }
        except:
            return None
    
    def format_size(self, size: int) -> str:
        """فرمت اندازه فایل"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def get_file_type(self, file_path: str) -> str:
        """تشخیص نوع فایل"""
        ext = os.path.splitext(file_path.lower())[1]
        
        type_mapping = {
            'تصاویر': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'ویدیو': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            'صوتی': ['.mp3', '.wav', '.flac', '.aac'],
            'سند': ['.pdf', '.doc', '.docx', '.txt'],
            'آرشیو': ['.zip', '.rar', '.7z']
        }
        
        for file_type, extensions in type_mapping.items():
            if ext in extensions:
                return file_type
                
        return 'فایل' if ext else 'پوشه'
    
    def cancel(self):
        """لغو اسکن"""
        self.is_cancelled = True

# Main Application Class
class PersianFileCopierPyQt5(QMainWindow):
    """برنامه اصلی کپی فایل ایرانی - نسخه PyQt5"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config = ConfigManager()
        self.license_manager = LicenseManager(self.config)
        
        # Initialize data structures
        self.file_cache = {}
        self.active_tasks = {}
        self.task_counter = 0
        self.scanner_worker = None
        
        # Setup UI
        self.init_ui()
        self.setup_styling()
        self.setup_connections()
        
        # Start initial scan and load drives
        self.start_drive_scan()
        self.load_drives_tree()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        # Window settings
        self.setWindowTitle(f"{self.config.get('app_settings', 'app_name')} v{self.config.get('app_settings', 'version')} - {self.config.get('app_settings', 'company')}")
        self.setGeometry(*self.config.get('app_settings', 'window_geometry'))
        
        if self.config.get('app_settings', 'window_maximized'):
            self.showMaximized()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create tab widget
        self.create_tabs(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_tabs(self, parent_layout):
        """ایجاد تب‌های اصلی برنامه"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # File Browser Tab (Main Tab)
        self.create_file_browser_tab()
        
        # Settings Tab
        self.create_settings_tab()
        
        # About Tab
        self.create_about_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_file_browser_tab(self):
        """تب اصلی - مرورگر فایل‌ها و کپی"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Main content area with splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left section - File list (60%)
        self.create_file_section(main_splitter)
        
        # Right section - Split into drives/destinations (top) and tasks (bottom) (40%)
        self.create_right_section(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([600, 400])
        main_layout.addWidget(main_splitter)
        
        self.tab_widget.addTab(tab, "📁 مدیریت فایل‌ها")
    
    def create_file_section(self, parent_splitter):
        """بخش چپ - لیست فایل‌ها با جستجو"""
        file_frame = QFrame()
        file_frame.setFrameStyle(QFrame.StyledPanel)
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(8, 8, 8, 8)
        file_layout.setSpacing(6)
        
        # Header
        header_label = QLabel("📁 فهرست فایل‌ها")
        header_label.setFont(QFont("B Nazanin", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(header_label)
        
        # Compact search section
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.Box)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(6, 6, 6, 6)
        search_layout.setSpacing(4)
        
        # Search row
        search_row = QHBoxLayout()
        search_label = QLabel("🔍")
        search_label.setFont(QFont("Arial", 12))
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("جستجو در فایل‌ها...")
        self.search_entry.setFont(QFont("B Nazanin", 10))
        self.search_entry.setMaximumHeight(28)
        
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_entry)
        search_layout.addLayout(search_row)
        
        # Filter row
        filter_row = QHBoxLayout()
        
        self.format_filter = QComboBox()
        self.format_filter.setFont(QFont("B Nazanin", 9))
        self.format_filter.setMaximumHeight(26)
        format_options = [
            "همه فرمت‌ها", "📷 تصاویر", "🎬 ویدیوها", "🎵 صوتی", 
            "📄 اسناد", "📊 جداول", "📋 ارائه", "📦 آرشیو",
            "⚙️ برنامه", "💻 کد", "🔤 فونت", "🗄️ دیتابیس"
        ]
        self.format_filter.addItems(format_options)
        
        self.size_filter = QComboBox()
        self.size_filter.setFont(QFont("B Nazanin", 9))
        self.size_filter.setMaximumHeight(26)
        size_options = ["همه اندازه‌ها", "🟢 کوچک", "🟡 متوسط", "🟠 بزرگ", "🔴 خیلی بزرگ"]
        self.size_filter.addItems(size_options)
        
        filter_row.addWidget(self.format_filter)
        filter_row.addWidget(self.size_filter)
        search_layout.addLayout(filter_row)
        
        file_layout.addWidget(search_frame)
        
        # File count label
        self.file_count_label = QLabel("تعداد فایل‌ها: 0")
        self.file_count_label.setFont(QFont("B Nazanin", 9))
        self.file_count_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(self.file_count_label)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["📁 نام", "📂 مسیر", "📄 نوع", "💾 اندازه"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.file_tree.setFont(QFont("B Nazanin", 9))
        
        # Set column widths
        self.file_tree.setColumnWidth(0, 150)  # Name
        self.file_tree.setColumnWidth(1, 200)  # Path
        self.file_tree.setColumnWidth(2, 70)   # Type
        self.file_tree.setColumnWidth(3, 80)   # Size
        
        file_layout.addWidget(self.file_tree)
        
        # Action buttons under file list
        action_frame = QFrame()
        action_frame.setFrameStyle(QFrame.Box)
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(4, 4, 4, 4)
        
        self.refresh_btn = QPushButton("🔄 بروزرسانی")
        self.refresh_btn.setFont(QFont("B Nazanin", 9))
        self.refresh_btn.setMaximumHeight(30)
        
        self.clear_search_btn = QPushButton("🗑️ پاک کردن")
        self.clear_search_btn.setFont(QFont("B Nazanin", 9))
        self.clear_search_btn.setMaximumHeight(30)
        
        self.select_all_btn = QPushButton("☑️ انتخاب همه")
        self.select_all_btn.setFont(QFont("B Nazanin", 9))
        self.select_all_btn.setMaximumHeight(30)
        
        action_layout.addWidget(self.refresh_btn)
        action_layout.addWidget(self.clear_search_btn)
        action_layout.addWidget(self.select_all_btn)
        
        file_layout.addWidget(action_frame)
        parent_splitter.addWidget(file_frame)
    

    
    def create_right_section(self, parent_splitter):
        """بخش راست - درایوها/مقصدها (بالا) و تسک‌ها (پایین)"""
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(4)
        
        # Create vertical splitter for top/bottom sections
        right_splitter = QSplitter(Qt.Vertical)
        
        # Top section - Drives and destinations
        self.create_drives_destinations_section(right_splitter)
        
        # Bottom section - Tasks
        self.create_tasks_section(right_splitter)
        
        # Set splitter proportions (50/50)
        right_splitter.setSizes([200, 200])
        right_layout.addWidget(right_splitter)
        
        parent_splitter.addWidget(right_frame)
    
    def create_drives_destinations_section(self, parent_splitter):
        """بخش بالای راست - درایوها و پوشه‌های مقصد"""
        drives_frame = QFrame()
        drives_frame.setFrameStyle(QFrame.Box)
        drives_layout = QVBoxLayout(drives_frame)
        drives_layout.setContentsMargins(6, 6, 6, 6)
        drives_layout.setSpacing(4)
        
        # Header
        header_label = QLabel("🖥️ درایوها و مقصدها")
        header_label.setFont(QFont("B Nazanin", 12, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        drives_layout.addWidget(header_label)
        
        # Drives tree with destinations
        self.drives_tree = QTreeWidget()
        self.drives_tree.setHeaderHidden(True)
        self.drives_tree.setFont(QFont("B Nazanin", 10))
        self.drives_tree.setRootIsDecorated(True)
        self.drives_tree.setIndentation(20)
        
        # Enable click handling
        self.drives_tree.itemClicked.connect(self.on_destination_clicked)
        
        drives_layout.addWidget(self.drives_tree)
        parent_splitter.addWidget(drives_frame)
    
    def create_tasks_section(self, parent_splitter):
        """بخش پایین راست - تسک‌های کپی"""
        tasks_frame = QFrame()
        tasks_frame.setFrameStyle(QFrame.Box)
        tasks_layout = QVBoxLayout(tasks_frame)
        tasks_layout.setContentsMargins(6, 6, 6, 6)
        tasks_layout.setSpacing(4)
        
        # Header
        header_label = QLabel("📊 تسک‌های کپی")
        header_label.setFont(QFont("B Nazanin", 12, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        tasks_layout.addWidget(header_label)
        
        # Task control buttons (larger size)
        task_control_frame = QFrame()
        task_control_layout = QHBoxLayout(task_control_frame)
        task_control_layout.setContentsMargins(4, 4, 4, 4)
        task_control_layout.setSpacing(6)
        
        self.pause_all_btn = QPushButton("⏸️ مکث همه")
        self.pause_all_btn.setFont(QFont("B Nazanin", 10))
        self.pause_all_btn.setMinimumHeight(32)
        self.pause_all_btn.setMinimumWidth(80)
        
        self.resume_all_btn = QPushButton("▶️ ادامه همه")
        self.resume_all_btn.setFont(QFont("B Nazanin", 10))
        self.resume_all_btn.setMinimumHeight(32)
        self.resume_all_btn.setMinimumWidth(80)
        
        self.cancel_all_btn = QPushButton("❌ لغو همه")
        self.cancel_all_btn.setFont(QFont("B Nazanin", 10))
        self.cancel_all_btn.setMinimumHeight(32)
        self.cancel_all_btn.setMinimumWidth(80)
        
        self.clear_completed_btn = QPushButton("🧹 پاک‌سازی")
        self.clear_completed_btn.setFont(QFont("B Nazanin", 10))
        self.clear_completed_btn.setMinimumHeight(32)
        self.clear_completed_btn.setMinimumWidth(80)
        
        task_control_layout.addWidget(self.pause_all_btn)
        task_control_layout.addWidget(self.resume_all_btn)
        task_control_layout.addWidget(self.cancel_all_btn)
        task_control_layout.addWidget(self.clear_completed_btn)
        
        tasks_layout.addWidget(task_control_frame)
        
        # Tasks table (larger fonts and buttons)
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels([
            "📁 مبدأ", "📂 مقصد", "📊 پیشرفت", "🎛️ کنترل"
        ])
        
        # Set column widths (larger)
        self.tasks_table.setColumnWidth(0, 100)   # Source
        self.tasks_table.setColumnWidth(1, 100)   # Destination  
        self.tasks_table.setColumnWidth(2, 120)   # Progress
        self.tasks_table.setColumnWidth(3, 120)   # Control
        
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setFont(QFont("B Nazanin", 9))
        self.tasks_table.setMinimumHeight(150)
        
        # Set row height larger
        self.tasks_table.verticalHeader().setDefaultSectionSize(40)
        
        tasks_layout.addWidget(self.tasks_table)
        parent_splitter.addWidget(tasks_frame)
    
    def set_destination_and_copy(self, path: str):
        """تنظیم مقصد و شروع کپی"""
        expanded_path = os.path.expanduser(path)
        self.destination_entry.setText(expanded_path)
        
        # Start copying selected files immediately
        selected_items = self.file_tree.selectedItems()
        if selected_items:
            self.copy_selected_files()
        else:
            self.show_toast("ابتدا فایل‌هایی را انتخاب کنید", "warning")

    def create_search_section(self, parent_layout):
        """بخش جستجو و فیلتر"""
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.StyledPanel)
        search_layout = QVBoxLayout(search_frame)
        
        # Search row
        search_row = QHBoxLayout()
        
        search_label = QLabel("🔍 جستجو:")
        search_label.setFont(QFont("B Nazanin", 10, QFont.Bold))
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("نام فایل یا پسوند وارد کنید...")
        self.search_entry.setFont(QFont("B Nazanin", 10))
        
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_entry)
        search_layout.addLayout(search_row)
        
        # Filter row
        filter_row = QHBoxLayout()
        
        # Format filter
        format_label = QLabel("📂 فرمت:")
        format_label.setFont(QFont("B Nazanin", 10, QFont.Bold))
        
        self.format_filter = QComboBox()
        self.format_filter.setFont(QFont("B Nazanin", 10))
        format_options = [
            "همه فرمت‌ها",
            "📷 تصاویر (.jpg, .png, .gif, .bmp, .tiff)",
            "🎬 ویدیوها (.mp4, .avi, .mkv, .mov, .wmv)",
            "🎵 صوتی (.mp3, .wav, .flac, .aac, .ogg)",
            "📄 اسناد (.pdf, .doc, .docx, .txt, .rtf)",
            "📊 جداول (.xls, .xlsx, .csv, .ods)",
            "📋 ارائه (.ppt, .pptx, .odp)",
            "📦 آرشیو (.zip, .rar, .7z, .tar, .gz)",
            "⚙️ برنامه (.exe, .msi, .deb, .dmg, .app)",
            "💻 کد (.py, .js, .html, .css, .cpp, .java)",
            "🔤 فونت (.ttf, .otf, .woff, .eot)",
            "🗄️ دیتابیس (.db, .sqlite, .mdb, .sql)"
        ]
        self.format_filter.addItems(format_options)
        
        # Size filter
        size_label = QLabel("💾 اندازه:")
        size_label.setFont(QFont("B Nazanin", 10, QFont.Bold))
        
        self.size_filter = QComboBox()
        self.size_filter.setFont(QFont("B Nazanin", 10))
        size_options = [
            "همه اندازه‌ها",
            "🟢 کوچک (< 1 MB)",
            "🟡 متوسط (1-10 MB)",
            "🟠 بزرگ (10-100 MB)", 
            "🔴 خیلی بزرگ (> 100 MB)"
        ]
        self.size_filter.addItems(size_options)
        
        filter_row.addWidget(format_label)
        filter_row.addWidget(self.format_filter)
        filter_row.addWidget(size_label)
        filter_row.addWidget(self.size_filter)
        filter_row.addStretch()
        search_layout.addLayout(filter_row)
        
        # Action buttons
        buttons_row = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 بروزرسانی")
        self.refresh_btn.setFont(QFont("B Nazanin", 10))
        
        self.clear_search_btn = QPushButton("🗑️ پاک کردن")
        self.clear_search_btn.setFont(QFont("B Nazanin", 10))
        
        self.select_all_btn = QPushButton("☑️ انتخاب همه")
        self.select_all_btn.setFont(QFont("B Nazanin", 10))
        
        buttons_row.addWidget(self.refresh_btn)
        buttons_row.addWidget(self.clear_search_btn)
        buttons_row.addWidget(self.select_all_btn)
        buttons_row.addStretch()
        search_layout.addLayout(buttons_row)
        
        parent_layout.addWidget(search_frame)
    
    def create_file_tree_section(self, parent_splitter):
        """بخش درخت فایل‌ها"""
        file_frame = QFrame()
        file_frame.setFrameStyle(QFrame.StyledPanel)
        file_layout = QVBoxLayout(file_frame)
        
        # Header
        header_label = QLabel("📁 فهرست فایل‌ها")
        header_label.setFont(QFont("B Nazanin", 12, QFont.Bold))
        file_layout.addWidget(header_label)
        
        # File count label
        self.file_count_label = QLabel("تعداد فایل‌ها: 0")
        self.file_count_label.setFont(QFont("B Nazanin", 9))
        file_layout.addWidget(self.file_count_label)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["📁 نام", "📂 مسیر", "📄 نوع", "💾 اندازه", "🖥️ درایو"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.file_tree.setFont(QFont("B Nazanin", 9))
        
        # Set column widths
        self.file_tree.setColumnWidth(0, 200)  # Name
        self.file_tree.setColumnWidth(1, 300)  # Path
        self.file_tree.setColumnWidth(2, 80)   # Type
        self.file_tree.setColumnWidth(3, 100)  # Size
        self.file_tree.setColumnWidth(4, 80)   # Drive
        
        file_layout.addWidget(self.file_tree)
        parent_splitter.addWidget(file_frame)
    
    def create_control_section(self, parent_splitter):
        """بخش کنترل‌های میانی"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.StyledPanel)
        control_layout = QVBoxLayout(control_frame)
        
        # Header
        header_label = QLabel("⚙️ کنترل‌ها")
        header_label.setFont(QFont("B Nazanin", 12, QFont.Bold))
        control_layout.addWidget(header_label)
        
        # Copy controls
        copy_group = QGroupBox("📋 کپی فایل‌ها")
        copy_group.setFont(QFont("B Nazanin", 10, QFont.Bold))
        copy_layout = QVBoxLayout(copy_group)
        
        self.copy_selected_btn = QPushButton("📁 کپی انتخاب شده")
        self.copy_selected_btn.setFont(QFont("B Nazanin", 10))
        self.copy_selected_btn.setMinimumHeight(40)
        
        self.copy_all_btn = QPushButton("📁 کپی همه")
        self.copy_all_btn.setFont(QFont("B Nazanin", 10))
        self.copy_all_btn.setMinimumHeight(40)
        
        copy_layout.addWidget(self.copy_selected_btn)
        copy_layout.addWidget(self.copy_all_btn)
        control_layout.addWidget(copy_group)
        
        # Task controls
        task_group = QGroupBox("📊 مدیریت تسک‌ها")
        task_group.setFont(QFont("B Nazanin", 10, QFont.Bold))
        task_layout = QVBoxLayout(task_group)
        
        self.pause_all_btn = QPushButton("⏸️ مکث همه")
        self.pause_all_btn.setFont(QFont("B Nazanin", 10))
        
        self.resume_all_btn = QPushButton("▶️ ادامه همه")
        self.resume_all_btn.setFont(QFont("B Nazanin", 10))
        
        self.cancel_all_btn = QPushButton("❌ لغو همه")
        self.cancel_all_btn.setFont(QFont("B Nazanin", 10))
        
        self.clear_completed_btn = QPushButton("🧹 پاک کردن تکمیل شده")
        self.clear_completed_btn.setFont(QFont("B Nazanin", 10))
        
        task_layout.addWidget(self.pause_all_btn)
        task_layout.addWidget(self.resume_all_btn)
        task_layout.addWidget(self.cancel_all_btn)
        task_layout.addWidget(self.clear_completed_btn)
        control_layout.addWidget(task_group)
        
        # Overall progress
        progress_group = QGroupBox("📈 پیشرفت کلی")
        progress_group.setFont(QFont("B Nazanin", 10, QFont.Bold))
        progress_layout = QVBoxLayout(progress_group)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setFont(QFont("B Nazanin", 9))
        
        self.overall_status_label = QLabel("آماده")
        self.overall_status_label.setFont(QFont("B Nazanin", 9))
        
        progress_layout.addWidget(self.overall_progress)
        progress_layout.addWidget(self.overall_status_label)
        control_layout.addWidget(progress_group)
        
        control_layout.addStretch()
        parent_splitter.addWidget(control_frame)
    
    def create_tasks_section(self, parent_splitter):
        """بخش تسک‌های کپی"""
        tasks_frame = QFrame()
        tasks_frame.setFrameStyle(QFrame.StyledPanel)
        tasks_layout = QVBoxLayout(tasks_frame)
        
        # Header
        header_label = QLabel("📊 تسک‌های کپی")
        header_label.setFont(QFont("B Nazanin", 12, QFont.Bold))
        tasks_layout.addWidget(header_label)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels([
            "📁 مبدأ", "📂 مقصد", "📊 پیشرفت", "⚡ سرعت", "⏱️ زمان باقی", "🎛️ کنترل"
        ])
        
        # Set column widths
        header = self.tasks_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.tasks_table.setColumnWidth(0, 150)
        self.tasks_table.setColumnWidth(1, 150)
        self.tasks_table.setColumnWidth(2, 100)
        self.tasks_table.setColumnWidth(3, 80)
        self.tasks_table.setColumnWidth(4, 100)
        
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setFont(QFont("B Nazanin", 9))
        
        tasks_layout.addWidget(self.tasks_table)
        parent_splitter.addWidget(tasks_frame)
    
    def create_destinations_tab(self):
        """تب مقصدهای کپی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_label = QLabel("📂 مقصدهای کپی")
        header_label.setFont(QFont("B Nazanin", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # Current destination
        current_group = QGroupBox("📍 مقصد فعلی")
        current_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        current_layout = QHBoxLayout(current_group)
        
        self.destination_entry = QLineEdit()
        self.destination_entry.setFont(QFont("B Nazanin", 10))
        self.destination_entry.setPlaceholderText("مسیر مقصد را انتخاب کنید...")
        
        self.browse_dest_btn = QPushButton("📁 انتخاب پوشه")
        self.browse_dest_btn.setFont(QFont("B Nazanin", 10))
        
        current_layout.addWidget(self.destination_entry)
        current_layout.addWidget(self.browse_dest_btn)
        layout.addWidget(current_group)
        
        # Quick destinations
        quick_group = QGroupBox("⚡ مقصدهای سریع")
        quick_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        quick_layout = QGridLayout(quick_group)
        
        quick_destinations = self.config.get('destinations', 'quick_destinations', {})
        row, col = 0, 0
        
        for name, path in quick_destinations.items():
            btn = QPushButton(name)
            btn.setFont(QFont("B Nazanin", 10))
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, p=path: self.set_destination(p))
            quick_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addWidget(quick_group)
        
        # Recent destinations
        recent_group = QGroupBox("🕒 مقصدهای اخیر")
        recent_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QTreeWidget()
        self.recent_list.setHeaderLabels(["📂 مسیر", "📅 تاریخ"])
        self.recent_list.setFont(QFont("B Nazanin", 10))
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📂 مقصدها")
    
    def create_settings_tab(self):
        """تب تنظیمات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Font settings
        self.create_font_settings(scroll_layout)
        
        # Theme settings  
        self.create_theme_settings(scroll_layout)
        
        # Performance settings
        self.create_performance_settings(scroll_layout)
        
        # License settings
        self.create_license_settings(scroll_layout)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "⚙️ تنظیمات")
    
    def create_font_settings(self, parent_layout):
        """تنظیمات فونت"""
        font_group = QGroupBox("🔤 تنظیمات فونت")
        font_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        font_layout = QFormLayout(font_group)
        
        # Font family
        self.font_family_combo = QComboBox()
        self.font_family_combo.setFont(QFont("B Nazanin", 10))
        
        # Load system fonts
        available_fonts = ["B Nazanin", "Tahoma", "Arial", "Calibri", "IRANSans", "Vazir"]
        self.font_family_combo.addItems(available_fonts)
        
        current_font = self.config.get('font_settings', 'primary_font', 'B Nazanin')
        if current_font in available_fonts:
            self.font_family_combo.setCurrentText(current_font)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.config.get('font_settings', 'font_size', 11))
        
        # Apply button
        self.apply_font_btn = QPushButton("✅ اعمال فونت")
        self.apply_font_btn.setFont(QFont("B Nazanin", 10))
        
        font_layout.addRow("👤 نوع فونت:", self.font_family_combo)
        font_layout.addRow("📏 اندازه فونت:", self.font_size_spin)
        font_layout.addRow("", self.apply_font_btn)
        
        parent_layout.addWidget(font_group)
    
    def create_theme_settings(self, parent_layout):
        """تنظیمات تم"""
        theme_group = QGroupBox("🎨 تنظیمات تم")
        theme_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        theme_layout = QFormLayout(theme_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.setFont(QFont("B Nazanin", 10))
        
        themes = ["🌙 تیره", "☀️ روشن", "🔵 آبی", "🟢 سبز"]
        self.theme_combo.addItems(themes)
        
        current_theme = self.config.get('ui_settings', 'theme', 'dark')
        theme_mapping = {"dark": 0, "light": 1, "blue": 2, "green": 3}
        self.theme_combo.setCurrentIndex(theme_mapping.get(current_theme, 0))
        
        # Animation speed
        self.animation_speed_spin = QSpinBox()
        self.animation_speed_spin.setRange(100, 1000)
        self.animation_speed_spin.setSuffix(" ms")
        self.animation_speed_spin.setValue(self.config.get('ui_settings', 'animation_speed', 300))
        
        # Toast duration
        self.toast_duration_spin = QSpinBox()
        self.toast_duration_spin.setRange(3000, 30000)
        self.toast_duration_spin.setSuffix(" ms")
        self.toast_duration_spin.setValue(self.config.get('ui_settings', 'toast_duration', 10000))
        
        theme_layout.addRow("🎨 تم رنگی:", self.theme_combo)
        theme_layout.addRow("🎬 سرعت انیمیشن:", self.animation_speed_spin)
        theme_layout.addRow("⏱️ مدت نمایش Toast:", self.toast_duration_spin)
        
        # Apply settings button
        self.apply_settings_btn = QPushButton("✅ اعمال تغییرات")
        self.apply_settings_btn.setFont(QFont("B Nazanin", 11, QFont.Bold))
        self.apply_settings_btn.setMinimumHeight(40)
        theme_layout.addRow("", self.apply_settings_btn)
        
        parent_layout.addWidget(theme_group)
    
    def create_performance_settings(self, parent_layout):
        """تنظیمات عملکرد"""
        perf_group = QGroupBox("⚡ تنظیمات عملکرد")
        perf_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        perf_layout = QFormLayout(perf_group)
        
        # Max concurrent tasks
        self.max_tasks_spin = QSpinBox()
        self.max_tasks_spin.setRange(1, 10)
        self.max_tasks_spin.setValue(self.config.get('file_operations', 'max_concurrent_tasks', 3))
        
        # Chunk size
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1024, 65536)
        self.chunk_size_spin.setSuffix(" bytes")
        self.chunk_size_spin.setValue(self.config.get('file_operations', 'chunk_size', 8192))
        
        # Verify copy
        self.verify_copy_check = QCheckBox("تأیید کپی")
        self.verify_copy_check.setFont(QFont("B Nazanin", 10))
        self.verify_copy_check.setChecked(self.config.get('file_operations', 'verify_copy', True))
        
        # Auto retry
        self.auto_retry_check = QCheckBox("تلاش مجدد خودکار")
        self.auto_retry_check.setFont(QFont("B Nazanin", 10))
        self.auto_retry_check.setChecked(self.config.get('file_operations', 'auto_retry', True))
        
        perf_layout.addRow("🔄 حداکثر تسک همزمان:", self.max_tasks_spin)
        perf_layout.addRow("📦 اندازه chunk:", self.chunk_size_spin)
        perf_layout.addRow("✅", self.verify_copy_check)
        perf_layout.addRow("🔁", self.auto_retry_check)
        
        parent_layout.addWidget(perf_group)
    
    def create_license_settings(self, parent_layout):
        """تنظیمات لایسنس"""
        license_group = QGroupBox("🔐 مدیریت لایسنس")
        license_group.setFont(QFont("B Nazanin", 12, QFont.Bold))
        license_layout = QVBoxLayout(license_group)
        
        # License status
        license_info = self.license_manager.get_license_info()
        
        status_layout = QHBoxLayout()
        status_label = QLabel("وضعیت:")
        status_label.setFont(QFont("B Nazanin", 10, QFont.Bold))
        
        self.license_status_label = QLabel(f"{license_info['type']} - {license_info['status']}")
        self.license_status_label.setFont(QFont("B Nazanin", 10))
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.license_status_label)
        status_layout.addStretch()
        license_layout.addLayout(status_layout)
        
        # License key input
        key_layout = QHBoxLayout()
        
        self.license_key_entry = QLineEdit()
        self.license_key_entry.setFont(QFont("B Nazanin", 10))
        self.license_key_entry.setPlaceholderText("کلید لایسنس را وارد کنید...")
        self.license_key_entry.setText(license_info['key'])
        
        self.paste_license_btn = QPushButton("📋")
        self.paste_license_btn.setFont(QFont("Arial", 10))
        self.paste_license_btn.setMaximumWidth(35)
        self.paste_license_btn.setToolTip("جایگذاری از clipboard")
        
        key_layout.addWidget(self.license_key_entry)
        key_layout.addWidget(self.paste_license_btn)
        license_layout.addLayout(key_layout)
        
        # Action buttons (simplified)
        buttons_layout = QHBoxLayout()
        
        self.activate_license_btn = QPushButton("🔓 فعال‌سازی")
        self.activate_license_btn.setFont(QFont("B Nazanin", 10))
        
        self.purchase_license_btn = QPushButton("🛒 خرید نسخه کامل")
        self.purchase_license_btn.setFont(QFont("B Nazanin", 10))
        
        buttons_layout.addWidget(self.activate_license_btn)
        buttons_layout.addWidget(self.purchase_license_btn)
        license_layout.addLayout(buttons_layout)
        
        # License info (single type)
        info_text = QLabel("""
💡 نسخه کامل:
• کپی نامحدود فایل‌ها
• پشتیبانی کامل
• بروزرسانی مادام‌العمر
• قیمت: 500,000 تومان
        """)
        info_text.setFont(QFont("B Nazanin", 9))
        info_text.setWordWrap(True)
        license_layout.addWidget(info_text)
        
        parent_layout.addWidget(license_group)
    
    def create_about_tab(self):
        """تب درباره ما"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(f"{self.config.get('app_settings', 'app_name')} v{self.config.get('app_settings', 'version')}")
        title_label.setFont(QFont("B Nazanin", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        company_label = QLabel(self.config.get('app_settings', 'company'))
        company_label.setFont(QFont("B Nazanin", 14))
        company_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(company_label)
        layout.addWidget(header_frame)
        
        # Content area
        content_scroll = QScrollArea()
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Load about content
        self.load_about_content(content_layout)
        
        content_scroll.setWidget(content_widget)
        content_scroll.setWidgetResizable(True)
        layout.addWidget(content_scroll)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        support_btn = QPushButton("📞 پشتیبانی")
        support_btn.setFont(QFont("B Nazanin", 10))
        support_btn.clicked.connect(self.open_support)
        
        website_btn = QPushButton("🌐 وب‌سایت")
        website_btn.setFont(QFont("B Nazanin", 10))
        website_btn.clicked.connect(self.open_website)
        
        telegram_btn = QPushButton("📱 تلگرام")
        telegram_btn.setFont(QFont("B Nazanin", 10))
        telegram_btn.clicked.connect(self.open_telegram)
        
        buttons_layout.addWidget(support_btn)
        buttons_layout.addWidget(website_btn)
        buttons_layout.addWidget(telegram_btn)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.tab_widget.addTab(tab, "ℹ️ درباره ما")
    
    def load_about_content(self, parent_layout):
        """بارگذاری محتوای درباره ما از فایل HTML"""
        try:
            # Use QTextEdit with rich text (more reliable than QWebView)
            about_text = QTextEdit()
            about_text.setFont(QFont("B Nazanin", 11))
            about_text.setReadOnly(True)
            
            if os.path.exists("about_us.html"):
                with open("about_us.html", 'r', encoding='utf-8') as f:
                    html_content = f.read()
                about_text.setHtml(html_content)
            else:
                # Default rich text content
                default_content = f"""
                <div style="font-family: 'B Nazanin', Tahoma; font-size: 12px; direction: rtl; padding: 10px;">
                    <h1 style="color: #0078d4; text-align: center; margin-bottom: 20px;">
                        {self.config.get('app_settings', 'app_name')} v{self.config.get('app_settings', 'version')}
                    </h1>
                    
                    <div style="background: linear-gradient(135deg, #f0f8ff, #e6f3ff); padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #0078d4;">
                        <p style="text-align: center; font-size: 14px; margin: 0;">
                            نرم‌افزاری پیشرفته و قدرتمند برای مدیریت و کپی فایل‌ها است که با هدف 
                            تسهیل کار کاربران ایرانی طراحی شده است.
                        </p>
                    </div>
                    
                    <h2 style="color: #106ebe; border-bottom: 2px solid #106ebe; padding-bottom: 5px;">🔧 امکانات اصلی:</h2>
                    <ul style="line-height: 1.8;">
                        <li style="margin: 8px 0;">📁 مرور و جستجوی پیشرفته فایل‌ها در همه درایوها</li>
                        <li style="margin: 8px 0;">🔍 فیلتر بر اساس نوع و اندازه فایل (12 دسته)</li>
                        <li style="margin: 8px 0;">⚡ کپی چندگانه با نمایش پیشرفت زنده</li>
                        <li style="margin: 8px 0;">🔤 پشتیبانی کامل از فونت‌های فارسی</li>
                        <li style="margin: 8px 0;">🎨 رابط کاربری زیبا و کاربردی با تم‌های مختلف</li>
                        <li style="margin: 8px 0;">📊 مدیریت پیشرفته تسک‌های کپی</li>
                        <li style="margin: 8px 0;">🚀 عملکرد بالا و بهینه با PyQt5</li>
                        <li style="margin: 8px 0;">🌳 نمایش درختواره‌ای درایوها و پوشه‌ها</li>
                    </ul>
                    
                    <h2 style="color: #106ebe; border-bottom: 2px solid #106ebe; padding-bottom: 5px;">💼 مزایای نسخه کامل:</h2>
                    <ul style="line-height: 1.8;">
                        <li style="margin: 8px 0; color: #27ae60;"><b>✅ کپی نامحدود فایل‌ها</b></li>
                        <li style="margin: 8px 0; color: #27ae60;"><b>📞 پشتیبانی 24/7</b></li>
                        <li style="margin: 8px 0; color: #27ae60;"><b>🔄 بروزرسانی رایگان مادام‌العمر</b></li>
                        <li style="margin: 8px 0; color: #27ae60;"><b>⚙️ امکانات پیشرفته کپی</b></li>
                    </ul>
                    
                    <div style="background: #f0f8ff; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0; border: 2px solid #0078d4;">
                        <h2 style="color: #0078d4; margin-top: 0;">{self.config.get('app_settings', 'company')}</h2>
                        <p style="margin: 10px 0; font-size: 14px;"><b>📞 پشتیبانی:</b> {self.config.get('zarinpal', 'support_telegram')}</p>
                        <p style="margin: 10px 0; font-size: 14px;"><b>🌐 درگاه پرداخت:</b> {self.config.get('zarinpal', 'payment_url')}</p>
                        <p style="margin: 10px 0; font-size: 12px; color: #666;">ورژن: {self.config.get('app_settings', 'version')} - نسخه PyQt5</p>
                    </div>
                    
                    <div style="background: #fff8dc; padding: 15px; border-radius: 8px; border-left: 4px solid #ffa500;">
                        <p style="margin: 0; font-size: 13px; color: #b8860b;">
                            <b>نکته:</b> این نسخه PyQt5 عملکرد بهتری نسبت به نسخه CustomTkinter دارد و برای استفاده حرفه‌ای توصیه می‌شود.
                        </p>
                    </div>
                </div>
                """
                about_text.setHtml(default_content)
            
            parent_layout.addWidget(about_text)
            
        except Exception as e:
            print(f"Error loading about content: {e}")
            # Fallback to simple text
            fallback_label = QLabel(f"خطا در بارگذاری محتوا: {e}")
            fallback_label.setFont(QFont("B Nazanin", 11))
            fallback_label.setWordWrap(True)
            parent_layout.addWidget(fallback_label)
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = self.statusBar()
        self.status_bar.setFont(QFont("B Nazanin", 10))
        
        # Status label
        self.status_label = QLabel("آماده")
        self.status_bar.addWidget(self.status_label)
        
        # File count
        self.status_file_count = QLabel("فایل‌ها: 0")
        self.status_bar.addPermanentWidget(self.status_file_count)
        
        # License status
        license_info = self.license_manager.get_license_info()
        self.status_license = QLabel(f"لایسنس: {license_info['type']}")
        self.status_bar.addPermanentWidget(self.status_license)
    
    def create_menu_bar(self):
        """ایجاد نوار منو"""
        menubar = self.menuBar()
        menubar.setFont(QFont("B Nazanin", 10))
        
        # File menu
        file_menu = menubar.addMenu("📁 فایل")
        
        refresh_action = file_menu.addAction("🔄 بروزرسانی")
        refresh_action.triggered.connect(self.refresh_files)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("🚪 خروج")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("🔧 ابزارها")
        
        clear_cache_action = tools_menu.addAction("🗑️ پاک کردن کش")
        clear_cache_action.triggered.connect(self.clear_cache)
        
        # Help menu
        help_menu = menubar.addMenu("❓ راهنما")
        
        about_action = help_menu.addAction("ℹ️ درباره")
        about_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        
                 support_action = help_menu.addAction("📞 پشتیبانی")
         support_action.triggered.connect(self.open_support)
    
    def setup_styling(self):
        """تنظیم استایل و تم برنامه"""
        theme = self.config.get('ui_settings', 'theme', 'dark')
        self.apply_theme(theme)
    
    def apply_theme(self, theme_name):
        """اعمال تم مشخص"""
        if theme_name == "light":
            self.setStyleSheet(self.get_light_theme())
        elif theme_name == "blue":
            self.setStyleSheet(self.get_blue_theme())
        elif theme_name == "green":
            self.setStyleSheet(self.get_green_theme())
        else:  # dark
            self.setStyleSheet(self.get_dark_theme())
    
    def get_dark_theme(self):
        """تم تیره بهبود یافته"""
        return """
            QMainWindow {
                background-color: #404040;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #666666;
                background-color: #4a4a4a;
            }
            QTabWidget::tab-bar {
                alignment: right;
            }
            QTabBar::tab {
                background-color: #606060;
                color: #ffffff;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                border-bottom: 2px solid #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #707070;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666666;
                border-radius: 6px;
                margin: 6px;
                padding-top: 12px;
                color: #ffffff;
                background-color: #4a4a4a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #4a4a4a;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            QTreeWidget, QTableWidget {
                border: 1px solid #666666;
                alternate-background-color: #4f4f4f;
                background-color: #454545;
                color: #ffffff;
                gridline-color: #666666;
            }
            QTreeWidget::item:selected, QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::item:hover, QTableWidget::item:hover {
                background-color: #555555;
            }
            QHeaderView::section {
                background-color: #606060;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #666666;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                background-color: #4a4a4a;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px;
                background-color: #4a4a4a;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 1px solid #666666;
                width: 8px;
                height: 8px;
                background-color: #ffffff;
            }
            QFrame {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 1px;
            }
            QFrame[frameShape="4"] { /* QFrame.Box */
                border: 2px solid #666666;
                border-radius: 6px;
            }
            QFrame[frameShape="1"] { /* QFrame.StyledPanel */
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #4a4a4a;
            }
            QLabel {
                color: #ffffff;
            }
            QStatusBar {
                background-color: #404040;
                color: #ffffff;
                border-top: 1px solid #666666;
            }
            QMenuBar {
                background-color: #404040;
                color: #ffffff;
                border-bottom: 1px solid #666666;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            QMenu {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #4a4a4a;
                border: 1px solid #666666;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
            }
            QSpinBox {
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 4px;
                background-color: #4a4a4a;
                color: #ffffff;
            }
        """
    
    def get_light_theme(self):
        """تم روشن"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 6px;
                margin: 6px;
                padding-top: 12px;
                color: #333333;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTreeWidget, QTableWidget {
                border: 1px solid #cccccc;
                alternate-background-color: #f9f9f9;
                background-color: #ffffff;
                color: #333333;
            }
            QTreeWidget::item:selected, QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QLineEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0078d4;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QLabel {
                color: #333333;
            }
        """
    
    def get_blue_theme(self):
        """تم آبی"""
        return """
            QMainWindow {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #34495e;
                background-color: #34495e;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #34495e;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 6px;
                margin: 6px;
                padding-top: 12px;
                color: #ecf0f1;
                background-color: #34495e;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QTreeWidget, QTableWidget {
                border: 1px solid #34495e;
                alternate-background-color: #2c3e50;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QTreeWidget::item:selected, QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QLineEdit, QComboBox {
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 6px;
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QFrame {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 4px;
            }
            QLabel {
                color: #ecf0f1;
            }
        """
    
    def get_green_theme(self):
        """تم سبز"""
        return """
            QMainWindow {
                background-color: #27ae60;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #2ecc71;
                background-color: #2ecc71;
            }
            QTabBar::tab {
                background-color: #2ecc71;
                color: #ffffff;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #27ae60;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #2ecc71;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 6px;
                margin: 6px;
                padding-top: 12px;
                color: #ffffff;
                background-color: #2ecc71;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QTreeWidget, QTableWidget {
                border: 1px solid #2ecc71;
                alternate-background-color: #27ae60;
                background-color: #2ecc71;
                color: #ffffff;
            }
            QTreeWidget::item:selected, QTableWidget::item:selected {
                background-color: #27ae60;
                color: white;
            }
            QLineEdit, QComboBox {
                border: 1px solid #2ecc71;
                border-radius: 4px;
                padding: 6px;
                background-color: #27ae60;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #229954;
            }
            QFrame {
                background-color: #2ecc71;
                border: 1px solid #27ae60;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
            }
        """
    
    def setup_connections(self):
        """اتصال سیگنال‌ها و اسلات‌ها"""
        # Search and filter connections
        self.search_entry.textChanged.connect(self.apply_filters)
        self.format_filter.currentTextChanged.connect(self.apply_filters)
        self.size_filter.currentTextChanged.connect(self.apply_filters)
        
        # Button connections
        self.refresh_btn.clicked.connect(self.refresh_files)
        self.clear_search_btn.clicked.connect(self.clear_filters)
        self.select_all_btn.clicked.connect(self.select_all_files)
        

        
        # Task control buttons
        self.pause_all_btn.clicked.connect(self.pause_all_tasks)
        self.resume_all_btn.clicked.connect(self.resume_all_tasks)
        self.cancel_all_btn.clicked.connect(self.cancel_all_tasks)
        self.clear_completed_btn.clicked.connect(self.clear_completed_tasks)
        
        # Destination buttons
        self.browse_dest_btn.clicked.connect(self.browse_destination)
        
        # Settings buttons
        self.apply_font_btn.clicked.connect(self.apply_font_settings)
        self.apply_settings_btn.clicked.connect(self.apply_all_settings)
        self.paste_license_btn.clicked.connect(self.paste_license_key)
        self.activate_license_btn.clicked.connect(self.activate_license)
        self.purchase_license_btn.clicked.connect(self.purchase_license)
        
        # File tree double click
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_click)
    
    def start_drive_scan(self):
        """شروع اسکن درایوها"""
        try:
            # Get available drives
            drives = []
            for partition in psutil.disk_partitions():
                if partition.mountpoint:
                    drives.append(partition.mountpoint)
            
            if drives:
                self.update_status("شروع اسکن درایوها...")
                self.scanner_worker = FileScannerWorker(drives, self.config)
                self.scanner_worker.file_found.connect(self.add_file_to_cache)
                self.scanner_worker.scan_completed.connect(self.scan_completed)
                self.scanner_worker.progress_updated.connect(self.update_status)
                self.scanner_worker.start()
            
        except Exception as e:
            print(f"Error starting drive scan: {e}")
            self.show_toast(f"خطا در اسکن درایوها: {e}", "error")
    
    def add_file_to_cache(self, file_info: dict):
        """اضافه کردن فایل به کش"""
        try:
            file_path = file_info['path']
            self.file_cache[file_path] = file_info
            
            # Add to tree if matches current filters
            if self.matches_current_filters(file_info):
                self.add_file_to_tree(file_info)
                
        except Exception as e:
            print(f"Error adding file to cache: {e}")
    
    def add_file_to_tree(self, file_info: dict):
        """اضافه کردن فایل به درخت"""
        try:
            item = QTreeWidgetItem([
                file_info['name'],
                file_info['path'],
                file_info['type'],
                file_info['size'],
                file_info['drive']
            ])
            self.file_tree.addTopLevelItem(item)
            
            # Update file count
            current_count = self.file_tree.topLevelItemCount()
            self.file_count_label.setText(f"تعداد فایل‌ها: {current_count}")
            self.status_file_count.setText(f"فایل‌ها: {len(self.file_cache)}")
            
        except Exception as e:
            print(f"Error adding file to tree: {e}")
    
    def scan_completed(self, total_files: int):
        """تکمیل اسکن"""
        self.update_status(f"اسکن تکمیل شد - {total_files} فایل یافت شد")
        self.show_toast(f"اسکن تکمیل شد! {total_files} فایل یافت شد", "success")
    
    def matches_current_filters(self, file_info: dict) -> bool:
        """بررسی انطباق فایل با فیلترهای فعلی"""
        try:
            # Search filter
            search_term = self.search_entry.text().lower().strip()
            if search_term:
                name = file_info['name'].lower()
                if not (search_term in name or 
                       (search_term.startswith(".") and name.endswith(search_term))):
                    return False
            
            # Format filter
            format_filter = self.format_filter.currentText()
            if format_filter != "همه فرمت‌ها":
                file_category = self.get_file_category(file_info['name'])
                if not self.matches_format_filter(file_category, format_filter):
                    return False
            
            # Size filter
            size_filter = self.size_filter.currentText()
            if size_filter != "همه اندازه‌ها":
                if not self.matches_size_filter(file_info.get('raw_size', 0), size_filter):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking filters: {e}")
            return True
    
    def get_file_category(self, filename: str) -> str:
        """دریافت دسته‌بندی فایل"""
        ext = os.path.splitext(filename.lower())[1]
        
        categories = self.config.get('filters', 'file_categories', {})
        for category, extensions in categories.items():
            if ext in extensions:
                return category
        return 'سایر'
    
    def matches_format_filter(self, file_category: str, format_filter: str) -> bool:
        """بررسی انطباق با فیلتر فرمت"""
        format_mapping = {
            "📷 تصاویر": "تصاویر",
            "🎬 ویدیوها": "ویدیوها", 
            "🎵 صوتی": "صوتی",
            "📄 اسناد": "اسناد",
            "📊 جداول": "جداول",
            "📋 ارائه": "ارائه",
            "📦 آرشیو": "آرشیو",
            "⚙️ برنامه": "برنامه",
            "💻 کد": "کد",
            "🔤 فونت": "فونت",
            "🗄️ دیتابیس": "دیتابیس"
        }
        
        for filter_key, category in format_mapping.items():
            if format_filter.startswith(filter_key.split()[0]):
                return file_category == category
        
        return False
    
    def matches_size_filter(self, raw_size: int, size_filter: str) -> bool:
        """بررسی انطباق با فیلتر اندازه"""
        if "کوچک" in size_filter:
            return raw_size < 1024 * 1024  # < 1 MB
        elif "متوسط" in size_filter:
            return 1024 * 1024 <= raw_size <= 10 * 1024 * 1024  # 1-10 MB
        elif "بزرگ" in size_filter and "خیلی" not in size_filter:
            return 10 * 1024 * 1024 < raw_size <= 100 * 1024 * 1024  # 10-100 MB
        elif "خیلی بزرگ" in size_filter:
            return raw_size > 100 * 1024 * 1024  # > 100 MB
        
        return True
    
    def apply_filters(self):
        """اعمال فیلترها"""
        try:
            # Clear current tree
            self.file_tree.clear()
            
            # Add files that match filters
            file_count = 0
            for file_path, file_info in self.file_cache.items():
                if self.matches_current_filters(file_info):
                    self.add_file_to_tree(file_info)
                    file_count += 1
            
            self.file_count_label.setText(f"تعداد فایل‌ها: {file_count}")
            
        except Exception as e:
            print(f"Error applying filters: {e}")
    
    def clear_filters(self):
        """پاک کردن فیلترها"""
        self.search_entry.clear()
        self.format_filter.setCurrentIndex(0)
        self.size_filter.setCurrentIndex(0)
        self.apply_filters()
    
    def select_all_files(self):
        """انتخاب همه فایل‌ها"""
        self.file_tree.selectAll()
    
    def refresh_files(self):
        """بروزرسانی فهرست فایل‌ها"""
        self.file_cache.clear()
        self.file_tree.clear()
        self.file_count_label.setText("تعداد فایل‌ها: 0")
        self.start_drive_scan()
    
    def copy_selected_files(self):
        """کپی فایل‌های انتخاب شده"""
        try:
            selected_items = self.file_tree.selectedItems()
            if not selected_items:
                self.show_toast("لطفاً فایل‌هایی را انتخاب کنید", "warning")
                return
            
            destination = self.destination_entry.text().strip()
            if not destination:
                self.show_toast("لطفاً مقصد کپی را انتخاب کنید", "warning")
                return
            
            # Check license limit
            if not self.license_manager.check_file_limit(len(selected_items)):
                self.show_license_restriction()
                return
            
            # Extract file paths
            file_paths = []
            for item in selected_items:
                file_path = item.text(1)  # Path column
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            if file_paths:
                self.start_copy_task(file_paths, destination)
            else:
                self.show_toast("فایل‌های انتخاب شده یافت نشدند", "error")
                
        except Exception as e:
            print(f"Error copying selected files: {e}")
            self.show_toast(f"خطا در کپی فایل‌ها: {e}", "error")
    
    def copy_all_files(self):
        """کپی همه فایل‌ها"""
        try:
            destination = self.destination_entry.text().strip()
            if not destination:
                self.show_toast("لطفاً مقصد کپی را انتخاب کنید", "warning")
                return
            
            # Get all visible files
            file_paths = []
            for i in range(self.file_tree.topLevelItemCount()):
                item = self.file_tree.topLevelItem(i)
                file_path = item.text(1)
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            if not file_paths:
                self.show_toast("فایلی برای کپی یافت نشد", "warning")
                return
            
            # Check license limit
            if not self.license_manager.check_file_limit(len(file_paths)):
                self.show_license_restriction()
                return
            
            self.start_copy_task(file_paths, destination)
            
        except Exception as e:
            print(f"Error copying all files: {e}")
            self.show_toast(f"خطا در کپی فایل‌ها: {e}", "error")
    
    def start_copy_task(self, file_paths: List[str], destination: str):
        """شروع تسک کپی"""
        try:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            
            # Create copy worker
            worker = FileCopyWorker(task_id, file_paths, destination, self.config)
            worker.progress_updated.connect(self.update_task_progress)
            worker.task_completed.connect(self.task_completed)
            worker.error_occurred.connect(self.task_error)
            
            # Add to active tasks
            self.active_tasks[task_id] = {
                'worker': worker,
                'source_files': file_paths,
                'destination': destination,
                'status': 'running',
                'progress': 0
            }
            
            # Add to tasks table
            self.add_task_to_table(task_id, file_paths, destination)
            
            # Start worker
            worker.start()
            
            self.show_toast(f"شروع کپی {len(file_paths)} فایل", "info")
            
        except Exception as e:
            print(f"Error starting copy task: {e}")
            self.show_toast(f"خطا در شروع کپی: {e}", "error")
    
    def add_task_to_table(self, task_id: str, file_paths: List[str], destination: str):
        """اضافه کردن تسک به جدول"""
        try:
            row = self.tasks_table.rowCount()
            self.tasks_table.insertRow(row)
            
            # Source (file count)
            source_text = f"{len(file_paths)} فایل"
            source_item = QTableWidgetItem(source_text)
            source_item.setFont(QFont("B Nazanin", 10))
            self.tasks_table.setItem(row, 0, source_item)
            
            # Destination
            dest_text = os.path.basename(destination) or destination
            dest_item = QTableWidgetItem(dest_text)
            dest_item.setFont(QFont("B Nazanin", 10))
            self.tasks_table.setItem(row, 1, dest_item)
            
            # Progress with speed combined (larger)
            progress_widget = QWidget()
            progress_layout = QVBoxLayout(progress_widget)
            progress_layout.setContentsMargins(4, 4, 4, 4)
            progress_layout.setSpacing(2)
            
            progress_bar = QProgressBar()
            progress_bar.setFont(QFont("B Nazanin", 9))
            progress_bar.setMinimumHeight(16)
            progress_layout.addWidget(progress_bar)
            
            speed_label = QLabel("0 MB/s")
            speed_label.setFont(QFont("B Nazanin", 9))
            speed_label.setAlignment(Qt.AlignCenter)
            progress_layout.addWidget(speed_label)
            
            self.tasks_table.setCellWidget(row, 2, progress_widget)
            
            # Individual control buttons (larger)
            control_widget = QWidget()
            control_layout = QHBoxLayout(control_widget)
            control_layout.setContentsMargins(4, 4, 4, 4)
            control_layout.setSpacing(4)
            
            pause_btn = QPushButton("⏸️")
            pause_btn.setMinimumSize(28, 28)
            pause_btn.setFont(QFont("Arial", 10))
            pause_btn.setToolTip("مکث")
            pause_btn.clicked.connect(lambda: self.pause_task(task_id))
            
            resume_btn = QPushButton("▶️")
            resume_btn.setMinimumSize(28, 28)
            resume_btn.setFont(QFont("Arial", 10))
            resume_btn.setToolTip("ادامه")
            resume_btn.clicked.connect(lambda: self.resume_task(task_id))
            
            cancel_btn = QPushButton("❌")
            cancel_btn.setMinimumSize(28, 28)
            cancel_btn.setFont(QFont("Arial", 10))
            cancel_btn.setToolTip("لغو")
            cancel_btn.clicked.connect(lambda: self.cancel_task(task_id))
            
            control_layout.addWidget(pause_btn)
            control_layout.addWidget(resume_btn)
            control_layout.addWidget(cancel_btn)
            
            self.tasks_table.setCellWidget(row, 3, control_widget)
            
            # Store row index and widgets for updates
            self.active_tasks[task_id]['row'] = row
            self.active_tasks[task_id]['progress_bar'] = progress_bar
            self.active_tasks[task_id]['speed_label'] = speed_label
            
        except Exception as e:
            print(f"Error adding task to table: {e}")
    
    def update_task_progress(self, task_id: str, progress: int, speed: str, eta: str):
        """بروزرسانی پیشرفت تسک"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task['progress'] = progress
                
                # Update progress bar and speed in the combined widget
                progress_bar = task.get('progress_bar')
                speed_label = task.get('speed_label')
                
                if progress_bar:
                    progress_bar.setValue(progress)
                    progress_bar.setFormat(f"{progress}% - {eta}")
                
                if speed_label:
                    speed_label.setText(speed)
                
        except Exception as e:
            print(f"Error updating task progress: {e}")
    
    def task_completed(self, task_id: str, success: bool, message: str):
        """تسک تکمیل شد"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task['status'] = 'completed' if success else 'failed'
                
                # Update progress bar
                progress_bar = task.get('progress_bar')
                speed_label = task.get('speed_label')
                
                if progress_bar:
                    if success:
                        progress_bar.setValue(100)
                        progress_bar.setFormat("✅ تکمیل شد")
                    else:
                        progress_bar.setFormat("❌ خطا")
                
                if speed_label:
                    speed_label.setText("تکمیل شد" if success else "خطا")
                
                # Show notification
                toast_type = "success" if success else "error"
                self.show_toast(message, toast_type)
                
                # Auto-remove completed tasks after delay
                QTimer.singleShot(30000, lambda: self.remove_completed_task(task_id))
                
        except Exception as e:
            print(f"Error handling task completion: {e}")
    
    def task_error(self, task_id: str, error_message: str):
        """خطا در تسک"""
        self.show_toast(f"خطا در تسک {task_id}: {error_message}", "error")
    

    
    def pause_task(self, task_id: str):
        """مکث تسک"""
        try:
            if task_id in self.active_tasks:
                worker = self.active_tasks[task_id]['worker']
                if hasattr(worker, 'pause'):
                    worker.pause()
                    self.show_toast(f"تسک {task_id} متوقف شد", "info")
        except Exception as e:
            print(f"Error pausing task: {e}")
    
    def resume_task(self, task_id: str):
        """ادامه تسک"""
        try:
            if task_id in self.active_tasks:
                worker = self.active_tasks[task_id]['worker']
                if hasattr(worker, 'resume'):
                    worker.resume()
                    self.show_toast(f"تسک {task_id} ادامه یافت", "info")
        except Exception as e:
            print(f"Error resuming task: {e}")
    
    def cancel_task(self, task_id: str):
        """لغو تسک"""
        try:
            if task_id in self.active_tasks:
                worker = self.active_tasks[task_id]['worker']
                if hasattr(worker, 'cancel'):
                    worker.cancel()
                    self.active_tasks[task_id]['status'] = 'cancelled'
                    self.show_toast(f"تسک {task_id} لغو شد", "warning")
        except Exception as e:
            print(f"Error cancelling task: {e}")
    
    def pause_all_tasks(self):
        """مکث همه تسک‌ها"""
        for task_id in self.active_tasks:
            self.pause_task(task_id)
    
    def resume_all_tasks(self):
        """ادامه همه تسک‌ها"""
        for task_id in self.active_tasks:
            self.resume_task(task_id)
    
    def cancel_all_tasks(self):
        """لغو همه تسک‌ها"""
        for task_id in list(self.active_tasks.keys()):
            self.cancel_task(task_id)
    
    def clear_completed_tasks(self):
        """پاک کردن تسک‌های تکمیل شده"""
        try:
            completed_tasks = []
            for task_id, task in self.active_tasks.items():
                if task['status'] in ['completed', 'failed', 'cancelled']:
                    completed_tasks.append(task_id)
            
            for task_id in completed_tasks:
                self.remove_completed_task(task_id)
            
            if completed_tasks:
                self.show_toast(f"{len(completed_tasks)} تسک تکمیل شده پاک شد", "info")
            else:
                self.show_toast("تسک تکمیل شده‌ای یافت نشد", "warning")
                
        except Exception as e:
            print(f"Error clearing completed tasks: {e}")
    
    def remove_completed_task(self, task_id: str):
        """حذف تسک تکمیل شده"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                row = task.get('row', -1)
                
                if row >= 0:
                    self.tasks_table.removeRow(row)
                    
                    # Update row indices for remaining tasks
                    for other_task in self.active_tasks.values():
                        if other_task.get('row', -1) > row:
                            other_task['row'] -= 1
                
                del self.active_tasks[task_id]
                
        except Exception as e:
            print(f"Error removing completed task: {e}")
    
    def browse_destination(self):
        """انتخاب پوشه مقصد"""
        try:
            current_dir = self.destination_entry.text() or os.path.expanduser("~")
            destination = QFileDialog.getExistingDirectory(
                self, 
                "انتخاب پوشه مقصد",
                current_dir
            )
            
            if destination:
                self.destination_entry.setText(destination)
                self.config.set('app_settings', 'last_destination', destination)
                
                # Add to recent destinations
                recent = self.config.get('destinations', 'recent_destinations', [])
                if destination not in recent:
                    recent.insert(0, destination)
                    recent = recent[:10]  # Keep only last 10
                    self.config.set('destinations', 'recent_destinations', recent)
                
                self.update_recent_destinations()
                
        except Exception as e:
            print(f"Error browsing destination: {e}")
    
    def set_destination(self, path: str):
        """تنظیم مقصد"""
        expanded_path = os.path.expanduser(path)
        self.destination_entry.setText(expanded_path)
    
    def update_recent_destinations(self):
        """بروزرسانی مقصدهای اخیر"""
        try:
            self.recent_list.clear()
            recent = self.config.get('destinations', 'recent_destinations', [])
            
            for dest in recent:
                item = QTreeWidgetItem([dest, datetime.now().strftime("%Y-%m-%d")])
                item.setFont(0, QFont("B Nazanin", 10))
                item.setFont(1, QFont("B Nazanin", 10))
                self.recent_list.addTopLevelItem(item)
                
        except Exception as e:
            print(f"Error updating recent destinations: {e}")
    
    def apply_font_settings(self):
        """اعمال تنظیمات فونت"""
        try:
            font_family = self.font_family_combo.currentText()
            font_size = self.font_size_spin.value()
            
            # Update config
            self.config.set('font_settings', 'primary_font', font_family)
            self.config.set('font_settings', 'font_size', font_size)
            
            # Apply to application
            font = QFont(font_family, font_size)
            QApplication.instance().setFont(font)
            
            self.show_toast(f"فونت {font_family} اعمال شد", "success")
            
        except Exception as e:
            print(f"Error applying font: {e}")
            self.show_toast(f"خطا در اعمال فونت: {e}", "error")
    
    def paste_license_key(self):
        """جایگذاری کلید لایسنس از clipboard"""
        try:
            clipboard = QApplication.clipboard()
            license_key = clipboard.text().strip()
            
            if license_key:
                self.license_key_entry.setText(license_key)
                self.show_toast("کلید لایسنس جایگذاری شد", "info")
            else:
                self.show_toast("clipboard خالی است", "warning")
                
        except Exception as e:
            print(f"Error pasting license: {e}")
    
    def activate_license(self):
        """فعال‌سازی لایسنس"""
        try:
            license_key = self.license_key_entry.text().strip()
            if not license_key:
                self.show_toast("لطفاً کلید لایسنس را وارد کنید", "warning")
                return
            
            success, message = self.license_manager.activate_license(license_key)
            
            if success:
                self.show_toast(message, "success")
                # Update license status display
                license_info = self.license_manager.get_license_info()
                self.license_status_label.setText(f"{license_info['type']} - {license_info['status']}")
                self.status_license.setText(f"لایسنس: {license_info['type']}")
            else:
                self.show_toast(message, "error")
                
        except Exception as e:
            print(f"Error activating license: {e}")
            self.show_toast(f"خطا در فعال‌سازی: {e}", "error")
    
    def purchase_license(self):
        """خرید لایسنس"""
        try:
            # Show purchase info
            purchase_info = f"""
🛒 خرید لایسنس {self.config.get('app_settings', 'app_name')}

📞 راه‌های تماس:
• تلفن: {self.config.get('zarinpal', 'company_phone')}
• ایمیل: {self.config.get('zarinpal', 'company_email')}
• تلگرام: {self.config.get('zarinpal', 'support_telegram')}

💰 قیمت‌ها:
• نسخه شخصی: 500,000 تومان
• نسخه تجاری: 1,200,000 تومان
• نسخه سازمانی: 2,500,000 تومان

🎁 مزایای نسخه کامل:
• کپی نامحدود فایل‌ها
• پشتیبانی 24/7
• بروزرسانی رایگان مادام‌العمر
• امکانات پیشرفته کپی

📋 مراحل خرید:
1. کلیک روی "بله" برای انتقال به درگاه پرداخت
2. پرداخت را انجام دهید
3. بعد از پرداخت، رسید را به آی دی تلگرام شرکت ارسال نمایید: {self.config.get('zarinpal', 'support_telegram')}

آیا می‌خواهید به سایت فروش منتقل شوید؟
            """
            
            reply = QMessageBox.question(
                self,
                "خرید لایسنس",
                purchase_info,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                payment_url = self.config.get('zarinpal', 'payment_url')
                webbrowser.open(payment_url)
                self.show_toast("در حال انتقال به درگاه پرداخت...", "info")
            
        except Exception as e:
            print(f"Error in purchase: {e}")
            self.show_toast(f"خطا در نمایش اطلاعات خرید: {e}", "error")
    
    def show_license_restriction(self):
        """نمایش محدودیت لایسنس"""
        license_info = self.license_manager.get_license_info()
        max_files = license_info['max_files']
        
        restriction_msg = f"""
🔒 محدودیت نسخه آزمایشی

شما می‌توانید حداکثر {max_files} فایل کپی کنید.
برای کپی نامحدود فایل‌ها، نسخه کامل را خریداری کنید.

آیا می‌خواهید به صفحه خرید منتقل شوید؟
        """
        
        reply = QMessageBox.question(
            self,
            "محدودیت لایسنس",
            restriction_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.purchase_license()
    
    def on_file_double_click(self, item: QTreeWidgetItem, column: int):
        """کلیک دوبل روی فایل"""
        try:
            file_path = item.text(1)  # Path column
            if os.path.exists(file_path):
                os.startfile(file_path)  # Windows
                # For Linux/Mac: subprocess.run(['xdg-open', file_path])
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def clear_cache(self):
        """پاک کردن کش"""
        self.file_cache.clear()
        self.file_tree.clear()
        self.file_count_label.setText("تعداد فایل‌ها: 0")
        self.status_file_count.setText("فایل‌ها: 0")
        self.show_toast("کش پاک شد", "info")
    
    def open_support(self):
        """باز کردن پشتیبانی"""
        telegram_url = f"https://t.me/{self.config.get('zarinpal', 'support_telegram', 'PersianFileSupport').replace('@', '')}"
        webbrowser.open(telegram_url)
    
    def open_website(self):
        """باز کردن وب‌سایت"""
        webbrowser.open(self.config.get('zarinpal', 'payment_url'))
    
    def open_telegram(self):
        """باز کردن تلگرام"""
        self.open_support()
    
    def show_toast(self, message: str, toast_type: str = "info"):
        """نمایش Toast notification"""
        try:
            duration = self.config.get('ui_settings', 'toast_duration', 10000)
            toast = ToastNotification(self, message, toast_type, duration)
            toast.show()
        except Exception as e:
            print(f"Error showing toast: {e}")
    
    def update_status(self, message: str):
        """بروزرسانی نوار وضعیت"""
        self.status_label.setText(message)
    
    def load_drives_tree(self):
        """بارگذاری درخت درایوها و پوشه‌ها"""
        try:
            self.drives_tree.clear()
            
            # Get all available drives
            for partition in psutil.disk_partitions():
                if partition.mountpoint:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        free_space = self.format_size(usage.free)
                        total_space = self.format_size(usage.total)
                        
                        # Create drive item
                        drive_text = f"🖥️ {partition.mountpoint} ({free_space} آزاد از {total_space})"
                        drive_item = QTreeWidgetItem([drive_text])
                        drive_item.setData(0, Qt.UserRole, partition.mountpoint)  # Store path
                        drive_item.setData(0, Qt.UserRole + 1, "drive")  # Mark as drive
                        
                        # Add main folders to drive
                        self.add_drive_folders(drive_item, partition.mountpoint)
                        
                        self.drives_tree.addTopLevelItem(drive_item)
                        
                    except (PermissionError, OSError):
                        continue
            
            # Add quick destinations at top
            self.add_quick_destinations()
            
        except Exception as e:
            print(f"Error loading drives tree: {e}")
    
    def add_quick_destinations(self):
        """اضافه کردن مقصدهای سریع به بالای درخت"""
        try:
            quick_item = QTreeWidgetItem(["📂 مقصدهای سریع"])
            quick_item.setData(0, Qt.UserRole + 1, "quick")
            
            quick_destinations = [
                ("🖥️ دسکتاپ", "~/Desktop"),
                ("📁 مستندات", "~/Documents"),
                ("📥 دانلودها", "~/Downloads"),
                ("🎵 موزیک", "~/Music"),
                ("🎬 ویدیوها", "~/Videos"),
                ("📷 عکس‌ها", "~/Pictures")
            ]
            
            for name, path in quick_destinations:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    dest_item = QTreeWidgetItem([name])
                    dest_item.setData(0, Qt.UserRole, expanded_path)
                    dest_item.setData(0, Qt.UserRole + 1, "folder")
                    quick_item.addChild(dest_item)
            
            # Insert at top
            self.drives_tree.insertTopLevelItem(0, quick_item)
            quick_item.setExpanded(True)
            
        except Exception as e:
            print(f"Error adding quick destinations: {e}")
    
    def add_drive_folders(self, drive_item, drive_path):
        """اضافه کردن پوشه‌های اصلی درایو"""
        try:
            # Add common directories
            common_dirs = ["Users", "Program Files", "Windows", "Documents and Settings"]
            
            # For Unix-like systems
            if not drive_path.endswith('\\'):
                common_dirs = ["home", "usr", "var", "opt", "etc"]
            
            for dir_name in common_dirs:
                dir_path = os.path.join(drive_path, dir_name)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    try:
                        folder_item = QTreeWidgetItem([f"📁 {dir_name}"])
                        folder_item.setData(0, Qt.UserRole, dir_path)
                        folder_item.setData(0, Qt.UserRole + 1, "folder")
                        
                        # Add dummy child to make it expandable
                        dummy = QTreeWidgetItem(["..."])
                        folder_item.addChild(dummy)
                        
                        drive_item.addChild(folder_item)
                    except (PermissionError, OSError):
                        continue
            
            # Add direct drive access
            drive_direct = QTreeWidgetItem([f"📂 ریشه {drive_path}"])
            drive_direct.setData(0, Qt.UserRole, drive_path)
            drive_direct.setData(0, Qt.UserRole + 1, "folder")
            drive_item.addChild(drive_direct)
            
        except Exception as e:
            print(f"Error adding drive folders: {e}")
    
    def on_destination_clicked(self, item, column):
        """کلیک روی مقصد در درخت"""
        try:
            item_type = item.data(0, Qt.UserRole + 1)
            if item_type in ["folder", "drive"]:
                destination_path = item.data(0, Qt.UserRole)
                if destination_path:
                    # Check if files are selected
                    selected_items = self.file_tree.selectedItems()
                    if selected_items:
                        self.start_copy_to_destination(destination_path)
                    else:
                        self.show_toast("ابتدا فایل‌هایی را از لیست چپ انتخاب کنید", "warning")
                        
                    # Load subfolders if clicked and has dummy child
                    if item.childCount() == 1 and item.child(0).text(0) == "...":
                        self.load_subfolders(item, destination_path)
            
        except Exception as e:
            print(f"Error handling destination click: {e}")
    
    def load_subfolders(self, parent_item, folder_path):
        """بارگذاری زیرپوشه‌ها"""
        try:
            # Remove dummy child
            parent_item.removeChild(parent_item.child(0))
            
            # Add real subfolders
            try:
                for item_name in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item_name)
                    if os.path.isdir(item_path):
                        try:
                            subfolder_item = QTreeWidgetItem([f"📁 {item_name}"])
                            subfolder_item.setData(0, Qt.UserRole, item_path)
                            subfolder_item.setData(0, Qt.UserRole + 1, "folder")
                            
                            # Check if it has subfolders
                            has_subfolders = False
                            try:
                                for sub_item in os.listdir(item_path):
                                    if os.path.isdir(os.path.join(item_path, sub_item)):
                                        has_subfolders = True
                                        break
                            except (PermissionError, OSError):
                                pass
                            
                            if has_subfolders:
                                dummy = QTreeWidgetItem(["..."])
                                subfolder_item.addChild(dummy)
                            
                            parent_item.addChild(subfolder_item)
                            
                        except (PermissionError, OSError):
                            continue
            except (PermissionError, OSError):
                pass
                
        except Exception as e:
            print(f"Error loading subfolders: {e}")
    
    def start_copy_to_destination(self, destination_path):
        """شروع کپی به مقصد انتخاب شده"""
        try:
            selected_items = self.file_tree.selectedItems()
            if not selected_items:
                self.show_toast("فایلی انتخاب نشده", "warning")
                return
            
            # Check license limit
            if not self.license_manager.check_file_limit(len(selected_items)):
                self.show_license_restriction()
                return
            
            # Extract file paths
            file_paths = []
            for item in selected_items:
                file_path = item.text(1)  # Path column
                if os.path.exists(file_path):
                    file_paths.append(file_path)
            
            if file_paths:
                self.start_copy_task(file_paths, destination_path)
                self.show_toast(f"شروع کپی {len(file_paths)} فایل به {os.path.basename(destination_path)}", "info")
            else:
                self.show_toast("فایل‌های انتخاب شده یافت نشدند", "error")
                
        except Exception as e:
            print(f"Error starting copy to destination: {e}")
            self.show_toast(f"خطا در شروع کپی: {e}", "error")
    
    def format_size(self, size: int) -> str:
        """فرمت اندازه فایل"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def apply_all_settings(self):
        """اعمال همه تنظیمات"""
        try:
            # Apply font settings
            font_family = self.font_family_combo.currentText()
            font_size = self.font_size_spin.value()
            
            self.config.set('font_settings', 'primary_font', font_family)
            self.config.set('font_settings', 'font_size', font_size)
            
            # Apply theme
            theme_index = self.theme_combo.currentIndex()
            theme_mapping = {0: "dark", 1: "light", 2: "blue", 3: "green"}
            theme = theme_mapping.get(theme_index, "dark")
            
            self.config.set('ui_settings', 'theme', theme)
            self.apply_theme(theme)
            
            # Apply other settings
            self.config.set('ui_settings', 'animation_speed', self.animation_speed_spin.value())
            self.config.set('ui_settings', 'toast_duration', self.toast_duration_spin.value())
            self.config.set('file_operations', 'max_concurrent_tasks', self.max_tasks_spin.value())
            self.config.set('file_operations', 'chunk_size', self.chunk_size_spin.value())
            self.config.set('file_operations', 'verify_copy', self.verify_copy_check.isChecked())
            self.config.set('file_operations', 'auto_retry', self.auto_retry_check.isChecked())
            
            # Apply font to application
            font = QFont(font_family, font_size)
            QApplication.instance().setFont(font)
            
            self.show_toast("همه تنظیمات با موفقیت اعمال شد", "success")
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            self.show_toast(f"خطا در اعمال تنظیمات: {e}", "error")
    
    def closeEvent(self, event):
        """رویداد بستن برنامه"""
        try:
            # Save window geometry
            geometry = [self.x(), self.y(), self.width(), self.height()]
            self.config.set('app_settings', 'window_geometry', geometry)
            self.config.set('app_settings', 'window_maximized', self.isMaximized())
            
            # Cancel any running scans
            if self.scanner_worker and self.scanner_worker.isRunning():
                self.scanner_worker.cancel()
                self.scanner_worker.wait(3000)
            
            # Cancel any active copy tasks
            for task_id in list(self.active_tasks.keys()):
                self.cancel_task(task_id)
            
            event.accept()
            
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()

# Main function
def main():
    """تابع اصلی برنامه"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Persian File Copier Pro - PyQt5")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("شرکت فناوری نوآئران مثبت سبز")
        
        # Set default font
        try:
            font = QFont("B Nazanin", 11)
            app.setFont(font)
        except:
            font = QFont("Tahoma", 11)
            app.setFont(font)
        
        # Create and show main window
        window = PersianFileCopierPyQt5()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()