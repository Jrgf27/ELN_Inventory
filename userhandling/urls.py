from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegisterUser, name = 'registerUser'),
]