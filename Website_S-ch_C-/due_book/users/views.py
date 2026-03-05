# due_book/users/views.py

from django.shortcuts import render
from django.views.generic import TemplateView

# ==================== REGISTER (UI-ONLY) ====================

class RegisterView(TemplateView):
    """
    View hiển thị form đăng ký - UI ONLY (chưa xử lý backend)
    Sprint FE: Chỉ render template
    Sprint BE: Sẽ thêm logic xử lý form
    """
    template_name = 'users/user_register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Đăng ký tài khoản'
        return context


# Hoặc sử dụng function-based view:
def user_register(request):
    """View hiển thị form đăng ký - UI ONLY"""
    return render(request, 'users/user_register.html', {
        'title': 'Đăng ký tài khoản'
    })