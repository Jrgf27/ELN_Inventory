from django.urls import path
from . import views

urlpatterns = [
    path('', views.SOPList, name = 'SOPList'),
    path('create/', views.CreateSOP, name = 'createSOP'),
    path('<int:id>', views.SpecificSOP, name = 'specificSOP'),
    path('edit/<int:id>', views.EditSOP, name = 'editSOP'),

    path('htmx/create-attachment-form/<int:id>', views.CreateAttachmentForm, name='create-attachment-form_SOP'),
    path('htmx/attachment/<int:id>', views.SpecificAttachment, name='specificAttachment_SOP'),
    path('htmx/attachment/<int:id>/delete', views.DeleteAttachment, name='deleteAttachment_SOP'),
]