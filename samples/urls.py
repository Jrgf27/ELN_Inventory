from django.urls import path
from . import views

urlpatterns = [
    path('', views.sampleTypeList, name = 'listSampleType'),
    path('create/', views.CreateSampleType, name = 'createSampleType'),
    path('<int:id>', views.SpecificSampleType, name = 'specificSampleType'),
    path('edit/<int:id>', views.EditSampleType, name = 'editSampleType'),
    
    path('sample/<int:id>', views.SpecificSample, name = 'specificSample'),
    path('sample/edit/<int:id>', views.EditSample, name = 'editSample'),

    path('htmx/sampletype/<int:id>/delete', views.DeleteSampleTypeHTMX, name='deleteSampleTypeHTMX'),
    path('htmx/sampletype/create', views.CreateSampleTypeHTMX, name='createSampleTypeHTMX'),

    path('htmx/sample/<int:id>/delete', views.DeleteSampleHTMX, name='deleteSampleHTMX'),
    path('htmx/sample/create', views.CreateSampleHTMX, name='createSampleHTMX'),
]