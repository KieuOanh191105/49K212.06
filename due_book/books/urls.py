"""
URLs for Books App
US4 - Đăng bài bán sách
"""
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),
    
    # Danh sách sách
    path('sach/', views.book_list, name='book_list'),
    
    # Sách của tôi - AC4.4
    path('sach/cua-toi/', views.my_books, name='my_books'),
    
    # Chi tiết sách - chưa 
    path('sach/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    
    # US4 - ĐĂNG BÁN SÁCH - done 
    path('dang-ban-sach/', views.BookCreateView.as_view(), name='book_create'),
    
    # Chỉnh sửa bài đăng - chưa phát triển
    path('sach/<int:pk>/chinh-sua/', views.book_update, name='book_update'),
    
    # Xóa bài đăng - chưa phát triển
    path('sach/<int:pk>/xoa/', views.book_delete, name='book_delete'),
]