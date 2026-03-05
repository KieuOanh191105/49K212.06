# due_book/users/urls.py

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Register (UI-ONLY)
    path('dang-ky/', views.RegisterView.as_view(), name='user_register'),
    # Hoặc dùng function-based view:
    # path('dang-ky/', views.user_register, name='user_register'),
]
