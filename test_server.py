#!/usr/bin/env python3
"""
Simple test script for Persian File Copier Pro
"""

import requests
import json
import time

def test_server():
    base_url = "http://localhost:8548"
    
    print("🧪 Testing Persian File Copier Pro Server...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']} - Version: {data['version']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False
    
    # Test 2: Get Drives
    print("\n2. Testing Drive Detection...")
    try:
        response = requests.get(f"{base_url}/api/drives")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['drives'])} drives")
            for drive in data['drives']:
                print(f"   📁 {drive['path']} - {drive['name']}")
        else:
            print(f"❌ Drive Detection Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Drive Detection Error: {e}")
    
    # Test 3: Get Tasks
    print("\n3. Testing Task Management...")
    try:
        response = requests.get(f"{base_url}/api/tasks")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} tasks")
            for task_id, task in data['tasks'].items():
                print(f"   📋 {task['type']} - {task['status']} - {task['progress']}%")
        else:
            print(f"❌ Task Management Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Task Management Error: {e}")
    
    # Test 4: Get Stats
    print("\n4. Testing System Stats...")
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"✅ System Stats:")
            print(f"   📁 Files: {stats['total_files']}")
            print(f"   📂 Directories: {stats['total_directories']}")
            print(f"   💾 Total Size: {stats['total_size']} bytes")
            print(f"   💿 Drives: {stats['total_drives']}")
            print(f"   📋 Tasks: {stats['total_tasks']}")
        else:
            print(f"❌ Stats Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats Error: {e}")
    
    # Test 5: Create Test File and Copy
    print("\n5. Testing File Copy...")
    try:
        # Create test file
        import os
        test_dir = "/tmp/persian_test"
        test_file = f"{test_dir}/test_file.txt"
        
        os.makedirs(test_dir, exist_ok=True)
        with open(test_file, "w") as f:
            f.write("This is a test file for Persian File Copier Pro\n")
            f.write("تست نرم‌افزار کپی فایل فارسی\n")
        
        print(f"✅ Created test file: {test_file}")
        
        # Test copy
        copy_data = {
            "source_files": [test_file],
            "destination": f"{test_dir}/copied",
            "options": {
                "verify_copy": True,
                "preserve_timestamps": True,
                "create_destination": True
            }
        }
        
        response = requests.post(
            f"{base_url}/api/copy",
            headers={"Content-Type": "application/json"},
            json=copy_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Copy started: {data['task_id']}")
            
            # Wait a moment and check task status
            time.sleep(2)
            response = requests.get(f"{base_url}/api/tasks")
            if response.status_code == 200:
                tasks = response.json()['tasks']
                if data['task_id'] in tasks:
                    task = tasks[data['task_id']]
                    print(f"   📊 Status: {task['status']} - Progress: {task['progress']}%")
                    
                    # Check if file was actually copied
                    copied_file = f"{test_dir}/copied/test_file.txt"
                    if os.path.exists(copied_file):
                        print(f"✅ File successfully copied to: {copied_file}")
                        with open(copied_file, "r") as f:
                            content = f.read()
                            print(f"   📄 Content: {content.strip()}")
                    else:
                        print(f"❌ File not found at: {copied_file}")
                else:
                    print("❌ Task not found in task list")
            else:
                print("❌ Failed to get task status")
        else:
            print(f"❌ Copy Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Copy Test Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print(f"🌐 Server is running at: http://localhost:8548")
    print("📱 Open the URL in your browser to use the web interface")
    
    return True

if __name__ == "__main__":
    test_server()