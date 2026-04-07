
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegisterForm(forms.ModelForm):
    """Form đăng ký tài khoản - bao gồm cả thông tin liên hệ bắt buộc"""

    # ===== THÔNG TIN TÀI KHOẢN =====
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu (ít nhất 6 ký tự)'
        }),
        label='Mật khẩu',
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        }),
        label='Xác nhận mật khẩu'
    )

    # ===== THÔNG TIN LIÊN HỆ (BẮT BUỘC) =====
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            
        }),
        label='Số điện thoại *',
        max_length=20,
        required=True
       
    )

    facebook_link = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: https://facebook.com/username'
        }),
        label='Link Facebook *',
        required=True
       
    )

    zalo_link = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: https://zalo.me/xxxxxxxxxxx'
        }),
        label='Link Zalo *',
        required=True,
      
    )

    # ===== EMAIL CHO PASSWORD RESET =====
    gmail_address = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '@gmail.com'
        }),
        label='Email',
        required=False,
        help_text='Dùng để nhận link đặt lại mật khẩu khi quên (tùy chọn)'
    )

    # ===== THÔNG TIN TÙY CHỌN =====
    student_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mã số sinh viên'
        }),
        label='Mã số sinh viên',
        max_length=50,
        required=False
    )

    address = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Địa chỉ giao dịch bạn muốn'
        }),
        label='Địa chỉ giao dịch',
        max_length=300,
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên đăng nhập'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '@due.udn.vn'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ và đệm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên'
            }),
        }
        labels = {
            'username': 'Tên đăng nhập',
            'email': 'Email sinh viên DUE *',
            'first_name': 'Họ và đệm',
            'last_name': 'Tên',
        }
       
        

    # ===== VALIDATION METHODS =====

    def clean_confirm_password(self):
        """Kiểm tra mật khẩu xác nhận"""
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Mật khẩu không khớp!')
        return confirm_password

    def clean_email(self):
        """Validate email sinh viên DUE"""
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email không được để trống!')

        email = email.strip().lower()

        # Kiểm tra đuôi email phải là @due.udn.vn
        if not email.endswith('@due.udn.vn'):
            raise forms.ValidationError(
                'Chỉ chấp nhận email sinh viên DUE có dạng: 12 chữ số + @due.udn.vn'
            )

        # Lấy phần trước dấu @
        local_part = email.split('@')[0]

        # Kiểm tra phải có đúng 12 ký tự
        if len(local_part) != 12:
            raise forms.ValidationError(
                'Chỉ chấp nhận email sinh viên DUE có dạng: 12 chữ số + @due.udn.vn'
            )

        # Kiểm tra chỉ gồm số
        if not local_part.isdigit():
            raise forms.ValidationError(
                'Chỉ chấp nhận email sinh viên DUE có dạng: 12 chữ số + @due.udn.vn'
            )

        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng!')

        return email

    def clean_username(self):
        """Kiểm tra tên đăng nhập đã tồn tại"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Tên đăng nhập đã tồn tại!')
        return username

    def clean_phone_number(self):
        """Validate số điện thoại"""
        phone = self.cleaned_data.get('phone_number')
        if not phone or not phone.strip():
            raise forms.ValidationError('Số điện thoại không được để trống!')
        phone = phone.strip().replace(' ', '').replace('.', '')
        if not phone.isdigit() or len(phone) < 9:
            raise forms.ValidationError('Số điện thoại không hợp lệ!')
        return phone

    def clean_facebook_link(self):
        """Validate Facebook link"""
        link = self.cleaned_data.get('facebook_link')
        if not link or not link.strip():
            raise forms.ValidationError('Link Facebook không được để trống!')
        return link.strip()

    def clean_zalo_link(self):
        """Validate Zalo link"""
        link = self.cleaned_data.get('zalo_link')
        if not link or not link.strip():
            raise forms.ValidationError('Link Zalo không được để trống!')
        return link.strip()

    def clean_gmail_address(self):
        """Validate Gmail address (optional)"""
        gmail = self.cleaned_data.get('gmail_address')
        if gmail:
            gmail = gmail.strip().lower()
            # Kiểm tra đuôi @gmail.com
            if not gmail.endswith('@gmail.com'):
                raise forms.ValidationError('Chỉ chấp nhận email có đuôi @gmail.com')
            # Kiểm tra email này đã được dùng bởi user khác chưa
            from .models import UserProfile
            existing_profiles = UserProfile.objects.filter(
                gmail_address=gmail
            ).exclude(user__username=self.cleaned_data.get('username', ''))
            if existing_profiles.exists():
                raise forms.ValidationError('Email này đã được sử dụng bởi tài khoản khác!')
            return gmail
        return gmail

    def save(self, commit=True):
        """
        Override save() để:
        1. Hash mật khẩu trước khi lưu
        2. Lưu thông tin vào UserProfile
        """
        from .models import UserProfile
        
        # 1. Lưu User với mật khẩu đã hash
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # 2. Cập nhật UserProfile với thông tin liên hệ
            # Lấy hoặc tạo profile nếu chưa có
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.facebook_link = self.cleaned_data.get('facebook_link', '')
            profile.zalo_link = self.cleaned_data.get('zalo_link', '')
            profile.gmail_address = self.cleaned_data.get('gmail_address', '')
            profile.student_id = self.cleaned_data.get('student_id', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.save()

        return user


# ==================== USER UPDATE FORM ====================
class UserUpdateForm(forms.ModelForm):
    """Form cập nhật thông tin User cơ bản"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ và đệm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'first_name': 'Họ và đệm',
            'last_name': 'Tên',
            'email': 'Email',
        }

    def clean_email(self):
        """Validate email: unique, lowercase, format"""
        email = self.cleaned_data.get('email', '').strip().lower()

        # Kiểm tra email không được để trống
        if not email:
            raise forms.ValidationError('Email không được để trống.')

        # Kiểm tra định dạng email cơ bản
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Email không đúng định dạng.')

        # Kiểm tra email uniqueness (ngoại trừ user hiện tại)
        existing_user = User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        ).first()

        if existing_user:
            raise forms.ValidationError(
                f'Email này đã được sử dụng bởi tài khoản "{existing_user.username}". '
                f'Vui lòng chọn email khác.'
            )

        return email


