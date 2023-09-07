from django.urls import path
from . import views

urlpatterns = [
    path('', views.EquipmentList, name = 'EquipmentList'),
    path('create/', views.CreateEquipment, name = 'createEquipment'),
    path('<int:id>', views.SpecificEquipment, name = 'specificEquipment'),
    path('edit/<int:id>', views.EditEquipment, name = 'editEquipment'),

    path('htmx/equipment/<int:id>/delete', views.DeleteEquipmentHTMX, name='deleteEquipmentHTMX'),
    path('htmx/equipment/create', views.CreateEquipmentHTMX, name='createEquipmentHTMX'),
]