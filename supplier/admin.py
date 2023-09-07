from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Suppliers, Suppliers_Versions, SuppliersItems, SuppliersItems_Versions)
class SupplierAdmin(admin.ModelAdmin):
    pass