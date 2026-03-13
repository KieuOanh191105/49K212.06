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
    
    # Chi tiết sách - US7
    path('sach/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail_alt'),
    
    # US4 - ĐĂNG BÁN SÁCH - done 
    path('dang-ban-sach/', views.BookCreateView.as_view(), name='book_create'),
    
    # Chỉnh sửa bài đăng
    path('sach/<int:pk>/chinh-sua/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book_alt'),
    
    # Xóa bài đăng
    path('sach/<int:pk>/xoa/', views.delete_book, name='delete_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book_alt'),
    
    # Routes cũ (redirect đến routes mới - tương thích ngược)
    path('sach/<int:pk>/cap-nhat/', views.book_update, name='book_update'),
]