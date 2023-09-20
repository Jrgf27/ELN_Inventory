from django.urls import path
from . import views

urlpatterns = [
    path('<str:projectname>', views.ReportList.as_view(), name = 'reportList'),
    path('<str:projectname>/create/', views.CreateReport, name = 'createReport'),
    path('<str:projectname>/<int:id>', views.SpecificReport.as_view(), name = 'specificReport'),
    path('<str:projectname>/edit/<int:id>', views.EditReport.as_view(), name = 'editReport'),
    
    path('htmx/create-reagents-form/<int:id>', views.CreateReagents.as_view(), name='create-reagents-form'),
    path('htmx/reagents/<int:id>/<int:stockId>', views.SpecificReagent, name='specificReagent'),
    path('htmx/reagents/<int:id>/<int:stockId>/delete', views.DeleteReagent, name='deleteReagent'),

    path('htmx/create-linkedreports-form/<int:id>', views.CreateLinkedReport.as_view(), name='create-linkedreports-form'),
    path('htmx/linkedreports/<int:id>/<int:linkedreportId>', views.SpecificLinkedReport, name='specificLinkedReport'),
    path('htmx/linkedreports/<int:id>/<int:linkedreportId>/delete', views.DeleteLinkedReport, name='deleteLinkedReport'),

    path('htmx/create-linkedsops-form/<int:id>', views.CreateLinkedSOP.as_view(), name='create-linkedsops-form'),
    path('htmx/linkedsops/<int:id>/<int:linkedsopId>', views.SpecificLinkedSOP, name='specificLinkedSOP'),
    path('htmx/linkedsops/<int:id>/<int:linkedsopId>/delete', views.DeleteLinkedSOP, name='deleteLinkedSOP'),

    path('htmx/create-attachment-form/<int:id>', views.CreateAttachment.as_view(), name='create-attachment-form'),
    path('htmx/attachment/<int:id>/<int:attachmentId>', views.SpecificAttachment, name='specificAttachment'),
    path('htmx/attachment/<int:id>/<int:attachmentId>/delete', views.DeleteAttachment, name='deleteAttachment'),

    path('htmx/create-newtag-form/<int:id>/<int:new>', views.CreateTag.as_view(), name='create-newtag-form'),
    path('htmx/reportTag/<int:reportId>/<int:tagId>/', views.SpecificTag, name='specificTag'),
    path('htmx/reportTag/<int:reportId>/<int:tagId>/delete', views.DeleteTagFromReport, name='deleteTag'),

    path('htmx/create-linkedSamples-form/<int:id>', views.CreateLinkedSample.as_view(), name='create-linkedSamples-form'),
    path('htmx/linkedSamples/<int:id>/<int:sampleId>', views.SpecificLinkedSample, name='specificLinkedSample'),
    path('htmx/linkedSamples/<int:id>/<int:sampleId>/delete', views.DeleteLinkedSample, name='deleteLinkedSample'),

    path('htmx/create-linkedEquipment-form/<int:id>', views.CreateEquipment.as_view(), name='create-linkedEquipment-form'),
    path('htmx/linkedEquipment/<int:id>/<int:equipmentId>', views.SpecificLinkedEquipment, name='specificLinkedEquipment'),
    path('htmx/linkedEquipment/<int:id>/<int:equipmentId>/delete', views.DeleteLinkedEquipment, name='deleteLinkedEquipment'),

    path('htmx/create-editor-form/<int:id>', views.CreateReportEditor.as_view(), name='create-reporteditor-form'),
    path('htmx/editor/<int:reportId>/<int:userId>/', views.SpecificReportEditor, name='specificReportEditor'),
    path('htmx/editor/<int:reportId>/<int:userId>/delete', views.DeleteReportEditor, name='deleteReportEditor'),

    path('htmx/create-reviewer-form/<int:id>', views.CreateReportReviewer.as_view(), name='create-reportreviewer-form'),
    path('htmx/reviewer/<int:reportId>/<int:userId>/', views.SpecificReportReviewer, name='specificReportReviewer'),
    path('htmx/reviewer/<int:reportId>/<int:userId>/delete', views.DeleteReportReviewer, name='deleteReportReviewer'),
    path('htmx/reviewer/<int:userId>/<int:decision>', views.ReportReviewDecision, name='decisionReportReview'),
]