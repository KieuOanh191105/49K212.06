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
            'password': 'test1234',
            'confirm_password': 'test1234',
            'phone_number': '0912345678',
            'facebook_link': 'https://facebook.com/test',
            'zalo_link': 'https://zalo.me/0912345678',
            'student_id': '231121521224',
            'address': 'Da Nang'
        }

    # TC01 - đăng ký hợp lệ
    def test_register_valid(self):
        form = UserRegisterForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    # TC02 - email rỗng
    def test_email_empty(self):
        data = self.valid_data.copy()
        data['email'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC03 - email sai domain
    def test_email_invalid_domain(self):
        data = self.valid_data.copy()
        data['email'] = 'abc@gmail.com'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC04 - email sai format (không đủ 12 số)
    def test_email_wrong_format(self):
        data = self.valid_data.copy()
        data['email'] = '123@due.udn.vn'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC05 - email trùng
    def test_email_duplicate(self):
        User.objects.create_user(
            username='olduser',
            email='123456789012@due.udn.vn',
            password='test1234'
        )

        form = UserRegisterForm(data=self.valid_data)
        self.assertFalse(form.is_valid())

    # TC06 - username trùng
    def test_username_duplicate(self):
        User.objects.create_user(
            username='testuser',
            email='999999999999@due.udn.vn',
            password='test1234'
        )

        form = UserRegisterForm(data=self.valid_data)
        self.assertFalse(form.is_valid())

    # TC07 - mật khẩu không khớp
    def test_password_not_match(self):
        data = self.valid_data.copy()
        data['confirm_password'] = 'abcd1234'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC08 - mật khẩu < 8 ký tự
    def test_password_too_short(self):
        data = self.valid_data.copy()
        data['password'] = '123456'
        data['confirm_password'] = '123456'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC09 - mật khẩu không có số
    def test_password_no_number(self):
        data = self.valid_data.copy()
        data['password'] = 'abcdefgh'
        data['confirm_password'] = 'abcdefgh'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC10 - phone rỗng
    def test_phone_empty(self):
        data = self.valid_data.copy()
        data['phone_number'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC11 - phone không phải số
    def test_phone_invalid(self):
        data = self.valid_data.copy()
        data['phone_number'] = 'abc123'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC12 - phone không đủ 10 số
    def test_phone_length_invalid(self):
        data = self.valid_data.copy()
        data['phone_number'] = '091234'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC13 - facebook rỗng
    def test_facebook_empty(self):
        data = self.valid_data.copy()
        data['facebook_link'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC14 - facebook sai format
    def test_facebook_invalid(self):
        data = self.valid_data.copy()
        data['facebook_link'] = 'facebook.com/test'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC15 - zalo rỗng
    def test_zalo_empty(self):
        data = self.valid_data.copy()
        data['zalo_link'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    # TC16 - thiếu field → form invalid
    def test_missing_required_field(self):
        data = self.valid_data.copy()
        del data['username']
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())