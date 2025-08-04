#!/usr/bin/env python3
"""
Simple Drag & Drop Test for Persian File Copier Pro
Tests if tkinterdnd2 is working properly
"""

import tkinter as tk
from tkinter import messagebox
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("❌ tkinterdnd2 not available")

def test_drag_drop():
    """Test drag and drop functionality"""
    
    if not HAS_DND:
        messagebox.showerror("خطا", "tkinterdnd2 نصب نیست!\nاجرا کنید: pip install tkinterdnd2")
        return
    
    # Create test window
    root = TkinterDnD.Tk()
    root.title("Drag & Drop Test")
    root.geometry("400x300")
    
    # Create drop zone
    drop_frame = tk.Frame(root, bg="lightblue", relief="raised", bd=2)
    drop_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    label = tk.Label(
        drop_frame, 
        text="فایل‌ها را اینجا بکشید و رها کنید\nDrag files here and drop",
        bg="lightblue",
        font=("Arial", 14),
        justify="center"
    )
    label.pack(expand=True)
    
    def on_drop(event):
        """Handle drop event"""
        try:
            files = event.data.split()
            files = [f.strip('{}') for f in files]
            message = f"فایل‌های دریافت شده:\n" + "\n".join(files)
            messagebox.showinfo("موفق!", message)
            print(f"✓ Files dropped: {files}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در پردازش: {e}")
            print(f"❌ Drop error: {e}")
    
    def on_drag_enter(event):
        """Visual feedback on drag enter"""
        drop_frame.configure(bg="lightgreen")
        label.configure(bg="lightgreen", text="رها کنید!\nDrop here!")
        print("🎯 Drag entered")
    
    def on_drag_leave(event):
        """Reset visual feedback"""
        drop_frame.configure(bg="lightblue")
        label.configure(bg="lightblue", text="فایل‌ها را اینجا بکشید و رها کنید\nDrag files here and drop")
        print("↩ Drag left")
    
    # Register drag and drop
    try:
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', on_drop)
        drop_frame.dnd_bind('<<DragEnter>>', on_drag_enter)
        drop_frame.dnd_bind('<<DragLeave>>', on_drag_leave)
        
        label.drop_target_register(DND_FILES)
        label.dnd_bind('<<Drop>>', on_drop)
        label.dnd_bind('<<DragEnter>>', on_drag_enter)
        label.dnd_bind('<<DragLeave>>', on_drag_leave)
        
        print("✓ Drag and drop registered successfully")
        
        # Add instruction
        instruction = tk.Label(
            root, 
            text="اگر کار کرد، مشکل در Persian File Copier Pro است\nاگر کار نکرد، مشکل در tkinterdnd2 است",
            font=("Arial", 10),
            fg="red"
        )
        instruction.pack(pady=5)
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در فعال‌سازی drag & drop: {e}")
        print(f"❌ DnD registration error: {e}")

if __name__ == "__main__":
    test_drag_drop()