from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(ItemCategory,
                ItemCategory_Versions)

class ItemCategoryAdmin(admin.ModelAdmin):
    pass