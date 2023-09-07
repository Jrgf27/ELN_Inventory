from django.urls import path
from . import views

urlpatterns = [
    path('', views.ItemList, name = 'ItemList'),
    path('create/', views.CreateItem, name = 'createItem'),
    path('<int:id>', views.SpecificItem, name = 'specificItem'),
    path('edit/<int:id>', views.EditItem, name = 'editItem'),

    path('htmx/item/<int:id>/delete', views.DeleteItemHTMX, name='deleteItemHTMX'),
    path('htmx/item/create', views.CreateItemHTMX, name='createItemHTMX'),
]
