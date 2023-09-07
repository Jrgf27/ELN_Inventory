from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(Locations,
                Locations_Versions)

class LocationsAdmin(admin.ModelAdmin):
    pass
