"""
Views for Books App
US4 - Đăng bài bán sách
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Book, Subject
from .forms import BookForm


# ==================== HOME & BOOK LIST ====================
def home(request):
    """Trang chủ"""
    return render(request, 'books/home.html')


def book_list(request):
    """Danh sách sách"""
    books = Book.objects.filter(status='available').select_related('subject', 'seller')
    
    # Tìm kiếm
    query = request.GET.get('q', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query)
        )
    
    # Phân trang
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'books/book_list.html', context)


# ==================== MY BOOKS (Sách của tôi) ====================
@login_required
def my_books(request):
    """
    Danh sách sách của tôi
    AC4.4 - Sau khi đăng bài, chuyển hướng về trang này
    """
    books = Book.objects.filter(seller=request.user)
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status', '')
    if status_filter:
        books = books.filter(status=status_filter)
    
    # Phân trang
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': Book.STATUS_CHOICES,
    }
    return render(request, 'books/my_books.html', context)


# ==================== CREATE BOOK (ĐĂNG BÁN SÁCH) ====================
class BookCreateView(LoginRequiredMixin, CreateView):
    """
    Đăng bài bán sách mới
    US4 - AC4.1 đến AC4.5
    """
    model = Book
    form_class = BookForm
    template_name = 'books/book_create.html'
    # Sẽ được ghi đè trong get_success_url
    success_url = reverse_lazy('books:my_books')

    def get_success_url(self):
        """AC4.4 - Điều hướng về màn hình 'Sách của tôi'"""
        return reverse('books:my_books')

    def form_valid(self, form):
        """
        Xử lý khi form hợp lệ
        AC4.4 - Đăng bài thành công
        """
        try:
            # Gán người bán là user hiện tại
            form.instance.seller = self.request.user
            
            # Trạng thái mặc định là 'available' (Đang bán)
            # Đã được set trong model, nhưng đảm bảo ở đây
            form.instance.status = 'available'
            
            # Lưu vào CSDL
            self.object = form.save()
            
            # Thông báo thành công (sẽ tự động biến mất sau 3 giây - xử lý bằng JS)
            messages.success(
                self.request, 
                'Đăng bài thành công!'
            )
            
            return super().form_valid(form)
            
        except Exception as e:
            # AC4.5 - Xử lý ngoại lệ (mất kết nối, v.v.)
            messages.error(
                self.request, 
                'Có lỗi xảy ra. Vui lòng thử lại.'
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Xử lý khi form không hợp lệ
        AC4.3 - Kiểm tra dữ liệu
        """
        # Lấy tất cả các lỗi
        errors = form.errors
        
        # Hiển thị thông báo lỗi tổng quát
        messages.error(
            self.request, 
            'Có lỗi trong form. Vui lòng kiểm tra lại.'
        )
        
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Thêm context cho template"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Đăng bán sách'
        context['subjects'] = Subject.objects.all()
        return context


# ==================== UPDATE BOOK (CHỈNH SỬA BÀI ĐĂNG) ====================
class BookUpdateView(LoginRequiredMixin, UpdateView):
    """Chỉnh sửa bài đăng"""

    model = Book
    form_class = BookForm
    template_name = 'books/book_update.html'

    def get_queryset(self):
        """Chỉ cho phép seller chỉnh sửa sách của mình"""
        return super().get_queryset().filter(seller=self.request.user)

    def get_success_url(self):
        return reverse('books:my_books')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật bài đăng thành công!')
        return super().form_valid(form)


# ==================== DELETE BOOK (XÓA BÀI ĐĂNG) ====================
class BookDeleteView(LoginRequiredMixin, DeleteView):
    """Xóa bài đăng"""

    model = Book
    success_url = reverse_lazy('books:my_books')

    def get_queryset(self):
        """Chỉ cho phép seller xóa sách của mình"""
        return super().get_queryset().filter(seller=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Đã xóa bài đăng thành công!')
        return super().delete(request, *args, **kwargs)


# ==================== BOOK DETAIL (CHI TIẾT SÁCH) ====================
class BookDetailView(DetailView):
    """Chi tiết sách"""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Tăng lượt xem
        obj.increment_view()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_books'] = Book.objects.filter(
            subject=self.object.subject,
            status='available'
        ).exclude(pk=self.object.pk)[:4]
        return context