# pylint: disable=relative-beyond-top-level
"""URL paths for Item Category Application"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCategory.as_view(), name = 'CategoryList'),
    path('create/', views.CreateCategory.as_view(), name = 'createCategory'),
    path('<int:category_id>', views.DetailCategory.as_view(), name = 'specificCategory'),
    path('edit/<int:category_id>', views.EditCategory.as_view(), name = 'editCategory'),

    path('htmx/category/<int:category_id>/delete',
         views.DeleteCategoryHTMX.as_view(),
         name='deleteCategoryHTMX'),
    path('htmx/category/create',
         views.CreateCategoryHTMX.as_view(),
         name='createCategoryHTMX'),
]
