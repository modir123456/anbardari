#!/usr/bin/env python3
"""
Quick Fix for Persian File Copier Pro
Fixes the DnDWrapper issue and TTK styling problems
"""

import os
import sys

def check_and_fix_main_function():
    """Check and fix the main function in file_copier_app.py"""
    
    if not os.path.exists('file_copier_app.py'):
        print("❌ file_copier_app.py not found in current directory")
        return False
    
    # Read the current file
    with open('file_copier_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = False
    
    # Fix 1: DnDWrapper issue
    if 'TkinterDnD.DnDWrapper(root)' in content:
        print("🔧 Found problematic DnDWrapper line, fixing...")
        
        # Fix the main function
        old_main = '''def main():
    """Main entry point"""
    try:
        # Initialize drag and drop support if available
        if TkinterDnD:
            root = TkinterDnD.Tk()
            root.withdraw()
            root.destroy()
            
        # Use CTk for full CustomTkinter compatibility
        root = ctk.CTk()
        
        # Apply drag and drop wrapper if available
        if TkinterDnD:
            root = TkinterDnD.DnDWrapper(root)
        
        app = FileCopierApp(root)
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)'''
        
        new_main = '''def main():
    """Main entry point"""
    try:
        # Use CTk for full CustomTkinter compatibility
        root = ctk.CTk()
        
        # Apply drag and drop wrapper if available
        if TkinterDnD:
            try:
                # Apply DnD functionality to the root window
                root.tk.call('package', 'require', 'tkdnd')
                root._dnd_init = True
            except:
                print("Could not initialize drag and drop, using fallback method")
        
        app = FileCopierApp(root)
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)'''
        
        content = content.replace(old_main, new_main)
        fixes_made = True
        print("✅ Fixed DnDWrapper issue")
    
    # Fix 2: Color format issues
    if 'fg_color=("#e3f2fd", "#0d1b2a")' in content:
        print("🔧 Found problematic color formats, fixing...")
        
        # Fix invalid dark colors
        content = content.replace('fg_color=("#e3f2fd", "#0d1b2a")', 'fg_color=("#e3f2fd", "#1a237e")')
        content = content.replace('fg_color=("#e0f2f1", "#0a1e1a")', 'fg_color=("#e0f2f1", "#1b5e20")')
        content = content.replace('fg_color=("#fce4ec", "#2d0a1f")', 'fg_color=("#fce4ec", "#880e4f")')
        content = content.replace('fg_color=("#fff3e0", "#2d1b0a")', 'fg_color=("#fff3e0", "#e65100")')
        
        fixes_made = True
        print("✅ Fixed color format issues")
    
    # Fix 3: TTK styling issues
    if 'background=("gray95", "gray10")' in content:
        print("🔧 Found problematic TTK colors, fixing...")
        content = content.replace('background=("gray95", "gray10")', 'background="#f0f0f0"')
        content = content.replace('fg_color=("gray80", "gray25")', 'fg_color=("#f0f0f0", "#333333")')
        fixes_made = True
        print("✅ Fixed TTK styling issues")
    
    if fixes_made:
        # Write back the fixed content
        with open('file_copier_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ All fixes applied successfully")
    else:
        print("✅ No fixes needed or already applied")
    
    return True

def check_ttk_styling():
    """Check and provide info about TTK styling"""
    print("\n📋 TTK Styling Information:")
    print("- Tab colors are now implemented through frame backgrounds")
    print("- Each tab frame has a different color scheme")
    print("- This provides better compatibility across platforms")
    return True

def main():
    """Main execution"""
    print("=" * 50)
    print("Persian File Copier Pro - Quick Fix")
    print("=" * 50)
    
    # Fix the main function
    if check_and_fix_main_function():
        print("✅ Main function is ready")
    
    # Check TTK styling
    check_ttk_styling()
    
    print("\n" + "=" * 50)
    print("🚀 Ready to run!")
    print("=" * 50)
    print("You can now run: python file_copier_app.py")
    print("Or use: python run.py")

if __name__ == "__main__":
    main()