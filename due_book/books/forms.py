"""
Forms for Books App
"""
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Book, Subject


class BookForm(forms.ModelForm):
    """
    Form đăng/cập nhật sách
    US4 - Đăng bài bán sách
    """

    # Giới hạn kích thước file ảnh (2.5MB)
    MAX_IMAGE_SIZE = 2.5 * 1024 * 1024  # 2.5MB in bytes
    
    # Các định dạng ảnh được chấp nhận
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']

    class Meta:
        model = Book
        fields = [
            'title', 'subject', 'price',
            'condition', 'description', 'notes', 'cover_image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên sách',
                'maxlength': '300',
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: 150000',
                'min': '1000',
                'max': '9999999999',
                'step': '1',
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mô tả về sách...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ghi chú thêm (gạch bớt, v.v.)'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': 'Tên sách',
            'subject': 'Môn học',
            'price': 'Giá bán (VNĐ)',
            'condition': 'Tình trạng',
            'description': 'Mô tả chi tiết',
            'notes': 'Ghi chú',
            'cover_image': 'Ảnh bìa',
        }
        error_messages = {
            'title': {
                'required': 'Vui lòng nhập Tên sách',
                'max_length': 'Tên sách không được vượt quá 300 ký tự',
            },
            'price': {
                'required': 'Vui lòng nhập Giá bán',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đặt giá trị mặc định cho condition nếu là form mới
        if not self.instance.pk:
            self.initial['condition'] = 'good'
        
        # Thêm class 'required' cho các trường bắt buộc
        self.fields['title'].required = True
        self.fields['price'].required = True
        self.fields['condition'].required = False
        self.fields['subject'].required = False
        self.fields['description'].required = False
        self.fields['notes'].required = False
        self.fields['cover_image'].required = False

    def clean_title(self):
        """Validate tên sách"""
        title = self.cleaned_data.get('title', '')
        
        if not title or not title.strip():
            raise ValidationError('Vui lòng nhập Tên sách')
        
        title = title.strip()
        
        if len(title) > 300:
            raise ValidationError('Tên sách không được vượt quá 300 ký tự')
        
        return title

    def clean_price(self):
        """Validate giá bán"""
        price = self.cleaned_data.get('price')
        
        if price is None:
            raise ValidationError('Vui lòng nhập Giá bán')
        
        try:
            price = int(price)
        except (ValueError, TypeError):
            raise ValidationError('Vui lòng nhập số hợp lệ')
        
        if price < 1000:
            raise ValidationError('Giá bán tối thiểu phải từ 1.000đ')
        
        if price > 9999999999:
            raise ValidationError('Giá bán không được vượt quá 9.999.999.999đ')
        
        return price

    def clean_cover_image(self):
        """Validate ảnh bìa"""
        image = self.cleaned_data.get('cover_image')
        
        if not image:
            return image
        
        # Kiểm tra kích thước file
        if image.size > self.MAX_IMAGE_SIZE:
            raise ValidationError('File không được vượt quá 2.5MB')
        
        # Kiểm tra định dạng file
        ext = image.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError('File ảnh không hợp lệ. Chỉ chấp nhận: jpg, jpeg, png, gif, webp, bmp')
        
        # Kiểm tra content type
        valid_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
        if hasattr(image, 'content_type') and image.content_type not in valid_content_types:
            raise ValidationError('File ảnh không hợp lệ')
        
        return image

    def clean(self):
        """Clean method chung"""
        cleaned_data = super().clean()
        return cleaned_data