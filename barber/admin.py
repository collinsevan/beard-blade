from django.contrib import admin
from .models import Service, TimeSlot, Booking, OpeningHours

"""
Admin configuration for the barber app.
Registers the Service model in the Django admin interface.
"""
admin.site.register(Service)

"""
Admin configuration for the barber app.
Registers the TimeSlot model in the Django admin panel.
"""
admin.site.register(TimeSlot)


class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Booking model.
    This allows the barber to manage bookings, including
    confirming or canceling them.
    """
    list_display = ('user', 'service', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'service__name')


admin.site.register(Booking, BookingAdmin)


class OpeningHoursAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the OpeningHours model.
    Displays the human-readable day name, open time, and close time.
    Allows filtering by day, ordering by day, and searching by day.
    """
    list_display = ('day_of_week_display', 'open_time', 'close_time')
    list_filter = ('day_of_week',)
    ordering = ('day_of_week',)
    search_fields = ('day_of_week',)

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = 'Day'


admin.site.register(OpeningHours, OpeningHoursAdmin)
