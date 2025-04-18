from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import Service, TimeSlot, Booking, OpeningHours, Review

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
    confirming or canceling them, with a cleaner editing form.
    """
    list_display = (
        "user",
        "service",
        "display_timeslots",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "service__name")
    actions = ["confirm_bookings", "decline_bookings"]
    filter_horizontal = ("timeslots",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("user", "service", "timeslots", "status")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def display_timeslots(self, obj):
        """
        Return a comma-separated string of dates and start times for each
        timeslot associated with the booking.
        """
        return ", ".join(
            [f"{slot.date} {slot.start_time}" for slot in obj.timeslots.all()]
        )
    display_timeslots.short_description = "Time Slots"

    def confirm_bookings(self, request, queryset):
        """Confirm selected bookings by updating their status to confirmed
        and marking associated timeslots as booked.
        """
        queryset.update(status="confirmed")
        for booking in queryset:
            booking.timeslots.update(status="booked")

    confirm_bookings.short_description = "Confirm selected bookings"

    def decline_bookings(self, request, queryset):
        """Decline selected bookings by updating their status to cancelled
        and reverting associated timeslots to available.
        """
        queryset.update(status="cancelled")
        for booking in queryset:
            booking.timeslots.update(status="available")

    decline_bookings.short_description = "Decline selected bookings"


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


class AdminStarRatingWidget(forms.RadioSelect):
    """
    A custom widget that renders a star rating input for the admin.
    It creates 5 hidden radio inputs and clickable labels showing star icons.
    """

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        output = ['<div class="star-rating-container">']
        for i in range(1, 6):
            checked = ' checked="checked"' if str(i) == str(value) else ''
            output.append(
                (
                    f'<input type="radio" name="{name}" value="{i}" '
                    f'id="{name}_{i}" style="display:none;"{checked}>'
                )
            )
            output.append(
                (
                    f'<label for="{name}_{i}" style="cursor:pointer;">'
                    f'&#9733;</label>'
                )
            )
        output.append('</div>')
        return mark_safe(''.join(output))


class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'rating': AdminStarRatingWidget(
                choices=[(i, i) for i in range(1, 6)]
            ),
        }


class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Review model.
    Displays the booking, user, rating, and created_at fields.
    Provides filtering by rating and creation date, and enables searching
    by username, service name, or comment content.
    """
    form = ReviewAdminForm
    list_display = ('booking', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'booking__service__name', 'comment')


admin.site.register(Review, ReviewAdmin)
