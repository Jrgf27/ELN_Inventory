from django.urls import path
from . import views

urlpatterns = [

    path('htmx/project/<int:id>/delete', views.DeleteProjectHTMX, name='deleteProjectHTMX'),
    path('htmx/project/create', views.CreateProjectHTMX, name='createProjectHTMX'),
]