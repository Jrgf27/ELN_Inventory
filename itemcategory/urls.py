from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryList, name = 'CategoryList'),
    path('create/', views.CreateCategory, name = 'createCategory'),
    path('<int:id>', views.SpecificCategory, name = 'specificCategory'),
    path('edit/<int:id>', views.EditCategory, name = 'editCategory'),

    path('htmx/category/<int:id>/delete', views.DeleteCategoryHTMX, name='deleteCategoryHTMX'),
    path('htmx/category/create', views.CreateCategoryHTMX, name='createCategoryHTMX'),
]