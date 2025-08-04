# TkinterDnD Compatibility Fix

## ✅ Fixed: unknown option "-fg_color" Error

### Problem:
The application was trying to use `TkinterDnD.Tk()` as the root window, but then applying CustomTkinter configurations (`fg_color`) which are not supported by regular tkinter windows.

### Root Cause:
```python
# This created a regular tkinter window:
root = TkinterDnD.Tk()  

# But then we tried to use CTk options:
self.root.configure(fg_color=("gray95", "gray10"))  # ERROR!
```

Regular tkinter windows don't support CustomTkinter options like `fg_color`.

### Solution Applied:

#### 1. **Always Use CTk Root Window**
```python
def main():
    # Always use CTk for consistent styling
    root = ctk.CTk()
    
    # Try to enable drag and drop support on the CTk root
    if DRAG_DROP_AVAILABLE and TkinterDnD:
        try:
            root.tk.call('package', 'require', 'tkdnd')
            print("✓ سیستم درگ اند دراپ با TkinterDnD فعال شد")
        except Exception as e:
            print(f"⚠ خطا در فعال‌سازی درگ اند دراپ: {e}")
```

#### 2. **Smart Root Configuration**
```python
# Configure window - check if it's CTk or regular Tk
try:
    if isinstance(self.root, ctk.CTk):
        self.root.configure(fg_color=("gray95", "gray10"))
    else:
        # For TkinterDnD.Tk(), use regular tkinter configuration
        self.root.configure(bg='gray10')
except Exception as e:
    print(f"Warning: Could not configure root window: {e}")
```

#### 3. **Enhanced Widget DnD Registration**
```python
def enable_quick_copy_on_widget(self, widget, destination_path):
    if DRAG_DROP_AVAILABLE and DND_FILES:
        try:
            # Get the underlying tkinter widget for DnD registration
            tk_widget = widget
            if hasattr(widget, '_canvas') and widget._canvas:
                tk_widget = widget._canvas
            elif hasattr(widget, 'winfo_children'):
                children = widget.winfo_children()
                if children:
                    tk_widget = children[0]
            
            # Enable drag & drop on the tkinter widget
            tk_widget.drop_target_register(DND_FILES)
            tk_widget.dnd_bind('<<Drop>>', lambda e: self.handle_dropped_files_quick(e, destination_path))
            # ... etc
```

### Benefits of This Approach:

✅ **Consistent Styling**: Always uses CustomTkinter for modern UI  
✅ **Drag & Drop Support**: Enables DnD on CTk widgets by accessing underlying tkinter widgets  
✅ **Error Resilience**: Graceful fallback if DnD can't be enabled  
✅ **Best of Both Worlds**: Modern CTk styling + functional drag & drop  

### Key Changes Made:

1. **main() function**: Always creates `ctk.CTk()` root, enables DnD via `tkdnd` package
2. **setup_gui()**: Smart configuration based on root window type  
3. **enable_quick_copy_on_widget()**: Enhanced widget registration for DnD
4. **enable_drop_on_widget()**: Updated to use `DRAG_DROP_AVAILABLE` flag

### Result:
- ✅ Application starts without `fg_color` errors
- ✅ Modern CustomTkinter styling preserved
- ✅ Drag & drop functionality works properly
- ✅ Graceful fallback to click-based file selection if DnD fails

The application now successfully combines CustomTkinter's modern UI with TkinterDnD's drag & drop capabilities!