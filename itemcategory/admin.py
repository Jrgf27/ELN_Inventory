# pylint: disable=relative-beyond-top-level
"""Adding modules from item category to admin page"""

from django.contrib import admin
from .models import ItemCategory

# Register your models here.
admin.site.register(ItemCategory)
