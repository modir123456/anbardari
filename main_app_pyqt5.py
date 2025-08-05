#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro - PyQt5 Professional Edition
شرکت فناوری نوآئران مثبت سبز
نسخه حرفه‌ای کپی کننده فایل پارسیان
"""

import sys
import os
import json
import shutil
import time
import threading
import queue
import psutil
from datetime import datetime, timedelta
import uuid
import hashlib
import base64
import re
import webbrowser
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QTabWidget, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QGroupBox,
    QFrame, QSplitter, QStatusBar, QMenuBar, QMenu, QAction,
    QMessageBox, QFileDialog, QCheckBox, QSpinBox, QSlider,
    QScrollArea, QListWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QFormLayout,
    QStyleFactory, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QSize, QPoint, QSettings, QTranslator, QLocale
)
from PyQt5.QtGui import (
    QFont, QPixmap, QIcon, QPalette, QColor, QLinearGradient,
    QBrush, QPainter, QFontDatabase, QMovie
)

# Configuration and Internationalization
class ConfigManager:
    """مدیریت تنظیمات پیشرفته نرم‌افزار"""
    
    def __init__(self, config_file="config_pro.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """بارگذاری تنظیمات"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()
    
    def get_default_config(self):
        """تنظیمات پیش‌فرض"""
        return {
            "app_info": {
                "name": "Persian File Copier Pro",
                "company": "شرکت فناوری نوآئران مثبت سبز",
                "version": "3.0",
                "website": "https://noavaran-positive-green.ir",
                "support_email": "support@noavaran-positive-green.ir"
            },
            "ui_settings": {
                "language": "fa",
                "theme": "modern_dark",
                "font_family": "Vazir",
                "font_size": 11,
                "window_size": [1200, 800],
                "animations": True,
                "transparency": 0.95
            },
            "performance": {
                "buffer_size": 8192,
                "max_threads": 4,
                "scan_depth": 3,
                "auto_retry": True,
                "retry_count": 3
            },
            "license": {
                "type": "trial",
                "trial_days": 30,
                "features": {
                    "max_files_per_operation": 100,
                    "max_file_size_mb": 500,
                    "advanced_features": False,
                    "commercial_use": False,
                    "priority_support": False
                }
            },
            "zarinpal": {
                "merchant_id": "YOUR_MERCHANT_ID",
                "sandbox": True,
                "products": {
                    "personal": {
                        "price": 299000,
                        "features": ["unlimited_files", "basic_support", "1_year_updates"]
                    },
                    "professional": {
                        "price": 799000,
                        "features": ["unlimited_files", "priority_support", "advanced_features", "commercial_use"]
                    },
                    "enterprise": {
                        "price": 1999000,
                        "features": ["unlimited_files", "enterprise_support", "all_features", "multi_user", "custom_integration"]
                    }
                }
            }
        }
    
    def save_config(self):
        """ذخیره تنظیمات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات: {e}")
            return False
    
    def get(self, section, key, default=None):
        """دریافت تنظیمات"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """تنظیم مقدار"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

