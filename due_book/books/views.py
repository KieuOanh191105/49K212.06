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

from .models import Book, Subject, PurchaseRequest
from .forms import BookForm, PurchaseRequestForm


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
        
        # Thêm context cho purchase request
        if self.request.user.is_authenticated:
            # Kiểm tra user đã gửi request cho sách này chưa
            existing_request = PurchaseRequest.objects.filter(
                book=self.object,
                buyer=self.request.user,
                status='pending'
            ).first()
            context['existing_request'] = existing_request
            context['purchase_form'] = PurchaseRequestForm()
        
        return context


# ==================== Yêu Cầu mua (US09) ====================

@login_required
def create_purchase_request(request, book_id):
    """
    Gửi yêu cầu mua sách - US09
    - Chỉ chấp nhận POST method
    - Kiểm tra: sách còn available, không phải chính chủ
    """
    book = get_object_or_404(Book, pk=book_id)
    
    # Kiểm tra sách còn bán không
    if not book.is_available:
        messages.error(request, 'Sách này hiện không còn bán.')
        return redirect('books:book_detail', pk=book_id)
    
    # Kiểm tra không phải chính chủ
    if book.seller == request.user:
        messages.error(request, 'Bạn không thể mua sách của chính mình!')
        return redirect('books:book_detail', pk=book_id)
    
    # Kiểm tra đã có request pending chưa
    existing_request = PurchaseRequest.objects.filter(
        book=book,
        buyer=request.user,
        status='pending'
    ).first()
    
    if existing_request:
        messages.warning(request, 'Bạn đã gửi yêu cầu mua sách này rồi. Vui lòng đợi người bán phản hồi.')
        return redirect('books:book_detail', pk=book_id)
    
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            try:
                purchase_request = form.save(commit=False)
                purchase_request.book = book
                purchase_request.buyer = request.user
                purchase_request.seller = book.seller
                purchase_request.save()
                
                messages.success(
                    request, 
                    f'Đã gửi yêu cầu mua sách thành công! Người bán sẽ sớm phản hồi.'
                )
                
                # TODO: Gửi email thông báo cho người bán (tùy chọn)
                # send_purchase_notification_email(purchase_request)
                
            except Exception as e:
                messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
        else:
            messages.error(request, 'Dữ liệu không hợp lệ.')
    else:
        messages.error(request, 'Yêu cầu không hợp lệ.')
    
    return redirect('books:book_detail', pk=book_id)


@login_required
def my_purchase_requests(request):
    """
    Danh sách yêu cầu mua sách của tôi (người mua)
    """
    requests_list = PurchaseRequest.objects.filter(
        buyer=request.user
    ).select_related('book', 'seller').order_by('-created_at')
    
    # Thống kê theo trạng thái
    pending_count = requests_list.filter(status='pending').count()
    approved_count = requests_list.filter(status='approved').count()
    rejected_count = requests_list.filter(status='rejected').count()
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests_list = requests_list.filter(status=status_filter)
    
    # Phân trang
    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': PurchaseRequest.STATUS_CHOICES,
        'title': 'Yêu cầu mua sách của tôi',
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'books/my_purchase_requests.html', context)


@login_required
def received_purchase_requests(request):
    """
    Danh sách yêu cầu mua sách nhận được (người bán xem)
    """
    requests_list = PurchaseRequest.objects.filter(
        seller=request.user
    ).select_related('book', 'buyer').order_by('-created_at')
    
    # Thống kê theo trạng thái
    pending_count = requests_list.filter(status='pending').count()
    approved_count = requests_list.filter(status='approved').count()
    rejected_count = requests_list.filter(status='rejected').count()
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests_list = requests_list.filter(status=status_filter)
    
    # Phân trang
    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': PurchaseRequest.STATUS_CHOICES,
        'title': 'Yêu cầu mua sách nhận được',
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'books/received_purchase_requests.html', context)


@login_required
def approve_purchase_request(request, request_id):
    """
    Người bán duyệt yêu cầu mua
    - Chỉ chấp nhận POST method
    - Cập nhật trạng thái request và sách
    """
    purchase_request = get_object_or_404(PurchaseRequest, pk=request_id)
    
    # Kiểm tra quyền: chỉ người bán mới được duyệt
    if purchase_request.seller != request.user:
        messages.error(request, 'Bạn không có quyền duyệt yêu cầu này.')
        return redirect('books:received_purchase_requests')
    
    # Kiểm tra request còn pending
    if not purchase_request.is_pending:
        messages.error(request, 'Yêu cầu này đã được xử lý rồi.')
        return redirect('books:received_purchase_requests')
    
    # Kiểm tra sách còn available
    if not purchase_request.book.is_available:
        messages.error(request, 'Sách này đã không còn bán.')
        return redirect('books:received_purchase_requests')
    
    if request.method == 'POST':
        try:
            purchase_request.approve()
            messages.success(
                request, 
                f'Đã duyệt yêu cầu mua "{purchase_request.book.title}". Sách đã được đánh dấu là đã bán.'
            )
        except Exception as e:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
    else:
        messages.error(request, 'Yêu cầu không hợp lệ.')
    
    return redirect('books:received_purchase_requests')


@login_required
def reject_purchase_request(request, request_id):
    """
    Người bán từ chối yêu cầu mua
    - Chỉ chấp nhận POST method
    """
    purchase_request = get_object_or_404(PurchaseRequest, pk=request_id)
    
    # Kiểm tra quyền: chỉ người bán mới được từ chối
    if purchase_request.seller != request.user:
        messages.error(request, 'Bạn không có quyền từ chối yêu cầu này.')
        return redirect('books:received_purchase_requests')
    
    # Kiểm tra request còn pending
    if not purchase_request.is_pending:
        messages.error(request, 'Yêu cầu này đã được xử lý rồi.')
        return redirect('books:received_purchase_requests')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        try:
            purchase_request.reject(reason)
            messages.success(
                request, 
                f'Đã từ chối yêu cầu mua "{purchase_request.book.title}".'
            )
        except Exception as e:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
    else:
        messages.error(request, 'Yêu cầu không hợp lệ.')
    
    return redirect('books:received_purchase_requests')


# ==================== SÁCH ĐÃ MUA - US11 ====================
@login_required
def purchased_books(request):
    """
    Trang Sách đã mua - US11
    Hiển thị danh sách sách đã mua (giao dịch đã được duyệt)
    """
    # Lấy danh sách purchase request đã approved của user hiện tại
    purchased_requests = PurchaseRequest.objects.filter(
        buyer=request.user,
        status='approved'
    ).select_related(
        'book', 'book__subject', 'seller', 'seller__profile'
    ).prefetch_related(
        'book__images'
    ).order_by('-processed_at')
    
    # Tạo danh sách sách đã mua
    purchased_list = []
    for pr in purchased_requests:
        purchased_list.append({
            'purchase_request': pr,
            'book': pr.book,
            'seller': pr.seller,
            'purchase_date': pr.processed_at or pr.updated_at,
        })
    
    # Thống kê
    total_count = len(purchased_list)
    
    # Phân trang
    paginator = Paginator(purchased_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'purchased_books': purchased_list,
        'page_obj': page_obj,
        'total_count': total_count,
        'title': 'Sách đã mua',
    }
    return render(request, 'books/purchased_books.html', context)
