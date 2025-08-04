#!/usr/bin/env python3
"""
Script to create a simple application icon for Persian File Copier Pro
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a simple application icon"""
    
    # Create a 256x256 image with a gradient background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Create gradient background (blue to light blue)
    for y in range(size):
        r = int(30 + (100 * y / size))
        g = int(144 + (50 * y / size))
        b = int(255 - (50 * y / size))
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Draw a folder icon shape
    folder_color = (255, 215, 0, 255)  # Gold color
    
    # Main folder body
    folder_rect = [40, 80, 216, 200]
    draw.rounded_rectangle(folder_rect, radius=10, fill=folder_color)
    
    # Folder tab
    tab_rect = [40, 60, 120, 80]
    draw.rounded_rectangle(tab_rect, radius=5, fill=folder_color)
    
    # Add some files inside folder
    file_color = (255, 255, 255, 200)
    for i, y_pos in enumerate([100, 120, 140, 160]):
        file_rect = [60, y_pos, 190, y_pos + 15]
        draw.rounded_rectangle(file_rect, radius=3, fill=file_color)
    
    # Add Persian text "فایل" (File)
    try:
        # Try to use a font that supports Persian
        font_size = 24
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "فایل"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = 210
        
        # Draw text with shadow
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 128))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
    except Exception as e:
        print(f"Could not add Persian text: {e}")
        # Fallback to English
        text = "FILE"
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (size - text_width) // 2
        y = 210
        
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 128))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Save as PNG first
    image.save("app_icon.png", "PNG")
    print("✓ Created app_icon.png")
    
    # Create ICO file for Windows
    try:
        # Create multiple sizes for ICO
        sizes = [16, 32, 48, 64, 128, 256]
        icons = []
        
        for size in sizes:
            resized = image.resize((size, size), Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # Save as ICO
        icons[0].save("app_icon.ico", format='ICO', sizes=[(s, s) for s in sizes])
        print("✓ Created app_icon.ico")
        
    except Exception as e:
        print(f"Could not create ICO file: {e}")
        print("PNG icon created successfully")

if __name__ == "__main__":
    create_app_icon()