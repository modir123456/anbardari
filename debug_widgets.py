#!/usr/bin/env python3
"""
Debug script to check widget structure in Persian File Copier Pro
"""

import tkinter as tk
import customtkinter as ctk

def analyze_widget_structure():
    """Analyze CustomTkinter widget structure"""
    
    # Create test window
    root = ctk.CTk()
    root.title("Widget Structure Analysis")
    root.geometry("600x400")
    
    # Create a test frame similar to drop zones
    test_frame = ctk.CTkFrame(root, height=120, border_width=3)
    test_frame.pack(fill="x", padx=10, pady=10)
    
    # Create nested elements
    info_frame = ctk.CTkFrame(test_frame, fg_color="transparent")
    info_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    name_label = ctk.CTkLabel(info_frame, text="📁 Test Folder", font=ctk.CTkFont(size=16, weight="bold"))
    name_label.pack(anchor="w")
    
    path_label = ctk.CTkLabel(info_frame, text="/test/path", font=ctk.CTkFont(size=12))
    path_label.pack(anchor="w")
    
    def analyze_widget(widget, name="", level=0):
        """Recursively analyze widget structure"""
        indent = "  " * level
        print(f"{indent}{name}: {type(widget).__name__}")
        
        # Check for common CustomTkinter attributes
        attrs = ['_canvas', '_text_label', '_bg_canvas', 'master']
        for attr in attrs:
            if hasattr(widget, attr):
                attr_value = getattr(widget, attr)
                if attr_value and attr_value != widget:
                    print(f"{indent}  {attr}: {type(attr_value).__name__}")
        
        # Check children
        if hasattr(widget, 'winfo_children'):
            children = widget.winfo_children()
            if children:
                print(f"{indent}  children: {len(children)}")
                for i, child in enumerate(children):
                    analyze_widget(child, f"child_{i}", level + 1)
        
        print()
    
    print("=" * 50)
    print("Widget Structure Analysis")
    print("=" * 50)
    
    analyze_widget(test_frame, "test_frame")
    analyze_widget(info_frame, "info_frame")
    analyze_widget(name_label, "name_label")
    analyze_widget(path_label, "path_label")
    
    print("=" * 50)
    print("Analysis complete. Close window to exit.")
    
    root.mainloop()

if __name__ == "__main__":
    analyze_widget_structure()