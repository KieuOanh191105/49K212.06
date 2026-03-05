"""
URLs for Users App - CHỈ CHỨC NĂNG ĐĂNG KÝ
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication - ĐĂNG KÝ (BẮT BUỘC)
    path('dang-ky/', views.RegisterView.as_view(), name='user_register'),

    # Authentication - ĐĂNG NHẬP/ĐĂNG XUẤT (OPTIONAL)
    path('dang-nhap/', views.user_login, name='user_login'),
    path('dang-xuat/', views.user_logout, name='user_logout'),
]