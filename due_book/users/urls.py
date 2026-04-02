"""
URLs for Users App
"""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # Authentication - ĐĂNG KÝ US1
    path('dang-ky/', views.RegisterView.as_view(), name='user_register'),

    # Authentication - ĐĂNG NHẬP/ĐĂNG XUẤT US2
    path('dang-nhap/', views.user_login, name='user_login'),
    path('dang-xuat/', views.user_logout, name='user_logout'),

    # Password Reset - QUÊN MẬT KHẨU (Custom - Hỗ trợ Gmail)
    path('quen-mat-khau/', views.CustomPasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url='/users/dang-nhap/?reset_sent=true'
    ), name='password_reset'),

    path('quen-mat-khau/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    path('khoi-phuc-mat-khau/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url='/users/dang-nhap/?reset_complete=true'
    ), name='password_reset_confirm'),

    path('khoi-phuc-mat-khau/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),

    # User Profile - HỒ SƠ NGƯỜI DÙNG
    path('ho-so/', views.user_profile, name='user_profile'),
    path('ho-so/cap-nhat/', views.edit_profile, name='user_edit_profile'),
    path('ho-so/<str:username>/', views.user_profile, name='user_profile_by_username'),
]
