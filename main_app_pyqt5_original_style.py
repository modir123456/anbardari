#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro - PyQt5 Original Style Edition
شرکت فناوری نوآئران مثبت سبز
نسخه PyQt5 با طراحی مشابه نسخه اولیه CustomTkinter
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
    QStyleFactory, QSpacerItem, QSizePolicy, QPushButton as QPushButton2
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QSize, QPoint, QSettings, QTranslator, QLocale
)
from PyQt5.QtGui import (
    QFont, QPixmap, QIcon, QPalette, QColor, QLinearGradient,
    QBrush, QPainter, QFontDatabase, QMovie
)

# Configuration Manager
class ConfigManager:
    """مدیریت تنظیمات برنامه"""
    
    def __init__(self, config_file="config_original.json"):
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
                "support_email": "support@noavaran-positive-green.ir",
                "purchase_url": "https://zarinp.al/735413"
            },
            "ui_settings": {
                "language": "fa",
                "theme": "original_style",
                "font_family": "Tahoma",
                "font_size": 10,
                "window_maximized": True
            },
            "performance": {
                "buffer_size": 8192,
                "max_threads": 4,
                "scan_depth": 3
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

class LicenseManager:
    """مدیریت لایسنس ساده"""
    
    def __init__(self):
        self.license_file = "license_original.dat"
        
    def get_trial_remaining_days(self):
        """محاسبه روزهای باقیمانده آزمایشی"""
        try:
            license_data = self.load_license()
            if not license_data:
                return 30
            
            install_date = license_data.get("install_date")
            if install_date:
                install_dt = datetime.fromisoformat(install_date)
                days_passed = (datetime.now() - install_dt).days
                return max(0, 30 - days_passed)
        except:
            pass
        return 30
    
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
            "install_date": datetime.now().isoformat()
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

class FileCopyWorker(QThread):
    """Worker برای کپی فایل‌ها"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, source_files, destination):
        super().__init__()
        self.source_files = source_files
        self.destination = destination
        self.is_paused = False
        self.is_cancelled = False
    
    def run(self):
        """اجرای عملیات کپی"""
        try:
            total_files = len(self.source_files)
            
            for i, source_file in enumerate(self.source_files):
                if self.is_cancelled:
                    break
                
                while self.is_paused:
                    self.msleep(100)
                    if self.is_cancelled:
                        break
                
                if self.is_cancelled:
                    break
                
                # شبیه‌سازی کپی فایل
                self.status_updated.emit(f"کپی {os.path.basename(source_file)}...")
                
                # کپی واقعی فایل
                dest_file = os.path.join(self.destination, os.path.basename(source_file))
                try:
                    shutil.copy2(source_file, dest_file)
                except Exception as e:
                    self.status_updated.emit(f"خطا در کپی: {str(e)}")
                
                # بروزرسانی پیشرفت
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)
                
                self.msleep(100)  # شبیه‌سازی زمان کپی
            
            if not self.is_cancelled:
                self.status_updated.emit("کپی با موفقیت تکمیل شد")
            else:
                self.status_updated.emit("کپی لغو شد")
                
        except Exception as e:
            self.status_updated.emit(f"خطا: {str(e)}")
        
        self.finished.emit()
    
    def pause(self):
        """توقف عملیات"""
        self.is_paused = True
    
    def resume(self):
        """ادامه عملیات"""
        self.is_paused = False
    
    def cancel(self):
        """لغو عملیات"""
        self.is_cancelled = True

class PersianFileCopierOriginal(QMainWindow):
    """کلاس اصلی نرم‌افزار با طراحی مشابه نسخه اولیه"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.license_manager = LicenseManager()
        
        # Application state
        self.copy_worker = None
        self.selected_files = []
        self.destination_path = ""
        
        # Setup UI
        self.init_ui()
        self.setup_styling()
        
        # Load initial data
        self.load_drives()
        self.check_license_status()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری مشابه نسخه اولیه"""
        # Window settings
        self.setWindowTitle("Persian File Copier Pro - Original Style")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # اگر تنظیمات maximize فعال باشد
        if self.config_manager.get("ui_settings", "window_maximized", True):
            self.showMaximized()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # Create main tab widget
        self.create_main_tabs(main_layout)
        
        # Create status bar
        self.create_status_bar()
    
    def create_main_tabs(self, main_layout):
        """ایجاد تب‌های اصلی مشابه نسخه اولیه"""
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # File Explorer Tab - مرورگر فایل
        self.create_file_explorer_tab()
        
        # Destinations Tab - مقاصد
        self.create_destinations_tab()
        
        # Settings Tab - تنظیمات
        self.create_settings_tab()
        
        # About Tab - درباره ما
        self.create_about_tab()
    
    def create_file_explorer_tab(self):
        """تب مرورگر فایل مشابه نسخه اولیه"""
        explorer_widget = QWidget()
        layout = QVBoxLayout(explorer_widget)
        
        # Drive selection area
        drive_frame = QFrame()
        drive_frame.setFrameStyle(QFrame.StyledPanel)
        drive_layout = QHBoxLayout(drive_frame)
        
        drive_label = QLabel("انتخاب درایو:")
        drive_label.setFont(QFont("Tahoma", 10, QFont.Bold))
        drive_layout.addWidget(drive_label)
        
        self.drive_combo = QComboBox()
        self.drive_combo.setMinimumWidth(200)
        self.drive_combo.currentTextChanged.connect(self.on_drive_changed)
        drive_layout.addWidget(self.drive_combo)
        
        drive_layout.addStretch()
        layout.addWidget(drive_frame)
        
        # Main splitter for file browser
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Folder tree
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_frame)
        
        folder_label = QLabel("پوشه‌ها:")
        folder_label.setFont(QFont("Tahoma", 10, QFont.Bold))
        left_layout.addWidget(folder_label)
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(['نام پوشه'])
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        left_layout.addWidget(self.folder_tree)
        
        # Right side - File list
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        
        file_label = QLabel("فایل‌ها:")
        file_label.setFont(QFont("Tahoma", 10, QFont.Bold))
        right_layout.addWidget(file_label)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(['نام فایل', 'اندازه', 'نوع', 'تاریخ تغییر'])
        self.file_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        right_layout.addWidget(self.file_tree)
        
        # File operations buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        self.select_all_btn = QPushButton("انتخاب همه")
        self.select_all_btn.clicked.connect(self.select_all_files)
        button_layout.addWidget(self.select_all_btn)
        
        self.copy_btn = QPushButton("کپی فایل‌های انتخابی")
        self.copy_btn.clicked.connect(self.copy_selected_files)
        button_layout.addWidget(self.copy_btn)
        
        self.browse_dest_btn = QPushButton("انتخاب مقصد...")
        self.browse_dest_btn.clicked.connect(self.browse_destination)
        button_layout.addWidget(self.browse_dest_btn)
        
        button_layout.addStretch()
        right_layout.addWidget(button_frame)
        
        # Destination display
        dest_frame = QFrame()
        dest_layout = QHBoxLayout(dest_frame)
        
        dest_label = QLabel("مقصد:")
        dest_label.setFont(QFont("Tahoma", 10, QFont.Bold))
        dest_layout.addWidget(dest_label)
        
        self.dest_line_edit = QLineEdit()
        self.dest_line_edit.setPlaceholderText("مسیر مقصد را انتخاب کنید...")
        dest_layout.addWidget(self.dest_line_edit)
        
        right_layout.addWidget(dest_frame)
        
        # Add to splitter
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # Progress area
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.StyledPanel)
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_label = QLabel("پیشرفت عملیات:")
        progress_label.setFont(QFont("Tahoma", 10, QFont.Bold))
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("آماده")
        progress_layout.addWidget(self.status_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("توقف")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_operation)
        control_layout.addWidget(self.pause_btn)
        
        self.resume_btn = QPushButton("ادامه")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self.resume_operation)
        control_layout.addWidget(self.resume_btn)
        
        self.cancel_btn = QPushButton("لغو")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        control_layout.addWidget(self.cancel_btn)
        
        control_layout.addStretch()
        progress_layout.addLayout(control_layout)
        
        layout.addWidget(progress_frame)
        
        self.tab_widget.addTab(explorer_widget, "مرورگر فایل")
    
    def create_destinations_tab(self):
        """تب مقاصد"""
        dest_widget = QWidget()
        layout = QVBoxLayout(dest_widget)
        
        # Header
        header_label = QLabel("مقاصد پیش‌فرض")
        header_label.setFont(QFont("Tahoma", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Quick destinations
        quick_frame = QGroupBox("مقاصد سریع")
        quick_layout = QGridLayout(quick_frame)
        
        destinations = [
            ("دسکتاپ", os.path.expanduser("~/Desktop")),
            ("دانلودها", os.path.expanduser("~/Downloads")),
            ("اسناد", os.path.expanduser("~/Documents")),
            ("تصاویر", os.path.expanduser("~/Pictures")),
            ("ویدیوها", os.path.expanduser("~/Videos")),
            ("موزیک", os.path.expanduser("~/Music"))
        ]
        
        for i, (name, path) in enumerate(destinations):
            btn = QPushButton(f"📁 {name}")
            btn.clicked.connect(lambda checked, p=path: self.set_destination(p))
            quick_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(quick_frame)
        
        # Custom destination
        custom_frame = QGroupBox("مقصد سفارشی")
        custom_layout = QVBoxLayout(custom_frame)
        
        custom_path_layout = QHBoxLayout()
        self.custom_dest_edit = QLineEdit()
        self.custom_dest_edit.setPlaceholderText("مسیر مقصد سفارشی...")
        custom_path_layout.addWidget(self.custom_dest_edit)
        
        browse_custom_btn = QPushButton("...")
        browse_custom_btn.setMaximumWidth(50)
        browse_custom_btn.clicked.connect(self.browse_custom_destination)
        custom_path_layout.addWidget(browse_custom_btn)
        
        custom_layout.addLayout(custom_path_layout)
        
        set_custom_btn = QPushButton("تنظیم به عنوان مقصد")
        set_custom_btn.clicked.connect(self.set_custom_destination)
        custom_layout.addWidget(set_custom_btn)
        
        layout.addWidget(custom_frame)
        
        layout.addStretch()
        
        self.tab_widget.addTab(dest_widget, "مقاصد")
    
    def create_settings_tab(self):
        """تب تنظیمات"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Header
        header_label = QLabel("تنظیمات برنامه")
        header_label.setFont(QFont("Tahoma", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Settings groups
        
        # General settings
        general_group = QGroupBox("تنظیمات عمومی")
        general_layout = QFormLayout(general_group)
        
        self.maximize_check = QCheckBox("اجرای maximized برنامه")
        self.maximize_check.setChecked(
            self.config_manager.get("ui_settings", "window_maximized", True)
        )
        general_layout.addRow("نمایش:", self.maximize_check)
        
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(1024, 65536)
        self.buffer_spin.setValue(
            self.config_manager.get("performance", "buffer_size", 8192)
        )
        general_layout.addRow("اندازه Buffer:", self.buffer_spin)
        
        layout.addWidget(general_group)
        
        # License settings
        license_group = QGroupBox("اطلاعات لایسنس")
        license_layout = QVBoxLayout(license_group)
        
        license_data = self.license_manager.load_license()
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            remaining_days = self.license_manager.get_trial_remaining_days()
            license_text = f"نسخه آزمایشی - {remaining_days} روز باقیمانده"
        else:
            license_text = f"لایسنس {license_type} - فعال"
        
        license_info_label = QLabel(license_text)
        license_info_label.setFont(QFont("Tahoma", 12, QFont.Bold))
        license_layout.addWidget(license_info_label)
        
        if license_type == "trial":
            purchase_btn = QPushButton("خرید لایسنس از زرین‌پال")
            purchase_btn.clicked.connect(self.open_purchase_page)
            purchase_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 12px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            license_layout.addWidget(purchase_btn)
        
        layout.addWidget(license_group)
        
        # Save settings button
        save_btn = QPushButton("ذخیره تنظیمات")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "تنظیمات")
    
    def create_about_tab(self):
        """تب درباره ما"""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)
        
        # Company info
        company_frame = QGroupBox("اطلاعات شرکت")
        company_layout = QVBoxLayout(company_frame)
        
        company_name = QLabel("شرکت فناوری نوآئران مثبت سبز")
        company_name.setAlignment(Qt.AlignCenter)
        company_name.setFont(QFont("Tahoma", 16, QFont.Bold))
        company_name.setStyleSheet("color: #2E8B57;")
        company_layout.addWidget(company_name)
        
        app_name = QLabel("Persian File Copier Pro v3.0 - Original Style")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Tahoma", 14))
        app_name.setStyleSheet("color: #4682B4;")
        company_layout.addWidget(app_name)
        
        description = QLabel("""
        نرم‌افزار حرفه‌ای کپی و مدیریت فایل
        • رابط کاربری ساده و کاربرپسند
        • کپی سریع و ایمن فایل‌ها
        • پشتیبانی کامل از زبان فارسی
        • طراحی مشابه نسخه اولیه CustomTkinter
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        company_layout.addWidget(description)
        
        layout.addWidget(company_frame)
        
        # Contact info
        contact_frame = QGroupBox("اطلاعات تماس")
        contact_layout = QFormLayout(contact_frame)
        
        contact_layout.addRow("وب‌سایت:", QLabel("https://noavaran-positive-green.ir"))
        contact_layout.addRow("ایمیل:", QLabel("support@noavaran-positive-green.ir"))
        contact_layout.addRow("خرید:", QLabel("https://zarinp.al/735413"))
        
        layout.addWidget(contact_frame)
        
        layout.addStretch()
        
        self.tab_widget.addTab(about_widget, "درباره ما")
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_message = QLabel("آماده")
        self.status_bar.addWidget(self.status_message)
        
        # License status
        license_data = self.license_manager.load_license()
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            remaining_days = self.license_manager.get_trial_remaining_days()
            license_text = f"آزمایشی ({remaining_days} روز باقیمانده)"
        else:
            license_text = f"لایسنس {license_type}"
        
        self.license_status = QLabel(license_text)
        self.status_bar.addPermanentWidget(self.license_status)
    
    def setup_styling(self):
        """راه‌اندازی استایل‌دهی مشابه نسخه اولیه"""
        # Set application style
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: right;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
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
                background-color: #cccccc;
                color: #666666;
            }
            QTreeWidget {
                border: 1px solid #cccccc;
                alternate-background-color: #f9f9f9;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
    
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
    
    # Event handlers
    def on_drive_changed(self, drive_text):
        """تغییر درایو"""
        self.status_message.setText(f"بارگذاری: {drive_text}")
        # Implementation for loading drive contents
        self.load_folders_and_files(drive_text)
    
    def load_folders_and_files(self, drive_text):
        """بارگذاری پوشه‌ها و فایل‌ها"""
        # Clear existing items
        self.folder_tree.clear()
        self.file_tree.clear()
        
        if drive_text == "همه درایوها":
            # Load all drives
            for partition in psutil.disk_partitions():
                try:
                    root_item = QTreeWidgetItem(self.folder_tree)
                    root_item.setText(0, partition.device)
                    root_item.setData(0, Qt.UserRole, partition.mountpoint)
                    
                    # Add some sample folders
                    self.add_sample_folders(root_item, partition.mountpoint)
                except:
                    continue
        else:
            # Load specific drive
            drive_path = drive_text.split()[0]  # Extract drive letter
            try:
                root_item = QTreeWidgetItem(self.folder_tree)
                root_item.setText(0, drive_path)
                root_item.setData(0, Qt.UserRole, drive_path)
                
                self.add_sample_folders(root_item, drive_path)
            except:
                pass
        
        self.folder_tree.expandAll()
    
    def add_sample_folders(self, parent_item, path):
        """افزودن پوشه‌های نمونه"""
        try:
            for item in os.listdir(path)[:10]:  # First 10 items only
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    folder_item = QTreeWidgetItem(parent_item)
                    folder_item.setText(0, item)
                    folder_item.setData(0, Qt.UserRole, item_path)
        except:
            pass
    
    def on_folder_selected(self, item, column):
        """انتخاب پوشه"""
        folder_path = item.data(0, Qt.UserRole)
        if folder_path:
            self.load_files_in_folder(folder_path)
    
    def load_files_in_folder(self, folder_path):
        """بارگذاری فایل‌های پوشه"""
        self.file_tree.clear()
        
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    file_item = QTreeWidgetItem(self.file_tree)
                    file_item.setText(0, item)
                    
                    # File size
                    try:
                        size = os.path.getsize(item_path)
                        size_str = self.format_file_size(size)
                        file_item.setText(1, size_str)
                    except:
                        file_item.setText(1, "نامشخص")
                    
                    # File type
                    ext = os.path.splitext(item)[1].lower()
                    file_item.setText(2, ext if ext else "فایل")
                    
                    # Modified date
                    try:
                        mtime = os.path.getmtime(item_path)
                        date_str = datetime.fromtimestamp(mtime).strftime("%Y/%m/%d %H:%M")
                        file_item.setText(3, date_str)
                    except:
                        file_item.setText(3, "نامشخص")
                    
                    file_item.setData(0, Qt.UserRole, item_path)
        except:
            pass
    
    def format_file_size(self, size):
        """فرمت اندازه فایل"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def select_all_files(self):
        """انتخاب همه فایل‌ها"""
        self.file_tree.selectAll()
    
    def copy_selected_files(self):
        """کپی فایل‌های انتخاب شده"""
        selected_items = self.file_tree.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "هشدار", "لطفاً فایل‌هایی را انتخاب کنید.")
            return
        
        destination = self.dest_line_edit.text().strip()
        if not destination or not os.path.exists(destination):
            QMessageBox.warning(self, "هشدار", "لطفاً مقصد معتبری را انتخاب کنید.")
            return
        
        # Get file paths
        self.selected_files = []
        for item in selected_items:
            file_path = item.data(0, Qt.UserRole)
            if file_path and os.path.exists(file_path):
                self.selected_files.append(file_path)
        
        if not self.selected_files:
            QMessageBox.warning(self, "هشدار", "فایل‌های معتبری برای کپی یافت نشد.")
            return
        
        # Start copy operation
        self.start_copy_operation()
    
    def start_copy_operation(self):
        """شروع عملیات کپی"""
        if self.copy_worker and self.copy_worker.isRunning():
            QMessageBox.warning(self, "هشدار", "عملیات کپی در حال اجرا است.")
            return
        
        self.destination_path = self.dest_line_edit.text().strip()
        
        # Setup UI for operation
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.copy_btn.setEnabled(False)
        
        # Create and start worker
        self.copy_worker = FileCopyWorker(self.selected_files, self.destination_path)
        self.copy_worker.progress_updated.connect(self.progress_bar.setValue)
        self.copy_worker.status_updated.connect(self.status_label.setText)
        self.copy_worker.finished.connect(self.on_copy_finished)
        self.copy_worker.start()
    
    def pause_operation(self):
        """توقف عملیات"""
        if self.copy_worker:
            self.copy_worker.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.status_label.setText("متوقف شده")
    
    def resume_operation(self):
        """ادامه عملیات"""
        if self.copy_worker:
            self.copy_worker.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.status_label.setText("در حال ادامه...")
    
    def cancel_operation(self):
        """لغو عملیات"""
        if self.copy_worker:
            self.copy_worker.cancel()
            self.copy_worker.wait()
        self.on_copy_finished()
    
    def on_copy_finished(self):
        """پایان عملیات کپی"""
        self.progress_bar.setVisible(False)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.copy_btn.setEnabled(True)
        
        if self.copy_worker and not self.copy_worker.is_cancelled:
            QMessageBox.information(self, "اطلاع", "کپی فایل‌ها با موفقیت تکمیل شد.")
        
        self.copy_worker = None
    
    def browse_destination(self):
        """انتخاب مقصد"""
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه مقصد")
        if folder:
            self.dest_line_edit.setText(folder)
    
    def set_destination(self, path):
        """تنظیم مقصد"""
        if os.path.exists(path):
            self.dest_line_edit.setText(path)
            self.tab_widget.setCurrentIndex(0)  # Switch to file explorer
    
    def browse_custom_destination(self):
        """انتخاب مقصد سفارشی"""
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه مقصد سفارشی")
        if folder:
            self.custom_dest_edit.setText(folder)
    
    def set_custom_destination(self):
        """تنظیم مقصد سفارشی"""
        path = self.custom_dest_edit.text().strip()
        if path and os.path.exists(path):
            self.dest_line_edit.setText(path)
            self.tab_widget.setCurrentIndex(0)  # Switch to file explorer
        else:
            QMessageBox.warning(self, "هشدار", "مسیر وارد شده معتبر نیست.")
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        # Update config
        self.config_manager.config["ui_settings"]["window_maximized"] = self.maximize_check.isChecked()
        self.config_manager.config["performance"]["buffer_size"] = self.buffer_spin.value()
        
        # Save to file
        if self.config_manager.save_config():
            QMessageBox.information(self, "موفقیت", "تنظیمات ذخیره شد.")
        else:
            QMessageBox.critical(self, "خطا", "خطا در ذخیره تنظیمات.")
    
    def open_purchase_page(self):
        """باز کردن صفحه خرید"""
        purchase_url = "https://zarinp.al/735413"
        webbrowser.open(purchase_url)
    
    def show_trial_expired_dialog(self):
        """نمایش دیالوگ پایان آزمایشی"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("پایان دوره آزمایشی")
        msg.setText("دوره آزمایشی شما به پایان رسیده است.")
        msg.setInformativeText("برای ادامه استفاده، لطفاً لایسنس خریداری کنید.")
        
        purchase_btn = msg.addButton("خرید لایسنس", QMessageBox.AcceptRole)
        msg.addButton("خروج", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == purchase_btn:
            self.open_purchase_page()

def main():
    """تابع اصلی"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Persian File Copier Pro - Original Style")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("شرکت فناوری نوآئران مثبت سبز")
    
    # Set Persian font
    try:
        font = QFont("Tahoma", 10)
        app.setFont(font)
    except:
        pass
    
    # Create and show main window
    window = PersianFileCopierOriginal()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()