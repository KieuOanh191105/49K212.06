
from django import forms
from django.contrib.auth.models import User


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
            'placeholder': 'VD: 0912345678'
        }),
        label='Số điện thoại *',
        max_length=20,
        required=True,
        help_text='Số điện thoại để người mua liên hệ'
    )

    facebook_link = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: https://facebook.com/username'
        }),
        label='Link Facebook *',
        required=True,
        help_text='Link profile Facebook của bạn'
    )

    zalo_link = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: https://zalo.me/0912345678'
        }),
        label='Link Zalo *',
        required=True,
        help_text='Link Zalo của bạn'
    )

    # ===== THÔNG TIN TÙY CHỌN =====
    student_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mã số sinh viên (nếu có)'
        }),
        label='Mã số sinh viên',
        max_length=50,
        required=False
    )

    address = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Địa chỉ giao dịch (nếu muốn)'
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
                'placeholder': 'VD: 231121521224@due.udn.vn'
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
        help_texts = {
            'email': 'Chỉ chấp nhận email sinh viên DUE (12 chữ số @due.udn.vn)',
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

    def save(self, commit=True):
        """
        Override save() để:
        1. Hash mật khẩu trước khi lưu
        2. Lưu thông tin vào UserProfile
        """
        # 1. Lưu User với mật khẩu đã hash
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # 2. Cập nhật UserProfile với thông tin liên hệ
            # Signal đã tạo profile rỗng, giờ update thông tin thực
            profile = user.profile
            profile.phone_number = self.cleaned_data['phone_number']
            profile.facebook_link = self.cleaned_data['facebook_link']
            profile.zalo_link = self.cleaned_data['zalo_link']
            profile.student_id = self.cleaned_data.get('student_id', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.save()

        return user