"""
URLs for Ratings App
"""
from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    # Đánh giá người bán sau khi mua sách
    path('danh-gia/<int:user_id>/', views.rating_create, name='rating_create'),
]