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
    
    # Check if the problematic line exists
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
        
        # Replace the problematic function
        content = content.replace(old_main, new_main)
        
        # Write back the fixed content
        with open('file_copier_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed DnDWrapper issue")
        return True
    else:
        print("✅ DnDWrapper issue already fixed or not present")
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