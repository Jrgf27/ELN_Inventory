from django.urls import path
from . import views

urlpatterns = [
    path('', views.SOPList.as_view(), name = 'SOPList'),
    path('create/', views.CreateSOP, name = 'createSOP'),
    path('<int:id>', views.SpecificSOP.as_view(), name = 'specificSOP'),
    path('edit/<int:id>', views.EditSOP.as_view(), name = 'editSOP'),

    path('htmx/create-attachment-form/<int:id>', views.CreateAttachment.as_view(), name='create-attachment-form_SOP'),
    path('htmx/attachment/<int:id>/<int:attachmentId>', views.SpecificAttachment, name='specificAttachment_SOP'),
    path('htmx/attachment/<int:id>/<int:attachmentId>/delete', views.DeleteAttachment, name='deleteAttachment_SOP'),

    path('htmx/create-trainer-form/<int:id>', views.CreateSOPTrainer.as_view(), name='create-SOPTrainer-form'),
    path('htmx/trainer/<int:SOPId>/<int:userId>/', views.SpecificSOPTrainer, name='specificSOPTrainer'),
    path('htmx/trainer/<int:SOPId>/<int:userId>/delete', views.DeleteSOPTrainer, name='deleteSOPTrainer'),

    path('htmx/create-trainee-form/<int:id>', views.CreateSOPTrainee.as_view(), name='create-SOPTrainee-form'),
    path('htmx/trainee/<int:SOPId>/<int:userId>/', views.SpecificSOPTrainee, name='specificSOPTrainee'),
    path('htmx/trainee/<int:SOPId>/<int:userId>/delete', views.DeleteSOPTrainee, name='deleteSOPTrainee'),
]