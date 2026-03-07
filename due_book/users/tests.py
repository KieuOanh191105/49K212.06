from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages


class UserLoginViewTests(TestCase):
    """Test cases cho chức năng đăng nhập"""

    def setUp(self):
        """Tạo user test trước mỗi test case"""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.login_url = reverse('users:user_login')
        self.home_url = reverse('books:home')

    def test_login_page_renders_correctly(self):
        """Test trang đăng nhập hiển thị đúng"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_login.html')
        self.assertIn('form', response.context)

    def test_login_success_with_valid_credentials(self):
        """Test đăng nhập thành công với thông tin hợp lệ"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')
        self.assertRedirects(response, self.home_url)

    def test_login_success_with_message(self):
        """Test đăng nhập thành công có thông báo"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertIn('Dang nhap thanh cong', messages_list[0].message)

    def test_login_fail_with_wrong_password(self):
        """Test đăng nhập thất bại với sai mật khẩu"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_login_fail_with_wrong_username(self):
        """Test đăng nhập thất bại với sai tên đăng nhập"""
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'testpassword123'
        })
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_login_fail_with_empty_credentials(self):
        """Test đăng nhập thất bại khi để trống thông tin"""
        response = self.client.post(self.login_url, {
            'username': '',
            'password': ''
        })
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_login_fail_with_message(self):
        """Test đăng nhập thất bại có thông báo lỗi"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertIn('khong dung', messages_list[0].message)

    def test_login_redirect_to_next_url(self):
        """Test đăng nhập chuyển hướng đến URL 'next'"""
        next_url = reverse('users:user_register')
        login_url_with_next = f"{self.login_url}?next={next_url}"
        
        response = self.client.post(login_url_with_next, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, next_url)

    def test_login_with_inactive_user(self):
        """Test đăng nhập với user bị vô hiệu hóa"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_already_logged_in_user_access_login_page(self):
        """Test user đã đăng nhập truy cập trang đăng nhập"""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.login_url)
        
        # Vẫn có thể truy cập trang đăng nhập
        self.assertEqual(response.status_code, 200)


class UserLogoutViewTests(TestCase):
    """Test cases cho chức năng đăng xuất"""

    def setUp(self):
        """Tạo user test và đăng nhập trước mỗi test case"""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.login_url = reverse('users:user_login')
        self.logout_url = reverse('users:user_logout')
        self.home_url = reverse('books:home')

    def test_logout_success(self):
        """Test đăng xuất thành công"""
        # Đăng nhập trước
        self.client.login(username='testuser', password='testpassword123')
        
        # Đảm bảo đã đăng nhập
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Đăng xuất
        response = self.client.get(self.logout_url, follow=True)
        
        # Kiểm tra đã đăng xuất
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, self.home_url)

    def test_logout_with_message(self):
        """Test đăng xuất có thông báo"""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.logout_url, follow=True)
        
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)
        self.assertIn('dang xuat', messages_list[0].message)

    def test_logout_without_login(self):
        """Test đăng xuất khi chưa đăng nhập"""
        response = self.client.get(self.logout_url, follow=True)
        
        # Vẫn chuyển hướng về home
        self.assertRedirects(response, self.home_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirect_to_home(self):
        """Test đăng xuất chuyển hướng về trang chủ"""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.logout_url)
        
        self.assertRedirects(response, self.home_url)


class LoginLogoutIntegrationTests(TestCase):
    """Test cases tích hợp cho luồng đăng nhập/đăng xuất"""

    def setUp(self):
        """Tạo user test trước mỗi test case"""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.login_url = reverse('users:user_login')
        self.logout_url = reverse('users:user_logout')
        self.home_url = reverse('books:home')

    def test_login_then_logout_flow(self):
        """Test luồng đăng nhập rồi đăng xuất"""
        # Bước 1: Đăng nhập
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)
        
        # Bước 2: Đăng xuất
        logout_response = self.client.get(self.logout_url, follow=True)
        
        self.assertFalse(logout_response.wsgi_request.user.is_authenticated)

    def test_multiple_login_attempts(self):
        """Test nhiều lần đăng nhập liên tiếp"""
        for _ in range(3):
            self.client.logout()
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'testpassword123'
            }, follow=True)
            self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_session_data_after_login(self):
        """Test session data sau khi đăng nhập"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        # Kiểm tra session có auth user id
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(
            str(self.user.pk),
            self.client.session['_auth_user_id']
        )

    def test_session_cleared_after_logout(self):
        """Test session được xóa sau khi đăng xuất"""
        self.client.login(username='testuser', password='testpassword123')
        self.assertIn('_auth_user_id', self.client.session)
        
        self.client.get(self.logout_url, follow=True)
        
        # Session được cleared
        self.assertFalse(self.client.session.get('_auth_user_id'))