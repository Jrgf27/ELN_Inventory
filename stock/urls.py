from django.urls import path
from . import views

urlpatterns = [
    path('', views.stockList, name = 'listStock'),
    path('create/', views.CreateStock, name = 'createStock'),
    path('<int:id>', views.SpecificStock, name = 'specificStock'),
    path('edit/<int:id>', views.EditStock, name = 'editStock'),

    path('htmx/stock/<int:id>/delete', views.DeleteStockHTMX, name='deleteStockHTMX'),
    path('htmx/stock/create', views.CreateStockHTMX, name='createStockHTMX'),
    path('htmx/stock/<int:id>/edit', views.EditStockHTMX, name='editStockHTMX'),
]