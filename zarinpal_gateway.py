import requests
import json
import hashlib
import uuid
from datetime import datetime
import webbrowser
import threading
import time
from urllib.parse import urlencode

class ZarinPalGateway:
    """کلاس مدیریت درگاه پرداخت زرین‌پال برای خرید خودکار لایسنس"""
    
    def __init__(self):
        # تنظیمات درگاه زرین‌پال (sandbox برای تست)
        self.merchant_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # کد پذیرنده
        self.sandbox_mode = True  # حالت تست
        
        if self.sandbox_mode:
            self.base_url = "https://sandbox.zarinpal.com"
            self.payment_gateway_url = "https://sandbox.zarinpal.com/pg/StartPay"
        else:
            self.base_url = "https://api.zarinpal.com"
            self.payment_gateway_url = "https://www.zarinpal.com/pg/StartPay"
        
        # قیمت‌های محصولات (به ریال)
        self.prices = {
            "personal": 5000000,    # 500,000 تومان = 5,000,000 ریال
            "commercial": 12000000, # 1,200,000 تومان = 12,000,000 ریال  
            "enterprise": 25000000  # 2,500,000 تومان = 25,000,000 ریال
        }
        
        # اطلاعات محصولات
        self.products = {
            "personal": {
                "name": "Persian File Copier Pro - نسخه شخصی",
                "description": "نسخه شخصی برای استفاده خانگی",
                "features": ["کپی نامحدود فایل", "پشتیبانی ایمیل", "بروزرسانی 1 ساله"]
            },
            "commercial": {
                "name": "Persian File Copier Pro - نسخه تجاری", 
                "description": "نسخه تجاری برای کسب و کار",
                "features": ["کپی نامحدود فایل", "پشتیبانی 24/7", "بروزرسانی مادام‌العمر", "امکانات پیشرفته"]
            },
            "enterprise": {
                "name": "Persian File Copier Pro - نسخه سازمانی",
                "description": "نسخه سازمانی برای شرکت‌ها",
                "features": ["کپی نامحدود فایل", "پشتیبانی اختصاصی", "مدیریت چند کاربره", "گزارش‌گیری پیشرفته"]
            }
        }

    def create_payment_request(self, product_type, customer_email, customer_name, callback_url):
        """ایجاد درخواست پرداخت در زرین‌پال"""
        try:
            if product_type not in self.prices:
                raise ValueError("نوع محصول نامعتبر است")
            
            amount = self.prices[product_type]
            product_info = self.products[product_type]
            
            # ایجاد شناسه منحصر به فرد برای تراکنش
            order_id = f"PFC-{uuid.uuid4().hex[:8].upper()}"
            
            # داده‌های درخواست پرداخت
            payment_data = {
                "merchant_id": self.merchant_id,
                "amount": amount,
                "currency": "IRT",  # تومان
                "description": f"{product_info['name']} - سفارش {order_id}",
                "callback_url": callback_url,
                "metadata": {
                    "email": customer_email,
                    "mobile": "",
                    "order_id": order_id,
                    "product_type": product_type,
                    "customer_name": customer_name
                }
            }
            
            # ارسال درخواست به زرین‌پال
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/pg/v4/payment/request.json",
                json=payment_data,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if result.get("data", {}).get("code") == 100:
                authority = result["data"]["authority"]
                payment_url = f"{self.payment_gateway_url}/{authority}"
                
                return {
                    "success": True,
                    "authority": authority,
                    "payment_url": payment_url,
                    "order_id": order_id,
                    "amount": amount,
                    "product_type": product_type
                }
            else:
                return {
                    "success": False,
                    "error": result.get("errors", {}).get("message", "خطای نامشخص در ایجاد درخواست"),
                    "error_code": result.get("errors", {}).get("code", "UNKNOWN")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"خطا در اتصال به درگاه پرداخت: {str(e)}",
                "error_code": "CONNECTION_ERROR"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"خطای غیرمنتظره: {str(e)}",
                "error_code": "UNKNOWN_ERROR"
            }

    def verify_payment(self, authority, amount):
        """تأیید پرداخت و صدور لایسنس"""
        try:
            verification_data = {
                "merchant_id": self.merchant_id,
                "amount": amount,
                "authority": authority
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/pg/v4/payment/verify.json",
                json=verification_data,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if result.get("data", {}).get("code") == 100:
                ref_id = result["data"]["ref_id"]
                card_hash = result["data"].get("card_hash", "")
                
                return {
                    "success": True,
                    "ref_id": ref_id,
                    "card_hash": card_hash,
                    "verified": True
                }
            else:
                return {
                    "success": False,
                    "error": result.get("errors", {}).get("message", "تراکنش تأیید نشد"),
                    "error_code": result.get("errors", {}).get("code", "VERIFICATION_FAILED")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"خطا در تأیید پرداخت: {str(e)}",
                "error_code": "CONNECTION_ERROR"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"خطای غیرمنتظره در تأیید: {str(e)}",
                "error_code": "UNKNOWN_ERROR"
            }

    def generate_license_after_payment(self, payment_info, product_type, customer_name, customer_email):
        """تولید خودکار لایسنس پس از تأیید پرداخت"""
        try:
            from serial_generator import LicenseGenerator
            
            # ایجاد نمونه تولیدکننده لایسنس
            license_gen = LicenseGenerator()
            
            # تولید سریال نامبر منحصر به فرد
            customer_data = {
                "name": customer_name,
                "email": customer_email,
                "product_type": product_type,
                "payment_ref": payment_info.get("ref_id", ""),
                "purchase_date": datetime.now().isoformat()
            }
            
            serial_number = license_gen.generate_serial(customer_data)
            
            # ذخیره اطلاعات لایسنس در فایل
            license_data = {
                "serial": serial_number,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "product_type": product_type,
                "purchase_date": datetime.now().isoformat(),
                "payment_reference": payment_info.get("ref_id", ""),
                "status": "active",
                "features": self.products[product_type]["features"]
            }
            
            # ذخیره در فایل JSON
            licenses_file = "generated_licenses.json"
            try:
                with open(licenses_file, 'r', encoding='utf-8') as f:
                    licenses = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                licenses = []
            
            licenses.append(license_data)
            
            with open(licenses_file, 'w', encoding='utf-8') as f:
                json.dump(licenses, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "serial_number": serial_number,
                "license_data": license_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطا در تولید لایسنس: {str(e)}"
            }

    def get_product_info(self, product_type):
        """دریافت اطلاعات محصول"""
        if product_type in self.products:
            info = self.products[product_type].copy()
            info["price"] = self.prices[product_type]
            info["price_formatted"] = f"{self.prices[product_type] // 10:,} تومان"
            return info
        return None

    def format_price(self, amount_rial):
        """فرمت کردن قیمت به صورت خوانا"""
        toman = amount_rial // 10
        return f"{toman:,} تومان"