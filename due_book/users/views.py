# Views for Users App
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.http import Http404
from django.db import models
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm, UserProfileForm, UserUpdateForm
from books.models import Book


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


# ==================== USER PROFILE ====================
def user_profile(request, username=None):
    """
    Hiển thị hồ sơ người dùng
    
    Logic:
    - Nếu có username: hiển thị hồ sơ của user đó
    - Nếu không có username: hiển thị hồ sơ của user đang đăng nhập
    
    Chỉ sử dụng GET request để hiển thị dữ liệu.
    Không có chức năng chỉnh sửa.
    """
    # Xác định user cần hiển thị profile
    if username:
        # Xem hồ sơ của người khác
        profile_user = get_object_or_404(User, username=username)
    else:
        # Xem hồ sơ của chính mình
        if not request.user.is_authenticated:
            messages.warning(request, 'Vui lòng đăng nhập để xem hồ sơ của bạn.')
            return redirect('users:user_login')
        profile_user = request.user
    
    # Lấy profile của user
    profile = profile_user.profile
    
    # Lấy sách đang bán (tối đa 6 cuốn)
    books_for_sale = Book.objects.filter(
        seller=profile_user,
        status='available'
    ).select_related('subject').order_by('-created_at')[:6]
    
    # Thống kê
    total_books_listed = Book.objects.filter(seller=profile_user).count()
    total_books_sold = Book.objects.filter(
        seller=profile_user,
        status='sold'
    ).count()
    total_books_available = Book.objects.filter(
        seller=profile_user,
        status='available'
    ).count()
    
    # Tổng lượt xem sách
    total_views = Book.objects.filter(seller=profile_user).aggregate(
        total=models.Sum('view_count')
    )['total'] or 0

    # Lấy đánh giá từ người mua
    try:
        from ratings.models import Rating
        ratings = Rating.objects.filter(
            seller=profile_user
        ).select_related('reviewer__profile', 'book').order_by('-created_at')[:5]
    except:
        ratings = []

    # Context cho template
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'books_for_sale': books_for_sale,
        'total_books_listed': total_books_listed,
        'total_books_sold': total_books_sold,
        'total_books_available': total_books_available,
        'total_views': total_views,
        'is_own_profile': request.user == profile_user,
        'ratings': ratings,
    }
    
    return render(request, 'users/user_profile.html', context)


# ==================== EDIT PROFILE ====================
@login_required
def edit_profile(request):
    """
    Chỉnh sửa hồ sơ người dùng
    
    Sử dụng 2 form:
    - UserUpdateForm: Cập nhật thông tin User (họ tên, email)
    - UserProfileForm: Cập nhật thông tin UserProfile
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công!')
            return redirect('users:user_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/user_edit_profile.html', context)
