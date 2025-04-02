from django.core.management.base import BaseCommand
from django.db.models import Count
from barber.models import TimeSlot, Booking


class Command(BaseCommand):
    help = "Checks database for duplicate timeslots and booking issues."

    def handle(self, *args, **kwargs):
        self.check_duplicates()
        self.check_bookings()

    def check_duplicates(self):
        duplicates = (TimeSlot.objects
                      .values("date", "start_time", "end_time")
                      .annotate(count=Count("id"))
                      .filter(count__gt=1))
        if duplicates.exists():
            self.stdout.write(self.style.WARNING(
                "Found duplicate timeslots:"
            ))
            for dup in duplicates:
                self.stdout.write(str(dup))
        else:
            self.stdout.write(self.style.SUCCESS(
                "No duplicate timeslots found."
            ))

    def check_bookings(self):
        issues = 0
        for booking in Booking.objects.all():
            slots = booking.timeslots.all().order_by("start_time")
            expected_slots = int(
                booking.service.duration.total_seconds() // 900)
            if slots.count() != expected_slots:
                issues += 1
                self.stdout.write(self.style.WARNING(
                    f"Booking {booking.id} has {slots.count()} slots, expected"
                    f"{expected_slots}."
                ))
        if issues == 0:
            self.stdout.write(self.style.SUCCESS(
                "All bookings have the correct number of timeslots."
            ))
