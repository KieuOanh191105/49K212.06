from django.contrib import admin
from .models import SellerReview


@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    """Admin cho đánh giá người bán"""
    list_display = ['id', 'buyer', 'seller', 'book', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['buyer__username', 'seller__username', 'book__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['buyer', 'seller', 'book', 'purchase_request']
    
    fieldsets = (
        ('Thông tin đánh giá', {
            'fields': ('buyer', 'seller', 'book', 'purchase_request')
        }),
        ('Nội dung đánh giá', {
            'fields': ('rating', 'comment')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
