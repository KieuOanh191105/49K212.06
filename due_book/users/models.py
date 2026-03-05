from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Thông tin bổ sung cho User
    Bao gồm thông tin liên hệ để người mua/người bán liên lạc
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # ===== THÔNG TIN LIÊN HỆ =====
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Số điện thoại'
    )
    
    facebook_link = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Link Facebook'
    )
    
    zalo_link = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Link Zalo'
    )
    
    # ===== THÔNG TIN TÙY CHỌN =====
    student_id = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Mã số sinh viên'
    )
    
    address = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name='Địa chỉ giao dịch'
    )
    
    # ===== THÔNG TIN HỆ THỐNG =====
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )
    
    class Meta:
        verbose_name = 'Thông tin người dùng'
        verbose_name_plural = 'Thông tin người dùng'
    
    def __str__(self):
        return f'Profile của {self.user.username}'