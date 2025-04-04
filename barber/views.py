from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.dateparse import parse_date
from barber.models import Booking, Service, TimeSlot
from datetime import date, datetime, timedelta
from collections import defaultdict
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView
)


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
    """
    Handles booking form submissions.
    Validates that all fields are provided and the selected date is not in
    the past. Retrieves the selected service and checks for contiguous
    available 15-minute timeslots based on the service duration. If found,
    creates a booking with status 'pending' and reserves those timeslots.
    """
    services_qs = Service.objects.all()

    if request.method == "POST":
        service_id = request.POST.get("service")
        selected_date_str = request.POST.get("date")
        start_time_str = request.POST.get("time")

        # Validate that all fields are provided.
        if not service_id or not selected_date_str or not start_time_str:
            messages.error(request, "All fields are required.")
            return redirect("book_now")

        # Parse and validate the selected date.
        selected_date = parse_date(selected_date_str)
        if selected_date is None:
            messages.error(request, "Invalid date format provided.")
            return redirect("book_now")
        if selected_date < date.today():
            messages.error(request, "You cannot select a past date.")
            return redirect("book_now")

        # Retrieve the service; 404 if not found.
        service = get_object_or_404(Service, pk=service_id)

        # Parse the selected time.
        try:
            selected_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect("book_now")

        start_datetime = datetime.combine(selected_date, selected_time)

        # Determine the number of 15-min slots required.
        required_slots = int(service.duration.total_seconds() // (15 * 60))
        if required_slots < 1:
            messages.error(request, "Service duration is invalid.")
            return redirect("book_now")

        # Check for available contiguous timeslots.
        slots_to_book = []
        available = True
        for i in range(required_slots):
            current_slot_start = (
                start_datetime + timedelta(minutes=15 * i)).time()
            current_slot_end = (
                start_datetime + timedelta(minutes=15 * (i + 1))).time()
            try:
                slot = TimeSlot.objects.get(
                    date=selected_date,
                    start_time=current_slot_start,
                    end_time=current_slot_end,
                    status="available"
                )
                slots_to_book.append(slot)
            except TimeSlot.DoesNotExist:
                available = False
                break

        if not available or len(slots_to_book) != required_slots:
            messages.error(
                request,
                "Selected time slots are not available. "
                "Please choose a different time."
            )
            return redirect("book_now")

        # Create the booking and reserve the timeslots.
        booking = Booking.objects.create(
            user=request.user,
            service=service,
            status="pending"
        )
        booking.timeslots.set(slots_to_book)
        for slot in slots_to_book:
            slot.status = "pending"
            slot.save()

        messages.success(
            request,
            "Booking request received. Await confirmation."
        )
        return redirect("profile")

    # Build a dictionary of available timeslots grouped by date
    # Filter out passed timeslots.
    timeslots_by_date = defaultdict(list)
    today = date.today()
    current_time = datetime.now().time()
    available_slots = TimeSlot.objects.filter(status='available')
    for slot in available_slots:
        # Check if time slot is earlier or equal to current time if not skip
        if slot.date == today and slot.start_time <= current_time:
            continue
        timeslots_by_date[str(slot.date)].append(
            slot.start_time.strftime("%H:%M"))

    return render(request, "booking.html", {
        "services": services_qs,
        "timeslots_by_date": dict(timeslots_by_date)
    })


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
