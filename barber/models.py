from django.db import models
from django.contrib.auth.models import User   # noqa F401


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
