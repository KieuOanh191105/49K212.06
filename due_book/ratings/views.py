"""
Views for Ratings App
US11 - Đánh giá người bán
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

from books.models import PurchaseRequest
from .models import SellerReview
from .forms import SellerReviewForm


@login_required
def rating_create(request, purchase_request_id):
    """
    Đánh giá người bán sau khi mua sách
    - Chỉ cho phép đánh giá nếu request đã approved
    - Chỉ người mua mới được đánh giá
    - Mỗi giao dịch chỉ được đánh giá 1 lần
    """
    purchase_request = get_object_or_404(
        PurchaseRequest.objects.select_related('book', 'seller', 'buyer'),
        pk=purchase_request_id
    )
    
    # Kiểm tra quyền: chỉ người mua mới được đánh giá
    if purchase_request.buyer != request.user:
        messages.error(request, 'Bạn không có quyền đánh giá giao dịch này.')
        return redirect('books:purchased_books')
    
    # Kiểm tra trạng thái: chỉ đánh giá khi đã approved
    if not purchase_request.is_approved:
        messages.error(request, 'Chỉ có thể đánh giá sau khi giao dịch đã hoàn tất.')
        return redirect('books:purchased_books')
    
    # Kiểm tra đã đánh giá chưa
    existing_review = SellerReview.objects.filter(
        purchase_request=purchase_request
    ).first()
    
    if existing_review:
        messages.info(request, 'Bạn đã đánh giá giao dịch này rồi.')
        return redirect('books:purchased_books')
    
    if request.method == 'POST':
        form = SellerReviewForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    review = form.save(commit=False)
                    review.buyer = request.user
                    review.seller = purchase_request.seller
                    review.book = purchase_request.book
                    review.purchase_request = purchase_request
                    review.save()
                
                messages.success(
                    request, 
                    f'Đánh giá thành công! Cảm ơn bạn đã đánh giá {purchase_request.seller.username}.'
                )
                return redirect('books:purchased_books')
                
            except Exception as e:
                messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
        else:
            messages.error(request, 'Vui lòng chọn số sao đánh giá.')
    else:
        form = SellerReviewForm()
    
    context = {
        'form': form,
        'purchase_request': purchase_request,
        'book': purchase_request.book,
        'seller': purchase_request.seller,
        'title': f'Đánh giá người bán - {purchase_request.seller.username}',
    }
    return render(request, 'ratings/rating_form.html', context)


@login_required
@require_POST
def rating_create_ajax(request, purchase_request_id):
    """
    API AJAX để đánh giá người bán (cho modal popup)
    """
    import json
    
    try:
        purchase_request = get_object_or_404(
            PurchaseRequest.objects.select_related('book', 'seller', 'buyer'),
            pk=purchase_request_id
        )
        
        # Kiểm tra quyền
        if purchase_request.buyer != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Bạn không có quyền đánh giá giao dịch này.'
            }, status=403)
        
        # Kiểm tra trạng thái
        if not purchase_request.is_approved:
            return JsonResponse({
                'success': False,
                'error': 'Chỉ có thể đánh giá sau khi giao dịch đã hoàn tất.'
            }, status=400)
        
        # Kiểm tra đã đánh giá chưa
        if SellerReview.objects.filter(purchase_request=purchase_request).exists():
            return JsonResponse({
                'success': False,
                'error': 'Bạn đã đánh giá giao dịch này rồi.'
            }, status=400)
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Dữ liệu không hợp lệ.'
            }, status=400)
        
        rating = data.get('rating')
        comment = data.get('comment', '').strip()
        
        # Validate rating
        if not rating or int(rating) < 1 or int(rating) > 5:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng chọn số sao từ 1 đến 5.'
            }, status=400)
        
        # Tạo đánh giá
        with transaction.atomic():
            review = SellerReview.objects.create(
                buyer=request.user,
                seller=purchase_request.seller,
                book=purchase_request.book,
                purchase_request=purchase_request,
                rating=int(rating),
                comment=comment
            )
        
        # Lấy thống kê cập nhật của người bán
        stats = SellerReview.get_seller_stats(purchase_request.seller)
        
        return JsonResponse({
            'success': True,
            'message': f'Đánh giá thành công!',
            'review': {
                'rating': review.rating,
                'rating_stars': review.rating_stars,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M')
            },
            'seller_stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Có lỗi xảy ra. Vui lòng thử lại.'
        }, status=500)


@login_required
def get_review_modal(request, purchase_request_id):
    """
    Lấy nội dung modal đánh giá (cho AJAX load)
    """
    purchase_request = get_object_or_404(
        PurchaseRequest.objects.select_related('book', 'seller'),
        pk=purchase_request_id
    )
    
    # Kiểm tra quyền
    if purchase_request.buyer != request.user:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    # Kiểm tra đã đánh giá chưa
    if SellerReview.objects.filter(purchase_request=purchase_request).exists():
        return JsonResponse({'error': 'Đã đánh giá'}, status=400)
    
    context = {
        'purchase_request': purchase_request,
        'book': purchase_request.book,
        'seller': purchase_request.seller,
    }
    return render(request, 'ratings/review_modal_content.html', context)


@login_required
def submit_review(request):
    """
    Submit đánh giá từ form modal (POST thông thường, không dùng AJAX)
    """
    if request.method != 'POST':
        messages.error(request, 'Yêu cầu không hợp lệ.')
        return redirect('books:purchased_books')
    
    purchase_request_id = request.POST.get('purchase_request_id')
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()
    
    # Validate required fields
    if not purchase_request_id:
        messages.error(request, 'Thiếu thông tin giao dịch.')
        return redirect('books:purchased_books')
    
    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            messages.error(request, 'Vui lòng chọn số sao từ 1 đến 5.')
            return redirect('books:purchased_books')
    except (TypeError, ValueError):
        messages.error(request, 'Vui lòng chọn số sao đánh giá.')
        return redirect('books:purchased_books')
    
    # Lấy purchase request
    try:
        purchase_request = PurchaseRequest.objects.select_related('book', 'seller', 'buyer').get(pk=purchase_request_id)
    except PurchaseRequest.DoesNotExist:
        messages.error(request, 'Giao dịch không tồn tại.')
        return redirect('books:purchased_books')
    
    # Kiểm tra quyền: chỉ người mua mới được đánh giá
    if purchase_request.buyer != request.user:
        messages.error(request, 'Bạn không có quyền đánh giá giao dịch này.')
        return redirect('books:purchased_books')
    
    # Kiểm tra trạng thái: chỉ đánh giá khi đã approved
    if not purchase_request.is_approved:
        messages.error(request, 'Chỉ có thể đánh giá sau khi giao dịch đã hoàn tất.')
        return redirect('books:purchased_books')
    
    # Kiểm tra đã đánh giá chưa
    if SellerReview.objects.filter(purchase_request=purchase_request).exists():
        messages.warning(request, 'Bạn đã đánh giá giao dịch này rồi.')
        return redirect('books:purchased_books')
    
    # Tạo đánh giá
    try:
        with transaction.atomic():
            review = SellerReview.objects.create(
                buyer=request.user,
                seller=purchase_request.seller,
                book=purchase_request.book,
                purchase_request=purchase_request,
                rating=rating,
                comment=comment
            )
        
        messages.success(
            request,
            f'Đánh giá thành công! Cảm ơn bạn đã đánh giá {purchase_request.seller.username|title}.'
        )
    except Exception as e:
        messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
    
    return redirect('books:purchased_books')
