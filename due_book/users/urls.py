"""
URLs for Users App
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

    # User Profile - HỒ SƠ NGƯỜI DÙNG
    path('ho-so/', views.user_profile, name='user_profile'),
    path('ho-so/cap-nhat/', views.edit_profile, name='user_edit_profile'),
    path('ho-so/<str:username>/', views.user_profile, name='user_profile_by_username'),
]
