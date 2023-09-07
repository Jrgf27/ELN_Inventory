from django.apps import AppConfig


class UserhandlingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userhandling'

    # def ready(self):
    #     # Insert the code that needs to be executed here
    #     from django.contrib.auth.models import Group, Permission

    #     group, created = Group.objects.get_or_create(name='InventoryManagement')

    #     can_add_items_permission = Permission.objects.get(codename='add_items')
    #     group.permissions.set([can_add_items_permission])