from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


"""
Service model for storing details about the barber's offerings.
Each service has a name, duration, and price.
"""


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration = models.DurationField()
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


"""
Booking model for managing user appointments.
Links a User, a Service, and a TimeSlot.
Validates that a confirmed booking uses an available time slot,
and updates the time slot's status accordingly.
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
        'Service', on_delete=models.CASCADE, related_name="bookings"
    )
    time_slot = models.ForeignKey(
        'TimeSlot', on_delete=models.CASCADE, related_name="bookings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    def clean(self):
        """
        Validate that a confirmed booking uses an available time slot.
        """
        if (self.status == 'confirmed' and
                self.time_slot.status != 'available'):
            raise ValidationError(
                "This time slot is not available for booking."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if (self.status == 'confirmed' and
                self.time_slot.status == 'available'):
            self.time_slot.status = 'booked'
            self.time_slot.save()

    def __str__(self):
        return (f"{self.user.username} - {self.service.name} on "
                f"{self.time_slot.date} at {self.time_slot.start_time}")
