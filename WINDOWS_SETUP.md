# Persian File Copier Pro - راهنمای نصب روی Windows

## 🚀 نصب سریع

### روش 1: اجرای خودکار (توصیه شده)

1. **دانلود فایل‌ها**:
   - تمام فایل‌های پروژه را در یک پوشه قرار دهید
   - مطمئن شوید که Python روی سیستم نصب است

2. **اجرای فایل start_windows.bat**:
   ```cmd
   # روی فایل start_windows.bat دوبار کلیک کنید
   # یا در Command Prompt اجرا کنید:
   start_windows.bat
   ```

3. **دسترسی به نرم‌افزار**:
   - مرورگر را باز کنید
   - به آدرس `http://localhost:8548` بروید

### روش 2: نصب دستی

#### مرحله 1: نصب Python
```cmd
# بررسی نصب Python
python --version

# اگر نصب نیست، از https://python.org دانلود و نصب کنید
```

#### مرحله 2: ایجاد محیط مجازی
```cmd
# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی محیط مجازی
venv\Scripts\activate.bat
```

#### مرحله 3: نصب وابستگی‌ها
```cmd
# نصب پکیج‌های Windows
pip install pywin32 wmi

# نصب سایر وابستگی‌ها
pip install -r requirements.txt
```

#### مرحله 4: اجرای سرور
```cmd
# اجرای سرور
python main.py
```

## 🔧 عیب‌یابی مشکلات رایج

### مشکل 1: Python پیدا نمی‌شود
```cmd
# بررسی PATH
echo %PATH%

# اضافه کردن Python به PATH (در صورت نیاز)
set PATH=%PATH%;C:\Python39\
```

### مشکل 2: خطای pywin32
```cmd
# نصب مجدد pywin32
pip uninstall pywin32
pip install pywin32

# یا استفاده از pipwin
pip install pipwin
pipwin install pywin32
```

### مشکل 3: خطای WMI
```cmd
# نصب WMI
pip install WMI

# یا نصب دستی
pip install https://github.com/tjguk/wmi/archive/master.zip
```

### مشکل 4: پورت در حال استفاده
```cmd
# بررسی پورت‌های در حال استفاده
netstat -ano | findstr :8548

# کشتن پروسه (PID را از خروجی بالا بگیرید)
taskkill /PID <PID> /F
```

### مشکل 5: دسترسی فایل
```cmd
# اجرا به عنوان Administrator
# روی Command Prompt راست کلیک کنید
# "Run as administrator" را انتخاب کنید
```

## 🎯 تست عملکرد

### تست 1: بررسی سلامت سرور
```cmd
# در Command Prompt جدید
curl http://localhost:8548/api/health
```

### تست 2: اجرای تست خودکار
```cmd
# در محیط مجازی
python test_server.py
```

### تست 3: تست کپی فایل
```cmd
# ایجاد فایل تست
echo Test file content > test.txt

# تست کپی
curl -X POST http://localhost:8548/api/copy -H "Content-Type: application/json" -d "{\"source_files\": [\"test.txt\"], \"destination\": \"copied\"}"
```

## 📁 ساختار فایل‌ها

```
anbardari-commercial-premium-version/
├── main.py                    # فایل اصلی سرور
├── config.py                  # تنظیمات
├── index.html                 # رابط کاربری
├── requirements.txt           # وابستگی‌ها
├── start_windows.bat         # فایل اجرا برای Windows
├── test_server.py            # تست خودکار
├── WINDOWS_SETUP.md          # این فایل راهنما
└── venv/                     # محیط مجازی (پس از ایجاد)
```

## 🎨 قابلیت‌های ویژه Windows

### 1. تشخیص درایوهای Windows
- تشخیص درایوهای C:, D:, E: و غیره
- نمایش نام درایوها
- تشخیص نوع درایو (HDD, SSD, USB)

### 2. بهینه‌سازی برای Windows
- استفاده از WMI برای اطلاعات سیستم
- پشتیبانی از مسیرهای Windows
- تشخیص دستگاه‌های USB

### 3. رابط کاربری سازگار
- پشتیبانی از فونت‌های فارسی
- طراحی responsive
- سازگار با مرورگرهای Windows

## 🔧 تنظیمات پیشرفته

### تغییر پورت سرور
```python
# در فایل config.py
DEFAULT_PORT = 8080  # تغییر پورت
```

### تنظیم مسیر پیش‌فرض
```python
# در فایل main.py
DEFAULT_SCAN_PATH = "C:\\Users\\YourUsername\\Documents"
```

### تنظیم اندازه بافر
```python
# در فایل config.py
BUFFER_SIZES = {
    'windows_hdd': 1024 * 1024,  # 1MB for Windows HDD
    'windows_ssd': 4 * 1024 * 1024,  # 4MB for Windows SSD
}
```

## 🚀 راه‌اندازی سریع

### برای کاربران جدید:
1. فایل `start_windows.bat` را اجرا کنید
2. منتظر بمانید تا نصب کامل شود
3. مرورگر را باز کنید و به `http://localhost:8548` بروید

### برای توسعه‌دهندگان:
```cmd
# کلون پروژه
git clone <repository-url>
cd anbardari-commercial-premium-version

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای سرور
python main.py
```

## 📊 نظارت بر عملکرد

### لاگ‌ها
```cmd
# مشاهده لاگ‌ها
type persian_file_copier.log
```

### آمار سیستم
```cmd
# دریافت آمار
curl http://localhost:8548/api/stats
```

### وضعیت تسک‌ها
```cmd
# مشاهده تسک‌ها
curl http://localhost:8548/api/tasks
```

## 🎉 نتیجه‌گیری

نرم‌افزار Persian File Copier Pro حالا کاملاً سازگار با Windows است و تمام قابلیت‌های درخواستی را دارد:

✅ **نصب آسان**: فایل start_windows.bat برای نصب خودکار
✅ **سازگاری کامل**: پشتیبانی از تمام ویژگی‌های Windows
✅ **عملکرد بهینه**: بهینه‌سازی شده برای Windows
✅ **رابط کاربری**: طراحی سازگار با Windows
✅ **عیب‌یابی**: راهنمای کامل برای حل مشکلات

برای شروع، کافی است فایل `start_windows.bat` را اجرا کنید! 🚀