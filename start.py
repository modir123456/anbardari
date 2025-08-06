#!/usr/bin/env python3
"""
Persian File Copier Pro - Ultimate Launcher
🚀 تک فایل اجرای برنامه
شرکت فناوری نوآوران مثبت سبز
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
from config import *

def print_header():
    """نمایش هدر برنامه"""
    print("=" * 60)
    print(f"🌟 {APP_NAME}")
    print(f"📦 نسخه {APP_VERSION} - {APP_EDITION}")
    print(f"🏢 {COMPANY_NAME}")
    print(f"📞 تلگرام: {TELEGRAM_ID}")
    print("=" * 60)

def install_dependencies():
    """نصب وابستگی‌های Python"""
    print("📦 نصب وابستگی‌های مورد نیاز...")
    
    required_packages = [
        "fastapi",
        "uvicorn[standard]",
        "websockets", 
        "pydantic",
        "psutil",
        "aiofiles",
        "python-multipart"
    ]
    
    # Try to install packages that might be missing
    for package in required_packages:
        try:
            __import__(package.split('[')[0])
            print(f"   ✅ {package} موجود است")
        except ImportError:
            print(f"   📦 نصب {package}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package, "--break-system-packages", "--quiet"
                ], check=True, capture_output=True)
                print(f"   ✅ {package} نصب شد")
            except subprocess.CalledProcessError:
                try:
                    # Try without --break-system-packages
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package, "--quiet"
                    ], check=True, capture_output=True)
                    print(f"   ✅ {package} نصب شد")
                except subprocess.CalledProcessError as e:
                    print(f"   ❌ خطا در نصب {package}: {e}")
                    return False
    
    return True

def check_files():
    """بررسی وجود فایل‌های ضروری"""
    required_files = ["main.py", "config.py", "index.html"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ فایل‌های ضروری یافت نشدند: {', '.join(missing_files)}")
        return False
    
    print("✅ همه فایل‌های ضروری موجودند")
    return True

def start_server():
    """راه‌اندازی سرور FastAPI"""
    print(f"🚀 راه‌اندازی سرور روی پورت {DEFAULT_PORT}...")
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(DEFAULT_PORT),
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ در حال راه‌اندازی سرور...")
        time.sleep(3)
        
        # Test if server is running
        try:
            import urllib.request
            test_url = f'http://localhost:{DEFAULT_PORT}/api/health'
            
            with urllib.request.urlopen(test_url, timeout=5) as response:
                if response.status == 200:
                    print("✅ سرور با موفقیت راه‌اندازی شد!")
                    return process
        except Exception as e:
            print(f"⚠️ تست سرور انجام نشد: {e}")
            # اما ادامه بده، ممکن است کار کند
            return process
            
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی سرور: {e}")
        return None

def open_browser():
    """باز کردن مرورگر"""
    url = f"http://localhost:{DEFAULT_PORT}"
    print(f"🌐 باز کردن مرورگر: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ مرورگر باز شد")
    except Exception as e:
        print(f"⚠️ خطا در باز کردن مرورگر: {e}")
        print(f"📋 لطفاً این آدرس را دستی باز کنید: {url}")

def show_running_info():
    """نمایش اطلاعات در حال اجرا"""
    print("\n" + "=" * 60)
    print("✅ Persian File Copier Pro در حال اجرا است!")
    print(f"🌐 آدرس اصلی: http://localhost:{DEFAULT_PORT}")
    print(f"📖 مستندات API: http://localhost:{DEFAULT_PORT}/docs")
    print("⏹️  برای توقف Ctrl+C را فشار دهید")
    print("=" * 60)

def cleanup_old_files():
    """پاک کردن فایل‌های قدیمی و اضافی"""
    old_files = [
        "web/index_pro.html",
        "backend/main.py", 
        "start_simple.py",
        "test_modern_ui.html",
        "README_MODERN.md",
        "run_modern.py"
    ]
    
    cleaned = 0
    for file_path in old_files:
        if Path(file_path).exists():
            try:
                if Path(file_path).is_file():
                    Path(file_path).unlink()
                    cleaned += 1
            except:
                pass
    
    if cleaned > 0:
        print(f"🧹 {cleaned} فایل قدیمی پاک شد")

def main():
    """تابع اصلی"""
    # پاک کردن صفحه (اختیاری)
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux/Mac
        os.system('clear')
    
    print_header()
    
    # پاک کردن فایل‌های اضافی
    cleanup_old_files()
    
    # بررسی فایل‌ها
    if not check_files():
        print("\n❌ فایل‌های ضروری موجود نیستند!")
        input("Enter را برای خروج فشار دهید...")
        sys.exit(1)
    
    # نصب وابستگی‌ها
    if not install_dependencies():
        print("\n❌ خطا در نصب وابستگی‌ها!")
        input("Enter را برای خروج فشار دهید...")
        sys.exit(1)
    
    # راه‌اندازی سرور
    server_process = start_server()
    if not server_process:
        print("\n❌ خطا در راه‌اندازی سرور!")
        input("Enter را برای خروج فشار دهید...")
        sys.exit(1)
    
    # نمایش اطلاعات
    show_running_info()
    
    # باز کردن مرورگر
    open_browser()
    
    try:
        print("\n📡 سرور در حال اجرا... برای توقف Ctrl+C فشار دهید")
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 در حال توقف...")
        server_process.terminate()
        
        try:
            server_process.wait(timeout=5)
            print("✅ سرور متوقف شد")
        except subprocess.TimeoutExpired:
            print("🔄 اجبار به توقف...")
            server_process.kill()
            print("✅ سرور به زور متوقف شد")
            
    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        print(f"\n🙏 از استفاده از {APP_NAME} متشکریم!")
        input("Enter را برای خروج فشار دهید...")

if __name__ == "__main__":
    main()