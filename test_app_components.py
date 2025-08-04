#!/usr/bin/env python3
"""
Test script for Persian File Copier Pro components
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"❌ tkinter import failed: {e}")
        return False
    
    try:
        import customtkinter as ctk
        print("✓ customtkinter imported successfully")
    except ImportError as e:
        print(f"❌ customtkinter import failed: {e}")
        return False
    
    try:
        import psutil
        print("✓ psutil imported successfully")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✓ PIL imported successfully")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    try:
        import hashlib
        import base64
        import uuid
        print("✓ crypto modules imported successfully")
    except ImportError as e:
        print(f"❌ crypto modules import failed: {e}")
        return False
    
    return True

def test_license_manager():
    """Test the license manager functionality"""
    print("\n🔑 Testing License Manager...")
    
    try:
        # Import the classes from the main app
        sys.path.append('.')
        from file_copier_app import LicenseManager
        
        # Create license manager
        lm = LicenseManager()
        print("✓ LicenseManager created successfully")
        
        # Test serial generation
        serial = lm.generate_serial("Test User", "test@example.com")
        print(f"✓ Serial generated: {serial}")
        
        # Test validation
        is_valid = lm.validate_serial(serial)
        print(f"✓ Serial validation: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ License manager test failed: {e}")
        return False

def test_native_drag_drop():
    """Test the native drag drop implementation"""
    print("\n🖱️ Testing Native Drag Drop...")
    
    try:
        from file_copier_app import NativeDragDrop
        print("✓ NativeDragDrop class imported successfully")
        return True
    except Exception as e:
        print(f"❌ NativeDragDrop test failed: {e}")
        return False

def test_icon_creation():
    """Test if icon files exist"""
    print("\n🎨 Testing Icon Files...")
    
    if os.path.exists("app_icon.png"):
        print("✓ app_icon.png exists")
    else:
        print("❌ app_icon.png not found")
        return False
    
    if os.path.exists("app_icon.ico"):
        print("✓ app_icon.ico exists")
    else:
        print("❌ app_icon.ico not found")
        return False
    
    return True

def test_serial_generator():
    """Test the serial generator script"""
    print("\n🔢 Testing Serial Generator...")
    
    if os.path.exists("serial_generator.py"):
        print("✓ serial_generator.py exists")
        
        try:
            # Try to import the serial generator classes
            import importlib.util
            spec = importlib.util.spec_from_file_location("serial_generator", "serial_generator.py")
            serial_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(serial_module)
            
            # Test SerialGenerator class
            sg = serial_module.SerialGenerator()
            print("✓ SerialGenerator class works")
            
            return True
            
        except Exception as e:
            print(f"❌ Serial generator test failed: {e}")
            return False
    else:
        print("❌ serial_generator.py not found")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Persian File Copier Pro - Component Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("License Manager", test_license_manager),
        ("Native Drag Drop", test_native_drag_drop),
        ("Icon Creation", test_icon_creation),
        ("Serial Generator", test_serial_generator)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The application is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)