# ==================== USER PROFILE FORM ====================
class UserProfileForm(forms.ModelForm):
    """Form cập nhật thông tin UserProfile"""

    class Meta:
        model = UserProfile
        fields = [
            'student_id', 'phone_number', 'gmail_address', 'facebook_link',
            'zalo_link', 'address', 'avatar'
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mã số sinh viên'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'gmail_address': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your-email@gmail.com'
            }),
            'facebook_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/username'
            }),
            'zalo_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zalo.me/09xxxxxxxxx'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Địa chỉ giao dịch'
            })
            # 'avatar': forms.FileInput(attrs={
            #     'class': 'form-control',
            #     'accept': 'image/*'
            # }),
        }
        labels = {
            'student_id': 'Mã số sinh viên',
            'phone_number': 'Số điện thoại',
            'gmail_address': 'Email Gmail (khôi phục mật khẩu)',
            'facebook_link': 'Link Facebook',
            'zalo_link': 'Link Zalo',
            'address': 'Địa chỉ',
            'avatar': 'Ảnh đại diện',
        }

    def clean_gmail_address(self):
        """Validate Gmail address (optional, must end with @gmail.com)"""
        gmail = self.cleaned_data.get('gmail_address', '').strip()

        # Nếu rỗng, cho phép (optional field)
        if not gmail:
            return gmail

        # Convert to lowercase
        gmail = gmail.lower()

        # Kiểm tra định dạng email cơ bản
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(gmail)
        except ValidationError:
            raise forms.ValidationError('Email Gmail không đúng định dạng.')

        # Kiểm tra đuôi @gmail.com
        if not gmail.endswith('@gmail.com'):
            raise forms.ValidationError(
                'Email phải có đuôi @gmail.com. Ví dụ: yourname@gmail.com'
            )

        # Kiểm tra uniqueness (ngoại trừ user hiện tại)
        from .models import UserProfile
        existing_profile = UserProfile.objects.filter(
            gmail_address__iexact=gmail
        ).exclude(
            pk=self.instance.pk
        ).first()

        if existing_profile:
            raise forms.ValidationError(
                f'Email Gmail này đã được sử dụng bởi tài khoản "{existing_profile.user.username}". '
                f'Vui lòng sử dụng email khác.'
            )

        return gmail