class LanguageManager:
    """مدیریت چندزبانه"""
    
    def __init__(self):
        self.current_language = "fa"
        self.translations = self.load_translations()
    
    def load_translations(self):
        """بارگذاری ترجمه‌ها"""
        return {
            "fa": {
                "app_title": "کپی کننده فایل پارسیان نسخه حرفه‌ای",
                "company": "شرکت فناوری نوآئران مثبت سبز",
                "file_explorer": "مرورگر فایل",
                "destination": "مقصد",
                "settings": "تنظیمات",
                "about": "درباره ما",
                "license": "لایسنس",
                "copy": "کپی",
                "paste": "چسباندن",
                "select_all": "انتخاب همه",
                "start_copy": "شروع کپی",
                "pause": "توقف",
                "cancel": "لغو",
                "progress": "پیشرفت",
                "status": "وضعیت",
                "ready": "آماده",
                "copying": "در حال کپی",
                "completed": "تکمیل شد",
                "error": "خطا",
                "warning": "هشدار",
                "information": "اطلاع",
                "success": "موفقیت",
                "purchase_license": "خرید لایسنس",
                "trial_version": "نسخه آزمایشی",
                "upgrade_now": "ارتقا",
                "features_limited": "امکانات محدود",
                "language": "زبان",
                "theme": "تم",
                "font": "فونت",
                "performance": "عملکرد",
                "advanced": "پیشرفته",
                "general": "عمومی",
                "ui_customization": "شخصی‌سازی رابط",
                "file_operations": "عملیات فایل",
                "security": "امنیت",
                "backup": "پشتیبان‌گیری",
                "notifications": "اعلانات",
                "updates": "بروزرسانی"
            },
            "en": {
                "app_title": "Persian File Copier Pro",
                "company": "Noavaran Positive Green Technology",
                "file_explorer": "File Explorer",
                "destination": "Destination",
                "settings": "Settings",
                "about": "About",
                "license": "License",
                "copy": "Copy",
                "paste": "Paste",
                "select_all": "Select All",
                "start_copy": "Start Copy",
                "pause": "Pause",
                "cancel": "Cancel",
                "progress": "Progress",
                "status": "Status",
                "ready": "Ready",
                "copying": "Copying",
                "completed": "Completed",
                "error": "Error",
                "warning": "Warning",
                "information": "Information",
                "success": "Success",
                "purchase_license": "Purchase License",
                "trial_version": "Trial Version",
                "upgrade_now": "Upgrade Now",
                "features_limited": "Features Limited",
                "language": "Language",
                "theme": "Theme",
                "font": "Font",
                "performance": "Performance",
                "advanced": "Advanced",
                "general": "General",
                "ui_customization": "UI Customization",
                "file_operations": "File Operations",
                "security": "Security",
                "backup": "Backup",
                "notifications": "Notifications",
                "updates": "Updates"
            }
        }
    
    def tr(self, key):
        """ترجمه متن"""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def set_language(self, lang):
        """تنظیم زبان"""
        if lang in self.translations:
            self.current_language = lang
            return True
        return False

class LicenseManager:
    """مدیریت لایسنس پیشرفته"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.license_file = "license.dat"
        
    def get_trial_remaining_days(self):
        """محاسبه روزهای باقیمانده آزمایشی"""
        license_data = self.load_license()
        if not license_data:
            return 30
        
        install_date = license_data.get("install_date")
        if install_date:
            install_dt = datetime.fromisoformat(install_date)
            days_passed = (datetime.now() - install_dt).days
            return max(0, 30 - days_passed)
        return 30
    
    def is_feature_available(self, feature):
        """بررسی دسترسی به ویژگی"""
        license_data = self.load_license()
        if not license_data:
            return False
            
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            trial_days = self.get_trial_remaining_days()
            if trial_days <= 0:
                return False
            
            # محدودیت‌های نسخه آزمایشی
            limitations = {
                "max_files_per_operation": 100,
                "max_file_size_mb": 500,
                "advanced_features": False,
                "commercial_use": False
            }
            
            return limitations.get(feature, True)
        
        elif license_type in ["personal", "professional", "enterprise"]:
            # ویژگی‌های مختلف براساس نوع لایسنس
            features = {
                "personal": {
                    "max_files_per_operation": 10000,
                    "max_file_size_mb": 10000,
                    "advanced_features": True,
                    "commercial_use": False,
                    "priority_support": False
                },
                "professional": {
                    "max_files_per_operation": -1,  # نامحدود
                    "max_file_size_mb": -1,
                    "advanced_features": True,
                    "commercial_use": True,
                    "priority_support": True,
                    "multi_threading": True
                },
                "enterprise": {
                    "max_files_per_operation": -1,
                    "max_file_size_mb": -1,
                    "advanced_features": True,
                    "commercial_use": True,
                    "priority_support": True,
                    "multi_threading": True,
                    "custom_integration": True,
                    "multi_user": True
                }
            }
            
            return features.get(license_type, {}).get(feature, False)
        
        return False
    
    def load_license(self):
        """بارگذاری اطلاعات لایسنس"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        # ایجاد لایسنس آزمایشی اولیه
        trial_license = {
            "type": "trial",
            "install_date": datetime.now().isoformat(),
            "machine_id": self.get_machine_id()
        }
        self.save_license(trial_license)
        return trial_license
    
    def save_license(self, license_data):
        """ذخیره لایسنس"""
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_machine_id(self):
        """دریافت شناسه ماشین"""
        try:
            import platform
            machine_info = f"{platform.node()}-{platform.machine()}"
            return hashlib.md5(machine_info.encode()).hexdigest()
        except:
            return "unknown"

