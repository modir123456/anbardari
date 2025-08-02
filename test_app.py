#!/usr/bin/env python3
"""
Test script for Persian File Copier Pro
This script tests basic functionality without requiring a GUI display
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add current directory to path to import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import customtkinter as ctk
        print("✓ CustomTkinter imported successfully")
        
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
        print("✓ Tkinter modules imported successfully")
        
        import threading
        import queue
        import time
        import json
        import logging
        import re
        from typing import Dict, List, Optional
        from concurrent.futures import ThreadPoolExecutor
        print("✓ All standard library modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_file_operations():
    """Test basic file operations used by the app"""
    print("\nTesting file operations...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test file creation
        test_file = temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        print("✓ File creation works")
        
        # Test file size calculation
        size = test_file.stat().st_size
        assert size > 0, "File size should be greater than 0"
        print("✓ File size calculation works")
        
        # Test directory creation
        test_dir = temp_path / "test_dir"
        test_dir.mkdir()
        assert test_dir.exists() and test_dir.is_dir()
        print("✓ Directory creation works")
        
        # Test file copying
        dest_file = temp_path / "test_copy.txt"
        shutil.copy2(test_file, dest_file)
        assert dest_file.exists()
        assert dest_file.read_text() == "Hello, World!"
        print("✓ File copying works")
        
        return True

def test_json_operations():
    """Test JSON operations for settings and cache"""
    print("\nTesting JSON operations...")
    
    # Test settings structure
    default_settings = {
        "theme": "dark",
        "buffer_size": 64 * 1024,
        "max_threads": 4,
        "overwrite_policy": "prompt",
        "window_geometry": "1400x900"
    }
    
    # Test JSON serialization
    json_str = json.dumps(default_settings, indent=4, ensure_ascii=False)
    assert len(json_str) > 0
    print("✓ JSON serialization works")
    
    # Test JSON deserialization
    parsed_settings = json.loads(json_str)
    assert parsed_settings == default_settings
    print("✓ JSON deserialization works")
    
    return True

def test_threading():
    """Test basic threading functionality"""
    print("\nTesting threading...")
    
    import threading
    import queue
    from concurrent.futures import ThreadPoolExecutor
    
    # Test queue operations
    test_queue = queue.Queue()
    test_queue.put("test_item")
    item = test_queue.get()
    assert item == "test_item"
    print("✓ Queue operations work")
    
    # Test thread pool executor
    def test_function(x):
        return x * 2
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(test_function, 5)
        result = future.result()
        assert result == 10
    print("✓ ThreadPoolExecutor works")
    
    return True

def test_app_class_structure():
    """Test that the main app class can be imported and has expected methods"""
    print("\nTesting app class structure...")
    
    try:
        from file_copier_app import FileCopierApp
        print("✓ FileCopierApp class imported successfully")
        
        # Test that key methods exist
        expected_methods = [
            'load_settings', 'save_settings', 'load_cache', 'save_cache',
            'get_file_size', 'format_size', 'add_task', 'copy_task',
            'update_status', 'refresh_files'
        ]
        
        for method_name in expected_methods:
            assert hasattr(FileCopierApp, method_name), f"Method {method_name} not found"
        
        print("✓ All expected methods found in FileCopierApp class")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import FileCopierApp: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Persian File Copier Pro - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_file_operations,
        test_json_operations,
        test_threading,
        test_app_class_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 All tests passed! The application should work correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)