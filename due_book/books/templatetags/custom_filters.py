from django import template

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
def seller_stats(user):
    """
    Lấy thống kê đánh giá của người bán
    Returns: dict với avg_rating, total_reviews
    """
    from ratings.models import SellerReview
    
    if not user or not user.is_authenticated:
        return {'avg_rating': 0, 'total_reviews': 0}
    
    return SellerReview.get_seller_stats(user)