from django import forms
from .models import Review

STAR_CHOICES = [
    (5, '5 ★★★★★'),
    (4, '4 ★★★★'),
    (3, '3 ★★★'),
    (2, '2 ★★'),
    (1, '1 ★'),
]


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=STAR_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'star-rating'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your review here...',
            'rows': 4,
        }),
        required=False
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
