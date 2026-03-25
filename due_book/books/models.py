"""
Models for Books App
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import os


def get_book_image_upload_path(instance, filename):
    """Upload path: media/books/YYYY/MM/filename"""
    from django.utils import timezone
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}_{instance.pk or 'new'}.{ext}"
    # Use current time if created_at is None (new book)
    date = instance.created_at if instance.created_at else timezone.now()
    return os.path.join('books',
                        date.strftime('%Y/%m'),
                        filename)


class Subject(models.Model):
    """Danh sách môn học"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Tên môn học')
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã môn học')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Môn học'
        verbose_name_plural = 'Danh sách môn học'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Book(models.Model):
    """Bài đăng bán sách"""

    # Trạng thái sách
    STATUS_CHOICES = [
        ('available', 'Đang bán'),
        ('sold', 'Đã bán'),
        ('reserved', 'Đang giữ'),
    ]

    # Tình trạng sách
    CONDITION_CHOICES = [
        ('new', 'Mới 100%'),
        ('like_new', 'Mới 95-99%'),
        ('good', 'Khá (80-94%)'),
        ('fair', 'Trung bình (60-79%)'),
        ('poor', 'Cũ (<60%)'),
    ]

    # Thông tin cơ bản
    title = models.CharField(max_length=300, verbose_name='Tên sách')
    subject = models.ForeignKey(Subject,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='books',
                                verbose_name='Môn học')

    # Thông tin bán hàng
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(1000)],
        verbose_name='Giá bán (VNĐ)'
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good',
        verbose_name='Tình trạng sách'
    )

    # Mô tả
    description = models.TextField(blank=True, verbose_name='Mô tả chi tiết')
    notes = models.TextField(
        blank=True,
        help_text='Ghi chú thêm (gạch bớt, đánh dấu, v.v.)',
        verbose_name='Ghi chú'
    )

    # Hình ảnh
    cover_image = models.ImageField(
        upload_to=get_book_image_upload_path,
        blank=True,
        null=True,
        verbose_name='Ảnh bìa'
    )

    # Trạng thái bài đăng
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Trạng thái'
    )

    # Thông tin người bán
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books_for_sale',
        verbose_name='Người bán'
    )

    # Người mua (được gán khi purchase request được duyệt)
    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchased_books',
        verbose_name='Người mua'
    )

    # Metadata
    view_count = models.PositiveIntegerField(default=0, verbose_name='Lượt xem')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đăng')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật lần cuối')

    class Meta:
        verbose_name = 'Sách'
        verbose_name_plural = 'Danh sách sách'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('books:book_detail', kwargs={'pk': self.pk})

    @property
    def is_available(self):
        """Check nếu sách còn bán"""
        return self.status == 'available'

    @property
    def condition_display_badge(self):
        """HTML badge cho tình trạng"""
        badges = {
            'new': '<span class="badge bg-success">Mới 100%</span>',
            'like_new': '<span class="badge bg-primary">Mới 95-99%</span>',
            'good': '<span class="badge bg-info">Khá</span>',
            'fair': '<span class="badge bg-warning">Trung bình</span>',
            'poor': '<span class="badge bg-secondary">Cũ</span>',
        }
        return badges.get(self.condition, '')

    def increment_view(self):
        """Tăng lượt xem"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    @property
    def seller_contact_info(self):
        """
        Lấy thông tin liên hệ của người bán từ UserProfile
        Returns: dict với phone, facebook, zalo
        """
        profile = self.seller.profile
        return {
            'phone': profile.phone_number,
            'facebook': profile.facebook_link,
            'zalo': profile.zalo_link,
        }


class BookImage(models.Model):
    """Ảnh phụ của sách (nhiều ảnh)"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_book_image_upload_path)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ảnh sách'
        verbose_name_plural = 'Danh sách ảnh'
        ordering = ['order']


class PurchaseRequest(models.Model):
    """
    Yêu cầu mua sách - US09
    Người mua gửi yêu cầu, người bán duyệt/từ chối
    """
    
    # Trạng thái yêu cầu
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối'),
      
    ]
    
    # Thông tin chính
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='purchase_requests',
        verbose_name='Sách'
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase_requests',
        verbose_name='Người mua'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_purchase_requests',
        verbose_name='Người bán'
    )
    
    # Trạng thái
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    
    # Lời nhắn từ người mua
    message = models.TextField(
        blank=True,
        default='',
        verbose_name='Lời nhắn',
        help_text='Lời nhắn gửi đến người bán'
    )
    
    # Lý do từ chối (tùy chọn)
    rejection_reason = models.TextField(
        blank=True,
        default='',
        verbose_name='Lý do từ chối'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày gửi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật')
    
    # Thời gian duyệt/từ chối
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ngày xử lý'
    )
    
    class Meta:
        verbose_name = 'Yêu cầu mua sách'
        verbose_name_plural = 'Danh sách yêu cầu mua sách'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Yêu cầu mua '{self.book.title}' từ {self.buyer.username}"
    
    def clean(self):
        """Validate: Không cho người bán tự mua sách của mình"""
        from django.core.exceptions import ValidationError
        # Chỉ kiểm tra khi cả buyer và seller đều đã được set
        if self.buyer_id and self.seller_id and self.buyer == self.seller:
            raise ValidationError('Bạn không thể mua sách của chính mình!')
    
    def save(self, *args, **kwargs):
        """Tự động set seller từ book khi tạo mới"""
        if not self.seller_id and self.book_id:
            self.seller = self.book.seller
        super().save(*args, **kwargs)
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        return self.status == 'rejected'
    
    def approve(self):
        """Duyệt yêu cầu mua"""
        from django.utils import timezone
        self.status = 'approved'
        self.processed_at = timezone.now()
        self.save()
        
        # Cập nhật trạng thái sách
        self.book.status = 'sold'
        self.book.buyer = self.buyer
        self.book.save()
    
    def reject(self, reason=''):
        """Từ chối yêu cầu mua"""
        from django.utils import timezone
        self.status = 'rejected'
        self.rejection_reason = reason
        self.processed_at = timezone.now()
        self.save()
