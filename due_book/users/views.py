# Views for Users App
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User

from .forms import UserRegisterForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_register.html'
    success_url = reverse_lazy('users:user_login')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                'Dang ky thanh cong! Chao mung {}.'.format(self.object.username)
            )
            return response
        except Exception as e:
            messages.error(self.request, 'Loi dang ky: {}'.format(str(e)))
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)


# ==================== LOGIN ====================
def user_login(request):
    """
    Xử lý đăng nhập người dùng
    
    Flow:
    1. Nếu là GET request → Hiển thị form login
    2. Nếu là POST request → Xử lý đăng nhập
       - Validate form
       - Authenticate user
       - Kiểm tra user.is_active
       - Login nếu hợp lệ
       - Redirect đến trang chủ hoặc trang 'next'
    """
    if request.method == 'POST':
        # Tạo form với dữ liệu từ request
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            # Lấy user đã được xác thực
            user = form.get_user()
            
            # Kiểm tra user có active không
            if not user.is_active:
                messages.error(request, 'Tài khoản của bạn đã bị khóa!')
                return render(request, 'users/user_login.html', {'form': form})
            
            # Tạo session cho user
            login(request, user)
            
            # Hiển thị thông báo thành công
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            
            # Redirect đến trang 'next' hoặc trang chủ
            next_url = request.GET.get('next', reverse_lazy('books:home'))
            return redirect(next_url)
        else:
            # Form không hợp lệ - hiển thị lỗi theo AC2.3
            messages.error(request, 'Vui lòng điền vào Tên đăng nhập và mật khẩu chính xác. Chú ý rằng cả hai khung thông tin đều phân biệt chữ hoa và chữ thường.')
    else:
        # GET request - tạo form rỗng
        form = AuthenticationForm()

    # Render template với form
    return render(request, 'users/user_login.html', {'form': form})


# ==================== LOGOUT ====================
def user_logout(request):
    """
    Xử lý đăng xuất người dùng
    """
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất!')
    return redirect('books:home')
