#!/bin/bash

# Persian File Copier Pro - Linux/macOS Launcher
# فارسی کاپیر فایل حرفه‌ای

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${2}${1}${NC}\n"
}

print_header() {
    clear
    print_color "================================================================================================" "$CYAN"
    print_color "" "$NC"
    print_color "                    Persian File Copier Pro v3.5.0" "$GREEN"
    print_color "                       فارسی کاپیر فایل حرفه‌ای" "$GREEN"
    print_color "" "$NC"
    print_color "================================================================================================" "$CYAN"
    print_color "" "$NC"
}

# Check if running as root
check_permissions() {
    if [ "$EUID" -eq 0 ]; then
        print_color "[تحذیر] برنامه با دسترسی root اجرا می‌شود." "$YELLOW"
        print_color "" "$NC"
    fi
}

# Check Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_color "[خطا] پایتون نصب نیست!" "$RED"
            print_color "لطفاً پایتون 3.8+ نصب کنید:" "$RED"
            
            if [[ "$OSTYPE" == "darwin"* ]]; then
                print_color "macOS: brew install python3" "$YELLOW"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                print_color "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv" "$YELLOW"
                print_color "CentOS/RHEL: sudo yum install python3 python3-pip" "$YELLOW"
                print_color "Arch Linux: sudo pacman -S python python-pip" "$YELLOW"
            fi
            
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    print_color "[✓] پایتون موجود است" "$GREEN"
    $PYTHON_CMD --version
}

# Setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_color "" "$NC"
        print_color "[...] ایجاد محیط مجازی پایتون..." "$BLUE"
        $PYTHON_CMD -m venv venv
        if [ $? -ne 0 ]; then
            print_color "[خطا] ایجاد محیط مجازی ناموفق بود!" "$RED"
            print_color "اگر خطای 'ensurepip' می‌بینید، این دستور را اجرا کنید:" "$YELLOW"
            print_color "sudo apt install python3-venv  # Ubuntu/Debian" "$YELLOW"
            exit 1
        fi
        print_color "[✓] محیط مجازی ایجاد شد" "$GREEN"
    else
        print_color "[✓] محیط مجازی موجود است" "$GREEN"
    fi
}

# Activate virtual environment and install dependencies
setup_dependencies() {
    print_color "" "$NC"
    print_color "[...] فعال‌سازی محیط مجازی..." "$BLUE"
    source venv/bin/activate
    
    print_color "[...] به‌روزرسانی pip..." "$BLUE"
    pip install --upgrade pip --quiet
    
    print_color "[...] نصب وابستگی‌ها..." "$BLUE"
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        print_color "[خطا] نصب وابستگی‌ها ناموفق بود!" "$RED"
        exit 1
    fi
    
    print_color "[✓] همه وابستگی‌ها نصب شدند" "$GREEN"
}

# Open browser in app mode
open_browser() {
    local url="http://localhost:8548"
    
    # Wait for server to start
    sleep 3
    
    # Try different browsers in app mode
    if command -v google-chrome &> /dev/null; then
        print_color "[🌐] باز کردن با Google Chrome..." "$CYAN"
        google-chrome --app="$url" --new-window --window-size=1400,900 --window-position=100,50 &>/dev/null &
    elif command -v chromium-browser &> /dev/null; then
        print_color "[🌐] باز کردن با Chromium..." "$CYAN"
        chromium-browser --app="$url" --new-window --window-size=1400,900 --window-position=100,50 &>/dev/null &
    elif command -v firefox &> /dev/null; then
        print_color "[🌐] باز کردن با Firefox..." "$CYAN"
        firefox --new-window "$url" &>/dev/null &
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_color "[🌐] باز کردن با Safari..." "$CYAN"
        open -a Safari "$url"
    else
        print_color "[🌐] باز کردن با مرورگر پیش‌فرض..." "$CYAN"
        if command -v xdg-open &> /dev/null; then
            xdg-open "$url" &>/dev/null &
        fi
    fi
}

# Start the application
start_app() {
    print_color "" "$NC"
    print_color "================================================================================================" "$CYAN"
    print_color "" "$NC"
    print_color "[🚀] راه‌اندازی Persian File Copier Pro..." "$GREEN"
    print_color "" "$NC"
    print_color "[📡] سرور: http://localhost:8548" "$BLUE"
    print_color "[📖] مستندات: http://localhost:8548/docs" "$BLUE"
    print_color "[🔧] برای توقف: Ctrl+C در این ترمینال" "$YELLOW"
    print_color "" "$NC"
    print_color "================================================================================================" "$CYAN"
    print_color "" "$NC"
    
    # Start server and browser
    open_browser &
    
    # Activate venv and start Python server
    source venv/bin/activate
    $PYTHON_CMD main.py
}

# Main execution
main() {
    print_header
    check_permissions
    check_python
    setup_venv
    setup_dependencies
    start_app
}

# Run main function
main "$@"