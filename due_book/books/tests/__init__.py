"""
Tests package for Books App

Structure:
- test_book_create.py: Tests for User Story 4 - Đăng bài bán sách
- test_book_list.py: Tests for User Story 5 - Xem danh sách sách với phân trang
"""

from .test_book_create import (
    BookCreateAccessTest,
    BookFormValidationTest,
    BookImageValidationTest,
    BookCreateSuccessTest,
    BookCreateCancelTest,
    MyBooksViewTest,
    BookConditionDefaultTest,
    BookModelTest,
)

from .test_book_list import (
    BookListViewTests,
    BookListPaginationEdgeCasesTest,
)

__all__ = [
    # User Story 4 - Đăng bài bán sách
    'BookCreateAccessTest',
    'BookFormValidationTest',
    'BookImageValidationTest',
    'BookCreateSuccessTest',
    'BookCreateCancelTest',
    'MyBooksViewTest',
    'BookConditionDefaultTest',
    'BookModelTest',
    # User Story 5 - Xem danh sách sách với phân trang
    'BookListViewTests',
    'BookListPaginationEdgeCasesTest',
]