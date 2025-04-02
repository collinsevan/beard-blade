from django.core.management.base import BaseCommand
from barber.models import OpeningHours, TimeSlot
from datetime import date, datetime, timedelta


class Command(BaseCommand):
    """
    Command to generate 15-min timeslots for future days.
    """

    help = (
        "Generates 15-min timeslots for future days based on\n"
        "OpeningHours."
    )

    def add_arguments(self, parser):
        """
        Add argument for the number of days to generate timeslots.
        """
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help=("Number of future days to generate timeslots "
                  "(default: 7)")
        )

    def handle(self, *args, **options):
        """
        Main handler that creates timeslots.
        """
        days = options["days"]
        today = date.today()
        created_count = 0

        for day_offset in range(days):
            current_date = today + timedelta(days=day_offset)
            weekday = current_date.weekday()  # 0=Mon, 6=Sun

            try:
                oh = OpeningHours.objects.get(day_of_week=weekday)
            except OpeningHours.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"No opening hours for {current_date} (wd "
                        f"{weekday}). Skipping."
                    )
                )
                continue

            start_dt = datetime.combine(current_date, oh.open_time)
            end_dt = datetime.combine(current_date, oh.close_time)

            # Create 15-min slots if time permits.
            while start_dt + timedelta(minutes=15) <= end_dt:
                slot_start = start_dt.time()
                slot_end = (start_dt + timedelta(minutes=15)).time()

                ts, created = TimeSlot.objects.get_or_create(
                    date=current_date,
                    start_time=slot_start,
                    end_time=slot_end,
                    defaults={"status": "available"}
                )
                if created:
                    created_count += 1
                    msg = (
                        f"Created timeslot on {current_date}:\n"
                        f"{slot_start} - {slot_end}"
                    )
                    self.stdout.write(self.style.SUCCESS(msg))
                start_dt += timedelta(minutes=15)

        self.stdout.write(
            self.style.SUCCESS(
                f"Total new timeslots created: {created_count}"
            )
        )
