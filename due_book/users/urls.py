"""
URLs for Users App - CHỈ CHỨC NĂNG ĐĂNG KÝ
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication - ĐĂNG KÝ US1
    path('dang-ky/', views.RegisterView.as_view(), name='user_register'),

    # Authentication - ĐĂNG NHẬP/ĐĂNG XUẤT US2
    path('dang-nhap/', views.user_login, name='user_login'),
    path('dang-xuat/', views.user_logout, name='user_logout'),
]