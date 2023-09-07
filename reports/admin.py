from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(Reports, 
                Reports_Versions, 
                ReportsAttachments,
                Tags,)

class ReportsAdmin(admin.ModelAdmin):
    pass