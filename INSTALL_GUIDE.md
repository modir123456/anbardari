# 🚀 راهنمای نصب Persian File Copier Pro - Modern Version

## 📋 فایل‌های مورد نیاز

برای اجرای برنامه، فایل‌های زیر را در پوشه پروژه خود کپی کنید:

### 1. فایل‌های اصلی:
```
your_project/
├── start_simple.py           # اسکریپت اجرای ساده
├── test_modern_ui.html       # رابط کاربری مدرن
└── backend/
    ├── main.py              # FastAPI backend
    └── requirements.txt     # Dependencies
```

### 2. محتوای backend/main.py:
کپی کنید از `/workspace/backend/main.py`

### 3. محتوای backend/requirements.txt:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
psutil==5.9.6
aiofiles==23.2.1
python-multipart==0.0.6
```

### 4. محتوای test_modern_ui.html:
کپی کنید از `/workspace/test_modern_ui.html`

### 5. محتوای start_simple.py:
کپی کنید از `/workspace/start_simple.py`

## 🚀 نحوه اجرا

### Windows:
```powershell
# فعال کردن virtual environment (اختیاری)
.venv\Scripts\Activate.ps1

# اجرای برنامه
python start_simple.py
```

### Linux/Mac:
```bash
# فعال کردن virtual environment (اختیاری)
source .venv/bin/activate

# اجرای برنامه
python3 start_simple.py
```

## ✅ آنچه برنامه انجام می‌دهد:

1. **نصب خودکار dependencies** - نیازی به نصب دستی نیست
2. **شروع FastAPI backend** - روی پورت 8000
3. **باز کردن رابط کاربری** - در مرورگر
4. **تست سلامت سیستم** - اطمینان از کارکرد

## 🌐 دسترسی پس از اجرا:

- **رابط کاربری مدرن**: فایل HTML که خودکار باز می‌شود
- **API Backend**: http://localhost:8000
- **مستندات API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🔧 ویژگی‌ها:

✅ جستجوی فایل سریع
✅ کپی فایل با نمایش پیشرفت
✅ مدیریت تسک‌ها
✅ تنظیمات کامل
✅ تم تاریک/روشن
✅ رابط فارسی زیبا

## 🐛 عیب‌یابی:

### اگر پورت 8000 اشغال است:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### اگر dependencies نصب نمی‌شوند:
```bash
# آپدیت pip
python -m pip install --upgrade pip

# نصب دستی
pip install fastapi uvicorn websockets pydantic psutil
```

## 📞 پشتیبانی:

در صورت مشکل، مراجعه کنید به:
- مستندات: http://localhost:8000/docs (پس از اجرا)
- فایل‌های log در پوشه پروژه

---

**🎉 برنامه آماده استفاده است!**