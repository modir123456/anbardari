#!/usr/bin/env python3
"""
Persian File Copier Pro - Professional Web UI Launcher
Enhanced HTML/CSS/JavaScript frontend with Python backend
شرکت فناوری نوآئران مثبت سبز
"""

import os
import sys
import subprocess
import platform
import time

def check_python_version():
    """بررسی نسخه پایتون"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 یا بالاتر مورد نیاز است")
        print(f"نسخه فعلی: {platform.python_version()}")
        return False
    return True

def install_requirements():
    """نصب پکیج‌های مورد نیاز"""
    requirements_file = 'requirements_web_pro.txt'
    
    if not os.path.exists(requirements_file):
        print(f"❌ فایل {requirements_file} یافت نشد")
        return False
    
    try:
        print("📦 در حال نصب پکیج‌های مورد نیاز...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ همه پکیج‌ها با موفقیت نصب شدند")
            return True
        else:
            print(f"❌ خطا در نصب پکیج‌ها: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در اجرای pip: {e}")
        return False

def check_dependencies():
    """بررسی وجود پکیج‌های مورد نیاز"""
    required_packages = {
        'eel': 'Eel',
        'psutil': 'psutil', 
        'requests': 'requests',
        'PIL': 'Pillow',
        'watchdog': 'watchdog'
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (نصب نشده)")
            missing_packages.append(package_name)
    
    return missing_packages

def setup_web_directory():
    """بررسی و ایجاد ساختار پوشه web"""
    web_dir = 'web'
    
    required_dirs = [
        'web',
        'web/css',
        'web/js'
    ]
    
    required_files = [
        'web/index_pro.html',
        'web/css/styles_pro.css',
        'web/css/themes.css',
        'web/js/app_pro.js'
    ]
    
    # ایجاد پوشه‌های مورد نیاز
    for directory in required_dirs:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"📁 پوشه {directory} ایجاد شد")
            except Exception as e:
                print(f"❌ خطا در ایجاد پوشه {directory}: {e}")
                return False
    
    # بررسی فایل‌های مورد نیاز
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ فایل‌های زیر یافت نشدند:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ ساختار پوشه web صحیح است")
    return True

def check_port_availability(port=8080):
    """بررسی در دسترس بودن پورت"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️ پورت {port} در حال استفاده است")
            return False
        else:
            print(f"✅ پورت {port} آزاد است")
            return True
            
    except Exception as e:
        print(f"❌ خطا در بررسی پورت: {e}")
        return False

def show_startup_info():
    """نمایش اطلاعات راه‌اندازی"""
    print("\n" + "="*70)
    print("🌟 Persian File Copier Pro - Professional Web Edition")
    print("شرکت فناوری نوآئران مثبت سبز")
    print("="*70)
    print("📋 ویژگی‌های این نسخه:")
    print("   🗄️ ایندکس‌گذاری هوشمند با SQLite")
    print("   🔄 بروزرسانی real-time فایل‌ها")
    print("   📱 تشخیص خودکار گوشی‌ها و USB")
    print("   🎨 رابط کاربری مدرن HTML/CSS/JS")
    print("   ⚡ عملکرد بالا و responsive")
    print("   🔍 جستجوی پیشرفته و فیلترها")
    print("   📊 مدیریت تسک‌های همزمان")
    print("   🛡️ سیستم لایسنس امن")
    print("-"*70)

def main():
    """تابع اصلی"""
    show_startup_info()
    
    # بررسی نسخه پایتون
    if not check_python_version():
        input("\nEnter را برای خروج فشار دهید...")
        return 1
    
    print(f"✅ Python {platform.python_version()}")
    
    # بررسی پکیج‌های مورد نیاز
    print("\n🔍 بررسی پکیج‌های مورد نیاز...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n📦 پکیج‌های ناموجود: {', '.join(missing)}")
        response = input("آیا مایل به نصب آنها هستید؟ (y/n): ").lower().strip()
        
        if response in ['y', 'yes', 'بله', '']:
            if not install_requirements():
                input("\nEnter را برای خروج فشار دهید...")
                return 1
        else:
            print("❌ بدون پکیج‌های مورد نیاز امکان اجرا وجود ندارد")
            input("\nEnter را برای خروج فشار دهید...")
            return 1
    
    # بررسی ساختار پوشه web
    print("\n🌐 بررسی ساختار فایل‌های web...")
    if not setup_web_directory():
        print("❌ ساختار فایل‌های web ناقص است")
        input("\nEnter را برای خروج فشار دهید...")
        return 1
    
    # بررسی پورت
    print("\n🔌 بررسی پورت شبکه...")
    if not check_port_availability(8080):
        print("💡 در صورت مشکل، برنامه‌های دیگری که از پورت 8080 استفاده می‌کنند را ببندید")
    
    print("\n🚀 راه‌اندازی Persian File Copier Pro - Web Edition...")
    print("🌐 آدرس: http://localhost:8080")
    print("⏹️ برای خروج Ctrl+C را فشار دهید")
    print("-"*70)
    
    try:
        # وارد کردن و اجرای برنامه اصلی
        from web_app_pro import main as run_web_app
        run_web_app()
        
    except ImportError as e:
        print(f"❌ خطا در وارد کردن برنامه اصلی: {e}")
        print("💡 اطمینان حاصل کنید که فایل web_app_pro.py موجود است")
        input("\nEnter را برای خروج فشار دهید...")
        return 1
        
    except KeyboardInterrupt:
        print("\n\n👋 برنامه توسط کاربر بسته شد")
        print("💾 تمام داده‌ها ذخیره شدند")
        return 0
        
    except Exception as e:
        print(f"\n❌ خطا در اجرای برنامه: {e}")
        print("\n🔧 راه‌حل‌های ممکن:")
        print("   1. برنامه را مجدداً راه‌اندازی کنید")
        print("   2. مطمئن شوید همه فایل‌ها کامل هستند")
        print("   3. با پشتیبانی تماس بگیرید: @PersianFileSupport")
        input("\nEnter را برای خروج فشار دهید...")
        return 1

if __name__ == '__main__':
    sys.exit(main())