from django.contrib import admin
from .models import Stock, Stock_Versions
# Register your models here.

@admin.register(Stock, Stock_Versions)
class StockAdmin(admin.ModelAdmin):
    pass