#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear

echo -e "${GREEN}"
echo "============================================"
echo " Persian File Copier Pro 3.5.0 - C# Edition"
echo " فارسی کاپیر فایل حرفه‌ای - نسخه C#"
echo "============================================"
echo -e "${NC}"

# Check if .NET is installed
if ! command -v dotnet &> /dev/null; then
    echo -e "${RED}❌ .NET is not installed!${NC}"
    echo -e "${YELLOW}Please install .NET 8.0 or later from: https://dotnet.microsoft.com/download${NC}"
    exit 1
fi

# Build the application if executable doesn't exist
if [ ! -f "PersianFileCopierPro" ]; then
    echo -e "${YELLOW}🔨 Building application...${NC}"
    dotnet publish -c Release -o . --self-contained false
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to build application!${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}🚀 Starting Persian File Copier Pro...${NC}"
echo ""
echo -e "${GREEN}🌐 Server will be available at: http://localhost:8548${NC}"
echo -e "${GREEN}📱 Open this URL in your web browser to access the application${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the application
if [ -f "PersianFileCopierPro" ]; then
    ./PersianFileCopierPro
else
    dotnet run
fi