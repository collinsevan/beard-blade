from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    """Render the home page with the hero section."""
    return render(request, 'home.html')


def about(request):
    """Render the About page with shop and barber details."""
    return render(request, 'about.html')


def base_view(request):
    """Renders the base template for testing."""
    return render(request, 'base.html')


@login_required
def book_now(request):
    return render(request, "booking.html")
