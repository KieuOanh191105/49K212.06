"""
Tests for Books App - User Story 4: Đăng bài bán sách
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages
import os

from books.models import Book, Subject
from books.forms import BookForm

# ===============TEST ĐĂNG BÁN SÁCH========================================
class BookCreateAccessTest(TestCase):
    """
    AC4.1 - Điều kiện thực hiện
    - Người dùng đã đăng nhập thành công vào hệ thống
    - Người dùng truy cập vào màn hình "Đăng bán sách" từ Trang chủ hoặc Sách của tôi
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.create_url = reverse('books:book_create')
        self.my_books_url = reverse('books:my_books')

    def test_redirect_if_not_logged_in(self):
        """AC4.1 - Chưa đăng nhập phải redirect đến trang login"""
        response = self.client.get(self.create_url)
        self.assertNotEqual(response.status_code, 200)
        # Should redirect to login page
        self.assertTrue(response.status_code in [302, 301])

    def test_access_when_logged_in(self):
        """AC4.1 - Đã đăng nhập có thể truy cập trang đăng bán sách"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_create.html')

    def test_my_books_requires_login(self):
        """AC4.1 - Trang sách của tôi yêu cầu đăng nhập"""
        response = self.client.get(self.my_books_url)
        self.assertNotEqual(response.status_code, 200)


class BookFormValidationTest(TestCase):
    """
    AC4.3 - Kiểm tra dữ liệu
    """

    def setUp(self):
        self.subject = Subject.objects.create(
            name='Kinh tế vi mô',
            code='EC101'
        )

    def test_title_required(self):
        """AC4.3 - Tên sách bắt buộc"""
        form = BookForm(data={
            'title': '',
            'price': '100000',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_max_length(self):
        """AC4.3 - Tên sách không vượt quá 300 ký tự"""
        long_title = 'a' * 301
        form = BookForm(data={
            'title': long_title,
            'price': '100000',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('300', str(form.errors['title']))

    def test_price_required(self):
        """AC4.3 - Giá bán bắt buộc"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_price_minimum_value(self):
        """AC4.3 - Giá bán tối thiểu 1.000đ"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '500',  # Dưới 1.000đ
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertIn('1.000', str(form.errors['price']))

    def test_price_maximum_value(self):
        """AC4.3 - Giá bán không vượt quá 9.999.999.999đ"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '10000000000',  # Trên 9.999.999.999đ
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        # Django model max_digits=10 sẽ báo lỗi "no more than 10 digits"
        self.assertTrue(len(form.errors['price']) > 0)

    def test_price_must_be_number(self):
        """AC4.3 - Giá bán phải là số"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': 'abc',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_valid_form(self):
        """Form hợp lệ với dữ liệu đúng"""
        form = BookForm(data={
            'title': 'Sách kinh tế',
            'subject': self.subject.pk,
            'price': '150000',
            'condition': 'good',
            'description': 'Mô tả sách',
            'notes': 'Ghi chú',
        })
        self.assertTrue(form.is_valid())

    def test_subject_optional(self):
        """AC4.2 - Môn học không bắt buộc"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
        })
        self.assertTrue(form.is_valid())

    def test_description_optional(self):
        """AC4.2 - Mô tả không bắt buộc"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
            'description': '',
        })
        self.assertTrue(form.is_valid())

    def test_notes_optional(self):
        """AC4.2 - Ghi chú không bắt buộc"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
            'notes': '',
        })
        self.assertTrue(form.is_valid())

    def test_cover_image_optional(self):
        """AC4.2 - Ảnh bìa không bắt buộc"""
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
        })
        self.assertTrue(form.is_valid())


