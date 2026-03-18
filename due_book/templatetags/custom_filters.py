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
