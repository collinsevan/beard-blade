from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


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


def register(request):
    """
    Registers a new user by validating input and creating a user if valid.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate that all fields are filled
        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, 'registration/register.html')
        # Validate matching passwords
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'registration/register.html')
        # Validate that the username is unique
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'registration/register.html')

        # Create the new user
        user = User.objects.create_user(
            username=username, email=email, password=password1)
        user.save()
        messages.success(
            request, "Your account has been created! Please log in.")
        return redirect('login')
    return render(request, 'registration/register.html')
