"""App module for item category application"""

from django.apps import AppConfig


class ItemcategoryConfig(AppConfig):
    """Item Category application config class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'itemcategory'
