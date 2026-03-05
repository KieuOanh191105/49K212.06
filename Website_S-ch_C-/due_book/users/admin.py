"""
Admin for Users App
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin cho UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Hồ sơ'
    fields = [
        'student_id', 'phone_number', 'facebook_link',
        'zalo_link', 'avatar', 'bio', 'address', 'is_verified'
    ]


class UserAdmin(BaseUserAdmin):
    """Admin interface cho User"""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)