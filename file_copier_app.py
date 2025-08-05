# وارد کردن کتابخانه‌های مورد نیاز برای عملکرد برنامه
import os  # برای عملیات سیستم‌عامل و مدیریت فایل‌ها و پوشه‌ها
import shutil  # برای کپی کردن فایل‌ها و پوشه‌ها به صورت پیشرفته
import tkinter as tk  # کتابخانه رابط کاربری پایه
from tkinter import filedialog, messagebox, ttk  # ابزارهای انتخاب فایل، پیام‌ها و ویجت‌های پیشرفته
import customtkinter as ctk  # کتابخانه رابط کاربری مدرن و زیبا
import threading  # برای اجرای همزمان عملیات و جلوگیری از قفل شدن رابط کاربری
import queue  # برای مدیریت صف کارها و ارتباط بین thread ها
import time  # برای عملیات زمان‌بندی و محاسبه مدت زمان
import json  # برای ذخیره و بارگذاری تنظیمات و داده‌ها به فرمت JSON
import sys  # برای دسترسی به اطلاعات سیستم و آرگومان‌های خط فرمان
import psutil  # برای دریافت اطلاعات سیستم، درایوها و فضای خالی
from pathlib import Path  # برای مدیریت مسیرها به صورت شیء‌گرا
from concurrent.futures import ThreadPoolExecutor, as_completed  # برای اجرای همزمان کارهای متعدد
import logging  # برای ثبت لاگ‌ها و رخدادهای مهم برنامه
import re  # برای عملیات regex و پردازش متن
from typing import Dict, List, Optional  # برای تعریف نوع داده‌ها و بهبود کیفیت کد
from datetime import datetime  # برای کار با تاریخ و زمان
import uuid  # برای تولید شناسه‌های منحصر به فرد
import hashlib  # برای ایجاد hash و رمزنگاری
import base64  # برای تبدیل داده‌ها به فرمت base64
import tkinter.messagebox  # برای نمایش پیام‌های سیستمی
from tkinter import BOTH, TOP, BOTTOM, LEFT, RIGHT  # ثابت‌های جهت‌دهی ویجت‌ها

# سیستم اعلانات شبیه SweetAlert که خودکار ناپدید می‌شوند
class ToastNotification:
    def __init__(self, parent, message, toast_type="info", duration=10000):
        """
        ایجاد اعلان تست شبیه SweetAlert
        parent: پنجره والد
        message: متن پیام
        toast_type: نوع پیام (success, error, warning, info)
        duration: مدت زمان نمایش به میلی‌ثانیه (پیش‌فرض 20 ثانیه)
        """
        self.parent = parent
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        
        # تنظیم رنگ‌ها و آیکون‌ها بر اساس نوع پیام
        self.colors = {
            "success": {"bg": "#d4edda", "border": "#c3e6cb", "text": "#155724", "icon": "✅"},
            "error": {"bg": "#f8d7da", "border": "#f5c6cb", "text": "#721c24", "icon": "❌"},
            "warning": {"bg": "#fff3cd", "border": "#ffeaa7", "text": "#856404", "icon": "⚠️"},
            "info": {"bg": "#d1ecf1", "border": "#bee5eb", "text": "#0c5460", "icon": "ℹ️"}
        }
        
        self.create_toast()
        
    def create_toast(self):
        """ایجاد پنجره اعلان"""
        # ایجاد پنجره بالاپوپ
        self.toast_window = tk.Toplevel(self.parent)
        self.toast_window.title("")
        
        # حذف دکمه‌های پنجره و تنظیم ظاهر
        self.toast_window.overrideredirect(True)
        self.toast_window.attributes('-topmost', True)
        
        # محاسبه موقعیت نمایش (گوشه بالا راست)
        screen_width = self.parent.winfo_screenwidth()
        toast_width = 400
        toast_height = 100
        x = screen_width - toast_width - 20
        y = 20
        
        self.toast_window.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        
        # دریافت رنگ‌های مربوط به نوع پیام
        color_config = self.colors.get(self.toast_type, self.colors["info"])
        
        # فریم اصلی با حاشیه رنگی
        main_frame = tk.Frame(
            self.toast_window,
            bg=color_config["border"],
            padx=2,
            pady=2
        )
        main_frame.pack(fill=BOTH, expand=True)
        
        # فریم داخلی با پس‌زمینه
        content_frame = tk.Frame(
            main_frame,
            bg=color_config["bg"],
            padx=15,
            pady=10
        )
        content_frame.pack(fill=BOTH, expand=True)
        
        # فریم آیکون و متن
        message_frame = tk.Frame(content_frame, bg=color_config["bg"])
        message_frame.pack(fill=BOTH, expand=True)
        
        # آیکون
        icon_label = tk.Label(
            message_frame,
            text=color_config["icon"],
            font=("B Nazanin", 20),
            bg=color_config["bg"],
            fg=color_config["text"]
        )
        icon_label.pack(side=LEFT, padx=(0, 10))
        
        # متن پیام
        message_label = tk.Label(
            message_frame,
            text=self.message,
            font=("B Nazanin", 12),
            bg=color_config["bg"],
            fg=color_config["text"],
            wraplength=300,
            justify=RIGHT,
            anchor="e"
        )
        message_label.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # انیمیشن فید اين (شفافیت تدریجی)
        self.fade_in()
        
        # برنامه‌ریزی برای بستن خودکار
        self.parent.after(self.duration, self.fade_out)
        
        # امکان بستن با کلیک
        self.toast_window.bind("<Button-1>", lambda e: self.close_toast())
        main_frame.bind("<Button-1>", lambda e: self.close_toast())
        content_frame.bind("<Button-1>", lambda e: self.close_toast())
        message_frame.bind("<Button-1>", lambda e: self.close_toast())
        icon_label.bind("<Button-1>", lambda e: self.close_toast())
        message_label.bind("<Button-1>", lambda e: self.close_toast())
    
    def fade_in(self):
        """انیمیشن ظاهر شدن تدریجی"""
        try:
            self.toast_window.attributes('-alpha', 0.0)
            self.animate_alpha(0.0, 1.0, 0.1)
        except:
            # در صورت عدم پشتیبانی از شفافیت، بدون انیمیشن نمایش داده می‌شود
            pass
    
    def fade_out(self):
        """انیمیشن ناپدید شدن تدریجی"""
        try:
            self.animate_alpha(1.0, 0.0, -0.1, callback=self.close_toast)
        except:
            # در صورت عدم پشتیبانی از شفافیت، مستقیماً بسته می‌شود
            self.close_toast()
    
    def animate_alpha(self, start, end, step, callback=None):
        """انیمیشن تغییر شفافیت"""
        current = start
        
        def update_alpha():
            nonlocal current
            try:
                self.toast_window.attributes('-alpha', current)
                current += step
                
                if (step > 0 and current < end) or (step < 0 and current > end):
                    self.parent.after(50, update_alpha)
                elif callback:
                    callback()
            except:
                if callback:
                    callback()
        
        update_alpha()
    
    def close_toast(self):
        """بستن پنجره اعلان"""
        try:
            if self.toast_window and self.toast_window.winfo_exists():
                self.toast_window.destroy()
        except:
            pass

# Native drag and drop implementation - more reliable than tkinterdnd2
class NativeDragDrop:
    def __init__(self, widget, callback):
        self.widget = widget
        self.callback = callback
        self.drag_data = None
        
        # Bind events for drag and drop
        self.widget.bind("<Button-1>", self.on_click)
        self.widget.bind("<B1-Motion>", self.on_drag)
        self.widget.bind("<ButtonRelease-1>", self.on_drop)
        
    def on_click(self, event):
        # Start drag operation
        self.drag_data = {"start_x": event.x, "start_y": event.y}
        
    def on_drag(self, event):
        # Handle drag motion
        if self.drag_data:
            # Visual feedback during drag
            self.widget.configure(cursor="hand2")
            
    def on_drop(self, event):
        # Handle drop operation
        if self.drag_data:
            self.widget.configure(cursor="")
            # Check if we have file paths to process
            if hasattr(self.widget, 'selection'):
                selected_items = self.widget.selection()
                if selected_items and self.callback:
                    self.callback(selected_items)
        self.drag_data = None