# Main Application Class
class PersianFileCopierPro(QMainWindow):
    """کلاس اصلی نرم‌افزار کپی کننده فایل پارسیان"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.license_manager = LicenseManager(self.config_manager)
        
        # Application state
        self.file_operations = []
        self.current_operation = None
        
        # Setup UI
        self.init_ui()
        self.setup_styling()
        self.setup_connections()
        
        # Load initial data
        self.load_drives()
        self.check_license_status()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        # Window settings
        self.setWindowTitle(self.language_manager.tr("app_title"))
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tool bar
        self.create_tool_bar()
        
        # Create main content
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
    
    def create_menu_bar(self):
        """ایجاد نوار منو"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('فایل')
        
        new_action = QAction('جدید', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        
        open_action = QAction('باز کردن', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('خروج', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('ابزارها')
        
        settings_action = QAction('تنظیمات', self)
        settings_action.setShortcut('F2')
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        license_action = QAction('مدیریت لایسنس', self)
        license_action.triggered.connect(self.open_license_manager)
        tools_menu.addAction(license_action)
        
        # Help menu
        help_menu = menubar.addMenu('راهنما')
        
        about_action = QAction('درباره ما', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        support_action = QAction('پشتیبانی', self)
        support_action.triggered.connect(self.open_support)
        help_menu.addAction(support_action)
    
    def create_tool_bar(self):
        """ایجاد نوار ابزار"""
        self.toolbar = self.addToolBar('Main')
        self.toolbar.setMovable(False)
        
        # Quick actions
        self.copy_action = self.toolbar.addAction('کپی')
        self.paste_action = self.toolbar.addAction('چسباندن')
        self.toolbar.addSeparator()
        
        self.settings_action = self.toolbar.addAction('تنظیمات')
        self.settings_action.triggered.connect(self.open_settings)
        
        # License status
        self.toolbar.addSeparator()
        self.license_label = QLabel()
        self.update_license_display()
        self.toolbar.addWidget(self.license_label)
    
    def create_main_content(self, main_layout):
        """ایجاد محتوای اصلی"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # File Explorer Tab
        self.create_file_explorer_tab()
        
        # Operations Tab
        self.create_operations_tab()
        
        # Settings Tab
        self.create_settings_tab()
        
        # About Tab
        self.create_about_tab()
    
    def create_file_explorer_tab(self):
        """تب مرورگر فایل"""
        explorer_widget = QWidget()
        layout = QHBoxLayout(explorer_widget)
        
        # Left side - Drive and folder tree
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_frame)
        
        # Drive selection
        drive_group = QGroupBox("انتخاب درایو")
        drive_layout = QVBoxLayout(drive_group)
        
        self.drive_combo = QComboBox()
        self.drive_combo.currentTextChanged.connect(self.on_drive_changed)
        drive_layout.addWidget(self.drive_combo)
        
        left_layout.addWidget(drive_group)
        
        # Folder tree
        folder_group = QGroupBox("مرورگر پوشه‌ها")
        folder_layout = QVBoxLayout(folder_group)
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(['نام', 'نوع', 'اندازه', 'تاریخ تغییر'])
        self.folder_tree.itemSelectionChanged.connect(self.on_folder_selection_changed)
        folder_layout.addWidget(self.folder_tree)
        
        left_layout.addWidget(folder_group)
        
        # Right side - File list and preview
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        
        # File list
        file_group = QGroupBox("لیست فایل‌ها")
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QTreeWidget()
        self.file_list.setHeaderLabels(['نام فایل', 'مسیر', 'اندازه', 'نوع'])
        self.file_list.setSelectionMode(QTreeWidget.ExtendedSelection)
        file_layout.addWidget(self.file_list)
        
        # File operations buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("انتخاب همه")
        self.select_all_btn.clicked.connect(self.select_all_files)
        button_layout.addWidget(self.select_all_btn)
        
        self.copy_selected_btn = QPushButton("کپی انتخاب شده")
        self.copy_selected_btn.clicked.connect(self.copy_selected_files)
        button_layout.addWidget(self.copy_selected_btn)
        
        file_layout.addLayout(button_layout)
        right_layout.addWidget(file_group)
        
        # Destination selection
        dest_group = QGroupBox("انتخاب مقصد")
        dest_layout = QVBoxLayout(dest_group)
        
        dest_input_layout = QHBoxLayout()
        self.destination_edit = QLineEdit()
        self.destination_edit.setPlaceholderText("مسیر مقصد را انتخاب کنید...")
        dest_input_layout.addWidget(self.destination_edit)
        
        self.browse_dest_btn = QPushButton("...")
        self.browse_dest_btn.setMaximumWidth(50)
        self.browse_dest_btn.clicked.connect(self.browse_destination)
        dest_input_layout.addWidget(self.browse_dest_btn)
        
        dest_layout.addLayout(dest_input_layout)
        right_layout.addWidget(dest_group)
        
        # Add to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(explorer_widget, "مرورگر فایل")
    
    def create_operations_tab(self):
        """تب عملیات"""
        operations_widget = QWidget()
        layout = QVBoxLayout(operations_widget)
        
        # Current operation display
        current_group = QGroupBox("عملیات جاری")
        current_layout = QVBoxLayout(current_group)
        
        self.operation_label = QLabel("هیچ عملیاتی در حال انجام نیست")
        current_layout.addWidget(self.operation_label)
        
        self.progress_bar = QProgressBar()
        current_layout.addWidget(self.progress_bar)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("شروع")
        self.start_btn.clicked.connect(self.start_operation)
        control_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("توقف")
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        self.cancel_btn = QPushButton("لغو")
        self.cancel_btn.setEnabled(False)
        control_layout.addWidget(self.cancel_btn)
        
        current_layout.addLayout(control_layout)
        layout.addWidget(current_group)
        
        # Operations history
        history_group = QGroupBox("تاریخچه عملیات")
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(['زمان', 'عملیات', 'منبع', 'مقصد', 'وضعیت'])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        
        layout.addWidget(history_group)
        
        self.tab_widget.addTab(operations_widget, "عملیات")
    
    def create_settings_tab(self):
        """تب تنظیمات پیشرفته"""
        settings_widget = QWidget()
        main_layout = QHBoxLayout(settings_widget)
        
        # Settings categories
        categories_list = QListWidget()
        categories_list.setMaximumWidth(200)
        categories_list.addItems([
            "عمومی", "زبان و منطقه", "ظاهر و تم", "فونت و نمایش",
            "عملکرد", "امنیت", "پشتیبان‌گیری", "اعلانات",
            "بروزرسانی", "لایسنس", "پیشرفته"
        ])
        categories_list.currentRowChanged.connect(self.on_settings_category_changed)
        main_layout.addWidget(categories_list)
        
        # Settings content
        self.settings_stack = QWidget()
        settings_scroll = QScrollArea()
        settings_scroll.setWidget(self.settings_stack)
        settings_scroll.setWidgetResizable(True)
        main_layout.addWidget(settings_scroll)
        
        # Initialize settings panels
        self.setup_settings_panels()
        
        self.tab_widget.addTab(settings_widget, "تنظیمات")
    
    def setup_settings_panels(self):
        """راه‌اندازی پنل‌های تنظیمات"""
        layout = QVBoxLayout(self.settings_stack)
        
        # General Settings
        general_group = QGroupBox("تنظیمات عمومی")
        general_layout = QFormLayout(general_group)
        
        self.startup_scan_check = QCheckBox("اسکن خودکار در شروع")
        general_layout.addRow("اسکن خودکار:", self.startup_scan_check)
        
        self.auto_backup_check = QCheckBox("پشتیبان‌گیری خودکار")
        general_layout.addRow("پشتیبان‌گیری:", self.auto_backup_check)
        
        layout.addWidget(general_group)
        
        # Language Settings
        lang_group = QGroupBox("تنظیمات زبان")
        lang_layout = QFormLayout(lang_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["فارسی", "English", "العربية"])
        self.language_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addRow("زبان:", self.language_combo)
        
        layout.addWidget(lang_group)
        
        # Appearance Settings
        appearance_group = QGroupBox("تنظیمات ظاهری")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["تیره مدرن", "روشن کلاسیک", "آبی حرفه‌ای", "سبز طبیعی"])
        appearance_layout.addRow("تم:", self.theme_combo)
        
        self.animations_check = QCheckBox("انیمیشن‌ها فعال")
        appearance_layout.addRow("انیمیشن:", self.animations_check)
        
        layout.addWidget(appearance_group)
        
        # Performance Settings
        perf_group = QGroupBox("تنظیمات عملکرد")
        perf_layout = QFormLayout(perf_group)
        
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(1024, 65536)
        self.buffer_size_spin.setValue(8192)
        self.buffer_size_spin.setSuffix(" بایت")
        perf_layout.addRow("اندازه buffer:", self.buffer_size_spin)
        
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 16)
        self.max_threads_spin.setValue(4)
        perf_layout.addRow("حداکثر thread:", self.max_threads_spin)
        
        layout.addWidget(perf_group)
        
        layout.addStretch()
    
    def create_about_tab(self):
        """تب درباره ما"""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)
        
        # Company info
        company_group = QGroupBox("اطلاعات شرکت")
        company_layout = QVBoxLayout(company_group)
        
        company_name = QLabel("شرکت فناوری نوآئران مثبت سبز")
        company_name.setAlignment(Qt.AlignCenter)
        company_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E8B57;")
        company_layout.addWidget(company_name)
        
        app_name = QLabel("Persian File Copier Pro v3.0")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("font-size: 16px; color: #4682B4;")
        company_layout.addWidget(app_name)
        
        description = QLabel("""
        نرم‌افزار حرفه‌ای کپی و مدیریت فایل با قابلیت‌های پیشرفته
        • پشتیبانی از فایل‌های بزرگ
        • کپی چندگانه با سرعت بالا
        • رابط کاربری زیبا و کاربرپسند
        • پشتیبانی 24/7
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        company_layout.addWidget(description)
        
        layout.addWidget(company_group)
        
        # Contact info
        contact_group = QGroupBox("اطلاعات تماس")
        contact_layout = QFormLayout(contact_group)
        
        contact_layout.addRow("وب‌سایت:", QLabel("https://noavaran-positive-green.ir"))
        contact_layout.addRow("ایمیل:", QLabel("support@noavaran-positive-green.ir"))
        contact_layout.addRow("تلفن:", QLabel("+98 21 1234 5678"))
        
        layout.addWidget(contact_group)
        
        # License info
        license_group = QGroupBox("اطلاعات لایسنس")
        license_layout = QVBoxLayout(license_group)
        
        self.license_info_label = QLabel()
        self.update_license_info()
        license_layout.addWidget(self.license_info_label)
        
        # Purchase button
        if self.license_manager.load_license().get("type") == "trial":
            purchase_btn = QPushButton("خرید لایسنس از زرین‌پال")
            purchase_btn.clicked.connect(self.open_zarinpal_purchase)
            purchase_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            license_layout.addWidget(purchase_btn)
        
        layout.addWidget(license_group)
        layout.addStretch()
        
        self.tab_widget.addTab(about_widget, "درباره ما")
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel("آماده")
        self.status_bar.addWidget(self.status_label)
        
        # Progress indicator
        self.status_progress = QProgressBar()
        self.status_progress.setVisible(False)
        self.status_progress.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.status_progress)
        
        # License status
        self.status_license = QLabel()
        self.update_license_display()
        self.status_bar.addPermanentWidget(self.status_license)
    
    def setup_styling(self):
        """راه‌اندازی استایل‌دهی"""
        # Set application style
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # Dark theme
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        QApplication.setPalette(dark_palette)
        
        # Custom styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
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
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
        """)
    
    def setup_connections(self):
        """راه‌اندازی اتصالات"""
        pass
    
    def load_drives(self):
        """بارگذاری درایوها"""
        self.drive_combo.clear()
        self.drive_combo.addItem("همه درایوها")
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                free_gb = usage.free // (1024**3)
                total_gb = usage.total // (1024**3)
                drive_text = f"{partition.device} ({free_gb}GB / {total_gb}GB آزاد)"
                self.drive_combo.addItem(drive_text)
            except:
                self.drive_combo.addItem(partition.device)
    
    def check_license_status(self):
        """بررسی وضعیت لایسنس"""
        license_data = self.license_manager.load_license()
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            remaining_days = self.license_manager.get_trial_remaining_days()
            if remaining_days <= 0:
                self.show_trial_expired_dialog()
            elif remaining_days <= 7:
                self.show_trial_warning_dialog(remaining_days)
    
    def update_license_display(self):
        """بروزرسانی نمایش لایسنس"""
        license_data = self.license_manager.load_license()
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            remaining_days = self.license_manager.get_trial_remaining_days()
            text = f"آزمایشی ({remaining_days} روز باقیمانده)"
            color = "orange" if remaining_days <= 7 else "green"
        else:
            text = f"لایسنس {license_type}"
            color = "green"
        
        style = f"color: {color}; font-weight: bold;"
        
        if hasattr(self, 'license_label'):
            self.license_label.setText(text)
            self.license_label.setStyleSheet(style)
        
        if hasattr(self, 'status_license'):
            self.status_license.setText(text)
            self.status_license.setStyleSheet(style)
    
    def update_license_info(self):
        """بروزرسانی اطلاعات لایسنس"""
        license_data = self.license_manager.load_license()
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            remaining_days = self.license_manager.get_trial_remaining_days()
            info_text = f"""
            نوع لایسنس: آزمایشی
            روزهای باقیمانده: {remaining_days}
            محدودیت‌ها:
            • حداکثر 100 فایل در هر عملیات
            • حداکثر 500 مگابایت برای هر فایل
            • عدم دسترسی به ویژگی‌های پیشرفته
            """
        else:
            info_text = f"""
            نوع لایسنس: {license_type}
            وضعیت: فعال
            ویژگی‌ها: نامحدود
            """
        
        if hasattr(self, 'license_info_label'):
            self.license_info_label.setText(info_text)
    
    # Event handlers
    def on_drive_changed(self, drive_text):
        """تغییر درایو"""
        self.status_label.setText(f"بارگذاری فایل‌های درایو: {drive_text}")
        # Implementation for loading drive files
    
    def on_folder_selection_changed(self):
        """تغییر انتخاب پوشه"""
        # Implementation for folder selection
        pass
    
    def on_settings_category_changed(self, row):
        """تغییر دسته تنظیمات"""
        # Implementation for settings category change
        pass
    
    def select_all_files(self):
        """انتخاب همه فایل‌ها"""
        if not self.license_manager.is_feature_available("max_files_per_operation"):
            self.show_license_limitation_dialog("انتخاب همه فایل‌ها")
            return
        
        self.file_list.selectAll()
    
    def copy_selected_files(self):
        """کپی فایل‌های انتخاب شده"""
        selected_items = self.file_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "هشدار", "لطفاً فایل‌هایی را انتخاب کنید.")
            return
        
        # Check license limitations
        if len(selected_items) > 100 and not self.license_manager.is_feature_available("max_files_per_operation"):
            self.show_license_limitation_dialog("کپی بیش از 100 فایل")
            return
        
        destination = self.destination_edit.text().strip()
        if not destination:
            QMessageBox.warning(self, "هشدار", "لطفاً مقصد را انتخاب کنید.")
            return
        
        # Start copy operation
        self.start_copy_operation(selected_items, destination)
    
    def browse_destination(self):
        """انتخاب مقصد"""
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه مقصد")
        if folder:
            self.destination_edit.setText(folder)
    
    def start_operation(self):
        """شروع عملیات"""
        # Implementation for starting operation
        pass
    
    def start_copy_operation(self, files, destination):
        """شروع عملیات کپی"""
        # Implementation for copy operation
        pass
    
    def change_language(self, language):
        """تغییر زبان"""
        lang_map = {
            "فارسی": "fa",
            "English": "en",
            "العربية": "ar"
        }
        
        lang_code = lang_map.get(language, "fa")
        if self.language_manager.set_language(lang_code):
            QMessageBox.information(self, "اطلاع", "برای اعمال تغییرات زبان، نرم‌افزار را مجدداً راه‌اندازی کنید.")
    
    def open_settings(self):
        """باز کردن تنظیمات"""
        self.tab_widget.setCurrentIndex(2)  # Settings tab
    
    def open_license_manager(self):
        """باز کردن مدیریت لایسنس"""
        dialog = LicenseDialog(self, self.license_manager)
        dialog.exec_()
        self.update_license_display()
        self.update_license_info()
    
    def show_about(self):
        """نمایش درباره ما"""
        self.tab_widget.setCurrentIndex(3)  # About tab
    
    def open_support(self):
        """باز کردن پشتیبانی"""
        webbrowser.open("https://noavaran-positive-green.ir/support")
    
    def open_zarinpal_purchase(self):
        """باز کردن صفحه خرید زرین‌پال"""
        # آدرس فروشگاه زرین‌پال
        zarinpal_url = "https://zarinp.al/735413"
        webbrowser.open(zarinpal_url)
    
    def show_trial_expired_dialog(self):
        """نمایش دیالوگ پایان آزمایشی"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("پایان دوره آزمایشی")
        msg.setText("دوره آزمایشی شما به پایان رسیده است.")
        msg.setInformativeText("برای ادامه استفاده از نرم‌افزار، لطفاً لایسنس خریداری کنید.")
        
        purchase_btn = msg.addButton("خرید لایسنس", QMessageBox.AcceptRole)
        msg.addButton("خروج", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == purchase_btn:
            self.open_zarinpal_purchase()
    
    def show_trial_warning_dialog(self, remaining_days):
        """نمایش هشدار پایان آزمایشی"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("یادآوری")
        msg.setText(f"تنها {remaining_days} روز از دوره آزمایشی شما باقی مانده است.")
        msg.setInformativeText("برای ادامه استفاده، لایسنس خریداری کنید.")
        
        purchase_btn = msg.addButton("خرید لایسنس", QMessageBox.AcceptRole)
        msg.addButton("بعداً", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == purchase_btn:
            self.open_zarinpal_purchase()
    
    def show_license_limitation_dialog(self, feature):
        """نمایش محدودیت لایسنس"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("محدودیت نسخه آزمایشی")
        msg.setText(f"ویژگی '{feature}' در نسخه آزمایشی محدود است.")
        msg.setInformativeText("برای دسترسی کامل، لایسنس خریداری کنید.")
        
        purchase_btn = msg.addButton("خرید لایسنس", QMessageBox.AcceptRole)
        msg.addButton("باشه", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == purchase_btn:
            self.open_zarinpal_purchase()


class LicenseDialog(QDialog):
    """دیالوگ مدیریت لایسنس"""
    
    def __init__(self, parent, license_manager):
        super().__init__(parent)
        self.license_manager = license_manager
        self.init_ui()
    
    def init_ui(self):
        """راه‌اندازی رابط"""
        self.setWindowTitle("مدیریت لایسنس")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # License status
        status_group = QGroupBox("وضعیت فعلی")
        status_layout = QVBoxLayout(status_group)
        
        license_data = self.license_manager.load_license()
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            remaining_days = self.license_manager.get_trial_remaining_days()
            status_text = f"نسخه آزمایشی - {remaining_days} روز باقیمانده"
        else:
            status_text = f"لایسنس {license_type} - فعال"
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(status_label)
        
        layout.addWidget(status_group)
        
        # License input
        input_group = QGroupBox("فعال‌سازی لایسنس")
        input_layout = QVBoxLayout(input_group)
        
        self.license_edit = QLineEdit()
        self.license_edit.setPlaceholderText("کد لایسنس را وارد کنید...")
        input_layout.addWidget(self.license_edit)
        
        activate_btn = QPushButton("فعال‌سازی")
        activate_btn.clicked.connect(self.activate_license)
        input_layout.addWidget(activate_btn)
        
        layout.addWidget(input_group)
        
        # Purchase options
        purchase_group = QGroupBox("خرید لایسنس")
        purchase_layout = QVBoxLayout(purchase_group)
        
        products = [
            ("شخصی", "299,000 تومان", "personal"),
            ("حرفه‌ای", "799,000 تومان", "professional"),
            ("سازمانی", "1,999,000 تومان", "enterprise")
        ]
        
        for name, price, product_id in products:
            btn = QPushButton(f"{name} - {price}")
            btn.clicked.connect(lambda checked, pid=product_id: self.purchase_license(pid))
            purchase_layout.addWidget(btn)
        
        layout.addWidget(purchase_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def activate_license(self):
        """فعال‌سازی لایسنس"""
        license_key = self.license_edit.text().strip()
        if not license_key:
            QMessageBox.warning(self, "خطا", "لطفاً کد لایسنس را وارد کنید.")
            return
        
        # Simple validation (در عمل باید با سرور بررسی شود)
        if len(license_key) == 20 and license_key.startswith("PFC"):
            license_data = {
                "type": "professional",
                "key": license_key,
                "activated_date": datetime.now().isoformat(),
                "machine_id": self.license_manager.get_machine_id()
            }
            
            if self.license_manager.save_license(license_data):
                QMessageBox.information(self, "موفقیت", "لایسنس با موفقیت فعال شد!")
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "خطا در ذخیره لایسنس.")
        else:
            QMessageBox.warning(self, "خطا", "کد لایسنس نامعتبر است.")
    
    def purchase_license(self, product_id):
        """خرید لایسنس"""
        # باز کردن صفحه خرید زرین‌پال
        zarinpal_url = "https://zarinp.al/735413"
        webbrowser.open(zarinpal_url)


def main():
    """تابع اصلی"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Persian File Copier Pro")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("شرکت فناوری نوآئران مثبت سبز")
    app.setOrganizationDomain("noavaran-positive-green.ir")
    
    # Load Persian font
    font_db = QFontDatabase()
    font_path = "fonts/Vazir.ttf"  # فونت فارسی
    if os.path.exists(font_path):
        font_db.addApplicationFont(font_path)
    
    # Set default font
    font = QFont("Vazir", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    # Create and show main window
    window = PersianFileCopierPro()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()