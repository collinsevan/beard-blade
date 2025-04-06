from django.core.management.base import BaseCommand
from django.utils import timezone
from barber.models import Booking


"""
Management command to update booking statuses based on end datetime.

This command iterates over all bookings with a status of 'confirmed'.
For each booking, it retrieves the end datetime using the get_end_datetime()
method. If the booking's end datetime is before the current time,
the booking's status is updated to 'completed' and saved.
"""


class Command(BaseCommand):
    help = ("Mark confirmed bookings as completed if their booking end "
            "time is in the past.")

    def handle(self, *args, **kwargs):
        now = timezone.now()
        bookings = Booking.objects.filter(status='confirmed')
        count = 0

        for booking in bookings:
            end_dt = booking.get_end_datetime()
            if end_dt and end_dt < now:
                booking.status = 'completed'
                booking.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Booking {booking.id} marked as completed."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"Total bookings updated: {count}")
        )
