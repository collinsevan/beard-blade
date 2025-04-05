from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

"""
Service model for storing details about the barber's offerings.
Each service has a name, duration, and price.
"""


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration = models.DurationField(
        help_text="Service duration as timedelta"
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def get_duration_display(self):
        """Formats duration as HH:MM"""
        total_minutes = self.duration.total_seconds() / 60
        hours, minutes = divmod(total_minutes, 60)
        return f"{int(hours)}h {int(minutes)}m"

    def __str__(self):
        return f"{self.name} - €{self.price} ({self.get_duration_display()})"


"""
TimeSlot model stores available appointment slots.
Each slot has a date, start time, end time, and a status field.
Includes validation and a computed duration property.
"""


class TimeSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('booked', 'Booked'),
        ('expired', 'Expired'),
    ]

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='available'
    )

    def clean(self):
        """Validate that end_time is after start_time."""
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    @property
    def duration(self):
        """Return the duration of the time slot as a timedelta."""
        dt_start = datetime.combine(self.date, self.start_time)
        dt_end = datetime.combine(self.date, self.end_time)
        return dt_end - dt_start

    def __str__(self):
        total_minutes = self.duration.total_seconds() / 60
        hours, minutes = divmod(total_minutes, 60)
        duration_str = f"{int(hours)}h {int(minutes)}m"
        return (f"{self.date} {self.start_time} - {self.end_time} "
                f"({self.status}, Duration: {duration_str})")

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('date', 'start_time', 'end_time')


"""
OpeningHours model represents the standard operating hours for the
barber shop. Each record stores the opening and closing times for a
specific day.
"""


class OpeningHours(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    day_of_week = models.IntegerField(choices=DAY_CHOICES, unique=True)
    open_time = models.TimeField(help_text="Time when the shop opens")
    close_time = models.TimeField(help_text="Time when the shop closes")

    def clean(self):
        """
        Validate that the closing time is later than the opening time.
        Only perform the check if both times are provided.
        """
        if self.open_time and self.close_time:
            if self.close_time <= self.open_time:
                raise ValidationError({
                    'close_time': (
                        f"Closing time must be after opening time for "
                        f"{self.get_day_of_week_display()}."
                    )
                })

    def __str__(self):
        return (f"{self.get_day_of_week_display()}: "
                f"{self.open_time.strftime('%H:%M')} - "
                f"{self.close_time.strftime('%H:%M')}")

    class Meta:
        verbose_name = "Opening Hour"


"""
Booking model for managing user appointments.
Links a User, a Service, and selected TimeSlots.
Validates that a confirmed booking uses contiguous available slots
matching the service duration.
"""


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="bookings"
    )
    timeslots = models.ManyToManyField(
        TimeSlot, related_name="bookings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    def clean(self):
        """
        Validate that the booking has contiguous time slots that match
        the service duration. Also, ensure that all selected time slots
        are available.
        """
        total_required_minutes = (
            self.service.duration.total_seconds() / 60
        )
        required_slots = int(total_required_minutes / 15)
        # Validate many-to-many fields if the instance is saved
        # and timeslots exist.
        if self.pk and self.timeslots.exists():
            if self.timeslots.count() != required_slots:
                raise ValidationError(
                    f"{self.service.name} requires {required_slots * 15} "
                    f"minutes. Please select exactly {required_slots} "
                    f"contiguous 15-minute slots."
                )
            # Order the time slots by start_time for contiguous check.
            slots = list(self.timeslots.all().order_by('start_time'))
            if not slots:
                raise ValidationError("No time slots selected.")
            for i in range(1, len(slots)):
                prev_end = datetime.combine(slots[i - 1].date,
                                            slots[i - 1].end_time)
                current_start = datetime.combine(slots[i].date,
                                                 slots[i].start_time)
                if current_start != prev_end:
                    raise ValidationError(
                        "Selected time slots are not contiguous."
                    )
            for slot in slots:
                if slot.status != 'available':
                    raise ValidationError(
                        "One or more selected time slots are not available."
                    )

    def save(self, *args, **kwargs):
        """
        Save booking and update time slot statuses accordingly.
        Mark time slots as pending on booking creation, update to booked
        on confirmation, or revert to available on cancellation.
        """
        if self.status in ['pending', 'confirmed']:
            self.full_clean()

        super().save(*args, **kwargs)

        if self.status == 'pending':
            self.timeslots.update(status='pending')
        elif self.status == 'confirmed':
            self.timeslots.update(status='booked')
        elif self.status == 'cancelled':
            self.timeslots.update(status='available')

    def __str__(self):
        if not self.pk:
            return f"{self.user.username} - {self.service.name}"
        try:
            count = self.timeslots.count()
        except Exception:
            count = 0
        return (
            f"{self.user.username} - {self.service.name} "
            f"({count} slots)"
        )

    def get_date(self):
        """Return the booking date from the earliest timeslot."""
        slots = self.timeslots.all().order_by('start_time')
        return slots.first().date if slots.exists() else None

    # Method to get the overall time range of the booking.
    def get_time_range(self):
        """
        Return a string representing the time range from the earliest start
        time to the latest end time, e.g., "10:00 - 10:45".
        """
        slots = self.timeslots.all().order_by('start_time')
        if not slots.exists():
            return ""
        start_time = slots.first().start_time.strftime("%H:%M")
        end_time = slots.last().end_time.strftime("%H:%M")
        return f"{start_time} - {end_time}"


class Review(models.Model):
    """
    Review model stores feedback for a completed booking.
    Each review is linked to a booking (OneToOne) so each booking has one
    review at most. It has a rating (1-5) and an optional comment.
    Timestamps are auto-set on creation and update.
    """
    booking = models.OneToOneField(
        'Booking', on_delete=models.CASCADE, related_name="review"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating out of 5"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validate that rating is between 1 and 5.
        """
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")

    def __str__(self):
        return (
            f"Review for {self.booking.service.name} by "
            f"{self.user.username}"
        )
