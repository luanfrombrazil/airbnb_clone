from django.contrib import admin

from .models import Property, PropertyImage, Reservation

admin.site.register(Property)
admin.site.register(PropertyImage)
admin.site.register(Reservation)
