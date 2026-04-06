"""
Script test gửi email với Django
Chạy: python test_email.py
"""
import os
import sys
import django

# Add path to project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'due_book'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'due_book.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("="*80)
print("📧 TEST GỬI EMAIL DJANGO")
print("="*80)

# Hiển thị cấu hình email
print(f"\n📋 Cấu hình Email:")
print(f"  - EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"  - EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"  - EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"  - EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"  - EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'None'}")
print(f"  - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Test gửi email
try:
    print("\n🚀 Đang gửi email test...")
    send_mail(
        subject='🧪 Test Email - DUE Book',
        message='Đây là email test từ DUE Book. Nếu bạn nhận được email này thì cấu hình SMTP đã đúng!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['vanthan1992.qn@gmail.com'],  # Gửi về chính email đó để test
        fail_silently=False,
    )
    print("✅ EMAIL GỬI THÀNH CÔNG!")
    print(f"   Vui lòng kiểm tra Inbox/Spam của {settings.EMAIL_HOST_USER}")

except Exception as e:
    print(f"❌ LỖI KHI GỬI EMAIL: {e}")
    print("\n💡 Các nguyên nhân có thể:")
    print("  1. App Password sai hoặc đã hết hạn")
    print("  2. Chưa bật 2-Step Verification cho Google Account")
    print("  3. Firewall/Antivirus chặn port 587")
    print("  4. Cần tạo lại App Password tại: https://myaccount.google.com/apppasswords")

print("\n" + "="*80)
