from django.contrib import admin

from .models import *
# Register your models here.


@admin.register(Items,
                Items_Versions)
class ItemsAdmin(admin.ModelAdmin):
    pass
