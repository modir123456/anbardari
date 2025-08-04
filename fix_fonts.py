#!/usr/bin/env python3
"""
Script to fix all fonts in the application to use B Nazanin
"""

import re

def fix_fonts_in_file(filename):
    """Fix fonts in a specific file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace CTkFont patterns that don't have family="B Nazanin"
        patterns = [
            # CTkFont(size=X) -> CTkFont(family="B Nazanin", size=X)
            (r'CTkFont\(size=(\d+)\)', r'CTkFont(family="B Nazanin", size=\1)'),
            # CTkFont(size=X, weight="Y") -> CTkFont(family="B Nazanin", size=X, weight="Y")
            (r'CTkFont\(size=(\d+), weight="([^"]+)"\)', r'CTkFont(family="B Nazanin", size=\1, weight="\2")'),
            # CTkFont(weight="Y") -> CTkFont(family="B Nazanin", weight="Y")
            (r'CTkFont\(weight="([^"]+)"\)', r'CTkFont(family="B Nazanin", weight="\1")'),
        ]
        
        changes_made = 0
        for pattern, replacement in patterns:
            # Only replace if it doesn't already have family="B Nazanin"
            matches = re.findall(pattern, content)
            for match in matches:
                original_match = re.search(pattern, content)
                if original_match:
                    # Check if this match already has family="B Nazanin"
                    full_match = original_match.group(0)
                    if 'family="B Nazanin"' not in full_match:
                        content = re.sub(pattern, replacement, content, count=1)
                        changes_made += 1
        
        if changes_made > 0:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed {changes_made} fonts in {filename}")
        else:
            print(f"✓ No font changes needed in {filename}")
            
    except Exception as e:
        print(f"❌ Error fixing fonts in {filename}: {e}")

def main():
    files_to_fix = [
        'file_copier_app.py',
        'serial_generator.py'
    ]
    
    print("🔧 Fixing fonts to use B Nazanin...")
    
    for filename in files_to_fix:
        fix_fonts_in_file(filename)
    
    print("✅ Font fixing completed!")

if __name__ == "__main__":
    main()