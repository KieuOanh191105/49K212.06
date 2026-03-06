from django.test import TestCase
from django.contrib.auth.models import User
from .forms import UserRegisterForm


class UserRegisterTest(TestCase):

    def setUp(self):
        # dữ liệu hợp lệ
        self.valid_data = {
            'username': 'testuser',
            'email': '123456789012@due.udn.vn',
            'first_name': 'Pham',
            'last_name': 'Tho',
            'password': '123456',
            'confirm_password': '123456',
            'phone_number': '0912345678',
            'facebook_link': 'https://facebook.com/test',
            'zalo_link': 'https://zalo.me/0912345678',
            'student_id': '231121521224',
            'address': 'Da Nang'
        }

    # 1 đăng ký hợp lệ
    def test_register_valid(self):
        form = UserRegisterForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    # 2 mật khẩu không khớp
    def test_password_not_match(self):
        data = self.valid_data.copy()
        data['confirm_password'] = 'abcdef'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # 3 email sai
    def test_email_invalid(self):
        data = self.valid_data.copy()
        data['email'] = 'abc@gmail.com'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # 4 email trùng
    def test_email_duplicate(self):
        User.objects.create_user(
            username='olduser',
            email='123456789012@due.udn.vn',
            password='123456'
        )

        form = UserRegisterForm(data=self.valid_data)
        self.assertFalse(form.is_valid())

    # 5 username trùng
    def test_username_duplicate(self):
        User.objects.create_user(
            username='testuser',
            email='999999999999@due.udn.vn',
            password='123456'
        )

        form = UserRegisterForm(data=self.valid_data)
        self.assertFalse(form.is_valid())

    # 6 phone sai
    def test_phone_invalid(self):
        data = self.valid_data.copy()
        data['phone_number'] = 'abc123'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())