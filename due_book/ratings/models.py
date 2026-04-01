from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class SellerReview(models.Model):
    """
    Đánh giá người bán sau khi mua sách - US11
    Lưu đánh giá từ người mua về người bán cho mỗi giao dịch
    """
    
    # Người mua (người đánh giá)
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name='Người mua'
    )
    
    # Người bán (người được đánh giá)
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name='Người bán'
    )
    
    # Sách đã mua (liên kết với giao dịch)
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Sách'
    )
    
    # Purchase request (để đảm bảo 1 đánh giá/giao dịch)
    purchase_request = models.ForeignKey(
        'books.PurchaseRequest',
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Yêu cầu mua'
    )
    
    # Số sao đánh giá (1-5)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Số sao'
    )
    
    # Bình luận (có thể để trống)
    comment = models.TextField(
        blank=True,
        default='',
        verbose_name='Bình luận'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đánh giá')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật')
    
    class Meta:
        verbose_name = 'Đánh giá người bán'
        verbose_name_plural = 'Danh sách đánh giá người bán'
        ordering = ['-created_at']
        # Đảm bảo mỗi giao dịch chỉ được đánh giá 1 lần
        constraints = [
            models.UniqueConstraint(
                fields=['purchase_request'],
                name='unique_review_per_purchase'
            )
        ]
    
    def __str__(self):
        return f"Đánh giá {self.rating}★ cho {self.seller.username} bởi {self.buyer.username}"
    
    @property
    def rating_stars(self):
        """Trả về chuỗi sao hiển thị"""
        filled = '★' * self.rating
        empty = '☆' * (5 - self.rating)
        return filled + empty
    
    @staticmethod
    def get_seller_stats(seller):
        """
        Lấy thống kê đánh giá của người bán
        Returns: dict với avg_rating, total_reviews
        """
        stats = seller.reviews_received.aggregate(
            avg_rating=Avg('rating'),
            total=models.Count('id')
        )
        return {
            'avg_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
            'total_reviews': stats['total'] or 0
        }
