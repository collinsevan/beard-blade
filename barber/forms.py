"""
Forms for the barber app.

This module contains the ReviewForm for creating and editing reviews,
including a star rating field and an optional comment field.
"""

from django import forms
from .models import Review

STAR_CHOICES = [
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
]


class ReviewForm(forms.ModelForm):
    """
    A ModelForm for the Review model.

    Provides a star rating field using radio buttons and a textarea
    for an optional comment.
    """
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
