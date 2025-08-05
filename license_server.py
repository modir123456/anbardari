#!/usr/bin/env python3
"""
Persian File Copier Pro - License Generator Server
Server ساده برای اجرای صفحه تولید لایسنس
شرکت فناوری نوآئران مثبت سبز
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

class LicenseHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler سفارشی برای سرو کردن فایل‌های HTML"""
    
    def end_headers(self):
        """اضافه کردن headers امنیتی"""
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        """Handle کردن درخواست‌های GET"""
        if self.path == '/':
            self.path = '/license_generator.html'
        elif self.path == '/license' or self.path == '/license/':
            self.path = '/license_generator.html'
        elif self.path == '/test' or self.path == '/test/':
            self.path = '/license_test.html'
        
        return super().do_GET()

def find_free_port(start_port=8080):
    """پیدا کردن پورت آزاد"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def main():
    """تابع اصلی برای اجرای سرور"""
    
    # تغییر directory به مکان اسکریپت
    script_dir = Path(__file__).parent
    web_dir = script_dir / 'web'
    
    # اگر پوشه web وجود دارد، به آن برویم
    if web_dir.exists():
        os.chdir(web_dir)
        print(f"📁 Changed directory to: {web_dir}")
    else:
        os.chdir(script_dir)
        print(f"📁 Changed directory to: {script_dir}")
    
    # پیدا کردن پورت آزاد
    port = find_free_port()
    if not port:
        print("❌ هیچ پورت آزادی پیدا نشد!")
        sys.exit(1)
    
    try:
        # ایجاد سرور
        with socketserver.TCPServer(("", port), LicenseHTTPRequestHandler) as httpd:
            server_url = f"http://localhost:{port}"
            
            print("🔑 Persian File Copier Pro - License Generator")
            print("=" * 50)
            print(f"🌐 Server started at: {server_url}")
            print(f"📂 Serving files from: {os.getcwd()}")
            print("=" * 50)
            print("🔗 URLs:")
            print(f"   📋 License Generator: {server_url}")
            print(f"   📋 Direct Access: {server_url}/license_generator.html")
            print("=" * 50)
            print("🚀 Opening browser automatically...")
            print("⏹️  Press Ctrl+C to stop the server")
            print()
            
            # باز کردن مرورگر
            try:
                webbrowser.open(server_url)
                print("✅ Browser opened successfully!")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"   Please manually open: {server_url}")
            
            print()
            print("🔄 Server is running... waiting for requests")
            print()
            
            # اجرای سرور
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n")
        print("🛑 Server stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()