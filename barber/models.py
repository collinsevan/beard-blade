from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User  # noqa F401


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
        return (f"{self.date} {self.start_time} - {self.end_time} "
                f"({self.status}, Duration: {self.duration})")

    class Meta:
        ordering = ['date', 'start_time']
