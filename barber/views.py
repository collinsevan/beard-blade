from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.dateparse import parse_date
from barber.models import Booking, Service, TimeSlot, Review
from datetime import date, datetime, timedelta
from collections import defaultdict
from django.utils import timezone
from .forms import ReviewForm
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView
)


def home(request):
    """Render the home page with the hero section."""
    return render(request, 'home.html')


def about(request):
    """
    Render the About page with establishment details and random reviews.
    """
    random_reviews = Review.objects.order_by('?')[:3]
    context = {'random_reviews': random_reviews}
    return render(request, 'about.html', context)


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
    For editing, if a GET parameter "edit" is provided, the form is
    prepopulated with the existing booking's data. On POST, if the time or
    date is changed, the existing booking is updated.
    """
    services_qs = Service.objects.all()

    # Check if this is an edit request by looking for an "edit" GET parameter.
    edit_booking = None
    if 'edit' in request.GET:
        booking_id = request.GET.get('edit')
        edit_booking = get_object_or_404(
            Booking, pk=booking_id, user=request.user)

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
                (
                    "Selected time slots are not available. Please choose a "
                    "different time."
                )
            )
            return redirect("book_now")

        if edit_booking:
            for old_slot in edit_booking.timeslots.all():
                old_slot.status = "available"
                old_slot.save()

            # Update the booking with the new service and timeslots.
            edit_booking.service = service
            edit_booking.timeslots.clear()
            edit_booking.status = "pending"
            edit_booking.save()

            edit_booking.timeslots.set(slots_to_book)
            for slot in slots_to_book:
                slot.status = "pending"
                slot.save()
            booking = edit_booking
        else:
            # Create a new booking instance and save it to get a primary key.
            booking = Booking(user=request.user,
                              service=service, status="pending")
            booking.save()
            booking.timeslots.set(slots_to_book)
            for slot in slots_to_book:
                slot.status = "pending"
                slot.save()

        messages.success(
            request, "Booking request received. Await confirmation.")
        return redirect("profile")

    # Build a dictionary of available timeslots grouped by date.
    # Filter out timeslots that have already passed today.
    timeslots_by_date = defaultdict(list)
    today = date.today()
    current_time = datetime.now().time()
    available_slots = TimeSlot.objects.filter(status='available')
    for slot in available_slots:
        # Check if time slot is earlier or equal to current time if so skip
        if slot.date == today and slot.start_time <= current_time:
            continue
        timeslots_by_date[str(slot.date)].append(
            slot.start_time.strftime("%H:%M"))

    # Prepopulate initial form data if editing.
    initial = {}
    if edit_booking:
        slots = edit_booking.timeslots.all().order_by("start_time")
        if slots.exists():
            initial["service"] = edit_booking.service.id
            initial["date"] = slots.first().date.strftime("%Y-%m-%d")
            initial["time"] = slots.first().start_time.strftime("%H:%M")

    context = {
        "services": services_qs,
        "timeslots_by_date": dict(timeslots_by_date),
        "initial": initial,
        "edit_booking": edit_booking,
    }
    return render(request, "booking.html", context)


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
    and their bookings. Retrieves all bookings for the user, lazy-updates up
    to 50 confirmed bookings to 'completed' if their earliest timeslot is in
    the past, and separates bookings into upcoming and past using the actual
    end datetime.
    """
    now = timezone.now()

    confirmed_bookings = Booking.objects.filter(
        user=request.user, status='confirmed'
    ).order_by('timeslots__date')[:50]

    for booking in confirmed_bookings:
        end_dt = booking.get_end_datetime()
        if end_dt and end_dt < now:
            booking.status = 'completed'
            booking.save()

    all_bookings = Booking.objects.filter(
        user=request.user
    ).exclude(status='cancelled').distinct().order_by('timeslots__date')

    upcoming_bookings = []
    past_bookings = []

    for booking in all_bookings:
        end_dt = booking.get_end_datetime()
        if end_dt and end_dt < now:
            past_bookings.append(booking)
        else:
            upcoming_bookings.append(booking)

    user_reviews = request.user.reviews.all()

    context = {
        'username': request.user.username,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'user_reviews': user_reviews,
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


@login_required
def booking_cancel(request, booking_id):
    """
    Cancel a booking. This view checks that the booking belongs to the
    current user, marks its status as "cancelled", and updates timeslot
    statuses accordingly. It then redirects back to the profile page.
    """
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    booking.status = "cancelled"
    booking.save()
    messages.success(request, "Booking cancelled successfully.")
    return redirect("profile")


def reviews(request):
    """
    Display all reviews on a dedicated Reviews page.
    """
    all_reviews = Review.objects.all().order_by('-created_at')
    context = {'all_reviews': all_reviews}
    return render(request, 'reviews.html', context)


@login_required
def delete_review(request, review_id):
    """
    Delete a review created by the logged-in user.
    Handles POST requests to delete the review,
    then redirects to the profile page.
    If accessed via GET, renders a confirmation page.
    """
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect("profile")
    return render(request, "delete_review.html", {"review": review})


@login_required
def create_review(request, booking_id):
    """
    Create a review for a completed booking.

    Only allow review creation if the booking is completed and no review
    exists. Display the ReviewForm with star rating and comment.
    """
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status != 'completed':
        messages.error(request, "You can only review a completed booking.")
        return redirect("profile")
    if hasattr(booking, 'review'):
        messages.info(request,
                      "This booking already has a review. Please edit it.")
        return redirect("edit_review", review_id=booking.review.id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.user = request.user
            review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect("profile")
    else:
        form = ReviewForm()
    return render(request, "review_form.html",
                  {"form": form, "booking": booking})


@login_required
def edit_review(request, review_id):
    """
    Edit an existing review.

    Display the ReviewForm prepopulated with the existing review data.
    """
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully.")
            return redirect("profile")
    else:
        form = ReviewForm(instance=review)
    return render(request, "review_form.html",
                  {"form": form, "booking": review.booking})


# Built-in Django error handlers
def custom_bad_request(request, exception):
    return render(request, '400.html', status=400)


def custom_permission_denied(request, exception):
    return render(request, '403.html', status=403)


def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)


def custom_server_error(request):
    return render(request, '500.html', status=500)


def custom_unauthorized(request, exception):
    return render(request, '401.html', status=401)


def custom_method_not_allowed(request, exception):
    return render(request, '405.html', status=405)


def custom_gone(request, exception):
    return render(request, '410.html', status=410)


def custom_too_many_requests(request, exception):
    return render(request, '429.html', status=429)


def custom_bad_gateway(request, exception):
    return render(request, '502.html', status=502)


def custom_service_unavailable(request, exception):
    return render(request, '503.html', status=503)


def custom_gateway_timeout(request, exception):
    return render(request, '504.html', status=504)