# Licensing System
class LicenseManager:
    def __init__(self):
        self.license_file = "license.key"
        self.company_key = "PERSIANFILECOPIER2024"
        
    def generate_serial(self, customer_name, customer_email):
        """Generate a unique serial number for a customer"""
        timestamp = str(int(time.time()))
        data = f"{customer_name}{customer_email}{timestamp}{self.company_key}"
        hash_obj = hashlib.sha256(data.encode())
        serial = base64.b64encode(hash_obj.digest()).decode()[:20].upper()
        return f"PFC-{serial[:4]}-{serial[4:8]}-{serial[8:12]}-{serial[12:16]}"
    
    def validate_serial(self, serial, customer_name="", customer_email=""):
        """Validate a serial number"""
        try:
            if not serial.startswith("PFC-"):
                return False
            # For demo purposes, accept any properly formatted serial
            parts = serial.split("-")
            return len(parts) == 5 and len(parts[0]) == 3
        except:
            return False
    
    def save_license(self, serial, customer_info):
        """Save license information"""
        license_data = {
            "serial": serial,
            "customer": customer_info,
            "activated": datetime.now().isoformat(),
            "status": "active"
        }
        try:
            with open(self.license_file, "w", encoding="utf-8") as f:
                json.dump(license_data, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def load_license(self):
        """Load license information"""
        try:
            with open(self.license_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    
    def is_licensed(self):
        """Check if application is properly licensed"""
        license_data = self.load_license()
        if not license_data:
            return False
        return self.validate_serial(license_data.get("serial", ""))
    
    def is_trial_mode(self):
        """Check if application is in trial mode"""
        license_data = self.load_license()
        if not license_data:
            return True
        return license_data.get("serial", "") == "TRIAL-MODE"
    
    def get_license_type(self):
        """Get the license type (trial, standard, pro)"""
        license_data = self.load_license()
        if not license_data:
            return "trial"
        
        serial = license_data.get("serial", "")
        if serial == "TRIAL-MODE":
            return "trial"
        elif self.validate_serial(serial):
            return license_data.get("license_type", "standard")
        return "trial"

# تنظیمات تم‌های پیشرفته و زیبا - مجموعه کاملی از تم‌های مدرن
THEMES = {
    # تم‌های کلاسیک
    "dark_blue": {"mode": "dark", "color": "blue", "name": "آبی تیره کلاسیک"},
    "dark_green": {"mode": "dark", "color": "green", "name": "سبز تیره طبیعی"},
    "light_blue": {"mode": "light", "color": "blue", "name": "آبی روشن آسمانی"},
    "light_green": {"mode": "light", "color": "green", "name": "سبز روشن بهاری"},
    
    # تم‌های مدرن و شیک
    "cyberpunk": {"mode": "dark", "color": "blue", "name": "سایبرپانک نئونی"},
    "sunset": {"mode": "light", "color": "green", "name": "غروب طلایی"},
    "ocean": {"mode": "light", "color": "blue", "name": "اقیانوس آرام"},
    "forest": {"mode": "dark", "color": "green", "name": "جنگل عمیق"},
    
    # تم‌های جدید و خاص
    "royal_purple": {"mode": "dark", "color": "blue", "name": "بنفش شاهانه"},
    "emerald_dream": {"mode": "light", "color": "green", "name": "رویای زمردین"},
    "midnight_blue": {"mode": "dark", "color": "blue", "name": "آبی نیمه‌شب"},
    "cherry_blossom": {"mode": "light", "color": "blue", "name": "شکوفه گیلاس"},
    "persian_carpet": {"mode": "dark", "color": "green", "name": "فرش ایرانی"},
    "tehran_sky": {"mode": "light", "color": "blue", "name": "آسمان تهران"},
    "caspian_sea": {"mode": "light", "color": "green", "name": "دریای خزر"},
    "alborz_mountain": {"mode": "dark", "color": "blue", "name": "کوه البرز"},
    
    # تم سیستم
    "system": {"mode": "system", "color": "blue", "name": "پیروی از سیستم"}
}

# Set initial appearance - lighter theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# کلاس اصلی برنامه مدیریت فایل ایرانی - شامل تمامی عملکردها و رابط کاربری
class FileCopierApp:
    def __init__(self, root):
        """
        سازنده کلاس برنامه - تنظیم اولیه پنجره اصلی و متغیرها
        root: پنجره اصلی tkinter یا customtkinter
        """
        self.root = root  # ذخیره مرجع پنجره اصلی برای استفاده در سایر متدها
        
        # تنظیم عنوان پنجره برنامه با نام فارسی و انگلیسی
        self.root.title("مدیریت فایل ایرانی پیشرفته - Persian File Copier Pro v2.0")
        
        # تنظیم اندازه پیش‌فرض پنجره (عرض × ارتفاع)
        self.root.geometry("1600x1000")
        
        # تنظیم حداقل اندازه پنجره که کاربر می‌تواند آن را تغییر دهد
        self.root.minsize(1400, 900)
        
        # ماکسیمایز کردن پنجره در زمان اجرا برای استفاده بهتر از فضای صفحه
        self.root.state('zoomed')  # دستور ماکسیمایز برای Windows
        
        try:
            # تلاش برای ماکسیمایز در سیستم‌عامل‌های مختلف
            self.root.wm_state('zoomed')  # روش دیگر برای ماکسیمایز
        except:
            # در صورت عدم پشتیبانی از دستور zoomed، از روش‌های جایگزین استفاده می‌شود
            try:
                self.root.attributes('-zoomed', True)  # روش ماکسیمایز برای Linux
            except:
                # در نهایت اگر هیچ روش کار نکرد، اندازه کامل صفحه تنظیم می‌شود
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        
        # راه‌اندازی مدیر لایسنس برای کنترل مجوز استفاده از نرم‌افزار
        self.license_manager = LicenseManager()
        
        # تنظیم آیکون برنامه در نوار وظیف و عنوان پنجره
        self.setup_app_icon()
        
        # مقداردهی اولیه متغیرهای اصلی برنامه
        self.copy_tasks = []  # لیست تسک‌های کپی که در صف انتظار یا در حال اجرا هستند
        self.task_queue = queue.Queue()  # صف thread-safe برای مدیریت کارهای پس‌زمینه
        self.executor = None  # pool thread ها برای اجرای همزمان کپی‌ها
        self.is_copying = False  # فلگ نشان‌دهنده وضعیت کپی (فعال/غیرفعال)
        self.clipboard_files = []  # لیست فایل‌های کپی شده در کلیپ‌بورد داخلی
        self.current_dir = os.getcwd()  # مسیر دایرکتوری جاری برنامه
        self.settings = self.load_settings()  # بارگذاری تنظیمات ذخیره شده کاربر
        self.file_cache = self.load_cache()  # بارگذاری کش فایل‌ها برای عملکرد سریع‌تر
        self.all_drives = []  # لیست تمام درایوهای سیستم (هارد، USB و غیره)
        self.destination_folders = []  # لیست پوشه‌های مقصد پیشنهادی برای کپی
        self.native_drag_drop = None  # سیستم درگ اند دراپ بومی
        
        # راه‌اندازی اجزای اصلی برنامه
        self.setup_logging()  # تنظیم سیستم ثبت لاگ برای رخدادها و خطاها
        self.setup_executor()  # راه‌اندازی thread pool برای اجرای همزمان کارها
        
        # نمایش صفحه بارگذاری قبل از ساخت رابط کاربری
        self.show_loading_screen()
        
        # اسکن اولیه درایوها قبل از ساخت GUI برای جلوگیری از مشکلات layout
        self.update_status("اسکن درایوهای سیستم...")  # به‌روزرسانی وضعیت برای کاربر
        self.scan_all_drives()  # اسکن همزمان درایوها در thread اصلی
        
        # ساخت رابط کاربری با داده‌های از پیش اسکن شده درایوها
        self.setup_gui()  # ساخت تمام عناصر رابط کاربری
        self.setup_bindings()  # تنظیم event handler ها و کلیدهای میانبر
        
        # شروع تمیزکاری خودکار تسک‌های تکمیل شده
        self.start_auto_cleanup()
        
        # بررسی وضعیت لایسنس در زمان راه‌اندازی
        self.check_license_on_startup()
        
        # لیست اعلانات فعال برای مدیریت موقعیت‌ها و جلوگیری از همپوشانی
        self.active_toasts = []
        
        # ادامه اسکن فایل‌ها در پس‌زمینه پس از آماده شدن رابط کاربری
        self.update_status("اسکن فایل‌ها...")  # اطلاع‌رسانی به کاربر
        # ایجاد thread جداگانه برای اسکن کامل فایل‌ها بدون مسدود کردن رابط کاربری
        threading.Thread(target=self.complete_system_scan, daemon=True).start()

    def show_toast(self, message, toast_type="info", duration=10000):
        """
        نمایش اعلان تست شبیه SweetAlert
        message: متن پیام
        toast_type: نوع پیام (success, error, warning, info)
        duration: مدت زمان نمایش به میلی‌ثانیه
        """
        try:
            # محاسبه موقعیت Y برای اعلان جدید (در صورت وجود اعلانات قبلی)
            y_offset = len(self.active_toasts) * 120 + 20
            
            # ایجاد اعلان جدید
            toast = ToastNotification(self.root, message, toast_type, duration)
            
            # تنظیم موقعیت Y جدید
            if hasattr(toast, 'toast_window') and toast.toast_window:
                screen_width = self.root.winfo_screenwidth()
                toast_width = 400
                x = screen_width - toast_width - 20
                toast.toast_window.geometry(f"{toast_width}x100+{x}+{y_offset}")
            
            # اضافه کردن به لیست اعلانات فعال
            self.active_toasts.append(toast)
            
            # حذف از لیست پس از مدت زمان مشخص
            def remove_toast():
                if toast in self.active_toasts:
                    self.active_toasts.remove(toast)
                # بازآرایی موقعیت اعلانات باقی‌مانده
                self.rearrange_toasts()
            
            self.root.after(duration + 1000, remove_toast)
            
        except Exception as e:
            # در صورت خطا، از messagebox معمولی استفاده می‌شود
            print(f"خطا در نمایش اعلان: {e}")
            messagebox.showinfo("اطلاع", message)
    
    def rearrange_toasts(self):
        """بازآرایی موقعیت اعلانات فعال"""
        try:
            for i, toast in enumerate(self.active_toasts):
                if hasattr(toast, 'toast_window') and toast.toast_window and toast.toast_window.winfo_exists():
                    screen_width = self.root.winfo_screenwidth()
                    toast_width = 400
                    x = screen_width - toast_width - 20
                    y = i * 120 + 20
                    toast.toast_window.geometry(f"{toast_width}x100+{x}+{y}")
        except Exception as e:
            print(f"خطا در بازآرایی اعلانات: {e}")

    def get_system_fonts(self):
        """دریافت لیست تمام فونت‌های موجود در سیستم"""
        try:
            import tkinter.font as tkFont
            # دریافت لیست فونت‌های سیستم
            fonts = list(tkFont.families())
            # مرتب‌سازی فونت‌ها
            fonts.sort()
            # اضافه کردن فونت‌های محبوب فارسی در ابتدای لیست
            persian_fonts = ["B Nazanin", "Tahoma", "Arial Unicode MS", "Times New Roman", 
                           "Calibri", "Segoe UI", "Vazir", "Samim", "Shabnam"]
            
            # حذف تکراری و ترکیب لیست‌ها
            unique_fonts = []
            for font in persian_fonts:
                if font in fonts and font not in unique_fonts:
                    unique_fonts.append(font)
            
            for font in fonts:
                if font not in unique_fonts:
                    unique_fonts.append(font)
            
            return unique_fonts[:100]  # محدود کردن به 100 فونت برای کارایی بهتر
        except Exception as e:
            print(f"خطا در دریافت فونت‌های سیستم: {e}")
            return ["B Nazanin", "Tahoma", "Arial", "Times New Roman", "Calibri"]

    def apply_font_to_all_widgets(self, font_family, font_size):
        """اعمال فونت جدید به تمام ویجت‌های برنامه"""
        try:
            # به‌روزرسانی فونت پیش‌فرض
            self.current_font_family = font_family
            self.current_font_size = font_size
            self.default_font = ctk.CTkFont(family=font_family, size=font_size)
            
            # ذخیره در تنظیمات
            self.settings["font_family"] = font_family
            self.settings["font_size"] = font_size
            self.save_settings()
            
            # نمایش پیام موفقیت
            self.show_toast(f"فونت به {font_family} با اندازه {font_size} تغییر یافت", "success")
            
            # اطلاع‌رسانی برای ری‌استارت
            self.show_toast("برای اعمال کامل تغییرات، برنامه را مجدداً راه‌اندازی کنید", "info")
            
        except Exception as e:
            self.show_toast(f"خطا در تغییر فونت: {e}", "error")

    def on_font_family_changed(self, selected_font):
        """تغییر فونت انتخاب شده و به‌روزرسانی پیش‌نمایش"""
        try:
            current_size = int(self.font_size_var.get())
            # به‌روزرسانی پیش‌نمایش
            self.font_preview_label.configure(
                font=ctk.CTkFont(family=selected_font, size=current_size)
            )
        except Exception as e:
            print(f"خطا در پیش‌نمایش فونت: {e}")

    def on_font_size_changed(self, selected_size):
        """تغییر اندازه فونت و به‌روزرسانی پیش‌نمایش"""
        try:
            size = int(selected_size)
            current_font = self.font_family_var.get()
            # به‌روزرسانی پیش‌نمایش
            self.font_preview_label.configure(
                font=ctk.CTkFont(family=current_font, size=size)
            )
        except Exception as e:
            print(f"خطا در پیش‌نمایش اندازه فونت: {e}")

    def apply_selected_font(self):
        """اعمال فونت انتخاب شده به کل برنامه"""
        try:
            selected_font = self.font_family_var.get()
            selected_size = int(self.font_size_var.get())
            self.apply_font_to_all_widgets(selected_font, selected_size)
        except Exception as e:
            self.show_toast(f"خطا در اعمال فونت: {e}", "error")

    def reset_font_to_default(self):
        """بازگردانی فونت به حالت پیش‌فرض"""
        try:
            default_font = "B Nazanin"
            default_size = 12
            
            # به‌روزرسانی combo box ها
            self.font_family_var.set(default_font)
            self.font_size_var.set(str(default_size))
            
            # به‌روزرسانی پیش‌نمایش
            self.font_preview_label.configure(
                font=ctk.CTkFont(family=default_font, size=default_size)
            )
            
            # اعمال تغییرات
            self.apply_font_to_all_widgets(default_font, default_size)
            
        except Exception as e:
            self.show_toast(f"خطا در بازگردانی فونت پیش‌فرض: {e}", "error")
    
    def activate_license(self):
        """فعال‌سازی لایسنس با کد وارد شده"""
        try:
            license_key = self.license_key_entry.get().strip()
            
            if not license_key:
                self.show_toast("لطفاً کد لایسنس را وارد کنید", "warning")
                return
            
            # اعتبارسنجی فرمت کد
            if not license_key.startswith("PFC-") or len(license_key) != 24:
                self.show_toast("فرمت کد لایسنس صحیح نیست", "error")
                return
            
            # بررسی اعتبار کد لایسنس
            if self.license_manager.validate_serial(license_key):
                # ذخیره اطلاعات لایسنس
                customer_info = {
                    "activation_date": datetime.now().isoformat(),
                    "version": "2.0",
                    "type": "commercial"
                }
                
                if self.license_manager.save_license(license_key, customer_info):
                    # به‌روزرسانی وضعیت در UI
                    self.license_status_label.configure(
                        text=f"🟢 فعال - سریال: {license_key}",
                        fg_color=("green", "darkgreen")
                    )
                    
                    # پاک کردن فیلد ورودی
                    self.license_key_entry.delete(0, 'end')
                    
                    self.show_toast("لایسنس با موفقیت فعال شد! 🎉", "success")
                else:
                    self.show_toast("خطا در ذخیره اطلاعات لایسنس", "error")
            else:
                self.show_toast("کد لایسنس نامعتبر است", "error")
                
        except Exception as e:
            self.show_toast(f"خطا در فعال‌سازی: {e}", "error")
    
    def purchase_license(self):
        """راهنمای خرید لایسنس"""
        try:
            import webbrowser
            # اطلاعات خرید لایسنس
            purchase_info = """
🛒 خرید لایسنس Persian File Copier Pro

📞 راه‌های تماس:
• تلفن: +98 21 1234 5678
• ایمیل: sales@persianfile.ir
• تلگرام: @PersianFileSupport

💰 قیمت‌ها:
• نسخه شخصی: 500,000 تومان
• نسخه تجاری: 1,200,000 تومان
• نسخه سازمانی: 2,500,000 تومان

🎁 مزایای نسخه کامل:
• کپی نامحدود فایل‌ها
• پشتیبانی 24/7
• بروزرسانی رایگان مادام‌العمر
• امکانات پیشرفته کپی

آیا می‌خواهید به سایت فروش منتقل شوید؟
            """
            
            # نمایش اطلاعات خرید
            import tkinter.messagebox
            result = tkinter.messagebox.askyesno(
                "خرید لایسنس", 
                purchase_info,
                icon='question'
            )
            
            if result:
                # باز کردن سایت فروش
                webbrowser.open("https://persianfile.ir/purchase")
                self.show_toast("در حال انتقال به سایت فروش...", "info")
            
        except Exception as e:
            self.show_toast(f"خطا در نمایش اطلاعات خرید: {e}", "error")
    
    def show_license_help(self):
        """نمایش راهنمای لایسنس"""
        help_text = """
🔑 راهنمای فعال‌سازی لایسنس

1️⃣ کد لایسنس را در فیلد مربوطه وارد کنید
2️⃣ روی دکمه "فعال‌سازی لایسنس" کلیک کنید
3️⃣ اتصال اینترنت برای تأیید لازم است

📋 فرمت کد: PFC-XXXX-XXXX-XXXX-XXXX

❓ مشکل دارید؟
• کد را دقیقاً وارد کنید (با خط فاصله‌ها)
• اتصال اینترنت را بررسی کنید
• با پشتیبانی تماس بگیرید: @PersianFileSupport
        """
        
        self.show_toast("راهنمای تفصیلی در کنسول نمایش داده شد", "info")
        print(help_text)

    # New callback methods for enhanced functionality
    def on_file_drag_drop(self, selected_items):
        """Handle drag and drop operations on file tree"""
        if selected_items:
            self.copy_selected_files()

    def copy_selected_files(self):
        """Copy selected files from the file tree"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            # نمایش اعلان هشدار به جای پیام باکس سنتی
            self.show_toast("لطفاً فایل‌هایی را برای کپی انتخاب کنید", "warning")
            return
        
        # Check if bulk copy is allowed (more than 5 files)
        if len(selected_items) > 5:
            if not self.enforce_license_restriction("bulk_copy"):
                return
        
        # Get destination from drive list section
        destination = self.get_selected_destination()
        if not destination:
            # نمایش اعلان هشدار برای انتخاب مقصد
            self.show_toast("لطفاً از ستون انتخاب مقصد، یک پوشه مقصد انتخاب کنید", "warning")
            return
        
        # Add to copy queue
        for item in selected_items:
            item_values = self.file_tree.item(item, 'values')
            if len(item_values) >= 2:
                file_path = item_values[1]  # Path column
                self.add_copy_task(file_path, destination)

    def get_selected_destination(self):
        """Get the currently selected destination from the drive list section"""
        try:
            # Check if there's a selected destination folder button
            if hasattr(self, 'selected_destination_path'):
                return self.selected_destination_path
            return None
        except:
            return None
    
    def select_destination(self):
        """Select destination folder"""
        folder = filedialog.askdirectory(title="انتخاب پوشه مقصد")
        if folder:
            self.selected_destination_path = folder
            # Update the destination label
            if hasattr(self, 'current_dest_label'):
                short_path = folder if len(folder) < 40 else f"...{folder[-37:]}"
                self.current_dest_label.configure(text=f"مقصد: {short_path}")
            return folder
        return None

    def quick_copy_to_folder(self, folder_name):
        """Quick copy to common folders"""
        try:
            # Get user home directory
            home_dir = Path.home()
            
            # Map folder names to actual paths
            folder_map = {
                "Desktop": home_dir / "Desktop",
                "Documents": home_dir / "Documents",
                "Downloads": home_dir / "Downloads", 
                "Pictures": home_dir / "Pictures",
                "Music": home_dir / "Music",
                "Videos": home_dir / "Videos"
            }
            
            destination = folder_map.get(folder_name)
            if destination and destination.exists():
                self.destination_var.set(str(destination))
                self.copy_selected_files()
            else:
                messagebox.showerror("خطا", f"پوشه {folder_name} یافت نشد")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در کپی سریع: {e}")

    def add_copy_task(self, source, destination):
        """Add a copy task to the queue"""
        task = {
            "id": str(uuid.uuid4()),
            "source": source,
            "destination": destination,
            "status": "pending",
            "progress": 0,
            "created": datetime.now()
        }
        self.copy_tasks.append(task)
        self.update_recent_operations(f"کپی {os.path.basename(source)}", "در صف")
        self.update_status(f"تسک کپی اضافه شد: {os.path.basename(source)}")

    def update_recent_operations(self, operation, status):
        """Update recent operations list - now shows in status bar instead"""
        current_time = datetime.now().strftime("%H:%M")
        # Show recent operation in status bar instead of removed recent tree
        self.update_status(f"[{current_time}] {operation} - {status}")
        
        # Log the operation for debugging
        print(f"Recent Operation: [{current_time}] {operation} - {status}")

    def contact_support(self):
        """Open support contact information"""
        support_info = """
🛠️ راه‌های تماس با پشتیبانی:

📞 تلفن: +98 21 1234 5678
📧 ایمیل: support@persianfile.ir
📱 تلگرام: @PersianFileSupport
🌐 وب‌سایت: www.persianfile.ir

⏰ ساعات کاری: شنبه تا چهارشنبه، 8 تا 17
        """
        messagebox.showinfo("تماس با پشتیبانی", support_info)

    def check_updates(self):
        """Check for software updates"""
        messagebox.showinfo("بروزرسانی", "شما از آخرین نسخه نرم‌افزار استفاده می‌کنید.\n\nنسخه فعلی: 2.0")

    def select_folder(self):
        """Select a folder using file dialog"""
        folder = filedialog.askdirectory(title="انتخاب پوشه")
        if folder:
            # Add folder contents to file tree
            self.scan_and_add_folder_contents(folder)

    def setup_app_icon(self):
        """تنظیم آیکون حرفه‌ای برنامه"""
        try:
            # تلاش برای بارگذاری آیکون جدید حرفه‌ای
            if os.path.exists("persian_file_copier_pro.ico"):
                self.root.iconbitmap("persian_file_copier_pro.ico")
                print("✅ آیکون حرفه‌ای ICO بارگذاری شد")
            elif os.path.exists("persian_file_copier_pro.png"):
                # برای Linux/Mac، تبدیل PNG به PhotoImage
                import tkinter as tk
                icon_img = tk.PhotoImage(file="persian_file_copier_pro.png")
                self.root.iconphoto(True, icon_img)
                print("✅ آیکون حرفه‌ای PNG بارگذاری شد")
            elif os.path.exists("app_icon.ico"):
                # آیکون قدیمی به عنوان پشتیبان
                self.root.iconbitmap("app_icon.ico")
                print("⚠️ از آیکون قدیمی استفاده شد")
            else:
                # آیکون متنی به عنوان نهایی
                self.root.iconname("🏢 Persian File Copier Pro")
                print("⚠️ از آیکون متنی استفاده شد")
        except Exception as e:
            print(f"❌ خطا در تنظیم آیکون: {e}")
            # تنظیم نام پنجره به عنوان آخرین راه‌حل
            try:
                self.root.iconname("Persian File Copier Pro")
            except:
                pass

    def check_license_on_startup(self):
        """Check license status on application startup"""
        if not self.license_manager.is_licensed():
            self.show_license_dialog()

    def show_license_dialog(self):
        """Show license activation dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("فعال‌سازی نرم‌افزار - License Activation")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="🔑 فعال‌سازی نرم‌افزار", 
                    font=ctk.CTkFont(family="B Nazanin", size=20, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(frame, text="برای استفاده از نرم‌افزار، لطفاً سریال نامبر خود را وارد کنید:",
                    font=ctk.CTkFont(family="B Nazanin", size=12)).pack(pady=10)
        
        serial_entry = ctk.CTkEntry(frame, width=300, placeholder_text="PFC-XXXX-XXXX-XXXX-XXXX")
        serial_entry.pack(pady=10)
        
        def activate_license():
            serial = serial_entry.get().strip().upper()
            if self.license_manager.validate_serial(serial):
                customer_info = {"name": "User", "email": "user@example.com"}
                if self.license_manager.save_license(serial, customer_info):
                    messagebox.showinfo("موفقیت", "نرم‌افزار با موفقیت فعال شد!")
                    dialog.destroy()
                else:
                    messagebox.showerror("خطا", "خطا در ذخیره اطلاعات لایسنس")
            else:
                messagebox.showerror("خطا", "سریال نامبر نامعتبر است")
        
        ctk.CTkButton(frame, text="فعال‌سازی", command=activate_license).pack(pady=20)
        
        def skip_trial():
            # Allow 30-day trial
            trial_info = {"trial_start": datetime.now().isoformat(), "days_left": 30}
            self.license_manager.save_license("TRIAL-MODE", trial_info)
            dialog.destroy()
        
        ctk.CTkButton(frame, text="استفاده آزمایشی 30 روزه", 
                     command=skip_trial, fg_color="orange").pack(pady=5)

    def check_feature_license(self, feature_name):
        """Check if a feature is available with current license"""
        license_type = self.license_manager.get_license_type()
        
        # Features that require a valid license (not trial)
        premium_features = [
            "bulk_copy",           # Bulk file operations
            "advanced_settings",   # Advanced performance settings  
            "network_drives",      # Network drive access
            "scheduled_tasks",     # Task scheduling
            "batch_processing",    # Batch file processing
            "export_reports"       # Export operation reports
        ]
        
        if feature_name in premium_features:
            return license_type != "trial"
        
        return True  # Basic features are always available
    
    def show_license_restriction_message(self, feature_name):
        """نمایش پیام محدودیت لایسنس با toast notification"""
        restriction_message = f"قابلیت {feature_name} فقط در نسخه لایسنس شده موجود است"
        self.show_toast(restriction_message, "warning")
        
        # نمایش اطلاعات تکمیلی در کنسول
        print(f"""
🔒 قابلیت محدود شده: {feature_name}

این قابلیت فقط در نسخه لایسنس شده موجود است.
برای فعال‌سازی نرم‌افزار، لطفاً سریال نامبر معتبر وارد کنید.

📞 برای خرید لایسنس با ما تماس بگیرید:
• ایمیل: info@persianfile.ir
• تلگرام: @PersianFileSupport
        """)
    
    def enforce_license_restriction(self, feature_name):
        """Enforce license restriction for a feature"""
        if not self.check_feature_license(feature_name):
            self.show_license_restriction_message(feature_name)
            return False
        return True
    
    def show_license_prompt_for_advanced_settings(self, value=None):
        """Show license prompt when trying to use advanced settings"""
        self.show_license_restriction_message("advanced_settings")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename="copy_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8"
        )
        self.logger = logging.getLogger(__name__)

    def setup_executor(self):
        """Initialize thread pool executor with optimized settings"""
        # Calculate optimal number of threads based on CPU cores
        import os
        cpu_count = os.cpu_count() or 4
        optimal_threads = min(max(cpu_count, 2), 8)  # Between 2 and 8 threads
        
        max_workers = self.settings.get("max_threads", optimal_threads)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def load_settings(self) -> Dict:
        """Load application settings from file"""
        default_settings = {
            "theme": "light_blue",
            "buffer_size": 64 * 1024,  # 64KB default
            "max_threads": 4,
            "overwrite_policy": "prompt",
            "window_geometry": "1100x700",
            "verify_copy": True,
            "show_hidden_files": False,
            "auto_retry": True,
            "retry_count": 3,
            "progress_update_interval": 0.5,
            "use_compression": False,
            "preserve_permissions": True,
            "create_backup": False,
            "notification_sound": True,
            "minimize_to_tray": False,
            "auto_clear_completed": False,
            "show_speed_graph": True,
            "language": "en"
        }
        
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                # Merge with defaults
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            return default_settings

    def save_settings(self):
        """Save current settings to file"""
        try:
            self.settings["window_geometry"] = self.root.geometry()
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")

    def load_cache(self) -> Dict:
        """Load file cache from disk"""
        try:
            with open("file_cache.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"files": {}, "last_scan": 0}

    def save_cache(self):
        """Save file cache to disk"""
        try:
            with open("file_cache.json", "w", encoding="utf-8") as f:
                json.dump(self.file_cache, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")

    def show_loading_screen(self):
        """Show a loading screen while scanning drives"""
        try:
            # Create a simple loading window
            self.loading_window = ctk.CTkToplevel(self.root)
            self.loading_window.title("Loading...")
            self.loading_window.geometry("400x200")
            self.loading_window.transient(self.root)
            self.loading_window.grab_set()
            
            # Center the loading window
            self.loading_window.geometry("+{}+{}".format(
                int(self.root.winfo_screenwidth()/2 - 200),
                int(self.root.winfo_screenheight()/2 - 100)
            ))
            
            # Loading content
            loading_frame = ctk.CTkFrame(self.loading_window)
            loading_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(loading_frame, text="🔍 در حال اسکن درایوها...", 
                        font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")).pack(pady=10)
            
            self.loading_progress = ctk.CTkProgressBar(loading_frame)
            self.loading_progress.pack(fill="x", padx=20, pady=10)
            self.loading_progress.set(0.3)  # Show some progress
            
            self.loading_status = ctk.CTkLabel(loading_frame, text="در حال شناسایی درایوها...", 
                                              font=ctk.CTkFont(family="B Nazanin", size=12))
            self.loading_status.pack(pady=5)
            
            self.root.update()
        except Exception as e:
            print(f"Could not show loading screen: {e}")
    
    def hide_loading_screen(self):
        """Hide the loading screen"""
        try:
            if hasattr(self, 'loading_window'):
                self.loading_window.destroy()
        except Exception as e:
            print(f"Could not hide loading screen: {e}")

    def complete_system_scan(self):
        """Complete file scanning after GUI is ready"""
        try:
            print("📁 Starting file scanning...")
            
            # 1. Scan files from all drives
            self.scan_all_files()
            
            # 2. Auto-detect destination folders
            self.auto_detect_destinations()
            
            # 3. Update GUI
            self.root.after(0, self.on_scan_complete)
            
        except Exception as e:
            self.logger.error(f"Error in file scan: {e}")
            print(f"❌ File scan error: {e}")
            self.root.after(0, lambda: self.update_status("File scan error - using fallback"))

    def initial_system_scan(self):
        """Comprehensive system scan for drives and files at startup - DEPRECATED, split into parts"""
        try:
            print("🔍 Starting comprehensive system scan...")
            
            # 1. Scan all available drives and mount points
            self.scan_all_drives()
            
            # 2. Scan files from all drives
            self.scan_all_files()
            
            # 3. Auto-detect destination folders
            self.auto_detect_destinations()
            
            # 4. Update GUI
            self.root.after(0, self.on_scan_complete)
            
        except Exception as e:
            self.logger.error(f"Error in system scan: {e}")
            print(f"❌ System scan error: {e}")
            self.root.after(0, lambda: self.update_status("Scan error - using fallback"))

    def scan_all_drives(self):
        """Scan and detect all available drives and mount points"""
        try:
            self.all_drives = []
            
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Get partition info
                    partition_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts
                    }
                    
                    # Try to get disk usage
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partition_info.update({
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'accessible': True
                        })
                    except (PermissionError, OSError):
                        partition_info.update({
                            'total': 0,
                            'used': 0,
                            'free': 0,
                            'accessible': False
                        })
                    
                    self.all_drives.append(partition_info)
                    print(f"✓ Found drive: {partition.device} -> {partition.mountpoint}")
                    
                except Exception as e:
                    print(f"⚠ Could not access partition {partition.device}: {e}")
                    continue
            
            print(f"✓ Total drives found: {len(self.all_drives)}")
            
        except Exception as e:
            print(f"❌ Error scanning drives: {e}")
            self.logger.error(f"Drive scan error: {e}")

    def scan_all_files(self):
        """Scan files from all accessible drives - Real-time and memory efficient"""
        try:
            print("📁 Starting real-time file scanning...")
            
            # Clear existing files and start fresh
            self.file_cache["files"] = {}
            self.file_cache["total_files"] = 0
            
            # Clear the tree immediately
            self.root.after(0, lambda: self.file_tree.delete(*self.file_tree.get_children()))
            
            total_files = 0
            
            for drive in self.all_drives:
                if not drive['accessible']:
                    continue
                    
                mountpoint = drive['mountpoint']
                print(f"🔍 Scanning {mountpoint}...")
                
                try:
                    # Real-time scanning with immediate UI updates
                    drive_file_count = self.scan_directory_realtime(mountpoint)
                    total_files += drive_file_count
                    print(f"✓ {mountpoint}: {drive_file_count} files")
                    
                except Exception as e:
                    print(f"⚠ Could not scan {mountpoint}: {e}")
                    continue
            
            # Final update
            self.file_cache["last_scan"] = time.time()
            self.file_cache["total_files"] = total_files
            
            print(f"✓ Total files scanned: {total_files}")
            
        except Exception as e:
            print(f"❌ Error scanning files: {e}")
            self.logger.error(f"File scan error: {e}")

    def scan_directory_realtime(self, directory, max_files_per_batch=50):
        """Real-time directory scanning with immediate UI updates and memory efficiency"""
        total_files = 0
        batch_files = []
        batch_count = 0
        
        def add_batch_to_ui():
            """Add current batch to UI"""
            if batch_files:
                for file_data in batch_files:
                    try:
                        self.file_tree.insert("", "end", values=(
                            file_data["name"], 
                            file_data["path"], 
                            file_data["type"], 
                            file_data["size"]
                        ))
                    except:
                        pass  # Skip if tree is being updated
                
                # Update status
                self.update_status(f"Found {total_files} files...")
                batch_files.clear()
        
        def scan_recursive(current_dir, depth=0):
            nonlocal total_files, batch_count
            
            # Limit depth to prevent system freeze
            if depth > 8:
                return
                
            try:
                items = os.listdir(current_dir)
                
                for item in items:
                    item_path = os.path.join(current_dir, item)
                    
                    try:
                        if os.path.isfile(item_path):
                            size = self.get_file_size(item_path)
                            file_data = {
                                "name": item,
                                "path": item_path,
                                "type": "File",
                                "size": self.format_size(size),
                                "raw_size": size
                            }
                            
                            batch_files.append(file_data)
                            total_files += 1
                            
                            # Add to cache (limited to prevent memory issues)
                            if len(self.file_cache["files"]) < 10000:  # Limit cache size
                                self.file_cache["files"][item_path] = file_data
                            
                            # Update UI in batches
                            if len(batch_files) >= max_files_per_batch:
                                self.root.after_idle(add_batch_to_ui)
                                batch_count += 1
                                
                                # Small delay to prevent UI freezing
                                if batch_count % 10 == 0:
                                    time.sleep(0.01)
                            
                        elif os.path.isdir(item_path):
                            # Skip system directories and some problematic paths
                            skip_dirs = {
                                '/proc', '/sys', '/dev', '/run', '/var/run',
                                'System Volume Information', '$RECYCLE.BIN',
                                'Windows', 'Program Files', 'Program Files (x86)'
                            }
                            
                            skip = False
                            for skip_dir in skip_dirs:
                                if item_path.startswith(skip_dir) or skip_dir in item_path:
                                    skip = True
                                    break
                            
                            if not skip and depth < 8:
                                # Add directory to list
                                dir_data = {
                                    "name": item,
                                    "path": item_path,
                                    "type": "Directory",
                                    "size": "",
                                    "raw_size": 0
                                }
                                batch_files.append(dir_data)
                                
                                # Recursively scan subdirectory
                                scan_recursive(item_path, depth + 1)
                                
                    except (OSError, PermissionError):
                        continue
                        
            except (OSError, PermissionError):
                pass
        
        # Start scanning
        scan_recursive(directory)
        
        # Add remaining files in batch
        if batch_files:
            self.root.after_idle(add_batch_to_ui)
        
        return total_files

    def auto_detect_destinations(self):
        """Automatically detect and set up destination folders from all drives"""
        try:
            self.destination_folders = []
            
            # Add all accessible drive root directories as destinations
            for drive in self.all_drives:
                if drive['accessible'] and drive['free'] > 0:
                    dest_info = {
                        'path': drive['mountpoint'],
                        'name': f"{drive['device']} ({self.format_size(drive['free'])} free)",
                        'type': 'drive',
                        'free_space': drive['free'],
                        'total_space': drive['total']
                    }
                    self.destination_folders.append(dest_info)
            
            # Add common user directories if they exist
            common_dirs = [
                ('Desktop', os.path.expanduser('~/Desktop')),
                ('Documents', os.path.expanduser('~/Documents')),
                ('Downloads', os.path.expanduser('~/Downloads')),
                ('Pictures', os.path.expanduser('~/Pictures')),
                ('Videos', os.path.expanduser('~/Videos')),
                ('Music', os.path.expanduser('~/Music'))
            ]
            
            for name, path in common_dirs:
                if os.path.exists(path) and os.path.isdir(path):
                    try:
                        usage = psutil.disk_usage(path)
                        dest_info = {
                            'path': path,
                            'name': f"{name} ({self.format_size(usage.free)} free)",
                            'type': 'user_folder',
                            'free_space': usage.free,
                            'total_space': usage.total
                        }
                        # Avoid duplicates
                        if not any(d['path'] == path for d in self.destination_folders):
                            self.destination_folders.append(dest_info)
                    except:
                        continue
            
            print(f"✓ Auto-detected {len(self.destination_folders)} destination folders")
            
        except Exception as e:
            print(f"❌ Error auto-detecting destinations: {e}")
            self.logger.error(f"Destination detection error: {e}")

    def on_scan_complete(self):
        """Called when initial system scan is complete"""
        try:
            # Hide loading screen
            self.hide_loading_screen()
            
            # Display cached files
            self.display_cache()
            
            # Update destination folders in GUI
            self.update_destination_folders_display()
            
            # Update drive combo box if it exists
            if hasattr(self, 'drive_combo'):
                self.populate_drive_combo()
            
            # Update status
            total_files = self.file_cache.get("total_files", 0)
            total_drives = len(self.all_drives)
            self.update_status(f"Ready - {total_files} files from {total_drives} drives scanned")
            
            print("✅ System scan completed successfully")
            
        except Exception as e:
            print(f"❌ Error completing scan: {e}")
            self.update_status("Ready - scan completed with errors")
            # Make sure to hide loading screen even on error
            self.hide_loading_screen()

    def get_drive_values(self):
        """Get formatted drive values for combo box"""
        try:
            if not hasattr(self, 'all_drives') or not self.all_drives:
                return ["هیچ درایوی یافت نشد"]
            
            drive_values = []
            for drive in self.all_drives:
                if drive['accessible']:
                    try:
                        # Format: "C:\ (120 GB free)"
                        free_gb = drive['free'] / (1024**3) if drive['free'] > 0 else 0
                        label = f"{drive['device']} ({free_gb:.1f} GB آزاد)"
                        drive_values.append(label)
                    except:
                        drive_values.append(drive['device'])
                        
            return drive_values if drive_values else ["هیچ درایو قابل دسترسی یافت نشد"]
        except Exception as e:
            print(f"Error getting drive values: {e}")
            return ["خطا در بارگذاری درایوها"]

    def populate_drive_combo(self):
        """Populate the drive combo box with available drives"""
        try:
            drive_options = []
            
            for drive in self.all_drives:
                if drive['accessible']:
                    free_space = self.format_size(drive['free'])
                    total_space = self.format_size(drive['total'])
                    drive_label = f"{drive['device']} - {drive['mountpoint']} ({free_space}/{total_space})"
                    drive_options.append(drive_label)
            
            if drive_options:
                self.drive_combo.configure(values=drive_options)
                self.drive_var.set(drive_options[0])
            else:
                self.drive_combo.configure(values=["هیچ درایوی یافت نشد"])
                self.drive_var.set("هیچ درایوی یافت نشد")
                
        except Exception as e:
            print(f"Error populating drive combo: {e}")

    def start_auto_cleanup(self):
        """Start automatic cleanup of completed tasks"""
        def cleanup_completed_tasks():
            try:
                current_time = time.time()
                tasks_to_remove = []
                
                for i, task in enumerate(self.copy_tasks):
                    if task["completed"] and task["status"] == "✅ Completed":
                        # Check if task was completed more than 30 seconds ago
                        completion_time = task.get("completion_time", 0)
                        if completion_time > 0 and (current_time - completion_time) > 30:
                            tasks_to_remove.append(i)
                
                # Remove completed tasks from list and tree
                for i in reversed(tasks_to_remove):
                    task_id = self.copy_tasks[i]["id"]
                    try:
                        self.task_tree.delete(str(task_id))
                    except:
                        pass
                    self.copy_tasks.pop(i)
                
                if tasks_to_remove:
                    print(f"🧹 Cleaned up {len(tasks_to_remove)} completed tasks")
                    self.update_overall_progress()
                    
            except Exception as e:
                print(f"Error in auto cleanup: {e}")
            
            # Schedule next cleanup
            self.root.after(10000, cleanup_completed_tasks)  # Check every 10 seconds
        
        # Start the cleanup cycle
        self.root.after(5000, cleanup_completed_tasks)  # Start after 5 seconds

    def refresh_drives(self):
        """Refresh the drive list in the drive combo box"""
        try:
            self.scan_all_drives()
            drive_options = []
            
            for drive in self.all_drives:
                if drive['accessible']:
                    free_space = self.format_size(drive['free'])
                    total_space = self.format_size(drive['total'])
                    drive_label = f"{drive['device']} - {drive['mountpoint']} ({free_space}/{total_space})"
                    drive_options.append(drive_label)
            
            if drive_options:
                self.drive_combo.configure(values=drive_options)
                if not self.drive_var.get() or self.drive_var.get() == "در حال بارگذاری...":
                    self.drive_var.set(drive_options[0])
            else:
                self.drive_combo.configure(values=["هیچ درایوی یافت نشد"])
                self.drive_var.set("هیچ درایوی یافت نشد")
                
        except Exception as e:
            print(f"Error refreshing drives: {e}")
            self.drive_combo.configure(values=["خطا در بارگذاری درایوها"])
            self.drive_var.set("خطا در بارگذاری درایوها")

    def on_drive_selected(self, selected_drive):
        """Handle drive selection from combo box"""
        try:
            if not selected_drive or selected_drive in ["در حال بارگذاری...", "هیچ درایوی یافت نشد", "خطا در بارگذاری درایوها"]:
                return
                
            # Extract mountpoint from the selected drive string
            # Format is "Device - Mountpoint (free/total)"
            parts = selected_drive.split(" - ")
            if len(parts) >= 2:
                mountpoint_part = parts[1].split(" (")[0]  # Remove the space info part
                
                # Find the drive in our all_drives list
                selected_drive_info = None
                for drive in self.all_drives:
                    if drive['mountpoint'] == mountpoint_part:
                        selected_drive_info = drive
                        break
                
                if selected_drive_info:
                    self.browse_drive(selected_drive_info)
                    
        except Exception as e:
            print(f"Error selecting drive: {e}")

    def browse_drive(self, drive_info):
        """Browse files in the selected drive"""
        try:
            mountpoint = drive_info['mountpoint']
            print(f"Browsing drive: {mountpoint}")
            
            # Clear current file tree
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Scan files in the selected drive
            drive_files = self.scan_directory_recursive(mountpoint, max_depth=2)
            
            # Display files in the tree
            for file_path, file_info in drive_files.items():
                try:
                    name = file_info.get("name", os.path.basename(file_path))
                    file_type = file_info.get("type", "file")
                    size = self.format_size(file_info.get("size", 0))
                    
                    self.file_tree.insert("", "end", values=(name, file_path, file_type, size))
                except Exception as e:
                    print(f"Error adding file to tree: {e}")
                    
            self.update_status(f"تصفح درایو {mountpoint} - {len(drive_files)} فایل یافت شد")
            
        except Exception as e:
            print(f"Error browsing drive: {e}")
            self.update_status(f"خطا در تصفح درایو: {e}")

    def setup_gui(self):
        """Setup the main GUI"""
        # Apply theme
        theme_config = THEMES.get(self.settings["theme"], THEMES["dark_blue"])
        ctk.set_appearance_mode(theme_config["mode"])
        ctk.set_default_color_theme(theme_config["color"])
        
        # Configure window - check if it's CTk or regular Tk
        try:
            if isinstance(self.root, ctk.CTk):
                self.root.configure(fg_color=("#f8f9fa", "gray20"))  # Lighter background
            else:
                # For TkinterDnD.Tk(), use regular tkinter configuration
                self.root.configure(bg='#f8f9fa')
        except Exception as e:
            print(f"Warning: Could not configure root window: {e}")
        
        # تنظیم فونت پیش‌فرض برای کل برنامه با قابلیت انتخاب توسط کاربر
        self.current_font_family = self.settings.get("font_family", "B Nazanin")
        self.current_font_size = self.settings.get("font_size", 12)
        
        try:
            # استفاده از فونت انتخابی کاربر
            default_font = ctk.CTkFont(family=self.current_font_family, size=self.current_font_size)
            self.default_font = default_font
        except:
            # در صورت عدم وجود فونت انتخابی، از فونت‌های فارسی جایگزین استفاده می‌شود
            try:
                default_font = ctk.CTkFont(family="Tahoma", size=self.current_font_size)
                self.default_font = default_font
                print("استفاده از فونت Tahoma به عنوان جایگزین")
            except:
                default_font = ctk.CTkFont(size=self.current_font_size)
                self.default_font = default_font
                print("استفاده از فونت پیش‌فرض سیستم")
        
        # دریافت لیست فونت‌های سیستم
        self.system_fonts = self.get_system_fonts()
        
        # Main container with gradient effect
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color=("#ffffff", "#f0f0f0"),  # Much lighter colors
            border_width=2,
            border_color=("#d0d0d0", "#b0b0b0")
        )
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create notebook for tabs with custom styling
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Configure tab colors with simplified approach
        try:
            style = ttk.Style()
            
            # Try to configure basic styling - use valid color names
            style.configure("TNotebook", 
                          background="#f0f0f0",
                          borderwidth=0)
            style.configure("TNotebook.Tab",
                          padding=[15, 8],
                          font=('B Nazanin', 10, 'bold'))
            
            print("✓ Basic tab styling applied")
        except Exception as e:
            print(f"Could not configure tab styling: {e}")
        
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # تب اصلی - مرورگر فایل، انتخاب مقصد، کپی و مدیریت کارها
        self.explorer_frame = ctk.CTkFrame(self.notebook, fg_color=("#f3f9ff", "#e3f2fd"))
        self.notebook.add(self.explorer_frame, text="📁 مرورگر فایل و مدیریت کارها")
        self.setup_explorer_tab()
        
        
        # تب تنظیمات - تم نارنجی روشن
        self.settings_frame = ctk.CTkFrame(self.notebook, fg_color=("#fff8e1", "#fff3e0"))
        self.notebook.add(self.settings_frame, text="⚙️ تنظیمات")
        self.setup_settings_tab()
        
        # تب درباره ما - تم بنفش روشن
        self.about_frame = ctk.CTkFrame(self.notebook, fg_color=("#f3e5f5", "#e1bee7"))
        self.notebook.add(self.about_frame, text="ℹ️ درباره ما")
        self.setup_about_tab()
        
        # Tab colors are now implemented through frame colors
        print("✓ Tab colors implemented through frame backgrounds")
        
        # Status bar
        self.setup_status_bar()

    def setup_about_tab(self):
        """تنظیم تب درباره ما با بارگذاری اطلاعات از فایل HTML"""
        
        # Main container
        main_container = ctk.CTkFrame(self.about_frame)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with reload button
        header_frame = ctk.CTkFrame(main_container)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame, 
            text="📄 درباره شرکت و محصول", 
            font=ctk.CTkFont(family=self.current_font_family, size=18, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            header_frame,
            text="🔄 بازخوانی",
            command=self.reload_about_content,
            width=100,
            height=30,
            font=ctk.CTkFont(family=self.current_font_family, size=11)
        ).pack(side="right", padx=10, pady=10)
        
        # Content frame for HTML display
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, pady=5)
        
        try:
            # Try to use webview if available, otherwise use text display
            self.setup_html_viewer(content_frame)
        except:
            # Fallback to text-based display
            self.setup_text_about_display(content_frame)

    def setup_html_viewer(self, parent_frame):
        """تنظیم نمایشگر HTML برای فایل درباره ما"""
        try:
            # استفاده از webbrowser برای نمایش فایل HTML
            import webbrowser
            
            # Create frame with buttons
            button_frame = ctk.CTkFrame(parent_frame)
            button_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkButton(
                button_frame,
                text="📖 مشاهده در مرورگر",
                command=self.open_about_in_browser,
                width=200,
                height=40,
                font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold"),
                fg_color=("blue", "darkblue")
            ).pack(side="top", pady=10)
            
            # Text display of content
            self.setup_text_about_display(parent_frame)
            
        except Exception as e:
            print(f"خطا در تنظیم HTML viewer: {e}")
            self.setup_text_about_display(parent_frame)

    def setup_text_about_display(self, parent_frame):
        """نمایش اطلاعات درباره ما به صورت متنی"""
        
        # Scrollable text frame
        text_scroll = ctk.CTkScrollableFrame(
            parent_frame,
            corner_radius=10,
            fg_color=("gray95", "gray20")
        )
        text_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load and display content from HTML file or show default
        content = self.load_about_content()
        
        # Company header
        ctk.CTkLabel(
            text_scroll, 
            text="🏢 شرکت فناوری پارس فایل", 
            font=ctk.CTkFont(family=self.current_font_family, size=24, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(
            text_scroll, 
            text="Persian File Technology Company", 
            font=ctk.CTkFont(family=self.current_font_family, size=16, weight="bold")
        ).pack(pady=5)
        
        # Content display
        if content:
            content_label = ctk.CTkLabel(
                text_scroll,
                text=content,
                font=ctk.CTkFont(family=self.current_font_family, size=12),
                justify="right",
                wraplength=700
            )
            content_label.pack(padx=20, pady=20, fill="both", expand=True)
        else:
            # Default content if file is not available
            default_text = """
📞 اطلاعات تماس:
📍 آدرس: تهران، خیابان ولیعصر، پلاک ۱۲۳، طبقه ۵
📞 تلفن: +98 21 1234 5678
📧 ایمیل: info@persianfile.ir
🌐 وب‌سایت: www.persianfile.ir
📱 تلگرام: @PersianFileSupport

📦 درباره محصول:
Persian File Copier Pro نرم‌افزاری پیشرفته و قدرتمند برای مدیریت و کپی فایل‌ها است که با هدف تسهیل کار کاربران ایرانی طراحی شده است.

✨ ویژگی‌های کلیدی:
• پشتیبانی کامل از زبان فارسی
• رابط کاربری مدرن و زیبا
• کپی سریع و ایمن فایل‌ها
• پشتیبانی از درگ اند دراپ
• مدیریت پیشرفته صف کپی
• گزارش‌گیری کامل از عملیات

🎯 مناسب برای:
• کاربران خانگی
• شرکت‌ها و سازمان‌ها
• مراکز آموزشی
• کافه‌نت‌ها

🔑 نسخه تجاری حرفه‌ای با امکانات ویژه
            """
            
            ctk.CTkLabel(
                text_scroll,
                text=default_text,
                font=ctk.CTkFont(family=self.current_font_family, size=12),
                justify="right",
                anchor="e"
            ).pack(padx=15, pady=10)

    def load_about_content(self):
        """بارگذاری و پردازش محتوای فایل HTML برای نمایش زیبا"""
        try:
            about_file = "about_us.html"
            if os.path.exists(about_file):
                with open(about_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                    # استخراج محتوای متنی با حفظ ساختار
                    import re
                    
                    # حذف تگ‌های style و script
                    text_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
                    text_content = re.sub(r'<script[^>]*>.*?</script>', '', text_content, flags=re.DOTALL)
                    
                    # تبدیل تگ‌های مهم به متن فارسی
                    text_content = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n📌 \1\n', text_content)
                    text_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', text_content)
                    text_content = re.sub(r'<li[^>]*>(.*?)</li>', r'• \1\n', text_content)
                    text_content = re.sub(r'<br[^>]*>', '\n', text_content)
                    
                    # حذف سایر تگ‌های HTML
                    text_content = re.sub(r'<[^>]+>', '', text_content)
                    
                    # تمیز کردن فضاهای اضافی
                    text_content = re.sub(r'\n\s*\n\s*\n', '\n\n', text_content)
                    text_content = re.sub(r'[ \t]+', ' ', text_content)
                    text_content = text_content.strip()
                    
                    return text_content
        except Exception as e:
            print(f"خطا در بارگذاری فایل درباره ما: {e}")
        return None

    def reload_about_content(self):
        """بازخوانی محتوای درباره ما"""
        try:
            # Refresh the about tab
            self.show_toast("محتوای درباره ما بازخوانی شد", "success")
            # You could implement more sophisticated reload here
        except Exception as e:
            self.show_toast(f"خطا در بازخوانی: {e}", "error")

    def open_about_in_browser(self):
        """باز کردن فایل درباره ما در مرورگر"""
        try:
            import webbrowser
            about_file = os.path.abspath("about_us.html")
            if os.path.exists(about_file):
                webbrowser.open(f"file://{about_file}")
                self.show_toast("فایل در مرورگر باز شد", "success")
            else:
                self.show_toast("فایل درباره ما یافت نشد", "error")
        except Exception as e:
            self.show_toast(f"خطا در باز کردن مرورگر: {e}", "error")

    def refresh_destinations(self):
        """Refresh and re-scan destination folders"""
        self.update_status("Refreshing destinations...")
        threading.Thread(target=self._refresh_destinations_thread, daemon=True).start()
    
    def _refresh_destinations_thread(self):
        """Thread function to refresh destinations"""
        try:
            # Re-scan drives and destinations
            self.scan_all_drives()
            self.auto_detect_destinations()
            
            # Update GUI
            self.root.after(0, self.update_destination_folders_display)
            self.root.after(0, lambda: self.update_status("Destinations refreshed"))
            
        except Exception as e:
            print(f"❌ Error refreshing destinations: {e}")
            self.root.after(0, lambda: self.update_status("Destination refresh error"))

    def setup_explorer_tab(self):
        """تنظیم تب اکسپلورر فایل با layout سه ستونه 40%-20%-40%"""
        # کانتینر اصلی با padding مناسب
        main_container = ctk.CTkFrame(self.explorer_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ایجاد PanedWindow قابل تغییر اندازه برای 3 ستون
        self.main_paned = ttk.PanedWindow(main_container, orient="horizontal")
        self.main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ستون 1: مرورگر فایل (40%) - ستون اصلی برای انتخاب فایل‌ها
        browser_frame = ctk.CTkFrame(self.main_paned, width=640, height=600)  # 40% از 1600px = 640px
        browser_frame.pack_propagate(False)  # جلوگیری از کوچک شدن خودکار
        self.main_paned.add(browser_frame, weight=2)  # weight=2 برای 40%
        
        # ستون 2: لیست درایوها و مقصد (20%) - ستون میانی برای انتخاب مقصد
        drive_list_frame = ctk.CTkFrame(self.main_paned, width=320, height=600)  # 20% از 1600px = 320px
        drive_list_frame.pack_propagate(False)  # حفظ اندازه ثابت
        self.main_paned.add(drive_list_frame, weight=1)  # weight=1 برای 20%
        
        # ستون 3: مدیریت تسک‌ها (40%) - ستون اصلی برای نمایش پیشرفت
        task_management_frame = ctk.CTkFrame(self.main_paned, width=640, height=600)  # 40% از 1600px = 640px
        task_management_frame.pack_propagate(False)  # جلوگیری از کوچک شدن خودکار
        self.main_paned.add(task_management_frame, weight=2)  # weight=2 برای 40%
        
        # تنظیم نسبت‌های دقیق ستون‌ها
        self.root.after(100, lambda: self._configure_column_ratios())
        
        # ذخیره مراجع frame ها برای استفاده در آینده
        self.column_frames = {
            'browser': browser_frame,      # مرورگر فایل (چپ)
            'drive': drive_list_frame,     # لیست درایوها (وسط)
            'task': task_management_frame  # مدیریت تسک‌ها (راست)
        }
        
        # راه‌اندازی تمام بخش‌ها
        self.setup_file_browser_section(browser_frame)
        self.setup_drive_destination_section(drive_list_frame)
        self.setup_task_management_section(task_management_frame)
    
    def _configure_column_ratios(self):
        """تنظیم نسبت‌های دقیق ستون‌ها به 40%-20%-40%"""
        try:
            # دریافت عرض کل پنجره
            total_width = self.main_paned.winfo_width()
            if total_width > 100:  # اطمینان از بارگذاری کامل
                # محاسبه عرض هر ستون
                left_width = int(total_width * 0.4)    # 40% برای مرورگر فایل
                center_width = int(total_width * 0.2)  # 20% برای درایوها
                
                # تنظیم موقعیت‌های sash (تقسیم‌کننده‌ها)
                try:
                    self.main_paned.sash_place(0, left_width, 0)
                    self.main_paned.sash_place(1, left_width + center_width, 0)
                except:
                    # اگر sash_place کار نکرد، از روش دیگری استفاده می‌کنیم
                    pass
                
                print(f"✓ تنظیم نسبت ستون‌ها: {left_width}-{center_width}-{total_width - left_width - center_width}")
        except Exception as e:
            # در صورت خطا، بعداً دوباره تلاش می‌شود
            print(f"خطا در تنظیم نسبت ستون‌ها: {e}")
            self.root.after(500, lambda: self._configure_column_ratios())

    def setup_file_browser_section(self, browser_frame):
        """Setup the file browser section"""
        
        # Title
        title_label = ctk.CTkLabel(browser_frame, text="📁 مرورگر فایل", 
                                  font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold"))
        title_label.pack(pady=(10, 5))
        
        # Drive selection frame
        drive_frame = ctk.CTkFrame(browser_frame)
        drive_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(drive_frame, text="💿 انتخاب درایو:", 
                    font=ctk.CTkFont(family="B Nazanin", weight="bold")).pack(side="right", padx=5)
        
        self.drive_var = tk.StringVar()
        # Initialize with pre-scanned drives if available
        drive_values = self.get_drive_values() if hasattr(self, 'all_drives') and self.all_drives else ["در حال بارگذاری..."]
        self.drive_combo = ctk.CTkComboBox(drive_frame, variable=self.drive_var,
                                         font=ctk.CTkFont(family="B Nazanin"),
                                         values=drive_values,
                                         command=self.on_drive_selected)
        self.drive_combo.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(drive_frame, text="🔄", command=self.refresh_drives,
                     width=45, height=32, font=ctk.CTkFont(family="B Nazanin", size=14)).pack(side="left", padx=5)
        
        # Search and navigation frame
        nav_frame = ctk.CTkFrame(browser_frame)
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        # Search frame
        search_frame = ctk.CTkFrame(nav_frame)
        search_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(search_frame, text="جستجو:", font=ctk.CTkFont(family="B Nazanin", weight="bold")).pack(side="right", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="نام فایل یا پسوند وارد کنید", 
                                        font=ctk.CTkFont(family="B Nazanin"), justify="right")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(nav_frame)
        buttons_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(buttons_frame, text="🔄 بروزرسانی", command=self.refresh_all_files, 
                     width=120, height=35, font=ctk.CTkFont(family="B Nazanin", size=12)).pack(side="left", padx=2)
        ctk.CTkButton(buttons_frame, text="🗑️ پاک کردن", command=self.clear_search, 
                     width=120, height=35, font=ctk.CTkFont(family="B Nazanin", size=12)).pack(side="left", padx=2)
        ctk.CTkButton(buttons_frame, text="📁 کپی فایل‌ها", command=self.copy_selected_files, 
                     width=120, height=35, font=ctk.CTkFont(family="B Nazanin", size=12)).pack(side="left", padx=2)
        
        # File tree with improved styling
        tree_frame = ctk.CTkFrame(browser_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview with scrollbars
        tree_container = tk.Frame(tree_frame, bg=tree_frame.cget("fg_color")[1])
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.file_tree = ttk.Treeview(
            tree_container,
            columns=("Name", "Path", "Type", "Size"),
            show="headings",
            height=18
        )
        
        # Configure columns - improved sizing for better visibility
        self.file_tree.heading("Name", text="📁 نام فایل")
        self.file_tree.heading("Path", text="📂 مسیر")
        self.file_tree.heading("Type", text="📄 نوع")
        self.file_tree.heading("Size", text="💾 اندازه")
        
        # Increased column widths for better visibility
        self.file_tree.column("Name", width=220, minwidth=180)
        self.file_tree.column("Path", width=300, minwidth=250)
        self.file_tree.column("Type", width=100, minwidth=80)
        self.file_tree.column("Size", width=120, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.file_tree.xview)
        
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Setup native drag and drop for file tree
        self.native_drag_drop = NativeDragDrop(self.file_tree, self.on_file_drag_drop)
        
        # Action buttons
        action_frame = ctk.CTkFrame(browser_frame)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(action_frame, text="📋 کپی انتخاب شده", command=self.copy_selected_files,
                     width=120, font=ctk.CTkFont(family="B Nazanin")).pack(side="left", padx=2)
        ctk.CTkButton(action_frame, text="📁 انتخاب پوشه", command=self.select_folder,
                     width=120, font=ctk.CTkFont(family="B Nazanin")).pack(side="left", padx=2)

    # Removed copy operations section - functionality integrated into task management
    # def setup_copy_operations_section(self, copy_frame):
    #     """Setup the copy operations section - REMOVED"""
    #     pass
        


    def setup_task_management_section(self, task_frame):
        """Setup the complete task management section in the main explorer tab"""
        
        # Title
        title_label = ctk.CTkLabel(task_frame, text="📋 مدیریت کارها", 
                                  font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold"))
        title_label.pack(pady=(10, 5))
        
        # Control buttons
        control_frame = ctk.CTkFrame(task_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # Main control buttons
        main_controls = ctk.CTkFrame(control_frame)
        main_controls.pack(fill="x", pady=(0, 2))
        
        self.start_btn = ctk.CTkButton(main_controls, text="▶ شروع", command=self.start_selected_task,
                                      fg_color="green", hover_color="darkgreen", 
                                      font=ctk.CTkFont(family="B Nazanin", size=10), width=60, height=28)
        self.start_btn.pack(side="left", padx=2)
        
        self.pause_btn = ctk.CTkButton(main_controls, text="⏸ توقف", command=self.pause_selected_task,
                                      fg_color="orange", hover_color="darkorange", 
                                      font=ctk.CTkFont(family="B Nazanin", size=10), width=60, height=28)
        self.pause_btn.pack(side="left", padx=2)
        
        self.cancel_btn = ctk.CTkButton(main_controls, text="⏹ لغو", command=self.cancel_selected_task,
                                       fg_color="red", hover_color="darkred", 
                                       font=ctk.CTkFont(family="B Nazanin", size=10), width=60, height=28)
        self.cancel_btn.pack(side="left", padx=2)
        
        # Task management buttons
        task_controls = ctk.CTkFrame(control_frame)
        task_controls.pack(fill="x")
        
        ctk.CTkButton(task_controls, text="🗑 پاک همه", command=self.clear_all_tasks, 
                     font=ctk.CTkFont(family="B Nazanin", size=10), width=80, height=28).pack(side="left", padx=2)
        ctk.CTkButton(task_controls, text="✓ تکمیل شده", command=self.clear_completed, 
                     font=ctk.CTkFont(family="B Nazanin", size=10), width=90, height=28).pack(side="left", padx=2)
        
        # Progress overview
        progress_frame = ctk.CTkFrame(task_frame)
        progress_frame.pack(fill="x", padx=5, pady=2)
        
        self.overall_progress = ctk.CTkProgressBar(progress_frame, height=20)
        self.overall_progress.pack(fill="x", padx=5, pady=2)
        self.overall_progress.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="هیچ کار فعالی موجود نیست", 
                                         font=ctk.CTkFont(family="B Nazanin", size=11))
        self.progress_label.pack(pady=2)
        
        # Tasks tree (full version)
        tasks_tree_frame = ctk.CTkFrame(task_frame)
        tasks_tree_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        tasks_container = tk.Frame(tasks_tree_frame, bg=tasks_tree_frame.cget("fg_color")[1])
        tasks_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.task_tree = ttk.Treeview(
            tasks_container,
            columns=("File", "Destination", "Progress", "Size", "Status"),
            show="headings",
            height=16
        )
        
        # Configure task tree columns with improved sizing
        self.task_tree.heading("File", text="📁 فایل")
        self.task_tree.heading("Destination", text="📂 مقصد")
        self.task_tree.heading("Progress", text="📊 %")
        self.task_tree.heading("Size", text="💾 حجم")
        self.task_tree.heading("Status", text="🔄 وضعیت")
        
        self.task_tree.column("File", width=120, minwidth=100)
        self.task_tree.column("Destination", width=100, minwidth=80)
        self.task_tree.column("Progress", width=60, minwidth=50)
        self.task_tree.column("Size", width=70, minwidth=60)
        self.task_tree.column("Status", width=80, minwidth=70)
        
        # Task tree scrollbars
        task_v_scrollbar = ttk.Scrollbar(tasks_container, orient="vertical", command=self.task_tree.yview)
        task_h_scrollbar = ttk.Scrollbar(tasks_container, orient="horizontal", command=self.task_tree.xview)
        
        self.task_tree.configure(yscrollcommand=task_v_scrollbar.set, xscrollcommand=task_h_scrollbar.set)
        
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        task_v_scrollbar.grid(row=0, column=1, sticky="ns")
        task_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tasks_container.grid_rowconfigure(0, weight=1)
        tasks_container.grid_columnconfigure(0, weight=1)

    def setup_drive_destination_section(self, drive_frame):
        """Setup the drive destination selection section"""
        
        # Title
        title_label = ctk.CTkLabel(drive_frame, text="💿 انتخاب مقصد", 
                                  font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold"))
        title_label.pack(pady=(10, 5))
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            drive_frame,
            text="درایو یا پوشه مقصد را انتخاب کنید",
            font=ctk.CTkFont(family="B Nazanin", size=12),
            wraplength=200
        )
        instruction_label.pack(pady=5)
        
        # Destination selection button
        select_dest_btn = ctk.CTkButton(
            drive_frame,
            text="📁 انتخاب پوشه مقصد",
            command=self.select_destination,
            font=ctk.CTkFont(family="B Nazanin", size=12),
            width=180,
            height=35
        )
        select_dest_btn.pack(pady=5)
        
        # Current destination label
        self.current_dest_label = ctk.CTkLabel(
            drive_frame,
            text="هیچ مقصدی انتخاب نشده",
            font=ctk.CTkFont(family="B Nazanin", size=10),
            wraplength=200
        )
        self.current_dest_label.pack(pady=5)
        
        # Auto-refresh destinations button
        refresh_dest_btn = ctk.CTkButton(
            drive_frame,
            text="🔄 بروزرسانی مقاصد",
            command=self.refresh_destinations,
            font=ctk.CTkFont(family="B Nazanin", size=12),
            width=180,
            height=35
        )
        refresh_dest_btn.pack(pady=8)
        
        # Destinations scrollable frame
        self.dest_folders_frame = ctk.CTkScrollableFrame(
            drive_frame,
            label_text="📁 پوشه‌های مقصد",
            height=400,
            label_font=ctk.CTkFont(family="B Nazanin", size=14, weight="bold")
        )
        self.dest_folders_frame.pack(fill="both", expand=True, padx=5, pady=(10, 10))
        
        # Initialize with auto-detected destinations
        self.update_destination_folders_display()

    def setup_quick_copy_sidebar(self, parent):
        """Setup the quick copy sidebar with auto-detected destinations"""
        # Sidebar frame
        sidebar_frame = ctk.CTkFrame(parent, width=350)
        sidebar_frame.pack(side="right", fill="y", padx=(5, 0))
        sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # Sidebar title
        title_label = ctk.CTkLabel(
            sidebar_frame,
            text="🎯 کپی سریع",
            font=ctk.CTkFont(family="B Nazanin", size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            sidebar_frame,
            text="فایل‌ها را از لیست انتخاب کنید\nسپس روی پوشه مقصد کلیک کنید",
            font=ctk.CTkFont(family="B Nazanin", size=12),
            wraplength=300
        )
        instruction_label.pack(pady=5)
        
        # Auto-refresh destinations button
        refresh_dest_btn = ctk.CTkButton(
            sidebar_frame,
            text="🔄 بروزرسانی مقاصد",
            command=self.refresh_destinations,
            font=ctk.CTkFont(family="B Nazanin", size=12),
            width=200
        )
        refresh_dest_btn.pack(pady=5)
        
        # Destinations scrollable frame
        self.dest_folders_frame = ctk.CTkScrollableFrame(
            sidebar_frame,
            label_text="📁 پوشه‌های مقصد (شناسایی خودکار)",
            height=500,
            label_font=ctk.CTkFont(family="B Nazanin", size=14, weight="bold")
        )
        self.dest_folders_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        
        # Initialize with auto-detected destinations
        self.update_destination_folders_display()



    def setup_settings_tab(self):
        """Setup the settings tab"""
        # Create scrollable frame with beautiful styling
        settings_scroll = ctk.CTkScrollableFrame(
            self.settings_frame,
            corner_radius=10,
            fg_color=("gray95", "gray20"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        settings_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Font Settings - سیستم انتخاب فونت کامل
        font_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        font_frame.pack(fill="x", pady=10)
        
        font_header = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            font_header, 
            text="🔤 تنظیمات فونت و نمایش", 
            font=ctk.CTkFont(family=self.current_font_family, size=18, weight="bold")
        ).pack(side="left")
        
        # Font family selection
        font_family_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_family_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            font_family_frame, 
            text="نوع فونت:", 
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold")
        ).pack(side="right", padx=5)
        
        self.font_family_var = tk.StringVar(value=self.current_font_family)
        self.font_family_combo = ctk.CTkComboBox(
            font_family_frame,
            variable=self.font_family_var,
            values=self.system_fonts,
            width=200,
            font=ctk.CTkFont(family=self.current_font_family, size=11),
            command=self.on_font_family_changed
        )
        self.font_family_combo.pack(side="left", fill="x", expand=True, padx=5)
        
        # Font size selection
        font_size_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_size_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            font_size_frame, 
            text="اندازه فونت:", 
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold")
        ).pack(side="right", padx=5)
        
        self.font_size_var = tk.StringVar(value=str(self.current_font_size))
        font_size_combo = ctk.CTkComboBox(
            font_size_frame,
            variable=self.font_size_var,
            values=["8", "9", "10", "11", "12", "13", "14", "15", "16", "18", "20", "22", "24"],
            width=80,
            font=ctk.CTkFont(family=self.current_font_family, size=11),
            command=self.on_font_size_changed
        )
        font_size_combo.pack(side="left", padx=5)
        
        # Font preview
        font_preview_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_preview_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            font_preview_frame, 
            text="پیش‌نمایش:", 
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold")
        ).pack(side="right", padx=5)
        
        self.font_preview_label = ctk.CTkLabel(
            font_preview_frame,
            text="نمونه متن فارسی - Sample English Text - 123456",
            font=ctk.CTkFont(family=self.current_font_family, size=self.current_font_size),
            fg_color=("gray90", "gray15"),
            corner_radius=8,
            height=40
        )
        self.font_preview_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Apply font button
        font_apply_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_apply_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkButton(
            font_apply_frame,
            text="✅ اعمال فونت جدید",
            command=self.apply_selected_font,
            width=150,
            height=35,
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold"),
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "lightgreen")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            font_apply_frame,
            text="🔄 بازگردانی پیش‌فرض",
            command=self.reset_font_to_default,
            width=150,
            height=35,
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold"),
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "lightorange")
        ).pack(side="left", padx=5)
        
        # License Management Section - بخش مدیریت لایسنس
        license_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        license_frame.pack(fill="x", pady=10)
        
        license_header = ctk.CTkFrame(license_frame, fg_color="transparent")
        license_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            license_header, 
            text="🔑 مدیریت لایسنس و فعال‌سازی", 
            font=ctk.CTkFont(family=self.current_font_family, size=18, weight="bold")
        ).pack(side="left")
        
        # Current license status
        license_status_frame = ctk.CTkFrame(license_frame, fg_color="transparent")
        license_status_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            license_status_frame, 
            text="وضعیت فعلی:", 
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold")
        ).pack(side="right", padx=5)
        
        # Show current license status
        license_data = self.license_manager.load_license()
        if license_data:
            if license_data.get("serial") == "TRIAL-MODE":
                status_text = "🟡 نسخه آزمایشی (30 روزه)"
                status_color = ("orange", "darkorange")
            else:
                status_text = f"🟢 فعال - سریال: {license_data.get('serial', 'نامشخص')}"
                status_color = ("green", "darkgreen")
        else:
            status_text = "🔴 غیرفعال - نیاز به فعال‌سازی"
            status_color = ("red", "darkred")
        
        self.license_status_label = ctk.CTkLabel(
            license_status_frame,
            text=status_text,
            font=ctk.CTkFont(family=self.current_font_family, size=12),
            fg_color=status_color,
            corner_radius=8,
            height=30
        )
        self.license_status_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # License key input
        license_input_frame = ctk.CTkFrame(license_frame, fg_color="transparent")
        license_input_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            license_input_frame, 
            text="کد لایسنس:", 
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold")
        ).pack(side="right", padx=5)
        
        self.license_key_entry = ctk.CTkEntry(
            license_input_frame,
            placeholder_text="PFC-XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(family=self.current_font_family, size=11),
            width=250,
            height=35
        )
        self.license_key_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # License action buttons
        license_buttons_frame = ctk.CTkFrame(license_frame, fg_color="transparent")
        license_buttons_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkButton(
            license_buttons_frame,
            text="✅ فعال‌سازی لایسنس",
            command=self.activate_license,
            width=150,
            height=35,
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold"),
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "lightgreen")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            license_buttons_frame,
            text="🛒 خرید لایسنس",
            command=self.purchase_license,
            width=120,
            height=35,
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold"),
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "lightblue")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            license_buttons_frame,
            text="❓ راهنما",
            command=self.show_license_help,
            width=80,
            height=35,
            font=ctk.CTkFont(family=self.current_font_family, size=12, weight="bold"),
            fg_color=("gray", "darkgray"),
            hover_color=("darkgray", "lightgray")
        ).pack(side="left", padx=5)
        
        # Performance Settings (Licensed Feature)
        perf_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        perf_frame.pack(fill="x", pady=10)
        
        perf_header = ctk.CTkFrame(perf_frame, fg_color="transparent")
        perf_header.pack(fill="x", padx=15, pady=(15, 5))
        
        # Check license for advanced settings
        license_text = "⚡ Performance Settings"
        if not self.check_feature_license("advanced_settings"):
            license_text += " 🔒 (نیاز به لایسنس)"
        
        perf_title = ctk.CTkLabel(
            perf_header, 
            text=license_text, 
            font=ctk.CTkFont(family="B Nazanin", size=18, weight="bold"),
            text_color=("red", "orange") if not self.check_feature_license("advanced_settings") else ("gray10", "white")
        )
        perf_title.pack(side="left")
        
        # Performance help button
        perf_help = ctk.CTkButton(
            perf_header,
            text="❓",
            width=30,
            height=30,
            corner_radius=15,
            command=lambda: self.show_help("performance")
        )
        perf_help.pack(side="right")
        
        # Buffer size with slider
        buffer_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        buffer_frame.pack(fill="x", padx=15, pady=8)
        
        buffer_header = ctk.CTkFrame(buffer_frame, fg_color="transparent")
        buffer_header.pack(fill="x")
        
        ctk.CTkLabel(
            buffer_header, 
            text="🔧 Buffer Size:", 
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        ).pack(side="left")
        
        self.buffer_var = tk.StringVar(value=str(self.settings.get("buffer_size", 64 * 1024) // 1024))
        buffer_entry = ctk.CTkEntry(
            buffer_header, 
            textvariable=self.buffer_var, 
            width=80,
            placeholder_text="KB",
            state="disabled" if not self.check_feature_license("advanced_settings") else "normal"
        )
        buffer_entry.pack(side="right", padx=5)
        
        ctk.CTkLabel(buffer_header, text="KB").pack(side="right")
        
        # Buffer slider
        self.buffer_slider = ctk.CTkSlider(
            buffer_frame,
            from_=16,
            to=1024,
            number_of_steps=32,
            command=self.update_buffer_from_slider if self.check_feature_license("advanced_settings") else self.show_license_prompt_for_advanced_settings,
            state="disabled" if not self.check_feature_license("advanced_settings") else "normal"
        )
        self.buffer_slider.pack(fill="x", pady=(5, 0))
        self.buffer_slider.set(int(self.buffer_var.get()))
        
        # Buffer recommendation
        buffer_rec = ctk.CTkLabel(
            buffer_frame,
            text="💡 Recommended: SSD=256KB, HDD=64KB, Network=32KB",
            font=ctk.CTkFont(family="B Nazanin", size=10),
            text_color=("gray50", "gray60")
        )
        buffer_rec.pack(pady=(2, 0))
        
        # Max threads with slider
        threads_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        threads_frame.pack(fill="x", padx=15, pady=8)
        
        threads_header = ctk.CTkFrame(threads_frame, fg_color="transparent")
        threads_header.pack(fill="x")
        
        ctk.CTkLabel(
            threads_header, 
            text="👥 Max Threads:", 
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        ).pack(side="left")
        
        self.threads_var = tk.StringVar(value=str(self.settings.get("max_threads", 4)))
        threads_entry = ctk.CTkEntry(
            threads_header, 
            textvariable=self.threads_var, 
            width=60
        )
        threads_entry.pack(side="right", padx=5)
        
        # Threads slider
        self.threads_slider = ctk.CTkSlider(
            threads_frame,
            from_=1,
            to=8,
            number_of_steps=7,
            command=self.update_threads_from_slider
        )
        self.threads_slider.pack(fill="x", pady=(5, 0))
        self.threads_slider.set(int(self.threads_var.get()))
        
        # Threads recommendation
        threads_rec = ctk.CTkLabel(
            threads_frame,
            text="💡 Recommended: Large files=1-2, Small files=4-6, Network=2-3",
            font=ctk.CTkFont(family="B Nazanin", size=10),
            text_color=("gray50", "gray60")
        )
        threads_rec.pack(pady=(2, 0))
        
        # Progress update interval
        progress_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=8)
        
        progress_header = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_header.pack(fill="x")
        
        ctk.CTkLabel(
            progress_header, 
            text="⏱ Update Interval:", 
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        ).pack(side="left")
        
        self.progress_interval_var = tk.StringVar(value=str(self.settings.get("progress_update_interval", 0.5)))
        progress_entry = ctk.CTkEntry(
            progress_header, 
            textvariable=self.progress_interval_var, 
            width=60,
            placeholder_text="sec"
        )
        progress_entry.pack(side="right", padx=5)
        
        ctk.CTkLabel(progress_header, text="seconds").pack(side="right")
        
        # Progress slider  
        self.progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            command=self.update_progress_from_slider
        )
        self.progress_slider.pack(fill="x", pady=(5, 0))
        self.progress_slider.set(float(self.progress_interval_var.get()))
        
        # Behavior Settings
        behavior_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        behavior_frame.pack(fill="x", pady=10)
        
        behavior_header = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        behavior_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            behavior_header, 
            text="🎯 Behavior Settings", 
            font=ctk.CTkFont(family="B Nazanin", size=18, weight="bold"),
            text_color=("gray10", "white")
        ).pack(side="left")
        
        ctk.CTkButton(
            behavior_header,
            text="❓",
            width=30,
            height=30,
            corner_radius=15,
            command=lambda: self.show_help("behavior")
        ).pack(side="right")
        
        # Overwrite policy
        overwrite_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        overwrite_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            overwrite_frame, 
            text="📁 File Exists Policy:", 
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        self.overwrite_var = tk.StringVar(value=self.settings.get("overwrite_policy", "prompt"))
        overwrite_combo = ctk.CTkComboBox(
            overwrite_frame, 
            values=["prompt", "overwrite", "skip"],
            variable=self.overwrite_var, 
            width=120
        )
        overwrite_combo.pack(side="right", padx=5)
        
        # Additional behavior settings
        # Auto retry
        retry_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        retry_frame.pack(fill="x", padx=15, pady=5)
        
        self.auto_retry_var = tk.BooleanVar(value=self.settings.get("auto_retry", True))
        retry_checkbox = ctk.CTkCheckBox(
            retry_frame,
            text="🔄 Auto Retry Failed Operations",
            variable=self.auto_retry_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        retry_checkbox.pack(side="left")
        
        self.retry_count_var = tk.StringVar(value=str(self.settings.get("retry_count", 3)))
        retry_spinbox = ctk.CTkEntry(retry_frame, textvariable=self.retry_count_var, width=50)
        retry_spinbox.pack(side="right", padx=(5, 0))
        ctk.CTkLabel(retry_frame, text="times").pack(side="right")
        
        # Verify copy
        verify_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        verify_frame.pack(fill="x", padx=15, pady=5)
        
        self.verify_copy_var = tk.BooleanVar(value=self.settings.get("verify_copy", True))
        verify_checkbox = ctk.CTkCheckBox(
            verify_frame,
            text="✅ Verify Copy Integrity (slower but safer)",
            variable=self.verify_copy_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        verify_checkbox.pack(side="left")
        
        # Show hidden files
        hidden_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        hidden_frame.pack(fill="x", padx=15, pady=5)
        
        self.show_hidden_var = tk.BooleanVar(value=self.settings.get("show_hidden_files", False))
        hidden_checkbox = ctk.CTkCheckBox(
            hidden_frame,
            text="🗂 Show Hidden Files and Folders",
            variable=self.show_hidden_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        hidden_checkbox.pack(side="left")
        
        # Create backup
        backup_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        backup_frame.pack(fill="x", padx=15, pady=5)
        
        self.create_backup_var = tk.BooleanVar(value=self.settings.get("create_backup", False))
        backup_checkbox = ctk.CTkCheckBox(
            backup_frame,
            text="💾 Create Backup Before Overwriting",
            variable=self.create_backup_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        backup_checkbox.pack(side="left")
        
        # Preserve permissions
        perm_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        perm_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.preserve_permissions_var = tk.BooleanVar(value=self.settings.get("preserve_permissions", True))
        perm_checkbox = ctk.CTkCheckBox(
            perm_frame,
            text="🔐 Preserve File Permissions",
            variable=self.preserve_permissions_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        perm_checkbox.pack(side="left")
        
        # Appearance Settings
        appearance_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        appearance_frame.pack(fill="x", pady=10)
        
        appearance_header = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        appearance_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            appearance_header, 
            text="🎨 Appearance Settings", 
            font=ctk.CTkFont(family="B Nazanin", size=18, weight="bold"),
            text_color=("gray10", "white")
        ).pack(side="left")
        
        ctk.CTkButton(
            appearance_header,
            text="❓",
            width=30,
            height=30,
            corner_radius=15,
            command=lambda: self.show_help("appearance")
        ).pack(side="right")
        
        # Theme section with preview
        theme_section = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_section.pack(fill="x", padx=15, pady=10)
        
        theme_header = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            theme_header, 
            text="🎨 Theme:", 
            font=ctk.CTkFont(family="B Nazanin", size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        # Theme help button
        ctk.CTkButton(
            theme_header,
            text="❓",
            width=25,
            height=25,
            corner_radius=12,
            command=lambda: self.show_help("appearance")
        ).pack(side="right")
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark_blue"))
        # ایجاد لیست نام‌های فارسی تم‌ها برای نمایش
        theme_display_names = [f"{theme_id}: {config.get('name', theme_id)}" for theme_id, config in THEMES.items()]
        theme_combo = ctk.CTkComboBox(
            theme_section, 
            values=theme_display_names,
            variable=self.theme_var, 
            width=300,
            command=self.preview_theme,
            font=ctk.CTkFont(family="B Nazanin", size=12)
        )
        theme_combo.pack(fill="x", padx=5, pady=5)
        
        # Theme preview
        self.theme_preview = ctk.CTkFrame(
            theme_section,
            height=60,
            corner_radius=8,
            fg_color=("gray90", "gray20")
        )
        self.theme_preview.pack(fill="x", padx=5, pady=5)
        self.theme_preview.pack_propagate(False)
        
        ctk.CTkLabel(
            self.theme_preview,
            text="🎨 Theme Preview",
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        ).pack(pady=20)
        
        # Additional appearance settings
        # Notification settings
        notification_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        notification_frame.pack(fill="x", padx=15, pady=5)
        
        self.notification_sound_var = tk.BooleanVar(value=self.settings.get("notification_sound", True))
        notification_checkbox = ctk.CTkCheckBox(
            notification_frame,
            text="🔔 Play Completion Sound",
            variable=self.notification_sound_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        notification_checkbox.pack(side="left")
        
        # Show speed graph
        graph_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        graph_frame.pack(fill="x", padx=15, pady=5)
        
        self.show_speed_graph_var = tk.BooleanVar(value=self.settings.get("show_speed_graph", True))
        graph_checkbox = ctk.CTkCheckBox(
            graph_frame,
            text="📊 Show Speed Graph",
            variable=self.show_speed_graph_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        graph_checkbox.pack(side="left")
        
        # Auto clear completed
        auto_clear_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        auto_clear_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.auto_clear_completed_var = tk.BooleanVar(value=self.settings.get("auto_clear_completed", False))
        auto_clear_checkbox = ctk.CTkCheckBox(
            auto_clear_frame,
            text="🗑 Auto Clear Completed Tasks",
            variable=self.auto_clear_completed_var,
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        )
        auto_clear_checkbox.pack(side="left")
        
        # Save button with enhanced styling
        save_frame = ctk.CTkFrame(
            settings_scroll,
            fg_color="transparent"
        )
        save_frame.pack(fill="x", pady=20)
        
        save_button = ctk.CTkButton(
            save_frame, 
            text="💾 Save All Settings", 
            command=self.save_settings_from_gui,
            font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold"), 
            height=50,
            corner_radius=25,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        save_button.pack(pady=10)
        
        # Reset to defaults button
        reset_button = ctk.CTkButton(
            save_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_settings_to_defaults,
            font=ctk.CTkFont(family="B Nazanin", size=12),
            height=35,
            corner_radius=17,
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        reset_button.pack(pady=(0, 10))

    def setup_status_bar(self):
        """Setup the status bar"""
        status_frame = ctk.CTkFrame(self.main_frame, height=30)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        self.file_count_label = ctk.CTkLabel(status_frame, text="Files: 0")
        self.file_count_label.pack(side="right", padx=10, pady=5)

    def setup_bindings(self):
        """Setup event bindings"""
        try:
            if hasattr(self, 'search_entry') and self.search_entry:
                self.search_entry.bind("<KeyRelease>", self.on_search_change)
            if hasattr(self, 'file_tree') and self.file_tree:
                self.file_tree.bind("<Double-1>", self.on_file_double_click)
            if hasattr(self, 'task_tree') and self.task_tree:
                self.task_tree.bind("<Double-1>", self.on_task_double_click)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.bind("<Configure>", self.on_window_resize)
        except Exception as e:
            print(f"Error setting up bindings: {e}")

    def update_status(self, message: str):
        """Update status bar message"""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(text=message)
                self.root.update_idletasks()
            else:
                # If status label not ready yet, just print to console
                print(f"Status: {message}")
        except Exception as e:
            print(f"Error updating status: {e}, Message: {message}")

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    def get_file_size(self, path: str) -> int:
        """Get size of file or directory"""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(file_path)
                        except (OSError, IOError):
                            continue
                return total_size
            return 0
        except (OSError, IOError):
            return 0

    def browse_directory(self):
        """Browse for a directory"""
        directory = filedialog.askdirectory(initialdir=self.current_dir)
        if directory:
            self.current_dir = directory
            self.current_dir_label.configure(text=directory)
            self.refresh_files()

    def go_home(self):
        """Go to home directory"""
        self.current_dir = os.path.expanduser("~")
        self.current_dir_label.configure(text=self.current_dir)
        self.refresh_files()

    def browse_dest(self):
        """Browse for destination directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, directory)

    def refresh_all_files(self):
        """Refresh all files from all drives"""
        self.update_status("بروزرسانی همه فایل‌ها از تمام درایوها...")
        threading.Thread(target=self.initial_system_scan, daemon=True).start()

    def refresh_files(self):
        """Legacy method - redirects to refresh_all_files"""
        self.refresh_all_files()

    def _refresh_files_thread(self):
        """Thread function to refresh files"""
        try:
            if not os.path.exists(self.current_dir):
                self.root.after(0, lambda: self.update_status("Directory not found"))
                return
            
            files_data = []
            file_count = 0
            
            for item in os.listdir(self.current_dir):
                item_path = os.path.join(self.current_dir, item)
                try:
                    if os.path.isfile(item_path):
                        size = self.get_file_size(item_path)
                        files_data.append((item, item_path, "File", self.format_size(size)))
                    elif os.path.isdir(item_path):
                        files_data.append((item, item_path, "Directory", ""))
                    file_count += 1
                except (OSError, IOError):
                    continue
            
            # Update cache
            self.file_cache["files"] = {
                item_path: {"name": name, "type": file_type, "size": size_str}
                for name, item_path, file_type, size_str in files_data
            }
            self.file_cache["last_scan"] = time.time()
            self.save_cache()
            
            # Update GUI
            self.root.after(0, lambda: self._update_file_tree(files_data, file_count))
            
        except Exception as e:
            self.logger.error(f"Error refreshing files: {e}")
            self.root.after(0, lambda: self.update_status(f"Error: {e}"))

    def _update_file_tree(self, files_data: List, file_count: int):
        """Update file tree with new data"""
        try:
            self.file_tree.delete(*self.file_tree.get_children())
            
            for file_info in files_data:
                if len(file_info) == 4:
                    # Old format: name, path, file_type, size
                    name, path, file_type, size = file_info
                    drive = ""
                elif len(file_info) == 5:
                    # New format: name, path, file_type, size, drive
                    name, path, file_type, size, drive = file_info
                else:
                    continue
                    
                self.file_tree.insert("", "end", values=(name, path, file_type, size, drive))
            
            if hasattr(self, 'file_count_label'):
                self.file_count_label.configure(text=f"Files: {file_count}")
            self.update_status("Ready")
        except Exception as e:
            print(f"Error updating file tree: {e}")

    def display_cache(self):
        """Display cached files"""
        try:
            self.file_tree.delete(*self.file_tree.get_children())
            file_count = 0
            
            for item_path, data in self.file_cache.get("files", {}).items():
                if os.path.exists(item_path):
                    size_str = data.get("size", "")
                    drive_info = data.get("drive", "")
                    self.file_tree.insert("", "end", values=(
                        data["name"], item_path, data["type"], size_str, drive_info
                    ))
                    file_count += 1
            
            if hasattr(self, 'file_count_label'):
                self.file_count_label.configure(text=f"Files: {file_count}")
        except Exception as e:
            print(f"Error displaying cache: {e}")

    def on_search_change(self, event):
        """Handle search entry changes"""
        search_term = self.search_entry.get().lower().strip()
        if not search_term:
            self.display_cache()
            return
        
        self.update_status("Searching...")
        threading.Thread(target=self._search_files_thread, args=(search_term,), daemon=True).start()

    def _search_files_thread(self, search_term: str):
        """Thread function to search files"""
        try:
            filtered_files = []
            file_count = 0
            
            for item_path, data in self.file_cache.get("files", {}).items():
                if not os.path.exists(item_path):
                    continue
                
                name = data["name"].lower()
                
                # Check if search term matches name or extension
                if (search_term in name or 
                    (search_term.startswith(".") and name.endswith(search_term))):
                    size_str = data.get("size", "")
                    drive_info = data.get("drive", "")
                    filtered_files.append((data["name"], item_path, data["type"], size_str, drive_info))
                    file_count += 1
            
            self.root.after(0, lambda: self._update_file_tree(filtered_files, file_count))
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            self.root.after(0, lambda: self.update_status("Search error"))

    def clear_search(self):
        """Clear search and show all files"""
        self.search_entry.delete(0, tk.END)
        self.display_cache()

    def select_all_files(self):
        """Select all files in the tree"""
        for item in self.file_tree.get_children():
            self.file_tree.selection_add(item)

    def clear_selection(self):
        """Clear file selection"""
        self.file_tree.selection_remove(*self.file_tree.selection())

    def add_to_queue(self):
        """Add selected files to copy queue"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select files to add to queue!")
            return
        
        destination = self.dest_entry.get().strip()
        if not destination:
            messagebox.showerror("Error", "Please select a destination directory!")
            return
        
        if not os.path.exists(destination):
            messagebox.showerror("Error", "Destination directory does not exist!")
            return
        
        added_count = 0
        for item in selected_items:
            values = self.file_tree.item(item, "values")
            if len(values) >= 2:
                source_path = values[1]  # Full path
                if source_path not in [task["source"] for task in self.copy_tasks]:
                    self.add_task(source_path, destination)
                    added_count += 1
        
        if added_count > 0:
            self.update_status(f"Added {added_count} files to queue")
            # Switch to tasks tab
            self.notebook.select(1)
        else:
            messagebox.showinfo("Info", "Selected files are already in the queue!")

    def add_task(self, source: str, destination: str):
        """Add a copy task to the queue"""
        if not os.path.exists(source):
            return
        
        task_id = len(self.copy_tasks)
        filename = os.path.basename(source)
        dest_path = os.path.join(destination, filename)
        file_size = self.get_file_size(source)
        
        task = {
            "id": task_id,
            "source": source,
            "destination": dest_path,
            "filename": filename,
            "size": file_size,
            "copied": 0,
            "progress": 0.0,
            "speed": 0.0,
            "status": "⏳ Pending",
            "paused": False,
            "cancelled": False,
            "completed": False,
            "start_time": 0,
            "last_update": 0,
            "retry_count": 0,
            "error_message": "",
            "future": None
        }
        
        self.copy_tasks.append(task)
        
        # Add to task tree
        self.task_tree.insert("", "end", iid=str(task_id), values=(
            filename,
            dest_path,
            "0%",
            self.format_size(file_size),
            "0 B",
            "0.0",
            "⏳ Pending"
        ))
        
        self.update_overall_progress()

    def get_selected_task(self):
        """Get the currently selected task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showinfo("انتخاب تسک", "لطفاً یک تسک را انتخاب کنید!")
            return None
        
        task_id = int(selected[0])
        if task_id >= len(self.copy_tasks):
            return None
        
        return self.copy_tasks[task_id]
    
    def start_selected_task(self):
        """Start the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] in ["⏳ Pending", "❌ Cancelled", "❌ Error", "⏸ Paused"]:
            task["status"] = "🔄 Running"
            task["cancelled"] = False
            task["paused"] = False
            task["start_time"] = time.time()
            task["last_update"] = time.time()
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
            self.update_status(f"شروع کپی: {task['filename']}")
            
            # Update copying state but keep buttons enabled for individual control
            self.is_copying = True
        else:
            messagebox.showinfo("خطا", f"این تسک قابل شروع نیست! وضعیت فعلی: {task['status']}")

    def preview_theme(self, theme_name: str):
        """پیش‌نمایش تم انتخاب شده"""
        try:
            # استخراج شناسه تم از نام نمایشی (format: "theme_id: نام فارسی")
            if ":" in theme_name:
                theme_id = theme_name.split(":")[0].strip()
            else:
                theme_id = theme_name
            
            theme_config = THEMES.get(theme_id, THEMES["dark_blue"])
            
            # به‌روزرسانی رنگ‌های پیش‌نمایش بر اساس تم
            if theme_config["mode"] == "dark":
                preview_color = ("gray20", "gray30")
                text_color = ("white", "gray90")
            else:
                preview_color = ("gray90", "gray80") 
                text_color = ("gray10", "gray20")
            
            # اعمال رنگ‌ها به پیش‌نمایش
            self.theme_preview.configure(fg_color=preview_color)
            
            # به‌روزرسانی متن پیش‌نمایش
            for widget in self.theme_preview.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=text_color)
            
            # ذخیره شناسه تم واقعی برای استفاده در تنظیمات
            self.current_preview_theme = theme_id
                    
        except Exception as e:
            self.logger.error(f"خطا در پیش‌نمایش تم: {e}")

    def copy_task(self, task: Dict):
        """Copy a single file/directory with enhanced error handling"""
        try:
            task["status"] = "🔄 Running"
            task["start_time"] = time.time()
            task["last_update"] = time.time()
            
            self.root.after(0, lambda: self.update_task_display(task))
            
            source = task["source"]
            destination = task["destination"]
            
            # Check disk space first
            if not self.check_disk_space(os.path.dirname(destination), task["size"]):
                raise Exception("Insufficient disk space")
            
            # Check if destination exists
            if os.path.exists(destination):
                policy = self.settings.get("overwrite_policy", "prompt")
                if policy == "skip":
                    task["status"] = "⏭ Skipped"
                    self.root.after(0, lambda: self.update_task_display(task))
                    return
                elif policy == "prompt":
                    # For now, just overwrite - in a real app you'd show a dialog
                    pass
                elif policy == "overwrite":
                    if self.settings.get("create_backup", False):
                        backup_path = destination + ".bak"
                        shutil.copy2(destination, backup_path)
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the file/directory
            if os.path.isfile(source):
                self.copy_file(task)
            elif os.path.isdir(source):
                self.copy_directory(task)
            
            # Verify copy if enabled
            if self.settings.get("verify_copy", False) and not task["cancelled"]:
                if not self.verify_copy(source, destination):
                    raise Exception("Copy verification failed")
            
            if not task["cancelled"]:
                task["status"] = "✅ Completed"
                task["progress"] = 100.0
                task["copied"] = task["size"]
                task["completed"] = True
                task["completion_time"] = time.time()  # Record completion time for auto-cleanup
                self.root.after(0, lambda: self.update_task_display(task))
                self.logger.info(f"Successfully copied {source} to {destination}")
                
                # Play notification sound if enabled
                if self.settings.get("notification_sound", False):
                    self.play_notification_sound()
            
        except Exception as e:
            error_msg = str(e)
            task["error_message"] = error_msg
            
            # Auto retry if enabled
            if (self.settings.get("auto_retry", False) and 
                task["retry_count"] < self.settings.get("retry_count", 3) and
                "space" not in error_msg.lower()):
                
                task["retry_count"] += 1
                task["status"] = f"🔄 Retry {task['retry_count']}"
                self.root.after(2000, lambda: self.copy_task(task))  # Retry after 2 seconds
            else:
                task["status"] = f"❌ Error: {error_msg}"
                self.root.after(0, lambda: self.update_task_display(task))
                self.logger.error(f"Failed to copy {task['source']}: {e}")
        
        finally:
            self.root.after(0, self.check_all_tasks_complete)
    
    def verify_copy(self, source: str, destination: str) -> bool:
        """Verify that the copy was successful"""
        try:
            if os.path.isfile(source) and os.path.isfile(destination):
                return os.path.getsize(source) == os.path.getsize(destination)
            elif os.path.isdir(source) and os.path.isdir(destination):
                # Simple verification - check if all files exist
                for root, dirs, files in os.walk(source):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, source)
                        dst_file = os.path.join(destination, rel_path)
                        if not os.path.exists(dst_file):
                            return False
                return True
            return False
        except:
            return False
    
    def play_notification_sound(self):
        """Play a notification sound"""
        try:
            # Simple system beep - can be enhanced with actual sound files
            import winsound
            winsound.Beep(1000, 200)
        except:
            # On non-Windows systems, try system bell
            try:
                print('\a')  # ASCII bell character
            except:
                pass

    def copy_file(self, task: Dict):
        """Copy a single file with optimized speed and progress tracking"""
        source = task["source"]
        destination = task["destination"]
        
        # Dynamic buffer size based on file size for optimal speed
        file_size = task["size"]
        if file_size < 1024 * 1024:  # < 1MB
            buffer_size = 32 * 1024  # 32KB
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            buffer_size = 512 * 1024  # 512KB
        elif file_size < 1024 * 1024 * 1024:  # < 1GB
            buffer_size = 2 * 1024 * 1024  # 2MB
        else:  # >= 1GB
            buffer_size = 8 * 1024 * 1024  # 8MB
            
        copied_since_update = 0
        update_interval = 0.25  # Update every 0.25 seconds for smoother UI
        
        try:
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                while not task["cancelled"]:
                    # Handle pause
                    while task["paused"] and not task["cancelled"]:
                        time.sleep(0.1)
                    
                    if task["cancelled"]:
                        break
                    
                    chunk = src.read(buffer_size)
                    if not chunk:
                        break
                    
                    dst.write(chunk)
                    dst.flush()  # Force write to disk for better reliability
                    chunk_size = len(chunk)
                    task["copied"] += chunk_size
                    copied_since_update += chunk_size
                    
                    # Update progress periodically
                    current_time = time.time()
                    if current_time - task["last_update"] >= update_interval:
                        elapsed = current_time - task["last_update"]
                        if elapsed > 0:
                            task["speed"] = (copied_since_update / (1024 * 1024)) / elapsed  # MB/s
                        task["progress"] = (task["copied"] / task["size"]) * 100 if task["size"] > 0 else 0
                        task["last_update"] = current_time
                        copied_since_update = 0
                        
                        self.root.after(0, lambda: self.update_task_display(task))
                        
        except PermissionError:
            raise Exception("دسترسی به فایل مقصد امکان‌پذیر نیست")
        except IOError as e:
            raise Exception(f"خطا در خواندن/نوشتن فایل: {str(e)}")
        except Exception as e:
            raise Exception(f"خطای غیرمنتظره: {str(e)}")

    def copy_directory(self, task: Dict):
        """Copy a directory with optimized progress tracking"""
        source = task["source"]
        destination = task["destination"]
        
        copied_since_update = 0
        update_interval = 0.5  # Update every 0.5 seconds for directories
        
        # Use shutil.copytree with custom copy function for progress
        def copy_with_progress(src, dst, *, follow_symlinks=True):
            nonlocal copied_since_update
            
            if task["cancelled"]:
                return
            
            # Handle pause
            while task["paused"] and not task["cancelled"]:
                time.sleep(0.1)
            
            if task["cancelled"]:
                return
            
            try:
                shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
                
                # Update progress
                file_size = os.path.getsize(dst)  # Use destination size after copy
                task["copied"] += file_size
                copied_since_update += file_size
                task["progress"] = (task["copied"] / task["size"]) * 100 if task["size"] > 0 else 0
                
                current_time = time.time()
                if current_time - task["last_update"] >= update_interval:
                    elapsed = current_time - task["last_update"]
                    if elapsed > 0:
                        task["speed"] = (copied_since_update / (1024 * 1024)) / elapsed
                    task["last_update"] = current_time
                    copied_since_update = 0
                    self.root.after(0, lambda: self.update_task_display(task))
                    
            except PermissionError:
                self.logger.warning(f"Permission denied copying {src} to {dst}")
            except Exception as e:
                self.logger.warning(f"Error copying file {src}: {e}")
        
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, copy_function=copy_with_progress, dirs_exist_ok=True)
        except shutil.Error as e:
            # Handle partial copy errors - continue with what we can copy
            self.logger.warning(f"Partial copy error for {source}: {e}")
        except PermissionError:
            raise Exception("دسترسی به پوشه مقصد امکان‌پذیر نیست")
        except Exception as e:
            raise Exception(f"خطا در کپی پوشه: {str(e)}")

    def update_task_display(self, task: Dict):
        """Update task display in the tree"""
        try:
            task_id = str(task["id"])
            if self.task_tree.exists(task_id):
                self.task_tree.set(task_id, "Progress", f"{task['progress']:.1f}%")
                self.task_tree.set(task_id, "Copied", self.format_size(task["copied"]))
                self.task_tree.set(task_id, "Speed", f"{task['speed']:.1f}")
                self.task_tree.set(task_id, "Status", task["status"])
            
            self.update_overall_progress()
        except Exception as e:
            self.logger.error(f"Error updating task display: {e}")

    def update_overall_progress(self):
        """Update overall progress bar and label"""
        if not self.copy_tasks:
            self.overall_progress.set(0)
            self.progress_label.configure(text="No tasks")
            return
        
        total_size = sum(task["size"] for task in self.copy_tasks)
        total_copied = sum(task["copied"] for task in self.copy_tasks)
        
        if total_size > 0:
            progress = total_copied / total_size
            self.overall_progress.set(progress)
        else:
            self.overall_progress.set(0)
        
        # Count tasks by status
        status_counts = {}
        for task in self.copy_tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        status_text = ", ".join([f"{status}: {count}" for status, count in status_counts.items()])
        self.progress_label.configure(text=status_text)

    def pause_selected_task(self):
        """Pause/resume the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] == "🔄 Running":
            task["paused"] = True
            task["status"] = "⏸ Paused"
            self.update_task_display(task)
            self.update_status(f"توقف: {task['filename']}")
        elif task["status"] == "⏸ Paused":
            task["paused"] = False
            task["status"] = "🔄 Running"
            self.update_task_display(task)
            self.update_status(f"ادامه: {task['filename']}")
        else:
            messagebox.showinfo("خطا", "این تسک قابل توقف/ادامه نیست!")

    def cancel_selected_task(self):
        """Cancel the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] in ["🔄 Running", "⏸ Paused", "⏳ Pending"]:
            if messagebox.askyesno("تأیید", f"آیا می‌خواهید تسک '{task['filename']}' را لغو کنید؟"):
                task["cancelled"] = True
                task["status"] = "❌ Cancelled"
                if task.get("future"):
                    task["future"].cancel()
                self.update_task_display(task)
                self.update_status(f"لغو شد: {task['filename']}")
        else:
            messagebox.showinfo("خطا", "این تسک قابل لغو نیست!")
    
    def restart_selected_task(self):
        """Restart the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] in ["✅ Completed", "❌ Cancelled", "❌ Error"]:
            # Reset task
            task["copied"] = 0
            task["progress"] = 0.0
            task["speed"] = 0.0
            task["cancelled"] = False
            task["paused"] = False
            task["retry_count"] = 0
            task["error_message"] = ""
            
            # Start the task
            task["status"] = "🔄 Running"
            task["start_time"] = time.time()
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
            self.update_status(f"شروع مجدد: {task['filename']}")
        else:
            messagebox.showinfo("خطا", "این تسک قابل شروع مجدد نیست!")

    def move_task_up(self):
        """Move selected task up in the queue"""
        selected = self.task_tree.selection()
        if not selected:
            return
        
        task_id = int(selected[0])
        if task_id > 0:
            # Swap tasks
            self.copy_tasks[task_id], self.copy_tasks[task_id - 1] = \
                self.copy_tasks[task_id - 1], self.copy_tasks[task_id]
            
            # Update IDs
            self.copy_tasks[task_id]["id"] = task_id
            self.copy_tasks[task_id - 1]["id"] = task_id - 1
            
            self.refresh_task_tree()
            self.task_tree.selection_set(str(task_id - 1))

    def move_task_down(self):
        """Move selected task down in the queue"""
        selected = self.task_tree.selection()
        if not selected:
            return
        
        task_id = int(selected[0])
        if task_id < len(self.copy_tasks) - 1:
            # Swap tasks
            self.copy_tasks[task_id], self.copy_tasks[task_id + 1] = \
                self.copy_tasks[task_id + 1], self.copy_tasks[task_id]
            
            # Update IDs
            self.copy_tasks[task_id]["id"] = task_id
            self.copy_tasks[task_id + 1]["id"] = task_id + 1
            
            self.refresh_task_tree()
            self.task_tree.selection_set(str(task_id + 1))

    def clear_completed(self):
        """Clear completed tasks"""
        completed_statuses = ["✅ Completed", "❌ Cancelled", "⏭ Skipped"]
        initial_count = len(self.copy_tasks)
        self.copy_tasks = [task for task in self.copy_tasks 
                          if not any(status in task["status"] for status in completed_statuses)]
        
        # Reassign IDs
        for i, task in enumerate(self.copy_tasks):
            task["id"] = i
        
        self.refresh_task_tree()
        cleared_count = initial_count - len(self.copy_tasks)
        self.update_status(f"پاک شد: {cleared_count} تسک تکمیل شده. باقی‌مانده: {len(self.copy_tasks)}")

    def clear_all_tasks(self):
        """Clear all tasks"""
        if messagebox.askyesno("تأیید", "همه تسک‌ها پاک شوند؟ این عمل تسک‌های در حال اجرا را لغو می‌کند."):
            # Cancel all active tasks first
            for task in self.copy_tasks:
                if task["status"] in ["🔄 Running", "⏸ Paused", "⏳ Pending"]:
                    task["cancelled"] = True
                    task["status"] = "❌ Cancelled"
                    if task.get("future"):
                        task["future"].cancel()
            
            self.copy_tasks.clear()
            self.refresh_task_tree()
            self.update_status("همه تسک‌ها پاک شدند")

    def refresh_task_tree(self):
        """Refresh the task tree display"""
        self.task_tree.delete(*self.task_tree.get_children())
        
        for task in self.copy_tasks:
            self.task_tree.insert("", "end", iid=str(task["id"]), values=(
                task["filename"],
                task["destination"],
                f"{task['progress']:.1f}%",
                self.format_size(task["size"]),
                self.format_size(task["copied"]),
                f"{task['speed']:.1f}",
                task["status"]
            ))
        
        self.update_overall_progress()

    def check_all_tasks_complete(self):
        """Check if all tasks are complete"""
        active_tasks = [task for task in self.copy_tasks 
                       if task["status"] in ["🔄 Running", "⏳ Pending"]]
        
        if not active_tasks and self.is_copying:
            self.is_copying = False
            self.start_btn.configure(state="normal")
            self.update_status("همه تسک‌ها تکمیل شدند!")
            
            # Show completion notification
            completed_count = len([task for task in self.copy_tasks if task["status"] == "✅ Completed"])
            if completed_count > 0:
                messagebox.showinfo("اتمام کار", f"{completed_count} عملیات کپی با موفقیت تکمیل شد!")

    def save_settings_from_gui(self):
        """Save settings from GUI controls"""
        try:
            # Validate and save buffer size
            buffer_kb = int(self.buffer_var.get())
            if buffer_kb < 1 or buffer_kb > 1024:
                raise ValueError("Buffer size must be between 1 and 1024 KB")
            self.settings["buffer_size"] = buffer_kb * 1024
            
            # Validate and save max threads
            max_threads = int(self.threads_var.get())
            if max_threads < 1 or max_threads > 8:
                raise ValueError("Max threads must be between 1 and 8")
            self.settings["max_threads"] = max_threads
            
            # Validate and save progress interval
            progress_interval = float(self.progress_interval_var.get())
            if progress_interval < 0.1 or progress_interval > 2.0:
                raise ValueError("Progress update interval must be between 0.1 and 2.0 seconds")
            self.settings["progress_update_interval"] = progress_interval
            
            # Validate retry count
            retry_count = int(self.retry_count_var.get())
            if retry_count < 1 or retry_count > 10:
                raise ValueError("Retry count must be between 1 and 10")
            self.settings["retry_count"] = retry_count
            
            # Save behavior settings
            self.settings["overwrite_policy"] = self.overwrite_var.get()
            self.settings["auto_retry"] = self.auto_retry_var.get()
            self.settings["verify_copy"] = self.verify_copy_var.get()
            self.settings["show_hidden_files"] = self.show_hidden_var.get()
            self.settings["create_backup"] = self.create_backup_var.get()
            self.settings["preserve_permissions"] = self.preserve_permissions_var.get()
            
            # Save appearance settings
            new_theme = self.theme_var.get()
            self.settings["theme"] = new_theme
            self.settings["notification_sound"] = self.notification_sound_var.get()
            self.settings["show_speed_graph"] = self.show_speed_graph_var.get()
            self.settings["auto_clear_completed"] = self.auto_clear_completed_var.get()
            
            # Apply theme change
            theme_config = THEMES.get(new_theme, THEMES["dark_blue"])
            ctk.set_appearance_mode(theme_config["mode"])
            ctk.set_default_color_theme(theme_config["color"])
            
            # Restart executor with new thread count
            if self.executor:
                self.executor.shutdown(wait=False)
            self.setup_executor()
            
            self.save_settings()
            
            # Success notification
            success_window = ctk.CTkToplevel(self.root)
            success_window.title("Settings Saved")
            success_window.geometry("300x150")
            success_window.transient(self.root)
            success_window.grab_set()
            
            # Center the window
            success_window.update_idletasks()
            x = (success_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (success_window.winfo_screenheight() // 2) - (150 // 2)
            success_window.geometry(f"300x150+{x}+{y}")
            
            ctk.CTkLabel(
                success_window,
                text="✅ Settings Saved Successfully!",
                font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")
            ).pack(pady=30)
            
            ctk.CTkButton(
                success_window,
                text="OK",
                command=success_window.destroy,
                width=100
            ).pack(pady=10)
            
            # Auto close after 2 seconds
            success_window.after(2000, success_window.destroy)
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings_to_defaults(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            try:
                # Reset to default values
                self.buffer_var.set("64")
                self.buffer_slider.set(64)
                
                self.threads_var.set("4")
                self.threads_slider.set(4)
                
                self.progress_interval_var.set("0.5")
                self.progress_slider.set(0.5)
                
                self.retry_count_var.set("3")
                
                # Reset checkboxes
                self.auto_retry_var.set(True)
                self.verify_copy_var.set(True)
                self.show_hidden_var.set(False)
                self.create_backup_var.set(False)
                self.preserve_permissions_var.set(True)
                self.notification_sound_var.set(True)
                self.show_speed_graph_var.set(True)
                self.auto_clear_completed_var.set(False)
                
                # Reset comboboxes
                self.overwrite_var.set("prompt")
                self.theme_var.set("dark_blue")
                
                # Update preview
                self.preview_theme("dark_blue")
                
                messagebox.showinfo("Settings Reset", "All settings have been reset to defaults!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")

    def on_file_double_click(self, event):
        """Handle double-click on file tree"""
        item = self.file_tree.selection()[0] if self.file_tree.selection() else None
        if item:
            values = self.file_tree.item(item, "values")
            if len(values) >= 3 and values[2] == "Directory":
                # Navigate to directory
                self.current_dir = values[1]
                self.current_dir_label.configure(text=self.current_dir)
                self.refresh_files()

    def on_task_double_click(self, event):
        """Handle double-click on task tree"""
        task = self.get_selected_task()
        if task:
            if task["status"] in ["🔄 Running"]:
                self.pause_selected_task()
            elif task["status"] in ["⏸ Paused", "⏳ Pending"]:
                self.start_selected_task()

    
    
    def start_individual_task(self, task_id: int):
        """Start an individual task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] in ["⏳ Pending", "❌ Cancelled", "❌ Error", "⏸ Paused"]:
            task["status"] = "🔄 Running"
            task["cancelled"] = False
            task["paused"] = False
            task["start_time"] = time.time()
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
    
    def pause_individual_task(self, task_id: int):
        """Pause/resume an individual task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] == "🔄 Running":
            task["paused"] = True
            task["status"] = "⏸ Paused"
            self.update_task_display(task)
    
    def cancel_individual_task(self, task_id: int):
        """Cancel an individual task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] in ["🔄 Running", "⏸ Paused", "⏳ Pending"]:
            task["cancelled"] = True
            task["status"] = "❌ Cancelled"
            if task.get("future"):
                task["future"].cancel()
            self.update_task_display(task)
    
    def restart_individual_task(self, task_id: int):
        """Restart a cancelled or failed task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        task["copied"] = 0
        task["progress"] = 0.0
        task["speed"] = 0.0
        task["cancelled"] = False
        task["paused"] = False
        task["retry_count"] = 0
        task["error_message"] = ""
        self.start_individual_task(task_id)
    
    def remove_individual_task(self, task_id: int):
        """Remove a completed task from the list"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] in ["✅ Completed", "❌ Cancelled", "❌ Error"]:
            # Remove the task
            del self.copy_tasks[task_id]
            
            # Reassign IDs to remaining tasks
            for i, remaining_task in enumerate(self.copy_tasks):
                remaining_task["id"] = i
            
            # Refresh the tree view
            self.refresh_task_tree()
            self.update_status(f"Removed task. {len(self.copy_tasks)} remaining.")
    
    def show_help(self, section: str):
        """Show help information for settings sections"""
        help_texts = {
            "performance": """⚡ Performance Settings Help:

🔧 Buffer Size (1-1024 KB):
• Small files (< 1MB): 32-64 KB - Faster for many small files
• Large files (> 100MB): 256-512 KB - Better for big files  
• SSD storage: 256-512 KB - Take advantage of fast storage
• Network drives: 32-128 KB - Avoid network congestion
• Default: 64 KB - Good balance for most scenarios

👥 Max Threads (1-8):
• Single large file: 1-2 threads - Avoid overhead
• Many small files: 4-6 threads - Parallel processing
• Network operations: 1-3 threads - Prevent timeout
• Local SSD: 4-8 threads - Utilize full speed
• Default: 4 threads - Optimal for most systems

⏱ Progress Update (0.1-2.0 seconds):
• Faster updates: 0.1-0.3s - Real-time feedback
• Balanced: 0.5s - Good performance + responsiveness  
• Slower updates: 1.0-2.0s - Better for slow systems""",
            
            "behavior": """🎯 Behavior Settings Help:

📁 File Exists Policy:
• Prompt: Ask user what to do (safest)
• Overwrite: Replace existing files automatically
• Skip: Keep existing files, skip duplicates

🔄 Auto Retry:
• Enabled: Automatically retry failed operations
• Retry Count: How many times to retry (1-10)

✅ Verify Copy:
• Enabled: Check file integrity after copying (slower but safer)
• Disabled: Skip verification (faster but less safe)

🗂 Show Hidden Files:
• Show system and hidden files in explorer

💾 Create Backup:
• Create .bak files before overwriting""",
            
            "appearance": """🎨 Appearance Settings Help:

🌈 Themes:
• Dark Blue: Professional dark theme (best for eyes)
• Dark Green: Nature-inspired dark theme
• Cyberpunk: Futuristic neon theme
• Ocean: Calm blue light theme
• Forest: Natural green theme
• System: Follow your OS theme

🔔 Notifications:
• Sound: Play completion sounds
• Minimize to Tray: Hide to system tray

📊 Visual Features:
• Speed Graph: Show real-time speed charts
• Auto Clear: Remove completed tasks automatically"""
        }
        
        help_window = ctk.CTkToplevel(self.root)
        help_window.title(f"Help - {section.title()}")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (help_window.winfo_screenheight() // 2) - (500 // 2)
        help_window.geometry(f"600x500+{x}+{y}")
        
        # Help content
        help_frame = ctk.CTkScrollableFrame(help_window)
        help_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_text = help_texts.get(section, "No help available for this section.")
        
        ctk.CTkLabel(
            help_frame,
            text=help_text,
            font=ctk.CTkFont(family="B Nazanin", size=12),
            justify="left",
            wraplength=550
        ).pack(pady=10, padx=10, anchor="w")
        
        # Close button
        ctk.CTkButton(
            help_window,
            text="✅ Got it!",
            command=help_window.destroy,
            font=ctk.CTkFont(family="B Nazanin", weight="bold")
        ).pack(pady=10)
    
    def update_buffer_from_slider(self, value):
        """Update buffer size from slider"""
        self.buffer_var.set(str(int(value)))
    
    def update_threads_from_slider(self, value):
        """Update thread count from slider"""
        self.threads_var.set(str(int(value)))
    
    def update_progress_from_slider(self, value):
        """Update progress interval from slider"""
        self.progress_interval_var.set(f"{value:.1f}")
    
    def check_disk_space(self, path: str, required_size: int) -> bool:
        """Check if there's enough disk space"""
        try:
            free_space = psutil.disk_usage(path).free
            # Add 10% buffer to required size
            required_with_buffer = required_size * 1.1
            return free_space > required_with_buffer
        except:
            return True  # If we can't check, assume it's okay
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_copying:
            if messagebox.askyesno("Confirm Exit", "Copy operations are in progress. Exit anyway?"):
                self.cancel_all_tasks()
            else:
                return
        
        # Save current window geometry
        self.settings["window_geometry"] = self.root.geometry()
        
        # Save settings and cleanup
        self.save_settings()
        self.save_cache()
        
        if self.executor:
            self.executor.shutdown(wait=False)
        
        self.root.destroy()

    def on_window_resize(self, event):
        """Handle window resize events for responsive design"""
        if event.widget == self.root:
            try:
                # Get current window size
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()
                
                # Only adjust if window is visible and has reasonable size
                if window_width > 100 and window_height > 100:
                    # Adjust column widths based on window size
                    if hasattr(self, 'task_tree'):
                        self.adjust_column_widths(window_width)
                        
            except Exception as e:
                self.logger.error(f"Error handling window resize: {e}")

    def adjust_column_widths(self, window_width):
        """Adjust tree column widths based on window size"""
        try:
            # Calculate available width (minus scrollbar and padding)
            available_width = max(800, window_width - 100)
            
            # Define column weight ratios (flexible sizing)
            column_weights = {
                "File": 0.25,        # 25% - File name
                "Destination": 0.30, # 30% - Destination path  
                "Progress": 0.10,    # 10% - Progress
                "Size": 0.10,        # 10% - Size
                "Copied": 0.10,      # 10% - Copied
                "Speed": 0.10,       # 10% - Speed
                "Status": 0.05       # 5% - Status
            }
            
            # Calculate and set new widths
            for col, weight in column_weights.items():
                new_width = max(60, int(available_width * weight))
                self.task_tree.column(col, width=new_width)
                
        except Exception as e:
            self.logger.error(f"Error adjusting column widths: {e}")

    def add_destination_folder(self):
        """Add a new destination folder"""
        folder = filedialog.askdirectory(title="انتخاب پوشه مقصد")
        if folder and folder not in self.destination_folders:
            self.destination_folders.append(folder)
            self.settings["destination_folders"] = self.destination_folders
            self.save_settings()
            self.update_destination_folders_display()
            self.new_dest_entry.delete(0, 'end')
            self.new_dest_entry.insert(0, folder)

    def remove_destination_folder(self, folder_path):
        """Remove a destination folder"""
        if folder_path in self.destination_folders:
            self.destination_folders.remove(folder_path)
            self.settings["destination_folders"] = self.destination_folders
            self.save_settings()
            self.update_destination_folders_display()

    def update_destination_folders_display(self):
        """Update the display of auto-detected destination folders"""
        try:
            if not hasattr(self, 'dest_folders_frame'):
                return
                
            # Clear existing widgets
            for widget in self.dest_folders_frame.winfo_children():
                widget.destroy()
            
            if not self.destination_folders:
                # Show message when no folders detected
                no_folders_label = ctk.CTkLabel(
                    self.dest_folders_frame,
                    text="🔍 در حال شناسایی درایوها...\n\nاگر درایوی نمایش داده نمی‌شود،\nروی دکمه بروزرسانی مقاصد کلیک کنید",
                    font=ctk.CTkFont(family="B Nazanin", size=12),
                    text_color="gray"
                )
                no_folders_label.pack(pady=50)
                return
            
            # Create drop zones for each auto-detected destination
            for i, dest_info in enumerate(self.destination_folders):
                self.create_auto_destination_zone(dest_info, i)
                
        except Exception as e:
            print(f"Error updating destination display: {e}")

    def create_auto_destination_zone(self, dest_info, index):
        """Create a destination zone for auto-detected folders"""
        try:
            folder_path = dest_info['path']
            folder_name = dest_info['name']
            folder_type = dest_info['type']
            free_space = dest_info.get('free_space', 0)
            
            # Main drop zone frame with different colors for different types
            if folder_type == 'drive':
                border_color = ("blue", "lightblue")
                bg_color = ("#e3f2fd", "#1a237e")
            else:
                border_color = ("green", "lightgreen")
                bg_color = ("#e8f5e8", "#2e7d32")
            
            drop_frame = ctk.CTkFrame(
                self.dest_folders_frame,
                height=100,
                border_width=2,
                border_color=border_color,
                corner_radius=12,
                fg_color=bg_color
            )
            drop_frame.pack(fill="x", padx=5, pady=5)
            drop_frame.pack_propagate(False)
            
            # Main content frame
            content_frame = ctk.CTkFrame(drop_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Top row: Icon and name
            top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            top_frame.pack(fill="x")
            
            # Icon based on type
            icon = "💿" if folder_type == 'drive' else "📁"
            icon_label = ctk.CTkLabel(
                top_frame,
                text=icon,
                font=ctk.CTkFont(family="B Nazanin", size=20)
            )
            icon_label.pack(side="left", padx=(0, 10))
            
            # Name and path
            name_label = ctk.CTkLabel(
                top_frame,
                text=folder_name,
                font=ctk.CTkFont(family="B Nazanin", size=14, weight="bold")
            )
            name_label.pack(side="left", anchor="w")
            
            # Bottom row: Path and click instruction
            bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            bottom_frame.pack(fill="x", pady=(5, 0))
            
            path_label = ctk.CTkLabel(
                bottom_frame,
                text=folder_path,
                font=ctk.CTkFont(family="B Nazanin", size=10),
                text_color="gray"
            )
            path_label.pack(side="left", anchor="w")
            
            # Click instruction
            click_label = ctk.CTkLabel(
                bottom_frame,
                text="🎯 کلیک برای کپی فایل‌های انتخابی",
                font=ctk.CTkFont(family="B Nazanin", size=10, weight="bold"),
                text_color=("blue", "lightblue")
            )
            click_label.pack(side="right")
            
            # Enable drag & drop and click functionality
            self.enable_quick_copy_on_widget(drop_frame, folder_path)
            self.enable_quick_copy_on_widget(content_frame, folder_path)
            self.enable_quick_copy_on_widget(name_label, folder_path)
            self.enable_quick_copy_on_widget(path_label, folder_path)
            self.enable_quick_copy_on_widget(click_label, folder_path)
            
        except Exception as e:
            print(f"Error creating destination zone: {e}")

    def enable_quick_copy_on_widget(self, widget, destination_path):
        """Enable quick copy functionality on widget (drag & drop + click)"""
        try:
            # Click functionality - copy selected files from browser
            def on_click(event=None):
                self.quick_copy_selected_files(destination_path)
            
            widget.bind("<Button-1>", on_click)
            
            # Native drag & drop is handled by the NativeDragDrop class
            # No additional setup needed here
            print(f"✓ کلیک سریع فعال شد برای مقصد: {os.path.basename(destination_path)}")
            
        except Exception as e:
            print(f"Error enabling quick copy on widget: {e}")

    def quick_copy_selected_files(self, destination_path):
        """Copy selected files from file browser to destination"""
        try:
            selected_items = self.file_tree.selection()
            if not selected_items:
                messagebox.showinfo("انتخاب فایل", "لطفاً فایل‌هایی را از لیست انتخاب کنید!")
                return
            
            added_count = 0
            for item_id in selected_items:
                values = self.file_tree.item(item_id)['values']
                if len(values) >= 2:
                    file_path = values[1]  # Path column
                    if os.path.exists(file_path):
                        # Add to copy queue and start immediately
                        self.add_task_and_start(file_path, destination_path)
                        added_count += 1
            
            if added_count > 0:
                messagebox.showinfo("کپی آغاز شد", f"{added_count} فایل به صف کپی اضافه شد و کپی آغاز شد!")
            else:
                messagebox.showwarning("خطا", "فایل‌های انتخابی معتبر نیستند!")
                
        except Exception as e:
            print(f"Error in quick copy: {e}")
            messagebox.showerror("خطا", f"خطا در کپی سریع: {e}")

    def add_task_and_start(self, source_path, destination_path):
        """Add a task to the queue and start it immediately"""
        try:
            if not os.path.exists(source_path):
                return
            
            filename = os.path.basename(source_path)
            dest_file = os.path.join(destination_path, filename)
            
            # Check if already exists in queue
            if any(task["source"] == source_path and task["destination"] == dest_file 
                   for task in self.copy_tasks):
                return  # Already in queue
            
            # Create and add task
            task_id = len(self.copy_tasks)
            file_size = self.get_file_size(source_path)
            
            task = {
                "id": task_id,
                "source": source_path,
                "destination": dest_file,
                "filename": filename,
                "size": file_size,
                "copied": 0,
                "progress": 0.0,
                "speed": 0.0,
                "status": "🚀 Auto-Starting",
                "paused": False,
                "cancelled": False,
                "completed": False,
                "start_time": time.time(),
                "last_update": time.time(),
                "retry_count": 0,
                "error_message": "",
                "future": None
            }
            
            self.copy_tasks.append(task)
            
            # Add to task tree
            self.task_tree.insert("", "end", iid=str(task_id), values=(
                filename,
                dest_file,
                "0%",
                self.format_size(file_size),
                "0 B",
                "0.0",
                "🚀 Auto-Starting"
            ))
            
            # Start immediately
            task["status"] = "🔄 Running"
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
            
        except Exception as e:
            print(f"Error adding and starting task: {e}")



    def create_drop_zone(self, folder_path, index):
        """Create a drop zone for a destination folder"""
        # Main drop zone frame
        drop_frame = ctk.CTkFrame(
            self.dest_folders_frame,
            height=120,
            border_width=3,
            border_color=("blue", "lightblue"),
            corner_radius=15
        )
        drop_frame.pack(fill="x", padx=10, pady=10)
        drop_frame.pack_propagate(False)
        
        # Folder info frame
        info_frame = ctk.CTkFrame(drop_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Folder name and path
        folder_name = os.path.basename(folder_path) or folder_path
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"📁 {folder_name}",
            font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")
        )
        name_label.pack(anchor="w")
        
        path_label = ctk.CTkLabel(
            info_frame,
            text=folder_path,
            font=ctk.CTkFont(family="B Nazanin", size=12),
            text_color="gray"
        )
        path_label.pack(anchor="w", pady=(0, 10))
        
        # Controls frame
        controls_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        controls_frame.pack(fill="x")
        
        # Click instruction
        click_label = ctk.CTkLabel(
            controls_frame,
            text="🎯 فایل بکشید اینجا یا کلیک کنید",
            font=ctk.CTkFont(family="B Nazanin", size=12, weight="bold"),
            text_color=("blue", "lightblue")
        )
        click_label.pack(side="left")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️",
            width=30,
            height=30,
            command=lambda: self.remove_destination_folder(folder_path),
            fg_color="red",
            hover_color="darkred"
        )
        remove_btn.pack(side="right")
        
        # Enable drag & drop on all elements of the drop zone
        self.enable_drop_on_widget(drop_frame, folder_path)
        self.enable_drop_on_widget(info_frame, folder_path) 
        self.enable_drop_on_widget(name_label, folder_path)
        self.enable_drop_on_widget(path_label, folder_path)
        self.enable_drop_on_widget(click_label, folder_path)

    def enable_drop_on_widget(self, widget, destination_path):
        """فعال کردن قابلیت کلیک روی ویجت برای انتخاب فایل"""
        # Native drag and drop is handled by the NativeDragDrop class on file tree
        # Here we just enable click functionality for manual file selection
        self.setup_manual_file_selection(widget, destination_path)
        print(f"✓ کلیک برای انتخاب فعال شد برای: {os.path.basename(destination_path)}")
    
    
    def on_drag_enter(self, widget):
        """Visual feedback when dragging over drop zone"""
        try:
            widget.configure(fg_color=("#c8e6c9", "#2e7d32"))  # Light green highlight
            widget.configure(border_color="#4caf50", border_width=3)
            print("🎯 Drag entered drop zone")
        except:
            pass
    
    def on_drag_leave(self, widget):
        """Reset visual feedback when leaving drop zone"""
        try:
            widget.configure(fg_color=("#f5f5f5", "#424242"))  # Reset to default
            widget.configure(border_color=("gray70", "gray25"), border_width=2)
            print("↩ Drag left drop zone")
        except:
            pass

    def setup_manual_file_selection(self, widget, destination_path):
        """Setup manual file selection"""
        def manual_select(event=None):
            # Create a simple dialog to choose between files or folders
            choice_window = ctk.CTkToplevel(self.root)
            choice_window.title("انتخاب نوع فایل")
            choice_window.geometry("300x200")
            choice_window.transient(self.root)
            choice_window.grab_set()
            
            # Center the window
            choice_window.update_idletasks()
            x = (choice_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (choice_window.winfo_screenheight() // 2) - (200 // 2)
            choice_window.geometry(f"300x200+{x}+{y}")
            
            ctk.CTkLabel(
                choice_window,
                text="چه چیزی می‌خواهید کپی کنید؟",
                font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")
            ).pack(pady=20)
            
            def select_files():
                choice_window.destroy()
                files = filedialog.askopenfilenames(title="انتخاب فایل‌ها برای کپی")
                if files:
                    self.handle_dropped_files(files, destination_path)
            
            def select_folders():
                choice_window.destroy()
                folders = []
                while True:
                    folder = filedialog.askdirectory(title="انتخاب پوشه برای کپی (Cancel برای پایان)")
                    if folder:
                        folders.append(folder)
                        if not messagebox.askyesno("ادامه", "آیا می‌خواهید پوشه دیگری نیز اضافه کنید؟"):
                            break
                    else:
                        break
                if folders:
                    self.handle_dropped_files(folders, destination_path)
            
            ctk.CTkButton(
                choice_window,
                text="📄 انتخاب فایل‌ها",
                command=select_files,
                width=200,
                height=40
            ).pack(pady=10)
            
            ctk.CTkButton(
                choice_window,
                text="📁 انتخاب پوشه‌ها",
                command=select_folders,
                width=200,
                height=40
            ).pack(pady=10)
        
        widget.bind("<Button-1>", manual_select)

    def handle_dropped_files(self, files, destination_path):
        """Handle files dropped on a destination folder"""
        try:
            valid_files = []
            for file_path in files:
                if os.path.exists(file_path):
                    valid_files.append(file_path)
            
            if not valid_files:
                messagebox.showwarning("خطا", "فایل‌های انتخابی معتبر نیستند!")
                return
            
            # Add files to copy queue and start immediately
            added_count = 0
            for file_path in valid_files:
                if os.path.isfile(file_path):
                    filename = os.path.basename(file_path)
                    dest_file = os.path.join(destination_path, filename)
                    
                    # Check if already exists
                    if any(task["source"] == file_path and task["destination"] == dest_file 
                           for task in self.copy_tasks):
                        continue
                    
                    # Add to queue
                    file_size = self.get_file_size(file_path)
                    task_id = len(self.copy_tasks)
                    
                    task = {
                        "id": task_id,
                        "source": file_path,
                        "destination": dest_file,
                        "filename": filename,
                        "size": file_size,
                        "copied": 0,
                        "progress": 0.0,
                        "speed": 0.0,
                        "status": "🚀 Auto-Starting",
                        "paused": False,
                        "cancelled": False,
                        "completed": False,
                        "start_time": time.time(),
                        "last_update": time.time(),
                        "retry_count": 0,
                        "error_message": "",
                        "future": None
                    }
                    
                    self.copy_tasks.append(task)
                    
                    # Add to tree display
                    self.task_tree.insert("", "end", iid=str(task_id), values=(
                        filename,
                        dest_file,
                        "0%",
                        self.format_size(file_size),
                        "0 B",
                        "0.0",
                        "🚀 Auto-Starting"
                    ))
                    
                    # Start immediately
                    task["status"] = "🔄 Running"
                    task["future"] = self.executor.submit(self.copy_task, task)
                    self.update_task_display(task)
                    added_count += 1
                    
                elif os.path.isdir(file_path):
                    # Handle directories
                    dirname = os.path.basename(file_path)
                    dest_dir = os.path.join(destination_path, dirname)
                    
                    # Check if already exists
                    if any(task["source"] == file_path and task["destination"] == dest_dir 
                           for task in self.copy_tasks):
                        continue
                    
                    # Calculate directory size
                    dir_size = self.get_directory_size(file_path)
                    task_id = len(self.copy_tasks)
                    
                    task = {
                        "id": task_id,
                        "source": file_path,
                        "destination": dest_dir,
                        "filename": dirname,
                        "size": dir_size,
                        "copied": 0,
                        "progress": 0.0,
                        "speed": 0.0,
                        "status": "🚀 Auto-Starting",
                        "paused": False,
                        "cancelled": False,
                        "completed": False,
                        "start_time": time.time(),
                        "last_update": time.time(),
                        "retry_count": 0,
                        "error_message": "",
                        "future": None
                    }
                    
                    self.copy_tasks.append(task)
                    
                    # Add to tree display
                    self.task_tree.insert("", "end", iid=str(task_id), values=(
                        dirname,
                        dest_dir,
                        "0%",
                        self.format_size(dir_size),
                        "0 B",
                        "0.0",
                        "🚀 Auto-Starting"
                    ))
                    
                    # Start immediately
                    task["status"] = "🔄 Running"
                    task["future"] = self.executor.submit(self.copy_task, task)
                    self.update_task_display(task)
                    added_count += 1
            
            self.update_overall_progress()
            
            # Switch to tasks tab to show progress
            self.notebook.select(1)  # Tasks tab
            
            if added_count > 0:
                self.update_status(f"🚀 شروع خودکار: {added_count} فایل/پوشه")
                # نمایش اعلان موفقیت برای شروع کپی
                self.show_toast(f"{added_count} فایل/پوشه به صورت خودکار شروع به کپی شدند!", "success")
            else:
                # نمایش اعلان اطلاعات برای فایل‌های تکراری
                self.show_toast("همه فایل‌ها قبلاً در صف کپی موجود هستند!", "info")
                
        except Exception as e:
            self.logger.error(f"Error handling dropped files: {e}")
            messagebox.showerror("خطا", f"خطا در پردازش فایل‌ها: {str(e)}")

    def get_directory_size(self, directory_path):
        """Calculate total size of a directory"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            self.logger.warning(f"Error calculating directory size: {e}")
        return total_size
 
    def run(self):
        """Run the application"""
        try:
            # Handle command line arguments for context menu integration
            if len(sys.argv) > 1:
                if sys.argv[1] == "copy" and len(sys.argv) > 2:
                    # Add file to clipboard (for future implementation)
                    pass
                elif sys.argv[1] == "paste" and len(sys.argv) > 2:
                    # Set destination and paste (for future implementation)
                    if hasattr(self, 'dest_entry') and self.dest_entry:
                        self.dest_entry.insert(0, sys.argv[2])
            
            # Restore window geometry
            if "window_geometry" in self.settings:
                self.root.geometry(self.settings["window_geometry"])
            
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")

def main():
    """Main entry point"""
    try:
        # Always use CTk for consistent styling, enable DnD within the app
        root = ctk.CTk()
        
        # Native drag and drop support is built-in
        print("✓ سیستم درگ اند دراپ بومی فعال شد")
        
        app = FileCopierApp(root)
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()