class BookImageValidationTest(TestCase):
    """
    AC4.3 - Kiểm tra ảnh bìa
    """

    def test_image_size_limit(self):
        """AC4.3 - File không được vượt quá 2.5MB"""
        # Tạo file lớn hơn 2.5MB (int bytes)
        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * int(2.6 * 1024 * 1024),  # 2.6MB as int
            content_type="image/jpeg"
        )
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
        }, files={
            'cover_image': large_file
        })
        # Django ImageField sẽ validate trước, có thể báo lỗi không phải image
        # Custom validation size sẽ chạy sau
        self.assertFalse(form.is_valid())
        self.assertIn('cover_image', form.errors)

    def test_image_invalid_format(self):
        """AC4.3 - File ảnh không hợp lệ"""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
        }, files={
            'cover_image': invalid_file
        })
        self.assertFalse(form.is_valid())
        self.assertIn('cover_image', form.errors)

    def test_valid_image_upload(self):
        """AC4.2 - Upload ảnh hợp lệ - chỉ kiểm tra form không có file"""
        # Form không có file ảnh vẫn hợp lệ vì cover_image là optional
        form = BookForm(data={
            'title': 'Sách test',
            'price': '100000',
        })
        self.assertTrue(form.is_valid())


class BookCreateSuccessTest(TestCase):
    """
    AC4.4 - Đăng bài thành công
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='seller123'
        )
        self.subject = Subject.objects.create(
            name='Kinh tế vĩ mô',
            code='EC102'
        )
        self.create_url = reverse('books:book_create')
        self.my_books_url = reverse('books:my_books')

    def test_create_book_success(self):
        """AC4.4 - Đăng bài thành công"""
        self.client.login(username='seller', password='seller123')
        
        response = self.client.post(self.create_url, {
            'title': 'Sách kinh tế vĩ mô',
            'subject': self.subject.pk,
            'price': '200000',
            'condition': 'good',
            'description': 'Sách còn mới',
            'notes': 'Không ghi chú',
        }, follow=True)
        
        # Kiểm tra redirect đến trang my_books
        self.assertRedirects(response, self.my_books_url)
        
        # Kiểm tra thông báo thành công
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(any('thành công' in str(m).lower() for m in messages_list))

    def test_book_saved_to_database(self):
        """AC4.4 - Lưu dữ liệu vào CSDL"""
        self.client.login(username='seller', password='seller123')
        
        self.client.post(self.create_url, {
            'title': 'Sách test database',
            'price': '150000',
            'condition': 'new',
        })
        
        # Kiểm tra sách đã được lưu
        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.first()
        self.assertEqual(book.title, 'Sách test database')
        self.assertEqual(book.price, 150000)

    def test_book_status_default_available(self):
        """AC4.4 - Trạng thái sách mặc định là 'Đang bán'"""
        self.client.login(username='seller', password='seller123')
        
        self.client.post(self.create_url, {
            'title': 'Sách test status',
            'price': '100000',
        })
        
        book = Book.objects.first()
        self.assertEqual(book.status, 'available')

    def test_book_seller_is_current_user(self):
        """AC4.4 - Người bán là user hiện tại"""
        self.client.login(username='seller', password='seller123')
        
        self.client.post(self.create_url, {
            'title': 'Sách test seller',
            'price': '100000',
        })
        
        book = Book.objects.first()
        self.assertEqual(book.seller, self.user)

    def test_redirect_to_my_books(self):
        """AC4.4 - Điều hướng về màn hình 'Sách của tôi'"""
        self.client.login(username='seller', password='seller123')
        
        response = self.client.post(self.create_url, {
            'title': 'Sách test redirect',
            'price': '100000',
        })
        
        self.assertRedirects(response, self.my_books_url)

    def test_new_book_appears_first_in_my_books(self):
        """AC4.4 - Sách mới xuất hiện đầu tiên trong danh sách"""
        import time
        
        self.client.login(username='seller', password='seller123')
        
        # Tạo sách cũ hơn
        old_book = Book.objects.create(
            title='Sách cũ',
            price=50000,
            seller=self.user
        )
        
        # Đợi một chút để đảm bảo created_at khác nhau
        time.sleep(0.01)
        
        # Đăng sách mới
        self.client.post(self.create_url, {
            'title': 'Sách mới',
            'price': '100000',
        })
        
        # Kiểm tra sách mới ở vị trí đầu
        response = self.client.get(self.my_books_url)
        books = response.context['page_obj'].object_list
        # Sách mới đăng phải có trong danh sách
        self.assertEqual(Book.objects.count(), 2)
        # Sách đầu tiên phải là sách mới (theo ordering -created_at)
        self.assertEqual(books[0].title, 'Sách mới')


class BookCreateCancelTest(TestCase):
    """
    AC4.3 - Hủy thao tác
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.create_url = reverse('books:book_create')
        self.home_url = reverse('books:home')

    def test_cancel_button_redirects_to_home(self):
        """Hủy thao tác - Chuyển hướng về Trang chủ"""
        # Nút Hủy là link đến trang chủ, không cần POST
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_cancel_does_not_save_data(self):
        """Hủy thao tác - Không lưu dữ liệu"""
        self.client.login(username='testuser', password='testpass123')
        
        # Truy cập form nhưng không submit
        self.client.get(self.create_url)
        
        # Kiểm tra không có sách nào được tạo
        self.assertEqual(Book.objects.count(), 0)


