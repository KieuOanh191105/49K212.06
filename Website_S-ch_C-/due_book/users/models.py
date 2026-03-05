from django.db import models

# Create your models here.
# users/models.py - FILE HOÀN CHỈNH CHO PROJECT B

"""
Models for Users App - CHỨC NĂNG ĐĂNG KÝ
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Hồ sơ mở rộng của User"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # ===== THÔNG TIN SINH VIÊN =====
    student_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Mã số sinh viên'
    )

    # ===== THÔNG TIN LIÊN HỆ (BẮT BUỘC KHI ĐĂNG KÝ) =====
    phone_number = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name='Số điện thoại'
    )

    facebook_link = models.URLField(
        blank=False,
        null=False,
        verbose_name='Link Facebook'
    )

    zalo_link = models.URLField(
        blank=True,
        null=True,
        verbose_name='Link Zalo'
    )

    # ===== THÔNG TIN CÁ NHÂN =====
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Ảnh đại diện'
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name='Giới thiệu bản thân'
    )
    address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Địa chỉ giao dịch'
    )

    # ===== METADATA =====
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Đã xác minh'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

    def __str__(self):
        return f"Profile: {self.user.get_full_name() or self.user.username}"

    @property
    def display_name(self):
        """Tên hiển thị"""
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.username


# ===== SIGNAL TẠO PROFILE TỰ ĐỘNG =====
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Tự động tạo UserProfile khi tạo User mới.
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            phone_number='',
            facebook_link='',
            zalo_link=''
        )