#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro - Enhanced UI/UX Edition
شرکت فناوری نوآئران مثبت سبز
نسخه پیشرفته با UI بهبود یافته و عملکرد روان‌تر
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import os
import sys
import threading
import time
import json
import shutil
import psutil
import queue
import uuid
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from pathlib import Path
import hashlib
import base64
import webbrowser
import subprocess
from threading import Lock

# تنظیم CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# تنظیم لاگ‌گیری پیشرفته
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_enhanced.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class EnhancedThemeManager:
    """مدیریت تم‌های پیشرفته و جذاب"""
    
    def __init__(self):
        self.themes = {
            "dark_modern": {
                "name": "تیره مدرن",
                "bg_color": ["gray90", "gray13"],
                "fg_color": ["gray10", "gray90"],
                "button_color": ["#3B82F6", "#2563EB"],
                "button_hover": ["#2563EB", "#1D4ED8"],
                "success_color": ["#10B981", "#059669"],
                "warning_color": ["#F59E0B", "#D97706"],
                "error_color": ["#EF4444", "#DC2626"],
                "accent_color": ["#8B5CF6", "#7C3AED"],
                "progress_color": ["#06B6D4", "#0891B2"]
            },
            "light_vibrant": {
                "name": "روشن پرانرژی",
                "bg_color": ["gray95", "gray20"],
                "fg_color": ["gray20", "gray95"],
                "button_color": ["#FF6B6B", "#FF5252"],
                "button_hover": ["#FF5252", "#FF1744"],
                "success_color": ["#4ECDC4", "#26A69A"],
                "warning_color": ["#FFE66D", "#FFCC02"],
                "error_color": ["#FF6B6B", "#FF5252"],
                "accent_color": ["#A8E6CF", "#81C784"],
                "progress_color": ["#FFD93D", "#FFC107"]
            },
            "purple_dream": {
                "name": "رویای بنفش",
                "bg_color": ["#F3E8FF", "#1F1B24"],
                "fg_color": ["#1F1B24", "#F3E8FF"],
                "button_color": ["#8B5CF6", "#7C3AED"],
                "button_hover": ["#7C3AED", "#6D28D9"],
                "success_color": ["#34D399", "#10B981"],
                "warning_color": ["#FBBF24", "#F59E0B"],
                "error_color": ["#F87171", "#EF4444"],
                "accent_color": ["#A78BFA", "#8B5CF6"],
                "progress_color": ["#EC4899", "#DB2777"]
            },
            "ocean_blue": {
                "name": "آبی اقیانوس",
                "bg_color": ["#E0F2FE", "#0C4A6E"],
                "fg_color": ["#0C4A6E", "#E0F2FE"],
                "button_color": ["#0EA5E9", "#0284C7"],
                "button_hover": ["#0284C7", "#0369A1"],
                "success_color": ["#22D3EE", "#06B6D4"],
                "warning_color": ["#FB923C", "#EA580C"],
                "error_color": ["#F472B6", "#EC4899"],
                "accent_color": ["#38BDF8", "#0EA5E9"],
                "progress_color": ["#34D399", "#10B981"]
            },
            "sunset_orange": {
                "name": "نارنجی غروب",
                "bg_color": ["#FFF7ED", "#431407"],
                "fg_color": ["#431407", "#FFF7ED"],
                "button_color": ["#EA580C", "#DC2626"],
                "button_hover": ["#DC2626", "#B91C1C"],
                "success_color": ["#65A30D", "#4D7C0F"],
                "warning_color": ["#F59E0B", "#D97706"],
                "error_color": ["#DC2626", "#B91C1C"],
                "accent_color": ["#FB923C", "#EA580C"],
                "progress_color": ["#FBBF24", "#F59E0B"]
            },
            "forest_green": {
                "name": "سبز جنگلی",
                "bg_color": ["#F0FDF4", "#14532D"],
                "fg_color": ["#14532D", "#F0FDF4"],
                "button_color": ["#16A34A", "#15803D"],
                "button_hover": ["#15803D", "#166534"],
                "success_color": ["#22C55E", "#16A34A"],
                "warning_color": ["#EAB308", "#CA8A04"],
                "error_color": ["#DC2626", "#B91C1C"],
                "accent_color": ["#84CC16", "#65A30D"],
                "progress_color": ["#10B981", "#059669"]
            }
        }
        self.current_theme = "dark_modern"
    
    def get_theme(self, theme_name=None):
        """دریافت تم"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["dark_modern"])
    
    def apply_theme(self, theme_name):
        """اعمال تم"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_theme_names(self):
        """دریافت لیست نام تم‌ها"""
        return [theme["name"] for theme in self.themes.values()]