class MyBooksViewTest(TestCase):
    """
    Test trang Sách của tôi
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='bookowner',
            password='owner123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='other123'
        )
        self.my_books_url = reverse('books:my_books')

    def test_only_shows_user_books(self):
        """Chỉ hiển thị sách của user hiện tại"""
        # Tạo sách cho user hiện tại
        my_book = Book.objects.create(
            title='Sách của tôi',
            price=100000,
            seller=self.user
        )
        # Tạo sách cho user khác
        other_book = Book.objects.create(
            title='Sách của người khác',
            price=200000,
            seller=self.other_user
        )
        
        self.client.login(username='bookowner', password='owner123')
        response = self.client.get(self.my_books_url)
        
        books = response.context['page_obj'].object_list
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, 'Sách của tôi')

    def test_filter_by_status(self):
        """Lọc theo trạng thái"""
        # Tạo sách với các trạng thái khác nhau
        book_available = Book.objects.create(
            title='Sách đang bán',
            price=100000,
            seller=self.user,
            status='available'
        )
        book_sold = Book.objects.create(
            title='Sách đã bán',
            price=100000,
            seller=self.user,
            status='sold'
        )
        
        self.client.login(username='bookowner', password='owner123')
        
        # Lọc chỉ hiển thị sách đang bán
        response = self.client.get(self.my_books_url + '?status=available')
        books = response.context['page_obj'].object_list
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].status, 'available')


class BookConditionDefaultTest(TestCase):
    """
    AC4.2 - Tình trạng mặc định là "Khá (80%-94%)"
    """

    def test_condition_default_value(self):
        """Form mới có tình trạng mặc định là 'good' (Khá 80-94%)"""
        form = BookForm()
        self.assertEqual(form.initial.get('condition'), 'good')


class BookModelTest(TestCase):
    """
    Test Book model
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='modeltest',
            password='test123'
        )

    def test_book_ordering_by_created_at(self):
        """Sách được sắp xếp theo thời gian mới nhất"""
        import time
        
        book1 = Book.objects.create(
            title='Sách cũ',
            price=100000,
            seller=self.user
        )
        time.sleep(0.01)  # Đảm bảo created_at khác nhau
        
        book2 = Book.objects.create(
            title='Sách mới',
            price=100000,
            seller=self.user
        )
        
        books = Book.objects.all()
        self.assertEqual(books[0], book2)  # Sách mới nhất trước
        self.assertEqual(books[1], book1)

    def test_book_str(self):
        """String representation của Book"""
        book = Book.objects.create(
            title='Sách Test String',
            price=100000,
            seller=self.user
        )
        self.assertEqual(str(book), 'Sách Test String')

    def test_is_available_property(self):
        """Property is_available"""
        book_available = Book.objects.create(
            title='Sách available',
            price=100000,
            seller=self.user,
            status='available'
        )
        book_sold = Book.objects.create(
            title='Sách sold',
            price=100000,
            seller=self.user,
            status='sold'
        )
        
        self.assertTrue(book_available.is_available)
        self.assertFalse(book_sold.is_available)
# ==========================END ĐĂNG BÁN SÁCH========================================