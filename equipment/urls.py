from django.urls import path
from . import views

urlpatterns = [
    path('', views.EquipmentList.as_view(), name = 'EquipmentList'),
    path('<int:id>', views.SpecificEquipment.as_view(), name = 'specificEquipment'),
    path('edit/<int:id>', views.EditEquipment.as_view(), name = 'editEquipment'),

    path('htmx/equipment/<int:id>/delete', views.EquipmentHTMX.as_view(), name='deleteEquipmentHTMX'),
    path('htmx/equipment/create', views.EquipmentHTMX.as_view(), name='createEquipmentHTMX'),
]