class AnimatedProgressBar(ctk.CTkFrame):
    """پروگرس بار انیمیت شده برای هر تسک"""
    
    def __init__(self, parent, width=300, height=25, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        self.width = width
        self.height = height
        self.progress = 0.0
        self.max_value = 100.0
        
        # ایجاد canvas برای رسم
        self.canvas = tk.Canvas(
            self,
            width=width-4,
            height=height-4,
            highlightthickness=0,
            bg=self._apply_appearance_mode(("gray90", "gray20"))
        )
        self.canvas.pack(padx=2, pady=2)
        
        # ایجاد المان‌های پروگرس بار
        self.bg_rect = self.canvas.create_rectangle(
            0, 0, width-4, height-4,
            fill=self._apply_appearance_mode(("gray80", "gray30")),
            outline=""
        )
        
        self.progress_rect = self.canvas.create_rectangle(
            0, 0, 0, height-4,
            fill=self._apply_appearance_mode(("#3B82F6", "#2563EB")),
            outline=""
        )
        
        # متن درصد
        self.text_item = self.canvas.create_text(
            (width-4)//2, (height-4)//2,
            text="0%",
            fill=self._apply_appearance_mode(("gray20", "gray90")),
            font=("Arial", 10, "bold")
        )
        
        # متغیرهای انیمیشن
        self.target_progress = 0.0
        self.animation_speed = 0.1
        self.animate_progress()
    
    def set_progress(self, value):
        """تنظیم مقدار پیشرفت"""
        self.target_progress = max(0, min(100, value))
    
    def animate_progress(self):
        """انیمیشن روان پیشرفت"""
        if abs(self.progress - self.target_progress) > 0.5:
            # محاسبه مقدار جدید با انیمیشن روان
            diff = self.target_progress - self.progress
            self.progress += diff * self.animation_speed
            
            # محاسبه عرض پروگرس بار
            progress_width = (self.progress / 100.0) * (self.width - 4)
            
            # بروزرسانی رسم
            self.canvas.coords(
                self.progress_rect,
                0, 0, progress_width, self.height-4
            )
            
            # بروزرسانی متن
            self.canvas.itemconfig(
                self.text_item,
                text=f"{int(self.progress)}%"
            )
            
            # رنگ‌آمیزی براساس مقدار
            if self.progress < 30:
                color = "#EF4444"  # قرمز
            elif self.progress < 70:
                color = "#F59E0B"  # نارنجی
            else:
                color = "#10B981"  # سبز
            
            self.canvas.itemconfig(self.progress_rect, fill=color)
        
        # ادامه انیمیشن
        self.after(50, self.animate_progress)

class TaskRow(ctk.CTkFrame):
    """ردیف تسک با کنترل‌های inline"""
    
    def __init__(self, parent, task_data, theme_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.task_data = task_data
        self.theme_manager = theme_manager
        self.is_paused = False
        self.is_cancelled = False
        
        self.setup_ui()
        self.update_theme()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری ردیف"""
        # تنظیم grid weights
        self.grid_columnconfigure(1, weight=1)
        
        # آیکون وضعیت
        self.status_icon = ctk.CTkLabel(
            self, text="⏳", font=ctk.CTkFont(size=16), width=30
        )
        self.status_icon.grid(row=0, column=0, padx=5, pady=5)
        
        # اطلاعات تسک
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # نام تسک
        self.task_name = ctk.CTkLabel(
            info_frame,
            text=self.task_data.get("name", "نامشخص"),
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        self.task_name.grid(row=0, column=0, sticky="w", padx=10, pady=2)
        
        # جزئیات
        details = f"از: {self.task_data.get('source', 'نامشخص')} | به: {self.task_data.get('destination', 'نامشخص')}"
        self.task_details = ctk.CTkLabel(
            info_frame,
            text=details,
            font=ctk.CTkFont(size=10),
            anchor="w",
            text_color="gray"
        )
        self.task_details.grid(row=1, column=0, sticky="w", padx=10, pady=0)
        
        # پروگرس بار انیمیت شده
        self.progress_bar = AnimatedProgressBar(
            self, width=200, height=20,
            fg_color="transparent"
        )
        self.progress_bar.grid(row=0, column=2, padx=5, pady=5)
        
        # زمان باقیمانده
        self.time_remaining = ctk.CTkLabel(
            self, text="--:--", font=ctk.CTkFont(size=10), width=50
        )
        self.time_remaining.grid(row=0, column=3, padx=5, pady=5)
        
        # دکمه‌های کنترل
        self.setup_control_buttons()
    
    def setup_control_buttons(self):
        """راه‌اندازی دکمه‌های کنترل"""
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=0, column=4, padx=5, pady=5)
        
        # دکمه توقف/ادامه
        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="⏸️",
            width=30,
            height=25,
            command=self.toggle_pause,
            font=ctk.CTkFont(size=12)
        )
        self.pause_btn.pack(side="left", padx=1)
        
        # دکمه لغو
        self.cancel_btn = ctk.CTkButton(
            controls_frame,
            text="❌",
            width=30,
            height=25,
            command=self.cancel_task,
            font=ctk.CTkFont(size=12),
            fg_color="red",
            hover_color="darkred"
        )
        self.cancel_btn.pack(side="left", padx=1)
        
        # دکمه جزئیات
        self.details_btn = ctk.CTkButton(
            controls_frame,
            text="📋",
            width=30,
            height=25,
            command=self.show_details,
            font=ctk.CTkFont(size=12)
        )
        self.details_btn.pack(side="left", padx=1)
    
    def update_progress(self, progress, time_remaining=None):
        """بروزرسانی پیشرفت"""
        self.progress_bar.set_progress(progress)
        
        if time_remaining:
            self.time_remaining.configure(text=time_remaining)
        
        # بروزرسانی آیکون وضعیت
        if progress >= 100:
            self.status_icon.configure(text="✅")
        elif self.is_paused:
            self.status_icon.configure(text="⏸️")
        elif self.is_cancelled:
            self.status_icon.configure(text="❌")
        else:
            self.status_icon.configure(text="🔄")
    
    def toggle_pause(self):
        """توقف/ادامه تسک"""
        self.is_paused = not self.is_paused
        self.pause_btn.configure(text="▶️" if self.is_paused else "⏸️")
        self.update_progress(self.progress_bar.progress)
    
    def cancel_task(self):
        """لغو تسک"""
        self.is_cancelled = True
        self.status_icon.configure(text="❌")
        # غیرفعال کردن دکمه‌ها
        self.pause_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
    
    def show_details(self):
        """نمایش جزئیات تسک"""
        details_window = ctk.CTkToplevel(self)
        details_window.title("جزئیات تسک")
        details_window.geometry("400x300")
        
        # محتوای جزئیات
        details_text = ctk.CTkTextbox(details_window)
        details_text.pack(fill="both", expand=True, padx=20, pady=20)
        
        details_content = f"""
نام تسک: {self.task_data.get('name', 'نامشخص')}
منبع: {self.task_data.get('source', 'نامشخص')}
مقصد: {self.task_data.get('destination', 'نامشخص')}
وضعیت: {'متوقف شده' if self.is_paused else 'در حال اجرا' if not self.is_cancelled else 'لغو شده'}
پیشرفت: {int(self.progress_bar.progress)}%
زمان شروع: {self.task_data.get('start_time', 'نامشخص')}
"""
        details_text.insert("0.0", details_content)
        details_text.configure(state="disabled")
    
    def update_theme(self):
        """بروزرسانی تم"""
        theme = self.theme_manager.get_theme()
        self.configure(fg_color=theme["bg_color"])

class EnhancedTaskManager(ctk.CTkFrame):
    """مدیریت تسک‌های پیشرفته"""
    
    def __init__(self, parent, theme_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.theme_manager = theme_manager
        self.tasks = {}
        self.task_counter = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        # هدر
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="مدیریت تسک‌ها",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # دکمه‌های کنترل کلی
        self.setup_global_controls(header_frame)
        
        # ناحیه اسکرول برای تسک‌ها
        self.tasks_scroll = ctk.CTkScrollableFrame(self)
        self.tasks_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # پیام خالی بودن
        self.empty_message = ctk.CTkLabel(
            self.tasks_scroll,
            text="هیچ تسکی در حال اجرا نیست",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.empty_message.pack(pady=50)
    
    def setup_global_controls(self, parent):
        """دکمه‌های کنترل کلی"""
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)
        
        # توقف همه
        pause_all_btn = ctk.CTkButton(
            controls_frame,
            text="⏸️ توقف همه",
            command=self.pause_all_tasks,
            width=100,
            height=30
        )
        pause_all_btn.pack(side="left", padx=2)
        
        # ادامه همه
        resume_all_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ ادامه همه",
            command=self.resume_all_tasks,
            width=100,
            height=30
        )
        resume_all_btn.pack(side="left", padx=2)
        
        # لغو همه
        cancel_all_btn = ctk.CTkButton(
            controls_frame,
            text="❌ لغو همه",
            command=self.cancel_all_tasks,
            width=100,
            height=30,
            fg_color="red",
            hover_color="darkred"
        )
        cancel_all_btn.pack(side="left", padx=2)
        
        # پاک کردن تمام شده‌ها
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️ پاک کردن",
            command=self.clear_completed_tasks,
            width=100,
            height=30
        )
        clear_btn.pack(side="left", padx=2)
    
    def add_task(self, task_data):
        """افزودن تسک جدید"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        # پنهان کردن پیام خالی
        self.empty_message.pack_forget()
        
        # ایجاد ردیف تسک
        task_row = TaskRow(
            self.tasks_scroll,
            task_data,
            self.theme_manager,
            corner_radius=8,
            height=60
        )
        task_row.pack(fill="x", padx=5, pady=2)
        
        self.tasks[task_id] = task_row
        return task_id
    
    def update_task_progress(self, task_id, progress, time_remaining=None):
        """بروزرسانی پیشرفت تسک"""
        if task_id in self.tasks:
            self.tasks[task_id].update_progress(progress, time_remaining)
    
    def remove_task(self, task_id):
        """حذف تسک"""
        if task_id in self.tasks:
            self.tasks[task_id].destroy()
            del self.tasks[task_id]
            
            # نمایش پیام خالی در صورت نبود تسک
            if not self.tasks:
                self.empty_message.pack(pady=50)
    
    def pause_all_tasks(self):
        """توقف همه تسک‌ها"""
        for task in self.tasks.values():
            if not task.is_paused and not task.is_cancelled:
                task.toggle_pause()
    
    def resume_all_tasks(self):
        """ادامه همه تسک‌ها"""
        for task in self.tasks.values():
            if task.is_paused and not task.is_cancelled:
                task.toggle_pause()
    
    def cancel_all_tasks(self):
        """لغو همه تسک‌ها"""
        for task in self.tasks.values():
            if not task.is_cancelled:
                task.cancel_task()
    
    def clear_completed_tasks(self):
        """پاک کردن تسک‌های تمام شده"""
        completed_tasks = []
        for task_id, task in self.tasks.items():
            if task.progress_bar.progress >= 100 or task.is_cancelled:
                completed_tasks.append(task_id)
        
        for task_id in completed_tasks:
            self.remove_task(task_id)

class EnhancedFileCopierApp:
    """نسخه پیشرفته برنامه کپی فایل"""
    
    def __init__(self, root):
        self.root = root
        self.theme_manager = EnhancedThemeManager()
        
        # تنظیمات اولیه
        self.setup_window()
        self.create_ui()
        self.apply_smooth_animations()
    
    def setup_window(self):
        """تنظیمات پنجره"""
        self.root.title("Persian File Copier Pro - Enhanced Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # تنظیم فونت فارسی
        self.root.option_add("*Font", "B Nazanin 11")
    
    def create_ui(self):
        """ایجاد رابط کاربری"""
        # منوی اصلی
        self.create_menu()
        
        # نوار ابزار
        self.create_toolbar()
        
        # ناحیه اصلی
        self.create_main_area()
        
        # نوار وضعیت
        self.create_status_bar()
    
    def create_menu(self):
        """ایجاد منوی اصلی"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # منوی فایل
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="فایل", menu=file_menu)
        file_menu.add_command(label="جدید", command=self.new_project)
        file_menu.add_command(label="باز کردن", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # منوی نمایش
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="نمایش", menu=view_menu)
        
        # زیرمنوی تم‌ها
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="تم‌ها", menu=theme_menu)
        
        for theme_name, theme_data in self.theme_manager.themes.items():
            theme_menu.add_command(
                label=theme_data["name"],
                command=lambda tn=theme_name: self.change_theme(tn)
            )
    
    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        self.toolbar = ctk.CTkFrame(self.root, height=50)
        self.toolbar.pack(fill="x", padx=5, pady=2)
        
        # دکمه‌های اصلی
        buttons_data = [
            ("📁 انتخاب فایل‌ها", self.select_files),
            ("📂 انتخاب مقصد", self.select_destination),
            ("🚀 شروع کپی", self.start_copy),
            ("⚙️ تنظیمات", self.open_settings),
            ("🎨 تغییر تم", self.show_theme_selector)
        ]
        
        for text, command in buttons_data:
            btn = ctk.CTkButton(
                self.toolbar,
                text=text,
                command=command,
                width=120,
                height=35,
                corner_radius=8
            )
            btn.pack(side="left", padx=3, pady=7)
    
    def create_main_area(self):
        """ایجاد ناحیه اصلی"""
        # تقسیم ناحیه اصلی
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill="both", expand=True, padx=5, pady=2)
        
        # سمت چپ - انتخاب فایل‌ها
        self.create_file_selection_area()
        
        # سمت راست - مدیریت تسک‌ها
        self.create_task_management_area()
    
    def create_file_selection_area(self):
        """ناحیه انتخاب فایل‌ها"""
        left_frame = ctk.CTkFrame(self.root)
        self.main_paned.add(left_frame, weight=1)
        
        # عنوان
        title = ctk.CTkLabel(
            left_frame,
            text="انتخاب فایل‌ها و پوشه‌ها",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=10)
        
        # لیست فایل‌ها (موقتی)
        self.file_listbox = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # نمونه داده‌ها
        sample_files = [
            "Document1.pdf", "Image1.jpg", "Video1.mp4",
            "Music1.mp3", "Archive1.zip", "Document2.docx"
        ]
        for file in sample_files:
            self.file_listbox.insert(tk.END, file)
    
    def create_task_management_area(self):
        """ناحیه مدیریت تسک‌ها"""
        right_frame = ctk.CTkFrame(self.root)
        self.main_paned.add(right_frame, weight=2)
        
        # مدیریت تسک‌های پیشرفته
        self.task_manager = EnhancedTaskManager(
            right_frame,
            self.theme_manager,
            corner_radius=8
        )
        self.task_manager.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.pack(fill="x", padx=5, pady=2)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="آماده",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # نمایش تم فعلی
        self.theme_label = ctk.CTkLabel(
            self.status_bar,
            text=f"تم: {self.theme_manager.get_theme()['name']}",
            font=ctk.CTkFont(size=10)
        )
        self.theme_label.pack(side="right", padx=10, pady=5)
    
    def apply_smooth_animations(self):
        """اعمال انیمیشن‌های روان"""
        # تنظیم انیمیشن برای تب‌ها
        def smooth_tab_transition():
            # انیمیشن محو شدن و ظاهر شدن تب‌ها
            pass
        
        # اعمال انیمیشن hover برای دکمه‌ها
        def add_hover_effect(widget):
            def on_enter(e):
                widget.configure(cursor="hand2")
            
            def on_leave(e):
                widget.configure(cursor="")
            
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def change_theme(self, theme_name):
        """تغییر تم"""
        if self.theme_manager.apply_theme(theme_name):
            # بروزرسانی رنگ‌های رابط
            theme = self.theme_manager.get_theme()
            
            # بروزرسانی نوار وضعیت
            self.theme_label.configure(text=f"تم: {theme['name']}")
            self.status_label.configure(text=f"تم تغییر یافت به {theme['name']}")
            
            # بروزرسانی مدیریت تسک‌ها
            for task in self.task_manager.tasks.values():
                task.update_theme()
    
    def show_theme_selector(self):
        """نمایش انتخابگر تم"""
        theme_window = ctk.CTkToplevel(self.root)
        theme_window.title("انتخاب تم")
        theme_window.geometry("400x500")
        theme_window.resizable(False, False)
        
        # عنوان
        title = ctk.CTkLabel(
            theme_window,
            text="انتخاب تم مورد علاقه",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=20)
        
        # پیش‌نمایش تم‌ها
        themes_frame = ctk.CTkScrollableFrame(theme_window)
        themes_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for theme_name, theme_data in self.theme_manager.themes.items():
            theme_frame = ctk.CTkFrame(themes_frame, corner_radius=10)
            theme_frame.pack(fill="x", pady=5)
            
            # نام تم
            name_label = ctk.CTkLabel(
                theme_frame,
                text=theme_data["name"],
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.pack(pady=5)
            
            # پیش‌نمایش رنگ‌ها
            colors_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
            colors_frame.pack(pady=5)
            
            colors = [
                theme_data["button_color"][1],
                theme_data["success_color"][1],
                theme_data["warning_color"][1],
                theme_data["error_color"][1],
                theme_data["accent_color"][1]
            ]
            
            for i, color in enumerate(colors):
                color_label = ctk.CTkLabel(
                    colors_frame,
                    text="    ",
                    fg_color=color,
                    width=40,
                    height=20,
                    corner_radius=5
                )
                color_label.pack(side="left", padx=2)
            
            # دکمه انتخاب
            select_btn = ctk.CTkButton(
                theme_frame,
                text="انتخاب این تم",
                command=lambda tn=theme_name: [
                    self.change_theme(tn),
                    theme_window.destroy()
                ],
                width=120,
                height=30
            )
            select_btn.pack(pady=5)
    
    # متدهای موقت
    def new_project(self):
        self.status_label.configure(text="پروژه جدید ایجاد شد")
    
    def open_project(self):
        self.status_label.configure(text="باز کردن پروژه...")
    
    def select_files(self):
        """انتخاب فایل‌ها"""
        files = filedialog.askopenfilenames(
            title="انتخاب فایل‌ها",
            filetypes=[("همه فایل‌ها", "*.*")]
        )
        if files:
            self.file_listbox.delete(0, tk.END)
            for file in files:
                self.file_listbox.insert(tk.END, os.path.basename(file))
            self.status_label.configure(text=f"{len(files)} فایل انتخاب شد")
    
    def select_destination(self):
        """انتخاب مقصد"""
        destination = filedialog.askdirectory(title="انتخاب پوشه مقصد")
        if destination:
            self.status_label.configure(text=f"مقصد: {destination}")
    
    def start_copy(self):
        """شروع کپی"""
        # ایجاد تسک‌های نمونه
        selected_files = self.file_listbox.curselection()
        if not selected_files:
            messagebox.showwarning("هشدار", "لطفاً فایل‌هایی را انتخاب کنید")
            return
        
        for i, index in enumerate(selected_files):
            file_name = self.file_listbox.get(index)
            task_data = {
                "name": f"کپی {file_name}",
                "source": f"/path/to/{file_name}",
                "destination": "/path/to/destination",
                "start_time": datetime.now().strftime("%H:%M:%S")
            }
            
            task_id = self.task_manager.add_task(task_data)
            
            # شبیه‌سازی پیشرفت
            self.simulate_progress(task_id, i * 1000)
    
    def simulate_progress(self, task_id, delay=0):
        """شبیه‌سازی پیشرفت تسک"""
        def update_progress():
            for progress in range(0, 101, 2):
                if task_id in self.task_manager.tasks:
                    # محاسبه زمان باقیمانده
                    remaining_seconds = (100 - progress) * 0.5
                    remaining_time = f"{int(remaining_seconds//60):02d}:{int(remaining_seconds%60):02d}"
                    
                    self.task_manager.update_task_progress(
                        task_id, progress, remaining_time
                    )
                    time.sleep(0.1)
                else:
                    break
        
        # اجرای پیشرفت در thread جداگانه
        def delayed_start():
            time.sleep(delay / 1000)  # تبدیل به ثانیه
            update_progress()
        
        threading.Thread(target=delayed_start, daemon=True).start()
    
    def open_settings(self):
        """باز کردن تنظیمات"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("تنظیمات")
        settings_window.geometry("500x400")
        
        # تنظیمات ساده
        settings_label = ctk.CTkLabel(
            settings_window,
            text="تنظیمات برنامه",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.pack(pady=20)

def main():
    """تابع اصلی"""
    try:
        # ایجاد پنجره اصلی
        root = ctk.CTk()
        
        # ایجاد برنامه
        app = EnhancedFileCopierApp(root)
        
        # اجرای برنامه
        root.mainloop()
        
    except Exception as e:
        logging.error(f"خطا در اجرای برنامه: {e}")
        messagebox.showerror("خطا", f"خطا در اجرای برنامه:\n{str(e)}")

if __name__ == "__main__":
    main()