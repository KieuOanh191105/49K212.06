"""
URLs for Books App
"""
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),
    
    # Danh sách sách
    path('sach/', views.book_list, name='book_list'),
    
    # Các URL khác sẽ được thêm sau
    # path('sach/cua-toi/', views.my_books, name='my_books'),
    # path('sach/da-mua/', views.purchased_books, name='purchased_books'),
    # path('sach/dang-ban/', views.book_create, name='book_create'),
    # path('sach/<int:pk>/', views.book_detail, name='book_detail'),
]