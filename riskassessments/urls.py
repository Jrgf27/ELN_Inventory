from django.urls import path
from . import views

urlpatterns = [
    path('', views.RiskAssessmentList, name = 'RiskAssessmentList'),
    path('create/', views.CreateRiskAssessment, name = 'createRiskAssessment'),
    path('<int:id>', views.SpecificRiskAssessment, name = 'specificRiskAssessment'),
    path('edit/<int:id>', views.EditRiskAssessment, name = 'editRiskAssessment'),

    path('htmx/create-attachment-form/<int:id>', views.CreateAttachmentForm, name='create-attachment-form_riskAssessment'),
    path('htmx/attachment/<int:id>', views.SpecificAttachment, name='specificAttachment_riskAssessment'),
    path('htmx/attachment/<int:id>/delete', views.DeleteAttachment, name='deleteAttachment_riskAssessment'),
]