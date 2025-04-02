from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView  # noqa
from django.contrib import messages
from barber.models import Booking, Service
from datetime import date


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


@login_required
def profile(request):
    """
    Custom profile view for displaying the logged-in user's account details
    and their bookings. Retrieves all bookings for the user and separates
    them into upcoming and past bookings based on the current date.
    """
    # Retrieve all bookings for the current user
    all_bookings = Booking.objects.filter(
        user=request.user).order_by('timeslots__date')
    today = date.today()
    # Separate bookings into upcoming and past
    upcoming_bookings = all_bookings.filter(timeslots__date__gte=today)
    past_bookings = all_bookings.filter(timeslots__date__lt=today)
    context = {
        'username': request.user.username,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'profile.html', context)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


def services(request):
    """
    Render the services page displaying all available barber services.
    If no services exist, display a warning message.
    """
    services_qs = Service.objects.all()
    if not services_qs.exists():
        messages.warning(request, "No services available at this time.")
    return render(request, 'services.html', {'services': services_qs})
