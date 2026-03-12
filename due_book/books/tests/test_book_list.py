"""
Tests for Books App - User Story 5: Xem danh sách sách với phân trang

AC5.1 - Điều kiện truy cập
AC5.2 - Hiển thị thẻ sách
AC5.3 - Phân trang
AC5.4 - Trạng thái không có dữ liệu
"""
import time
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from books.models import Book, Subject


class BookListViewTests(TestCase):
    """
    Test suite cho User Story 5: Xem danh sách sách với phân trang
    """
    
    def setUp(self):
        """
        Setup dữ liệu test chung
        """
        self.client = Client()
        
        # Tạo user để test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Tạo subject để test
        self.subject = Subject.objects.create(
            name='Kinh tế vi mô',
            code='EC101'
        )
        
        # URL danh sách sách
        self.book_list_url = reverse('books:book_list')
    
    # ==================== HELPER METHODS ====================
    
    def create_book(self, title, price=100000, status='available', 
                    condition='good', subject=None, seller=None, 
                    cover_image=None, delay=0):
        """
        Helper method để tạo sách test
        
        Args:
            title: Tên sách
            price: Giá bán
            status: Trạng thái (available, sold, reserved)
            condition: Tình trạng
            subject: Môn học
            seller: Người bán
            cover_image: Ảnh bìa
            delay: Delay để tạo created_at khác nhau
        """
        if seller is None:
            seller = self.user
        if subject is None:
            subject = self.subject
            
        if delay > 0:
            time.sleep(delay)
            
        return Book.objects.create(
            title=title,
            price=price,
            status=status,
            condition=condition,
            subject=subject,
            seller=seller,
            cover_image=cover_image
        )
    
    # ==================== AC5.1: Điều kiện truy cập ====================
    
    def test_book_list_accessible_for_guest(self):
        """
        AC5.1 - Guest có thể truy cập trang danh sách sách
        
        Điều kiện:
        - User chưa đăng nhập
        
        Expected:
        - Response status code = 200
        - Template book_list.html được sử dụng
        """
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_list.html')
    
    def test_book_list_accessible_for_logged_user(self):
        """
        AC5.1 - User đã đăng nhập có thể truy cập trang danh sách sách
        
        Điều kiện:
        - User đã đăng nhập
        
        Expected:
        - Response status code = 200
        - Template book_list.html được sử dụng
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_list.html')
    
    # ==================== AC5.2: Hiển thị thẻ sách ====================
    
    def test_only_selling_books_displayed(self):
        """
        AC5.2.1 - Chỉ hiển thị sách trạng thái "Đang bán" (available)
        
        Điều kiện:
        - Tạo 3 sách với status khác nhau:
          * 1 available (Đang bán)
          * 1 sold (Đã bán)
          * 1 reserved (Đang giữ)
        
        Expected:
        - Chỉ sách available xuất hiện trong response
        """
        # Tạo sách với các trạng thái khác nhau
        book_available = self.create_book(
            title='Sách đang bán',
            status='available'
        )
        book_sold = self.create_book(
            title='Sách đã bán',
            status='sold'
        )
        book_reserved = self.create_book(
            title='Sách đang giữ',
            status='reserved'
        )
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra context
        books_in_context = response.context['page_obj'].object_list
        
        # Chỉ có 1 sách available
        self.assertEqual(len(books_in_context), 1)
        self.assertEqual(books_in_context[0].status, 'available')
        self.assertEqual(books_in_context[0].title, 'Sách đang bán')
        
        # Kiểm tra HTML không chứa sách sold/reserved
        self.assertContains(response, 'Sách đang bán')
        self.assertNotContains(response, 'Sách đã bán')
        self.assertNotContains(response, 'Sách đang giữ')
    
    def test_books_sorted_newest_first(self):
        """
        AC5.2.2 - Sách mới nhất hiển thị đầu tiên
        
        Điều kiện:
        - Tạo 3 sách với created_at khác nhau
        
        Expected:
        - Sách tạo sau cùng hiển thị đầu tiên (newest first)
        """
        # Tạo sách theo thứ tự thời gian
        book_old = self.create_book(title='Sách cũ nhất')
        time.sleep(0.01)  # Đảm bảo created_at khác nhau
        
        book_middle = self.create_book(title='Sách giữa')
        time.sleep(0.01)
        
        book_new = self.create_book(title='Sách mới nhất')
        
        response = self.client.get(self.book_list_url)
        
        books_in_context = list(response.context['page_obj'].object_list)
        
        # Kiểm tra thứ tự: mới nhất trước
        self.assertEqual(books_in_context[0].title, 'Sách mới nhất')
        self.assertEqual(books_in_context[1].title, 'Sách giữa')
        self.assertEqual(books_in_context[2].title, 'Sách cũ nhất')
    
    def test_book_card_displays_title(self):
        """
        AC5.2.3 - Card sách hiển thị tiêu đề
        """
        book = self.create_book(title='Giáo trình Kinh tế')
        
        response = self.client.get(self.book_list_url)
        
        self.assertContains(response, 'Giáo trình Kinh tế')
    
    def test_book_card_displays_price(self):
        """
        AC5.2.3 - Card sách hiển thị giá
        """
        book = self.create_book(title='Sách test giá', price=150000)
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra giá có trong response
        self.assertContains(response, '150000')
    
    def test_book_card_displays_condition(self):
        """
        AC5.2.3 - Card sách hiển thị tình trạng
        """
        book = self.create_book(
            title='Sách test tình trạng',
            condition='new'
        )
        
        response = self.client.get(self.book_list_url)
        
        # Condition display: "Mới 100%"
        self.assertContains(response, 'Mới 100%')
    
    def test_book_card_displays_subject(self):
        """
        AC5.2.3 - Card sách hiển thị môn học (nếu có)
        """
        book = self.create_book(
            title='Sách có môn học',
            subject=self.subject
        )
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra subject name có trong response
        self.assertContains(response, 'Kinh tế vi mô')
    
    def test_default_image_displayed(self):
        """
        AC5.2.4 - Hiển thị ảnh mặc định khi cover_image = null
        
        Điều kiện:
        - Sách không có cover_image (null)
        
        Expected:
        - HTML hiển thị placeholder image icon
        """
        book = self.create_book(
            title='Sách không có ảnh',
            cover_image=None
        )
        
        response = self.client.get(self.book_list_url)
        
        # Template sử dụng icon placeholder khi không có ảnh
        # Kiểm tra class placeholder-image hoặc icon book
        self.assertContains(response, 'placeholder-image')
        self.assertContains(response, 'fa-book')
    
    def test_price_format_vnd(self):
        """
        AC5.2.5 - Giá được format theo VNĐ
        
        Điều kiện:
        - Sách có giá 150000
        
        Expected:
        - HTML hiển thị "150000đ" (với suffix "đ")
        - Không hiển thị raw number không có format
        """
        book = self.create_book(title='Sách test format giá', price=150000)
        
        response = self.client.get(self.book_list_url)
        
        # Template sử dụng {{ book.price|floatformat:0 }}đ
        # Kiểm tra có suffix "đ"
        self.assertContains(response, '150000đ')
    
    def test_price_format_with_large_value(self):
        """
        AC5.2.5 - Test format giá với giá trị lớn
        """
        book = self.create_book(title='Sách giá cao', price=1500000)
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra format giá lớn
        self.assertContains(response, '1500000đ')
    
    # ==================== AC5.3: Phân trang ====================
    
    def test_pagination_page_size(self):
        """
        AC5.3 - Test pagination page size = 20 books/page
        
        Điều kiện:
        - Tạo 25 sách selling
        
        Expected:
        - Page 1: 20 books
        """
        # Tạo 25 sách
        for i in range(25):
            self.create_book(title=f'Sách test phân trang {i+1}')
        
        response = self.client.get(self.book_list_url)
        
        page_obj = response.context['page_obj']
        
        # Kiểm tra page 1 có 20 sách
        self.assertEqual(len(page_obj.object_list), 20)
        
        # Kiểm tra tổng số sách
        self.assertEqual(response.context['total_count'], 25)
    
    def test_pagination_page_two(self):
        """
        AC5.3 - Test pagination page 2
        
        Điều kiện:
        - Tạo 25 sách selling
        
        Expected:
        - Page 2: 5 books
        - Status 200
        """
        # Tạo 25 sách
        for i in range(25):
            self.create_book(title=f'Sách page 2 test {i+1}')
        
        # Request page 2
        response = self.client.get(self.book_list_url + '?page=2')
        
        self.assertEqual(response.status_code, 200)
        
        page_obj = response.context['page_obj']
        
        # Kiểm tra page 2 có 5 sách
        self.assertEqual(len(page_obj.object_list), 5)
        
        # Kiểm tra đang ở page 2
        self.assertEqual(page_obj.number, 2)
    
    def test_previous_button_disabled_on_first_page(self):
        """
        AC5.3 - Test previous button disabled khi ở page 1
        
        Điều kiện:
        - Tạo nhiều sách để có pagination
        - Request page 1
        
        Expected:
        - HTML chứa class "disabled" cho previous button
        """
        # Tạo 25 sách để có pagination
        for i in range(25):
            self.create_book(title=f'Sách test prev btn {i+1}')
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra previous button disabled
        # Template: <li class="page-item disabled"> cho previous
        self.assertContains(response, 'page-item disabled')
        
        # Kiểm tra không có trang trước
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
    
    def test_next_button_disabled_on_last_page(self):
        """
        AC5.3 - Test next button disabled khi ở trang cuối
        
        Điều kiện:
        - Tạo 25 sách (2 trang)
        - Request page 2 (trang cuối)
        
        Expected:
        - HTML chứa class "disabled" cho next button
        """
        # Tạo 25 sách để có 2 trang
        for i in range(25):
            self.create_book(title=f'Sách test next btn {i+1}')
        
        # Request page 2 (trang cuối)
        response = self.client.get(self.book_list_url + '?page=2')
        
        # Kiểm tra next button disabled
        self.assertContains(response, 'page-item disabled')
        
        # Kiểm tra không có trang sau
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_next())
    
    def test_pagination_has_other_pages(self):
        """
        AC5.3 - Test pagination có nhiều trang
        """
        # Tạo 25 sách
        for i in range(25):
            self.create_book(title=f'Sách pagination test {i+1}')
        
        response = self.client.get(self.book_list_url)
        
        page_obj = response.context['page_obj']
        
        # Có nhiều hơn 1 trang
        self.assertTrue(page_obj.has_other_pages())
        
        # Tổng số trang = 2
        self.assertEqual(page_obj.paginator.num_pages, 2)
    
    def test_pagination_page_numbers_displayed(self):
        """
        AC5.3 - Test page numbers được hiển thị
        """
        # Tạo 25 sách
        for i in range(25):
            self.create_book(title=f'Sách page num test {i+1}')
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra có page info
        self.assertContains(response, 'Trang')
        self.assertContains(response, '1 / 2')
    
    # ==================== AC5.4: Trạng thái không có dữ liệu ====================
    
    def test_empty_state_message(self):
        """
        AC5.4 - Test empty state khi không có sách selling
        
        Điều kiện:
        - Database không có sách nào status='available'
        
        Expected:
        - HTML hiển thị message "Chưa có sách nào được đăng bán"
        - Không hiển thị grid sách
        - Không hiển thị pagination
        """
        # Không tạo sách nào, database rỗng
        
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Kiểm tra empty state message
        # Template hiển thị "Chưa có sách nào" khi không có sách
        self.assertContains(response, 'Chưa có sách nào')
        
        # Kiểm tra context không có sách
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 0)
        
        # Kiểm tra total_count = 0
        self.assertEqual(response.context['total_count'], 0)
    
    def test_empty_state_no_pagination(self):
        """
        AC5.4 - Không hiển thị pagination khi không có sách
        """
        response = self.client.get(self.book_list_url)
        
        page_obj = response.context['page_obj']
        
        # Không có trang khác (không có pagination)
        self.assertFalse(page_obj.has_other_pages())
        
        # Paginator có 0 pages hoặc 1 empty page
        self.assertEqual(page_obj.paginator.count, 0)
    
    def test_empty_state_with_only_non_available_books(self):
        """
        AC5.4 - Empty state khi chỉ có sách sold/reserved (không có available)
        """
        # Tạo sách sold và reserved
        book_sold = self.create_book(
            title='Sách đã bán',
            status='sold'
        )
        book_reserved = self.create_book(
            title='Sách đang giữ',
            status='reserved'
        )
        
        response = self.client.get(self.book_list_url)
        
        # Vẫn hiển thị empty state vì không có sách available
        self.assertContains(response, 'Chưa có sách nào')
        
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 0)
    
    # ==================== Additional Edge Cases ====================
    
    def test_pagination_invalid_page(self):
        """
        Test pagination với page number không hợp lệ
        """
        # Tạo 25 sách
        for i in range(25):
            self.create_book(title=f'Sách invalid page {i+1}')
        
        # Request page không tồn tại (page 999)
        # Django Paginator.get_page() sẽ trả về last page
        response = self.client.get(self.book_list_url + '?page=999')
        
        self.assertEqual(response.status_code, 200)
        
        # Django get_page() tự động redirect về last page
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.number, 2)  # Last page
    
    def test_pagination_negative_page(self):
        """
        Test pagination với page number âm
        """
        # Tạo 25 sách
        for i in range(25):
            self.create_book(title=f'Sách negative page {i+1}')
        
        # Request page âm
        # Django Paginator.get_page() sẽ trả về last page cho giá trị không hợp lệ
        response = self.client.get(self.book_list_url + '?page=-1')
        
        self.assertEqual(response.status_code, 200)
        
        page_obj = response.context['page_obj']
        # Django get_page() trả về last page cho page number < 1
        self.assertEqual(page_obj.number, 2)  # Last page
    
    def test_book_list_with_search_query(self):
        """
        Test danh sách sách với search query
        """
        # Tạo subject khác không chứa từ khóa tìm kiếm
        subject_math = Subject.objects.create(
            name='Toán học',
            code='MATH101'
        )
        
        book1 = self.create_book(title='Giáo trình Kinh tế')
        book2 = self.create_book(title='Sách Toán cao cấp', subject=subject_math)
        
        response = self.client.get(self.book_list_url + '?q=Kinh tế')
        
        self.assertEqual(response.status_code, 200)
        
        # Kiểm tra context chỉ chứa sách có "Kinh tế"
        books_in_context = list(response.context['page_obj'].object_list)
        self.assertEqual(len(books_in_context), 1)
        self.assertEqual(books_in_context[0].title, 'Giáo trình Kinh tế')
        
        # Kiểm tra sách có "Kinh tế" trong response
        self.assertContains(response, 'Giáo trình Kinh tế')
    
    def test_book_list_context_data(self):
        """
        Test context data của book list view
        """
        book = self.create_book(title='Sách test context')
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra các context variables
        self.assertIn('page_obj', response.context)
        self.assertIn('query', response.context)
        self.assertIn('total_count', response.context)
        
        # Kiểm tra giá trị
        self.assertEqual(response.context['query'], '')
        self.assertEqual(response.context['total_count'], 1)
    
    def test_multiple_books_display(self):
        """
        Test hiển thị nhiều sách cùng lúc
        """
        # Tạo 5 sách
        for i in range(5):
            self.create_book(title=f'Sách đa dạng {i+1}')
        
        response = self.client.get(self.book_list_url)
        
        # Kiểm tra tất cả sách được hiển thị
        for i in range(5):
            self.assertContains(response, f'Sách đa dạng {i+1}')
        
        # Kiểm tra số lượng trong context
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 5)


class BookListPaginationEdgeCasesTest(TestCase):
    """
    Test các edge case cho pagination
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.book_list_url = reverse('books:book_list')
    
    def create_books(self, count):
        """Helper để tạo nhiều sách"""
        books = []
        for i in range(count):
            books.append(Book.objects.create(
                title=f'Sách test {i+1}',
                price=100000,
                status='available',
                seller=self.user
            ))
        return books
    
    def test_exactly_20_books_one_page(self):
        """
        Test với chính xác 20 sách - chỉ 1 trang
        """
        self.create_books(20)
        
        response = self.client.get(self.book_list_url)
        
        page_obj = response.context['page_obj']
        
        # 20 sách trên 1 trang
        self.assertEqual(len(page_obj.object_list), 20)
        
        # Không có trang khác
        self.assertFalse(page_obj.has_other_pages())
    
    def test_exactly_40_books_two_pages(self):
        """
        Test với chính xác 40 sách - 2 trang
        """
        self.create_books(40)
        
        # Page 1
        response = self.client.get(self.book_list_url)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 20)
        self.assertTrue(page_obj.has_next())
        
        # Page 2
        response = self.client.get(self.book_list_url + '?page=2')
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 20)
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
    
    def test_21_books_second_page_has_one(self):
        """
        Test với 21 sách - page 2 có 1 sách
        """
        self.create_books(21)
        
        response = self.client.get(self.book_list_url + '?page=2')
        
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 1)