#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Enhanced Edition
تست خطای فونت در نسخه Enhanced
"""

def test_font_config():
    """تست تنظیمات فونت"""
    try:
        import customtkinter as ctk
        
        # ایجاد پنجره test
        root = ctk.CTk()
        root.title("Font Test")
        
        # تست تنظیم فونت مشابه enhanced app
        try:
            root.option_add("*Font", ("B Nazanin", 11))
            print("✅ B Nazanin font configured successfully")
        except Exception as e:
            print(f"⚠️ B Nazanin failed, using fallback: {e}")
            try:
                root.option_add("*Font", ("Tahoma", 11))
                print("✅ Tahoma fallback configured successfully")
            except Exception as e2:
                print(f"❌ Font configuration failed: {e2}")
                return False
        
        # تست ایجاد widget
        label = ctk.CTkLabel(root, text="Font Test - آزمایش فونت")
        label.pack(pady=20)
        
        print("✅ Widget created successfully")
        
        # بستن پنجره
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """تابع اصلی تست"""
    print("=" * 50)
    print("Enhanced Edition Font Test")
    print("تست فونت نسخه Enhanced")
    print("=" * 50)
    
    if test_font_config():
        print("\n✅ All tests passed! Enhanced app should work correctly.")
        print("✅ همه تست‌ها موفق! برنامه Enhanced باید درست کار کند.")
    else:
        print("\n❌ Tests failed! Check font configuration.")
        print("❌ تست‌ها ناموفق! تنظیمات فونت را بررسی کنید.")

if __name__ == "__main__":
    main()