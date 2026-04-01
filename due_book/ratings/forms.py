"""
Forms for Ratings App
US11 - Đánh giá người bán
"""
from django import forms
from .models import SellerReview


class SellerReviewForm(forms.ModelForm):
    """
    Form đánh giá người bán sau khi mua sách
    """
    
    RATING_CHOICES = [
        (5, '5 sao - Xuất sắc'),
        (4, '4 sao - Tốt'),
        (3, '3 sao - Bình thường'),
        (2, '2 sao - Tệ'),
        (1, '1 sao - Rất tệ'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
        label='Đánh giá sao',
        required=True
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập bình luận của bạn (tùy chọn)...'
        }),
        label='Bình luận',
        required=False
    )
    
    class Meta:
        model = SellerReview
        fields = ['rating', 'comment']
    
    def clean_rating(self):
        """Validate rating phải từ 1-5"""
        rating = int(self.cleaned_data.get('rating', 0))
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Vui lòng chọn số sao từ 1 đến 5.')
        return rating