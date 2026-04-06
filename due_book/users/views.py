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
        # else:
        #     # Form không hợp lệ - hiển thị lỗi theo AC2.3
        #     messages.error(request, 'Vui lòng điền vào Tên đăng nhập và mật khẩu chính xác. Chú ý rằng cả hai khung thông tin đều phân biệt chữ hoa và chữ thường.')
    else:
        # GET request - tạo form rỗng
        form = AuthenticationForm()

        # Kiểm tra nếu vừa gửi password reset
        # if request.GET.get('reset_sent') == 'true':
        #     messages.info(
        #         request,
        #         'Vui lòng kiểm tra email của bạn để đặt lại mật khẩu.'
        #     )

        # Kiểm tra nếu vừa reset password thành công
        # if request.GET.get('reset_complete') == 'true':
        #     messages.success(
        #         request,
        #         'Mật khẩu đã được đặt lại thành công! Vui lòng đăng nhập với mật khẩu mới.'
        #     )

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
        CHỈ tìm user theo Gmail (UserProfile.gmail_address)
        KHÔNG tìm theo email trường (@due.udn.vn)
        """
        try:
            email = email.strip().lower() if email else ''
            print(f"🔍 DEBUG: Tìm user với Gmail: {email}")  # Debug log

            # Validate email phải có đuôi @gmail.com
            if not email.endswith('@gmail.com'):
                print(f"⚠️ DEBUG: Email không phải @gmail.com: {email}")  # Debug log
                return []  # Trả về empty list nếu không phải Gmail

            # Chỉ tìm user theo Gmail trong UserProfile
            try:
                profile_with_gmail = UserProfile.objects.filter(
                    gmail_address__iexact=email
                ).select_related('user').first()

                if profile_with_gmail and profile_with_gmail.user.is_active:
                    user = profile_with_gmail.user
                    print(f"✅ DEBUG: Tìm thấy user theo Gmail: {user.username}")  # Debug log
                    return [user]
                else:
                    print(f"❌ DEBUG: Không tìm thấy user với Gmail: {email}")  # Debug log
                    return []

            except Exception as e:
                print(f"❌ DEBUG: Lỗi khi tìm theo Gmail: {e}")  # Debug log
                import logging
                logging.getLogger(__name__).exception("Error in Gmail lookup")
                return []

        except Exception as e:
            import logging
            logging.getLogger(__name__).exception(f"Error in get_users: {e}")
            print(f"❌ DEBUG: Lỗi trong get_users: {e}")
            return []  # Return empty list thay vì crash

    def send_mail(self, user, opts):
        """
        Gửi email reset password đến Gmail của user
        KHÔNG gửi đến email trường
        """
        try:
            # Lấy Gmail từ UserProfile
            try:
                profile = UserProfile.objects.filter(user=user).first()
                if not profile or not profile.gmail_address:
                    print(f"❌ DEBUG: User {user.username} không có Gmail")  # Debug log
                    raise ValueError("User không có Gmail address")

                recipient_email = profile.gmail_address.lower()
                print(f"📧 DEBUG: Gửi email đến Gmail: {recipient_email}")  # Debug log

            except Exception as e:
                print(f"❌ DEBUG: Lỗi khi lấy Gmail: {e}")  # Debug log
                import logging
                logging.getLogger(__name__).exception(f"Error getting Gmail for user {user.username}")
                raise

            # Lấy domain từ SITE_URL (biến môi trường)
            # Ưu tiên đọc trực tiếp từ os.environ (tránh load_dotenv issue trên Render)
            import os
            from urllib.parse import urlparse

            site_url_env = os.environ.get('SITE_URL')
            if site_url_env:
                site_url = site_url_env
            else:
                # Fallback: Try getattr settings
                site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')

            parsed_url = urlparse(site_url)

            # DEBUG: In ra SITE_URL để kiểm tra
            print(f"🔍 DEBUG: SITE_URL from env = {site_url_env}")
            print(f"🔍 DEBUG: Final SITE_URL = {site_url}")
            print(f"🔍 DEBUG: protocol = {parsed_url.scheme}")
            print(f"🔍 DEBUG: domain = {parsed_url.netloc}")

            # Tạo context cho email template
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes

            context = {
                'email': recipient_email,
                'user': user,
                'protocol': parsed_url.scheme,  # http hoặc https từ SITE_URL
                'domain': parsed_url.netloc,     # domain từ SITE_URL (ví dụ: example.com)
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
            print("\n" + "="*80)
            print(f"📧 EMAIL NỘI DUNG (gửi đến Gmail: {recipient_email})")
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
            print(f"✅ DEBUG: Email đã gửi thành công đến Gmail: {recipient_email}")  # Debug log

        except Exception as e:
            print(f"❌ DEBUG: Lỗi khi gửi email: {e}")  # Debug log
            import logging
            logging.getLogger(__name__).exception(f"Error in send_mail for user {user.username}")
            raise

    def form_valid(self, form):
        """
        Override hoàn toàn form_valid để xử lý logic gửi email
        """
        try:
            email = form.cleaned_data['email']
            print(f"📝 DEBUG: form_valid() được gọi với email: {email}")  # Debug log

            # Lấy danh sách users
            users = self.get_users(email)

            if not users:
                # Vẫn hiển thị success để bảo mật (không tiết lộ user tồn tại hay không)
                # Nhưng log để debug
                print(f"⚠️ WARNING: Không tìm thấy user với email: {email}")
                return redirect(self.success_url)

            # Gửi email cho từng user
            for user in users:
                opts = {
                    'subject_template_name': self.subject_template_name,
                    'email_template_name': self.email_template_name,
                    'use_https': self.request.is_secure(),
                }

                try:
                    self.send_mail(user, opts)
                except Exception as e:
                    # Log lỗi nhưng không crash app
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Lỗi khi gửi email reset password cho user {user.username}: {str(e)}")
                    logger.exception(f"Full traceback: {e}")  # Log full traceback

                    # Hiển thị thông báo lỗi thân thiện
                    from django.contrib import messages
                    messages.error(
                        self.request,
                        'Không thể gửi email khôi phục. Vui lòng liên hệ admin hoặc thử lại sau.'
                    )
                    # Redirect về trang login với error message
                    return redirect('/users/dang-nhap/?email_error=true')

            return redirect(self.success_url)

        except Exception as e:
            # Catch toàn bộ lỗi khác (database, form validation, etc.)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Lỗi không mong muốn trong form_valid: {str(e)}")
            logger.exception(f"Full traceback: {e}")

            # Redirect về trang login với error message
            from django.contrib import messages
            messages.error(
                self.request,
                'Có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ admin.'
            )
            return redirect('/users/dang-nhap/?email_error=true')
