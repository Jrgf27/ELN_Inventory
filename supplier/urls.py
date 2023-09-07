from django.urls import path
from . import views

urlpatterns = [
    path('', views.SupplierList, name = 'SupplierList'),
    path('create/', views.CreateSupplier, name = 'createSupplier'),
    path('<int:id>', views.SpecificSupplier, name = 'specificSupplier'),
    path('edit/<int:id>', views.EditSupplier, name = 'editSupplier'),

    path('part/<int:id>', views.SpecificSupplierItem, name = 'specificSupplierItem'),
    path('part/edit/<int:id>', views.EditSupplierItem, name = 'editSupplierItem'),

    path('htmx/supplier/<int:id>/delete', views.DeleteSupplierHTMX, name='deleteSupplierHTMX'),
    path('htmx/supplier/create', views.CreateSupplierHTMX, name='createSupplierHTMX'),
    
    path('htmx/supplieritem/<int:id>/delete', views.DeleteSupplierItemHTMX, name='deleteSupplierItemHTMX'),
    path('htmx/supplieritem/create', views.CreateSupplierItemHTMX, name='createSupplierItemHTMX'),
]