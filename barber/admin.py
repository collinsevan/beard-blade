from django.contrib import admin
from .models import Service, TimeSlot, Booking


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
