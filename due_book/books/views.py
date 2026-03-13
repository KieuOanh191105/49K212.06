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
    """
    Danh sách sách
    - Tìm kiếm theo tên sách, mô tả, môn học
    - Phân trang 20 sách/trang
    - Dễ mở rộng thêm bộ lọc sau này
    """
    books = Book.objects.filter(status='available').select_related('subject', 'seller')
    
    # Tìm kiếm đơn giản (sẽ mở rộng thêm bộ lọc sau)
    query = request.GET.get('q', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query)
        )
    
    # Sắp xếp (mặc định mới nhất)
    books = books.order_by('-created_at')
    
    # Phân trang - 20 sách/trang
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Tổng số sách (để hiển thị)
    total_count = paginator.count
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_count': total_count,
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
@login_required
def edit_book(request, pk):
    """
    Chỉnh sửa bài đăng sách
    - Chỉ chủ bài đăng (seller) mới được sửa
    - Sử dụng BookForm
    """
    book = get_object_or_404(Book, pk=pk)
    
    # Kiểm tra quyền: chỉ seller mới được sửa
    if book.seller != request.user:
        messages.error(request, "Bạn không có quyền chỉnh sửa bài đăng này.")
        return redirect('books:my_books')
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật bài đăng thành công!")
                return redirect('books:my_books')
            except Exception as e:
                messages.error(request, "Có lỗi xảy ra. Vui lòng thử lại.")
        else:
            messages.error(request, "Có lỗi trong form. Vui lòng kiểm tra lại.")
    else:
        form = BookForm(instance=book)
    
    context = {
        'form': form,
        'book': book,
        'title': 'Chỉnh sửa bài đăng',
        'subjects': Subject.objects.all(),
    }
    return render(request, 'books/edit_book.html', context)


@login_required
def book_update(request, pk):
    """
    Redirect đến edit_book (giữ lại để tương thích ngược)
    """
    return redirect('books:edit_book', pk=pk)


# ==================== DELETE BOOK (XÓA BÀI ĐĂNG) ====================
@login_required
def delete_book(request, pk):
    """
    Xóa bài đăng sách
    - Chỉ chủ bài đăng (seller) mới được xóa
    - Chỉ chấp nhận POST method
    """
    book = get_object_or_404(Book, pk=pk)
    
    # Kiểm tra quyền: chỉ seller mới được xóa
    if book.seller != request.user:
        messages.error(request, "Bạn không có quyền xóa bài đăng này.")
        return redirect('books:my_books')
    
    # Chỉ chấp nhận POST method
    if request.method == 'POST':
        try:
            book_title = book.title
            book.delete()
            messages.success(request, f'Đã xóa bài đăng "{book_title}" thành công!')
        except Exception as e:
            messages.error(request, "Có lỗi xảy ra khi xóa. Vui lòng thử lại.")
    else:
        messages.error(request, "Yêu cầu không hợp lệ.")
    
    return redirect('books:my_books')


@login_required
def book_delete(request, pk):
    """
    Redirect đến delete_book (giữ lại để tương thích ngược)
    """
    return redirect('books:delete_book', pk=pk)


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