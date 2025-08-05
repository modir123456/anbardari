# 🚀 راهنمای سریع Persian File Copier Pro

## 📋 فهرست مطالب
- [اجرای سریع](#اجرای-سریع)
- [تولید لایسنس](#تولید-لایسنس)
- [ساخت فایل نصبی](#ساخت-فایل-نصبی)
- [مشکلات رایج](#مشکلات-رایج)

## 🚀 اجرای سریع

### نسخه عادی:
```bash
python3 run_web.py
```

### نسخه Pro:
```bash
python3 run_web_pro.py
```

## 🔑 تولید لایسنس

### روش 1: صفحه تولید لایسنس
```bash
python3 license_server.py
```
سپس به آدرس `http://localhost:8080` بروید

### روش 2: صفحه تست ساده
```bash
python3 license_server.py
```
سپس به آدرس `http://localhost:8080/test` بروید

### کلیدهای لایسنس معتبر:
- `PFC-PRO-2024-FULL`
- `PFC-PRO-UNLIMITED`
- `PERSIAN-FILE-COPIER-PRO`
- `PFC-PREMIUM-2024`

## 📦 ساخت فایل نصبی

### ساخت سریع:
```bash
# نصب وابستگی‌ها و ساخت
python3 quick_build.py advanced

# یا به صورت تعاملی
python3 quick_build.py
```

### ساخت کامل:
```bash
# شامل نصب‌کننده و نسخه قابل حمل
python3 build_installer.py
```

## 🔧 مشکلات رایج

### خطای import eel:
```bash
pip install eel psutil requests Pillow
```

### خطای win32api:
این خطا در Linux/Mac طبیعی است و برنامه کار می‌کند.

### لایسنس تولید نمی‌شود:
1. از صفحه تست استفاده کنید: `http://localhost:8080/test`
2. Console مرورگر را بررسی کنید (F12)
3. از دکمه "🧪 تست تولید" استفاده کنید

### PyInstaller نصب نیست:
```bash
pip install pyinstaller
```

## 📁 ساختار خروجی

### بعد از ساخت:
```
├── dist/                           # فایل‌های اجرایی
│   └── Persian_File_Copier_Pro.exe
├── installer/                      # نصب‌کننده‌ها
│   ├── Persian_File_Copier_Pro_Setup.exe    # Windows
│   ├── install.sh                          # Linux
│   ├── Portable/                           # نسخه قابل حمل
│   └── Persian_File_Copier_Pro_Portable.zip
└── build/                          # فایل‌های موقت
```

## 🆘 پشتیبانی

اگر مشکلی دارید:
1. فایل README.md کامل را بخوانید
2. صفحه تست را امتحان کنید
3. Console مرورگر را بررسی کنید
4. با تیم پشتیبانی تماس بگیرید

---
© 2024 شرکت فناوری نوآئران مثبت سبز