from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def times(value):
    """Repeat character '★' value times"""
    return range(value)


@register.filter
def neg_times(value, total):
    """Repeat character '☆' (total - value) times"""
    return range(total - value)


@register.filter
def to_local_time(value):
    """
    Convert UTC datetime to local time (Asia/Ho_Chi_Minh)
    Usage: {{ obj.created_at|to_local_time|date:"d/m/Y H:i" }}
    """
    if value is None:
        return value
    # Django will automatically convert to TIME_ZONE setting when USE_TZ=True
    # This ensures the datetime is timezone-aware and in correct format
    return timezone.localtime(value)


@register.filter
def seller_stats(user):
    """
    Lấy thống kê đánh giá của người bán
    Returns: dict với avg_rating, total_reviews
    """
    from ratings.models import SellerReview

    if not user or not user.is_authenticated:
        return {'avg_rating': 0, 'total_reviews': 0}

    return SellerReview.get_seller_stats(user)
