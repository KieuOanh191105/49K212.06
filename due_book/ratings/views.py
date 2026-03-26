"""
Views for Ratings App
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User


@login_required
def rating_create(request, user_id):
    """
    Đánh giá người bán sau khi mua sách
    (Chức năng sẽ được phát triển đầy đủ sau)
    """
    user_to_rate = get_object_or_404(User, pk=user_id)
    
    # TODO: Triển khai form đánh giá đầy đủ
    messages.info(request, f'Chức năng đánh giá {user_to_rate.username} sẽ được phát triển sớm.')
    return redirect('books:my_purchase_requests')