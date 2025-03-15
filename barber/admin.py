from django.contrib import admin
from .models import Service
from .models import TimeSlot

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
