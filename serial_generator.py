#!/usr/bin/env python3
"""
Persian File Copier Pro - Serial Number Generator
For commercial license generation and management

Usage: python serial_generator.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import hashlib
import base64
import time
import json
import os
from datetime import datetime, timedelta
import csv

class SerialGenerator:
    def __init__(self):
        self.company_key = "PERSIANFILECOPIER2024"
        self.generated_serials = []
        self.load_existing_serials()
        
    def load_existing_serials(self):
        """Load existing serials from file"""
        try:
            if os.path.exists("generated_serials.json"):
                with open("generated_serials.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.generated_serials = data.get("serials", [])
        except Exception as e:
            print(f"Could not load existing serials: {e}")
            self.generated_serials = []
    
    def save_serials(self):
        """Save generated serials to file"""
        try:
            data = {
                "serials": self.generated_serials,
                "last_updated": datetime.now().isoformat()
            }
            with open("generated_serials.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save serials: {e}")
    
    def generate_serial(self, customer_name, customer_email, license_type="standard"):
        """Generate a unique serial number"""
        timestamp = str(int(time.time()))
        data = f"{customer_name}{customer_email}{timestamp}{license_type}{self.company_key}"
        hash_obj = hashlib.sha256(data.encode())
        serial = base64.b64encode(hash_obj.digest()).decode()[:20].upper()
        
        # Format serial number
        formatted_serial = f"PFC-{serial[:4]}-{serial[4:8]}-{serial[8:12]}-{serial[12:16]}"
        
        # Store serial information
        serial_info = {
            "serial": formatted_serial,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "license_type": license_type,
            "generated_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat() if license_type != "lifetime" else None,
            "status": "active"
        }
        
        self.generated_serials.append(serial_info)
        self.save_serials()
        
        return formatted_serial, serial_info

class SerialGeneratorGUI:
    def __init__(self):
        self.generator = SerialGenerator()
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI"""
        # Configure customtkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Main window
        self.root = ctk.CTk()
        self.root.title("Persian File Copier Pro - Serial Generator")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="🔑 مولد سریال نامبر", 
                                  font=ctk.CTkFont(family="B Nazanin", size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Customer information frame
        customer_frame = ctk.CTkFrame(main_frame)
        customer_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(customer_frame, text="اطلاعات مشتری", 
                    font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")).pack(pady=10)
        
        # Customer name
        name_frame = ctk.CTkFrame(customer_frame)
        name_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(name_frame, text="نام مشتری:", width=100).pack(side="right", padx=5)
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="نام کامل مشتری")
        self.name_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Customer email
        email_frame = ctk.CTkFrame(customer_frame)
        email_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(email_frame, text="ایمیل:", width=100).pack(side="right", padx=5)
        self.email_entry = ctk.CTkEntry(email_frame, placeholder_text="email@example.com")
        self.email_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # License type
        license_frame = ctk.CTkFrame(customer_frame)
        license_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(license_frame, text="نوع لایسنس:", width=100).pack(side="right", padx=5)
        self.license_type = ctk.CTkComboBox(license_frame, 
                                           values=["standard", "professional", "enterprise", "lifetime"])
        self.license_type.pack(side="left", fill="x", expand=True, padx=5)
        self.license_type.set("standard")
        
        # Generate button
        generate_btn = ctk.CTkButton(customer_frame, text="🔄 تولید سریال نامبر", 
                                   command=self.generate_serial, height=40,
                                   font=ctk.CTkFont(family="B Nazanin", size=14, weight="bold"))
        generate_btn.pack(pady=15)
        
        # Generated serial display
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(result_frame, text="سریال نامبر تولید شده", 
                    font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")).pack(pady=10)
        
        self.serial_display = ctk.CTkEntry(result_frame, height=40, 
                                          font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold"))
        self.serial_display.pack(fill="x", padx=10, pady=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(result_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(action_frame, text="📋 کپی سریال", 
                     command=self.copy_serial).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="💾 ذخیره در فایل", 
                     command=self.save_to_file).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📧 ارسال ایمیل", 
                     command=self.send_email).pack(side="left", padx=5)
        
        # Generated serials list
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(list_frame, text="سریال‌های تولید شده", 
                    font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")).pack(pady=10)
        
        # Treeview for serials
        tree_container = tk.Frame(list_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.serials_tree = ttk.Treeview(tree_container, 
                                        columns=("Serial", "Customer", "Email", "Type", "Date"),
                                        show="headings", height=8)
        
        # Configure columns
        self.serials_tree.heading("Serial", text="سریال نامبر")
        self.serials_tree.heading("Customer", text="مشتری") 
        self.serials_tree.heading("Email", text="ایمیل")
        self.serials_tree.heading("Type", text="نوع")
        self.serials_tree.heading("Date", text="تاریخ")
        
        self.serials_tree.column("Serial", width=200)
        self.serials_tree.column("Customer", width=150)
        self.serials_tree.column("Email", width=200)
        self.serials_tree.column("Type", width=100)
        self.serials_tree.column("Date", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.serials_tree.yview)
        self.serials_tree.configure(yscrollcommand=scrollbar.set)
        
        self.serials_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load existing serials
        self.refresh_serials_list()
        
        # Export buttons
        export_frame = ctk.CTkFrame(list_frame)
        export_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(export_frame, text="📊 خروجی Excel", 
                     command=self.export_to_csv).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="🔄 بروزرسانی لیست", 
                     command=self.refresh_serials_list).pack(side="left", padx=5)
        
    def generate_serial(self):
        """Generate a new serial number"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        license_type = self.license_type.get()
        
        if not name or not email:
            messagebox.showerror("خطا", "لطفاً نام و ایمیل مشتری را وارد کنید")
            return
        
        try:
            serial, info = self.generator.generate_serial(name, email, license_type)
            self.serial_display.delete(0, tk.END)
            self.serial_display.insert(0, serial)
            
            # Clear form
            self.name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            
            # Refresh list
            self.refresh_serials_list()
            
            messagebox.showinfo("موفقیت", f"سریال نامبر با موفقیت تولید شد:\n{serial}")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید سریال: {e}")
    
    def copy_serial(self):
        """Copy serial to clipboard"""
        serial = self.serial_display.get()
        if serial:
            self.root.clipboard_clear()
            self.root.clipboard_append(serial)
            messagebox.showinfo("موفقیت", "سریال نامبر در کلیپ‌بورد کپی شد")
        else:
            messagebox.showwarning("هشدار", "سریال نامبری برای کپی وجود ندارد")
    
    def save_to_file(self):
        """Save serial to a text file"""
        serial = self.serial_display.get()
        if not serial:
            messagebox.showwarning("هشدار", "سریال نامبری برای ذخیره وجود ندارد")
            return
        
        filename = filedialog.asksaveasfilename(
            title="ذخیره سریال نامبر",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Find the serial info
                serial_info = None
                for info in self.generator.generated_serials:
                    if info["serial"] == serial:
                        serial_info = info
                        break
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("Persian File Copier Pro - License Information\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Serial Number: {serial}\n")
                    if serial_info:
                        f.write(f"Customer: {serial_info['customer_name']}\n")
                        f.write(f"Email: {serial_info['customer_email']}\n")
                        f.write(f"License Type: {serial_info['license_type']}\n")
                        f.write(f"Generated Date: {serial_info['generated_date']}\n")
                        if serial_info.get('expiry_date'):
                            f.write(f"Expiry Date: {serial_info['expiry_date']}\n")
                    f.write("\nThank you for purchasing Persian File Copier Pro!\n")
                
                messagebox.showinfo("موفقیت", f"سریال نامبر در فایل ذخیره شد:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره فایل: {e}")
    
    def send_email(self):
        """Show email template"""
        serial = self.serial_display.get()
        if not serial:
            messagebox.showwarning("هشدار", "سریال نامبری برای ارسال وجود ندارد")
            return
        
        # Find serial info
        serial_info = None
        for info in self.generator.generated_serials:
            if info["serial"] == serial:
                serial_info = info
                break
        
        email_template = f"""Subject: Persian File Copier Pro - License Activation

Dear {serial_info['customer_name'] if serial_info else 'Customer'},

Thank you for purchasing Persian File Copier Pro!

Your license information:
Serial Number: {serial}
License Type: {serial_info['license_type'] if serial_info else 'Standard'}

To activate your software:
1. Open Persian File Copier Pro
2. Go to the License Activation dialog
3. Enter your serial number: {serial}
4. Click "Activate"

For support, contact us at:
Email: support@persianfile.ir
Phone: +98 21 1234 5678

Best regards,
Persian File Technology Team
"""
        
        # Show email template in a dialog
        email_dialog = ctk.CTkToplevel(self.root)
        email_dialog.title("قالب ایمیل")
        email_dialog.geometry("600x500")
        
        text_widget = tk.Text(email_dialog, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", email_template)
        
        ctk.CTkButton(email_dialog, text="بستن", 
                     command=email_dialog.destroy).pack(pady=10)
    
    def refresh_serials_list(self):
        """Refresh the serials list"""
        # Clear existing items
        for item in self.serials_tree.get_children():
            self.serials_tree.delete(item)
        
        # Add serials
        for serial_info in reversed(self.generator.generated_serials):  # Most recent first
            date_str = datetime.fromisoformat(serial_info['generated_date']).strftime("%Y-%m-%d")
            self.serials_tree.insert("", "end", values=(
                serial_info['serial'],
                serial_info['customer_name'],
                serial_info['customer_email'],
                serial_info['license_type'],
                date_str
            ))
    
    def export_to_csv(self):
        """Export serials to CSV file"""
        if not self.generator.generated_serials:
            messagebox.showwarning("هشدار", "هیچ سریال نامبری برای خروجی وجود ندارد")
            return
        
        filename = filedialog.asksaveasfilename(
            title="خروجی CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Serial", "Customer", "Email", "License Type", "Generated Date", "Expiry Date", "Status"])
                    
                    for serial_info in self.generator.generated_serials:
                        writer.writerow([
                            serial_info['serial'],
                            serial_info['customer_name'],
                            serial_info['customer_email'],
                            serial_info['license_type'],
                            serial_info['generated_date'],
                            serial_info.get('expiry_date', 'Lifetime'),
                            serial_info['status']
                        ])
                
                messagebox.showinfo("موفقیت", f"داده‌ها در فایل CSV ذخیره شد:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره CSV: {e}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SerialGeneratorGUI()
    app.run()