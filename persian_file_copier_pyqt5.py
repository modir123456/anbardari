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

# License Management System  
class LicenseManager:
    """مدیریت لایسنس و احراز هویت"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.company_key = "PERSIANFILECOPIER2024"
        
    def generate_serial(self, customer_name: str, customer_email: str) -> str:
        """تولید سریال منحصربه‌فرد"""
        timestamp = str(int(time.time()))
        data = f"{customer_name}{customer_email}{timestamp}{self.company_key}"
        hash_obj = hashlib.sha256(data.encode())
        serial = base64.b64encode(hash_obj.digest()).decode()[:20].upper()
        return f"PFC-{serial[:4]}-{serial[4:8]}-{serial[8:12]}-{serial[12:16]}"
    
    def validate_license(self, license_key: str) -> bool:
        """اعتبارسنجی کلید لایسنس"""
        try:
            if not license_key or len(license_key) < 20:
                return False
            
            # Basic validation - in real app, check against server
            parts = license_key.split('-')
            if len(parts) != 5 or parts[0] != 'PFC':
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
            
            # Determine license type based on key pattern
            if 'PERS' in license_key:
                license_type = 'personal'
            elif 'COMM' in license_key:
                license_type = 'commercial' 
            elif 'CORP' in license_key:
                license_type = 'corporate'
            else:
                license_type = 'personal'
                
            self.config.set('license', 'license_type', license_type)
            return True, f"لایسنس {license_type} با موفقیت فعال شد"
        else:
            return False, "کلید لایسنس نامعتبر است"
    
    def check_file_limit(self, file_count: int) -> bool:
        """بررسی محدودیت تعداد فایل"""
        license_status = self.config.get('license', 'license_status', 'inactive')
        license_type = self.config.get('license', 'license_type', 'trial')
        
        if license_status == 'active' and license_type != 'trial':
            return True
            
        max_files = self.config.get('license', 'max_files_trial', 100)
        return file_count <= max_files
    
    def get_license_info(self) -> dict:
        """دریافت اطلاعات لایسنس"""
        return {
            'status': self.config.get('license', 'license_status', 'inactive'),
            'type': self.config.get('license', 'license_type', 'trial'),
            'key': self.config.get('license', 'license_key', ''),
            'activation_date': self.config.get('license', 'activation_date', ''),
            'max_files': self.config.get('license', 'max_files_trial', 100)
        }

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
        
        # Start initial scan
        self.start_drive_scan()
        
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
        
        # File Browser Tab
        self.create_file_browser_tab()
        
        # Destinations Tab  
        self.create_destinations_tab()
        
        # Settings Tab
        self.create_settings_tab()
        
        # About Tab
        self.create_about_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_file_browser_tab(self):
        """تب مرورگر فایل‌ها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Search and filter section
        self.create_search_section(layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # File tree (40%)
        self.create_file_tree_section(splitter)
        
        # Control section (20%)
        self.create_control_section(splitter)
        
        # Tasks section (40%)
        self.create_tasks_section(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 200, 400])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, "📁 مرورگر فایل")
    
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
        
        self.paste_license_btn = QPushButton("📋 جایگذاری")
        self.paste_license_btn.setFont(QFont("B Nazanin", 10))
        
        key_layout.addWidget(self.license_key_entry)
        key_layout.addWidget(self.paste_license_btn)
        license_layout.addLayout(key_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.activate_license_btn = QPushButton("🔓 فعال‌سازی لایسنس")
        self.activate_license_btn.setFont(QFont("B Nazanin", 10))
        
        self.purchase_license_btn = QPushButton("🛒 خرید لایسنس")
        self.purchase_license_btn.setFont(QFont("B Nazanin", 10))
        
        buttons_layout.addWidget(self.activate_license_btn)
        buttons_layout.addWidget(self.purchase_license_btn)
        license_layout.addLayout(buttons_layout)
        
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
            if os.path.exists("about_us.html"):
                with open("about_us.html", 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Simple HTML to text conversion for display
                import re
                # Remove HTML tags but preserve structure
                text_content = re.sub(r'<[^>]+>', '', html_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                about_text = QTextEdit()
                about_text.setFont(QFont("B Nazanin", 11))
                about_text.setPlainText(text_content)
                about_text.setReadOnly(True)
                about_text.setMaximumHeight(200)
                
                parent_layout.addWidget(about_text)
            else:
                # Default about content
                default_text = f"""
                {self.config.get('app_settings', 'app_name')} 
                
                نرم‌افزاری پیشرفته و قدرتمند برای مدیریت و کپی فایل‌ها است که با هدف 
                تسهیل کار کاربران ایرانی طراحی شده است.
                
                امکانات:
                • مرور و جستجوی پیشرفته فایل‌ها
                • فیلتر بر اساس نوع و اندازه فایل  
                • کپی چندگانه با نمایش پیشرفت
                • پشتیبانی از فونت‌های فارسی
                • رابط کاربری زیبا و کاربردی
                
                {self.config.get('app_settings', 'company')}
                """
                
                about_label = QLabel(default_text)
                about_label.setFont(QFont("B Nazanin", 11))
                about_label.setWordWrap(True)
                about_label.setAlignment(Qt.AlignRight)
                
                parent_layout.addWidget(about_label)
                
        except Exception as e:
            print(f"Error loading about content: {e}")
    
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
        # Dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabWidget::tab-bar {
                alignment: right;
            }
            QTabBar::tab {
                background-color: #555555;
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
                background-color: #666666;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
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
                border: 1px solid #555555;
                alternate-background-color: #404040;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QTreeWidget::item:selected, QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
                background-color: #404040;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
                background-color: #404040;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0078d4;
            }
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
            }
            QLabel {
                color: #ffffff;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-top: 1px solid #555555;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
        """)
    
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
        
        # Copy buttons
        self.copy_selected_btn.clicked.connect(self.copy_selected_files)
        self.copy_all_btn.clicked.connect(self.copy_all_files)
        
        # Task control buttons
        self.pause_all_btn.clicked.connect(self.pause_all_tasks)
        self.resume_all_btn.clicked.connect(self.resume_all_tasks)
        self.cancel_all_btn.clicked.connect(self.cancel_all_tasks)
        self.clear_completed_btn.clicked.connect(self.clear_completed_tasks)
        
        # Destination buttons
        self.browse_dest_btn.clicked.connect(self.browse_destination)
        
        # Settings buttons
        self.apply_font_btn.clicked.connect(self.apply_font_settings)
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
            self.tasks_table.setItem(row, 0, QTableWidgetItem(source_text))
            
            # Destination
            dest_text = os.path.basename(destination) or destination
            self.tasks_table.setItem(row, 1, QTableWidgetItem(dest_text))
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setFont(QFont("B Nazanin", 8))
            self.tasks_table.setCellWidget(row, 2, progress_bar)
            
            # Speed
            self.tasks_table.setItem(row, 3, QTableWidgetItem("0 MB/s"))
            
            # ETA
            self.tasks_table.setItem(row, 4, QTableWidgetItem("محاسبه..."))
            
            # Control buttons
            control_widget = QWidget()
            control_layout = QHBoxLayout(control_widget)
            control_layout.setContentsMargins(2, 2, 2, 2)
            
            pause_btn = QPushButton("⏸️")
            pause_btn.setMaximumSize(30, 25)
            pause_btn.setFont(QFont("Arial", 8))
            pause_btn.clicked.connect(lambda: self.pause_task(task_id))
            
            cancel_btn = QPushButton("❌")
            cancel_btn.setMaximumSize(30, 25)
            cancel_btn.setFont(QFont("Arial", 8))
            cancel_btn.clicked.connect(lambda: self.cancel_task(task_id))
            
            control_layout.addWidget(pause_btn)
            control_layout.addWidget(cancel_btn)
            
            self.tasks_table.setCellWidget(row, 5, control_widget)
            
            # Store row index for updates
            self.active_tasks[task_id]['row'] = row
            
        except Exception as e:
            print(f"Error adding task to table: {e}")
    
    def update_task_progress(self, task_id: str, progress: int, speed: str, eta: str):
        """بروزرسانی پیشرفت تسک"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task['progress'] = progress
                row = task.get('row', -1)
                
                if row >= 0:
                    # Update progress bar
                    progress_bar = self.tasks_table.cellWidget(row, 2)
                    if progress_bar:
                        progress_bar.setValue(progress)
                    
                    # Update speed
                    speed_item = self.tasks_table.item(row, 3)
                    if speed_item:
                        speed_item.setText(speed)
                    
                    # Update ETA
                    eta_item = self.tasks_table.item(row, 4)
                    if eta_item:
                        eta_item.setText(eta)
                
                # Update overall progress
                self.update_overall_progress()
                
        except Exception as e:
            print(f"Error updating task progress: {e}")
    
    def task_completed(self, task_id: str, success: bool, message: str):
        """تسک تکمیل شد"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task['status'] = 'completed' if success else 'failed'
                
                row = task.get('row', -1)
                if row >= 0:
                    # Update progress to 100% if successful
                    if success:
                        progress_bar = self.tasks_table.cellWidget(row, 2)
                        if progress_bar:
                            progress_bar.setValue(100)
                    
                    # Update ETA to show completion
                    eta_item = self.tasks_table.item(row, 4)
                    if eta_item:
                        eta_item.setText("تکمیل شد" if success else "خطا")
                
                # Show notification
                toast_type = "success" if success else "error"
                self.show_toast(message, toast_type)
                
                # Update overall progress
                self.update_overall_progress()
                
                # Auto-remove completed tasks after delay
                QTimer.singleShot(30000, lambda: self.remove_completed_task(task_id))
                
        except Exception as e:
            print(f"Error handling task completion: {e}")
    
    def task_error(self, task_id: str, error_message: str):
        """خطا در تسک"""
        self.show_toast(f"خطا در تسک {task_id}: {error_message}", "error")
    
    def update_overall_progress(self):
        """بروزرسانی پیشرفت کلی"""
        try:
            if not self.active_tasks:
                self.overall_progress.setValue(0)
                self.overall_status_label.setText("آماده")
                return
            
            total_progress = 0
            active_count = 0
            completed_count = 0
            
            for task in self.active_tasks.values():
                if task['status'] == 'running':
                    total_progress += task['progress']
                    active_count += 1
                elif task['status'] in ['completed', 'failed']:
                    total_progress += 100
                    completed_count += 1
            
            total_tasks = len(self.active_tasks)
            if total_tasks > 0:
                overall = int(total_progress / total_tasks)
                self.overall_progress.setValue(overall)
                
                if active_count > 0:
                    self.overall_status_label.setText(f"در حال کپی - {active_count} تسک فعال")
                elif completed_count == total_tasks:
                    self.overall_status_label.setText("همه تسک‌ها تکمیل شدند")
                else:
                    self.overall_status_label.setText("آماده")
            
        except Exception as e:
            print(f"Error updating overall progress: {e}")
    
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
                self.update_overall_progress()
                
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