#!/usr/bin/env python3
"""
Persian File Copier Pro - License Generator
🔑 ابزار تولید لایسنس برای مدیران
شرکت فناوری نوآوران مثبت سبز
"""

import hashlib
import secrets
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from config import APP_NAME, APP_VERSION, COMPANY_NAME, TELEGRAM_ID

class LicenseGenerator:
    def __init__(self):
        self.licenses_file = Path("generated_licenses.json")
        self.load_existing_licenses()
    
    def load_existing_licenses(self):
        """Load previously generated licenses"""
        try:
            if self.licenses_file.exists():
                with open(self.licenses_file, 'r', encoding='utf-8') as f:
                    self.licenses = json.load(f)
            else:
                self.licenses = []
        except Exception:
            self.licenses = []
    
    def save_licenses(self):
        """Save licenses to file"""
        try:
            with open(self.licenses_file, 'w', encoding='utf-8') as f:
                json.dump(self.licenses, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطا در ذخیره لایسنس‌ها: {e}")
    
    def generate_license_key(self, license_type='pro', customer_name='', days=365):
        """Generate a professional license key"""
        # Generate unique components
        prefix = "PFC-PRO" if license_type == 'pro' else "PFC-STD"
        year = str(datetime.now().year)
        
        # Create unique identifier based on customer and time
        unique_data = f"{customer_name}-{time.time()}-{secrets.token_hex(4)}"
        unique_hash = hashlib.sha256(unique_data.encode()).hexdigest()[:8].upper()
        
        # Build license key
        license_core = f"{prefix}-{year}-{unique_hash}"
        
        # Generate checksum
        checksum = hashlib.md5(license_core.encode()).hexdigest()[:4].upper()
        final_key = f"{license_core}-{checksum}"
        
        return final_key
    
    def validate_license_key(self, license_key):
        """Validate license key format"""
        try:
            if not license_key or len(license_key) < 20:
                return False, "طول کلید نامعتبر"
            
            parts = license_key.split('-')
            if len(parts) < 4:
                return False, "فرمت کلید نامعتبر"
            
            # Check prefix
            if parts[0] not in ['PFC']:
                return False, "پیشوند نامعتبر"
            
            if parts[1] not in ['PRO', 'STD']:
                return False, "نوع لایسنس نامعتبر"
            
            # Verify checksum
            license_core = '-'.join(parts[:-1])
            expected_checksum = hashlib.md5(license_core.encode()).hexdigest()[:4].upper()
            
            if parts[-1].upper() != expected_checksum:
                return False, "کنترل‌سام نامعتبر"
            
            return True, "معتبر"
            
        except Exception as e:
            return False, f"خطا در اعتبارسنجی: {e}"
    
    def create_license(self, customer_name, customer_email="", license_type='pro', days=365, notes=""):
        """Create a complete license entry"""
        license_key = self.generate_license_key(license_type, customer_name, days)
        
        # Validate the generated key
        is_valid, message = self.validate_license_key(license_key)
        if not is_valid:
            raise Exception(f"خطا در تولید کلید: {message}")
        
        license_data = {
            'license_key': license_key,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'license_type': license_type,
            'generated_date': datetime.now().isoformat(),
            'expiry_date': (datetime.now() + timedelta(days=days)).isoformat(),
            'days_valid': days,
            'status': 'generated',
            'notes': notes,
            'generator_version': APP_VERSION,
            'checksum_verified': is_valid
        }
        
        # Add to licenses list
        self.licenses.append(license_data)
        self.save_licenses()
        
        return license_data
    
    def list_licenses(self, filter_type=None):
        """List all generated licenses"""
        filtered_licenses = self.licenses
        
        if filter_type:
            filtered_licenses = [l for l in self.licenses if l['license_type'] == filter_type]
        
        return filtered_licenses
    
    def search_license(self, search_term):
        """Search licenses by customer name, email, or key"""
        results = []
        search_term = search_term.lower()
        
        for license_data in self.licenses:
            if (search_term in license_data.get('customer_name', '').lower() or
                search_term in license_data.get('customer_email', '').lower() or
                search_term in license_data.get('license_key', '').lower()):
                results.append(license_data)
        
        return results
    
    def export_license_file(self, license_data, export_path=None):
        """Export license to a file"""
        if not export_path:
            safe_name = "".join(c for c in license_data['customer_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            export_path = f"license_{safe_name}_{license_data['license_key'][:12]}.json"
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, ensure_ascii=False, indent=2)
            return export_path
        except Exception as e:
            raise Exception(f"خطا در صادر کردن: {e}")

def print_header():
    """Print application header"""
    print("=" * 70)
    print(f"🔑 {APP_NAME} - ابزار تولید لایسنس")
    print(f"📦 نسخه {APP_VERSION}")
    print(f"🏢 {COMPANY_NAME}")
    print(f"📞 تلگرام: {TELEGRAM_ID}")
    print("=" * 70)

def print_license_info(license_data):
    """Print license information"""
    print("\n" + "📄 اطلاعات لایسنس:")
    print(f"   🔑 کلید لایسنس: {license_data['license_key']}")
    print(f"   👤 نام مشتری: {license_data['customer_name']}")
    print(f"   📧 ایمیل: {license_data.get('customer_email', 'ندارد')}")
    print(f"   📋 نوع: {'حرفه‌ای' if license_data['license_type'] == 'pro' else 'استاندارد'}")
    print(f"   📅 تاریخ تولید: {license_data['generated_date'][:10]}")
    print(f"   ⏰ تاریخ انقضا: {license_data['expiry_date'][:10]}")
    print(f"   📝 یادداشت: {license_data.get('notes', 'ندارد')}")

def main_menu():
    """Main interactive menu"""
    generator = LicenseGenerator()
    
    while True:
        print("\n" + "📋 منوی اصلی:")
        print("1. 🔑 تولید لایسنس جدید")
        print("2. 📝 لیست لایسنس‌ها")
        print("3. 🔍 جستجوی لایسنس")
        print("4. ✅ اعتبارسنجی لایسنس")
        print("5. 📤 صادر کردن لایسنس")
        print("6. ❌ خروج")
        
        choice = input("\n🎯 انتخاب شما (1-6): ").strip()
        
        if choice == '1':
            create_new_license(generator)
        elif choice == '2':
            list_all_licenses(generator)
        elif choice == '3':
            search_licenses(generator)
        elif choice == '4':
            validate_license(generator)
        elif choice == '5':
            export_license(generator)
        elif choice == '6':
            print("\n🙏 از استفاده از ابزار تولید لایسنس متشکریم!")
            break
        else:
            print("❌ انتخاب نامعتبر!")

def create_new_license(generator):
    """Create new license interactive"""
    print("\n" + "🔑 تولید لایسنس جدید:")
    
    customer_name = input("👤 نام مشتری: ").strip()
    if not customer_name:
        print("❌ نام مشتری ضروری است!")
        return
    
    customer_email = input("📧 ایمیل مشتری (اختیاری): ").strip()
    
    print("\n📋 نوع لایسنس:")
    print("1. حرفه‌ای (Pro) - تمام امکانات")
    print("2. استاندارد (Standard) - امکانات محدود")
    
    type_choice = input("انتخاب نوع (1-2): ").strip()
    license_type = 'pro' if type_choice == '1' else 'standard'
    
    try:
        days = int(input("📅 مدت اعتبار (روز) [365]: ").strip() or "365")
    except ValueError:
        days = 365
    
    notes = input("📝 یادداشت (اختیاری): ").strip()
    
    try:
        license_data = generator.create_license(
            customer_name=customer_name,
            customer_email=customer_email,
            license_type=license_type,
            days=days,
            notes=notes
        )
        
        print("\n✅ لایسنس با موفقیت تولید شد!")
        print_license_info(license_data)
        
        # Ask to export
        export_choice = input("\n📤 آیا می‌خواهید لایسنس را به فایل ذخیره کنید؟ (y/n): ").strip().lower()
        if export_choice in ['y', 'yes', 'بله']:
            try:
                exported_file = generator.export_license_file(license_data)
                print(f"✅ لایسنس در فایل {exported_file} ذخیره شد")
            except Exception as e:
                print(f"❌ خطا در ذخیره: {e}")
                
    except Exception as e:
        print(f"❌ خطا در تولید لایسنس: {e}")

def list_all_licenses(generator):
    """List all licenses"""
    licenses = generator.list_licenses()
    
    if not licenses:
        print("\n📭 هیچ لایسنسی تولید نشده است")
        return
    
    print(f"\n📝 لیست لایسنس‌ها ({len(licenses)} مورد):")
    print("-" * 80)
    
    for i, license_data in enumerate(licenses, 1):
        print(f"{i:2}. {license_data['license_key']} | {license_data['customer_name']} | {license_data['license_type']}")
    
    # Show details
    try:
        detail_choice = input(f"\n🔍 شماره لایسنس برای نمایش جزئیات (1-{len(licenses)}) یا Enter: ").strip()
        if detail_choice:
            index = int(detail_choice) - 1
            if 0 <= index < len(licenses):
                print_license_info(licenses[index])
    except ValueError:
        pass

def search_licenses(generator):
    """Search licenses"""
    search_term = input("\n🔍 جستجو (نام، ایمیل، یا کلید): ").strip()
    
    if not search_term:
        print("❌ عبارت جستجو ضروری است!")
        return
    
    results = generator.search_license(search_term)
    
    if not results:
        print("📭 نتیجه‌ای یافت نشد")
        return
    
    print(f"\n🎯 نتایج جستجو ({len(results)} مورد):")
    print("-" * 80)
    
    for i, license_data in enumerate(results, 1):
        print(f"{i}. {license_data['license_key']} - {license_data['customer_name']}")
        print(f"   📧 {license_data.get('customer_email', 'ندارد')} | {license_data['license_type']} | {license_data['generated_date'][:10]}")

def validate_license(generator):
    """Validate a license key"""
    license_key = input("\n🔑 کلید لایسنس: ").strip()
    
    if not license_key:
        print("❌ کلید لایسنس ضروری است!")
        return
    
    is_valid, message = generator.validate_license_key(license_key)
    
    if is_valid:
        print(f"✅ لایسنس معتبر است: {message}")
        
        # Check in generated licenses
        found = False
        for license_data in generator.licenses:
            if license_data['license_key'] == license_key:
                print("\n📄 جزئیات لایسنس:")
                print_license_info(license_data)
                found = True
                break
        
        if not found:
            print("⚠️ این لایسنس در دیتابیس محلی یافت نشد (ممکن است جای دیگر تولید شده باشد)")
    else:
        print(f"❌ لایسنس نامعتبر: {message}")

def export_license(generator):
    """Export license to file"""
    if not generator.licenses:
        print("\n📭 هیچ لایسنسی برای صادر کردن وجود ندارد")
        return
    
    print(f"\n📤 انتخاب لایسنس برای صادر کردن:")
    for i, license_data in enumerate(generator.licenses, 1):
        print(f"{i}. {license_data['customer_name']} - {license_data['license_key']}")
    
    try:
        choice = int(input(f"\nانتخاب (1-{len(generator.licenses)}): ").strip())
        if 1 <= choice <= len(generator.licenses):
            license_data = generator.licenses[choice - 1]
            
            export_path = input("📁 نام فایل (Enter برای نام پیش‌فرض): ").strip()
            if not export_path:
                export_path = None
            
            try:
                exported_file = generator.export_license_file(license_data, export_path)
                print(f"✅ لایسنس در فایل {exported_file} ذخیره شد")
            except Exception as e:
                print(f"❌ خطا در صادر کردن: {e}")
        else:
            print("❌ انتخاب نامعتبر!")
    except ValueError:
        print("❌ شماره نامعتبر!")

if __name__ == "__main__":
    print_header()
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n🛑 عملیات لغو شد")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
    
    print("\n" + "=" * 70)