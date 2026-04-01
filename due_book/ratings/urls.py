"""
URLs for Ratings App
US11 - Đánh giá người bán
"""
from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    # Đánh giá người bán sau khi mua sách (trang riêng)
    path('danh-gia/<int:purchase_request_id>/', views.rating_create, name='rating_create'),
    
    # API AJAX đánh giá (cho modal popup)
    path('api/danh-gia/<int:purchase_request_id>/', views.rating_create_ajax, name='rating_create_ajax'),
    
    # Submit đánh giá từ form modal (POST thông thường)
    path('submit-review/', views.submit_review, name='submit_review'),
    
    # Lấy nội dung modal đánh giá
    path('modal/danh-gia/<int:purchase_request_id>/', views.get_review_modal, name='review_modal'),
]
