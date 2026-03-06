from django.shortcuts import render

# Create your views here.

def home(request):
    """Trang chủ"""
    return render(request, 'books/home.html')


def book_list(request):
    """Danh sách sách"""
    return render(request, 'books/book_list.html')