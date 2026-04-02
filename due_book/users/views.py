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
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings

from .forms import UserRegisterForm, UserProfileForm, UserUpdateForm
from .models import UserProfile
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

        # Kiểm tra nếu vừa gửi password reset
        if request.GET.get('reset_sent') == 'true':
            messages.info(
                request,
                '📧 Link đặt lại mật khẩu đã được gửi! Kiểm tra email (hoặc terminal) để nhận hướng dẫn.'
            )

        # Kiểm tra nếu vừa reset password thành công
        if request.GET.get('reset_complete') == 'true':
            messages.success(
                request,
                '✅ Mật khẩu đã được đặt lại thành công! Vui lòng đăng nhập với mật khẩu mới.'
            )

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
        from ratings.models import SellerReview
        reviews = SellerReview.objects.filter(
            seller=profile_user
        ).select_related('buyer__profile', 'book').order_by('-created_at')[:5]
        
        # Lấy thống kê đánh giá của người bán
        seller_stats = SellerReview.get_seller_stats(profile_user)
    except:
        reviews = []
        seller_stats = {'avg_rating': 0, 'total_reviews': 0}

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
        'reviews': reviews,
        'seller_stats': seller_stats,
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


# ==================== CUSTOM PASSWORD RESET ====================
class CustomPasswordResetView(PasswordResetView):
    """
    Custom Password Reset View - Hỗ trợ tìm user theo cả email trường và Gmail
    Ưu tiên gửi đến Gmail nếu có, nếu không thì gửi email trường
    """
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = '/users/dang-nhap/?reset_sent=true'

    def get_users(self, email):
        """
        Tìm user theo cả email trường (User.email) và Gmail (UserProfile.gmail_address)
        Ưu tiên user có Gmail
        """
        email = email.strip().lower()
        print(f"🔍 DEBUG: Tìm user với email: {email}")  # Debug log

        # 1. Tìm user theo Gmail trong UserProfile (ưu tiên)
        try:
            profile_with_gmail = UserProfile.objects.filter(
                gmail_address__iexact=email
            ).select_related('user').first()

            if profile_with_gmail and profile_with_gmail.user.is_active:
                user = profile_with_gmail.user
                print(f"✅ DEBUG: Tìm thấy user theo Gmail: {user.username}")  # Debug log
                # KHÔNG thay đổi user.email ở đây, sẽ thay trong send_mail()
                return [user]
        except Exception as e:
            print(f"❌ DEBUG: Lỗi khi tìm theo Gmail: {e}")  # Debug log

        # 2. Nếu không tìm theo Gmail, tìm theo email trường (User.email)
        users = list(User._default_manager.filter(
            models.Q(email__iexact=email) |
            models.Q(username__iexact=email)
        ).filter(is_active=True))

        if users:
            print(f"✅ DEBUG: Tìm thấy {len(users)} user theo email trường")  # Debug log
        else:
            print(f"❌ DEBUG: Không tìm thấy user nào!")  # Debug log

        return users

    def send_mail(self, user, opts):
        """
        Gửi email reset password
        Gửi đến Gmail nếu có, ngược lại gửi đến email trường
        """
        email_input = self.request.POST.get('email', '').strip().lower()
        recipient_email = user.email  # Mặc định là email trường

        # Kiểm tra xem email nhập vào có phải Gmail không
        try:
            profile = UserProfile.objects.filter(user=user).first()
            if profile and profile.gmail_address and profile.gmail_address.lower() == email_input:
                # Gửi đến Gmail
                recipient_email = email_input
                print(f"📧 DEBUG: Gửi email đến Gmail: {recipient_email}")  # Debug log
        except Exception as e:
            print(f"⚠️ DEBUG: Lỗi khi kiểm tra Gmail: {e}")  # Debug log

        print(f"📧 DEBUG: Đang gửi email đến: {recipient_email}")  # Debug log

        # Tạo context cho email template
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        context = {
            'email': recipient_email,
            'user': user,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': self.request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'site_name': 'DUE Book',
        }

        # Render email subject
        subject_template = opts['subject_template_name']
        from django.template.loader import render_to_string
        subject = render_to_string(subject_template, context).strip()

        # Render email body
        email_template = opts['email_template_name']
        body = render_to_string(email_template, context)

        # Gửi email
        try:
            print("\n" + "="*80)
            print(f"📧 EMAIL NỘI DUNG (gửi đến: {recipient_email})")
            print("="*80)
            print(f"Subject: {subject}")
            print(f"From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"To: {recipient_email}")
            print("-"*80)
            print(body)
            print("="*80 + "\n")

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                html_message=body,
                fail_silently=False,
            )
            print(f"✅ DEBUG: Email đã gửi thành công đến: {recipient_email}")  # Debug log
        except Exception as e:
            print(f"❌ DEBUG: Lỗi khi gửi email: {e}")  # Debug log
            raise

    def form_valid(self, form):
        """
        Override hoàn toàn form_valid để xử lý logic gửi email
        """
        email = form.cleaned_data['email']
        print(f"📝 DEBUG: form_valid() được gọi với email: {email}")  # Debug log

        # Tìm user (gọi get_users)
        users = self.get_users(email)
        print(f"📊 DEBUG: Số lượng user tìm thấy: {len(users)}")  # Debug log

        if not users:
            # Không tìm thấy user - vẫn redirect thành công (security)
            print(f"⚠️ DEBUG: Không tìm thấy user, redirect anyway")  # Debug log
            return redirect(self.success_url)

        # Gửi email cho mỗi user tìm thấy
        for user in users:
            print(f"👤 DEBUG: Xử lý user: {user.username}")  # Debug log

            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': self.html_email_template_name,
                'extra_email_context': self.extra_email_context,
            }

            # Gửi email
            self.send_mail(user, opts)

        print(f"✅ DEBUG: Gửi xong, redirect đến: {self.success_url}")  # Debug log
        return redirect(self.success_url)
