
"""
Views for Users App - CHỨC NĂNG ĐĂNG KÝ
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User

from .forms import UserRegisterForm


# ==================== REGISTER ====================
class RegisterView(CreateView):
    """Đăng ký tài khoản mới"""
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_register.html'
    success_url = reverse_lazy('user_login')

    def form_valid(self, form):
        """Xử lý khi form hợp lệ"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Chào mừng {self.object.username}! Đăng ký thành công.'
        )
        return response


# ==================== LOGIN (OPTIONAL) ====================
def user_login(request):
    """Đăng nhập"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            next_url = request.GET.get('next', reverse_lazy('home'))
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    else:
        form = AuthenticationForm()

    return render(request, 'users/user_login.html', {'form': form})

# Làm cho phần đăng xuất không nằm trong phần đăng ký 
# ==================== LOGOUT (OPTIONAL) ====================
def user_logout(request):
    """Đăng xuất"""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất!')
    return redirect('home')