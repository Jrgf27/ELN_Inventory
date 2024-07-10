from django.urls import path
from . import views

urlpatterns = [
    path('', views.ItemList.as_view(), name = 'ItemList'),
    path('<int:id>', views.SpecificItem.as_view(), name = 'specificItem'),
    path('edit/<int:id>', views.EditItem.as_view(), name = 'editItem'),

    path('htmx/item/<int:id>/delete', views.ItemHTMX.as_view(), name='deleteItemHTMX'),
    path('htmx/item/create', views.ItemHTMX.as_view(), name='createItemHTMX'),
]
