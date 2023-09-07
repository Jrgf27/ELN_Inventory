from django.urls import path
from . import views

urlpatterns = [
    path('', views.LocationList, name = 'LocationList'),
    path('create/', views.CreateLocation, name = 'createLocation'),
    path('<int:id>', views.SpecificLocation, name = 'specificLocation'),
    path('edit/<int:id>', views.EditLocation, name = 'editLocation'),

    path('htmx/location/<int:id>/delete', views.DeleteLocationHTMX, name='deleteLocationHTMX'),
    path('htmx/location/create', views.CreateLocationHTMX, name='createLocationHTMX'),
]
