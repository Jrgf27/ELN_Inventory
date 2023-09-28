from typing import Any
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.signing import TimestampSigner
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from .forms import *
from .models import *
from stock.models import Stock
from projects.models import Projects
from projects.forms import CreateNewProject

from htmxspecific.views import *

def ReportVersioning(action = None, reportModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    
    reportVersionModel = Reports_Versions(
        report = reportModel,
        title = reportModel.title,
        reportBody = reportModel.reportBody,
        reviewed = reportModel.reviewed,
        lastAction = action,
        lastEditedUserSignature = esignature,)
    reportVersionModel.save()

    reportVersionModel.linkedReports_versions.set(reportModel.linkedReports.all())
    reportVersionModel.reportTags.set(reportModel.reportTags.all())
    reportVersionModel.linkedSOPs.set(reportModel.linkedSOPs.all())
    reportVersionModel.linkedReagents.set(reportModel.linkedReagents.all())
    reportVersionModel.linkedSamples.set(reportModel.linkedSamples.all())
    reportVersionModel.linkedEquipments.set(reportModel.linkedEquipments.all())
    reportVersionModel.linkedAttachment.set(reportModel.linkedAttachment.all())
    reportVersionModel.canEditUsers.set(reportModel.canEditUsers.all())
    reportVersionModel.reportReviewers.set(reportModel.reportReviewers.all())

def ReportReviewingVersioning(action = None, reviewerModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    
    reviewerVersionModel = ReportReviewers_Versions(
        reportReviewer = reviewerModel,
        reviewer = reviewerModel.reviewer,
        reviewDecision = reviewerModel.reviewDecision,
        reviewed = reviewerModel.reviewed,
        reviewerSignature = reviewerModel.reviewerSignature,

        lastAction = action,
        lastEditedUserSignature = esignature,)
    reviewerVersionModel.save()

# Create your views here.
@method_decorator(login_required, name='dispatch')
class ReportList(TemplateView):
    template_name = 'reportList.html'

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(**kwargs)
        reportListObjects = Reports.objects.filter(isEnabled=True).filter(project=Projects.objects.get(name=context['projectname'])).order_by('-creationDate')

        paginator = Paginator(reportListObjects,20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        context= {
            'page_obj': page_obj,
            'projects': projects,
            'projectform':projectform,
            'selectedProject': context['projectname'],
        }
        return context

@method_decorator(login_required, name='dispatch')
class SpecificReport(TemplateView):
    template_name='specificReport.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reportInfo = Reports.objects.get(id=context['id'])

        if not reportInfo.isEnabled:
            return redirect('reportList', projectname=context['projectname'])
        
        elif reportInfo.project != Projects.objects.get(name=context['projectname']):
            return redirect('reportList', projectname=context['projectname'])

        editors= reportInfo.canEditUsers.all()
        reportReagentsList = reportInfo.linkedReagents.all()
        reportattachmentsList = reportInfo.linkedAttachment.all()
        reportLinkedReports = reportInfo.linkedReports.all()
        reportLinkedSOPs = reportInfo.linkedSOPs.all()
        reportLinkedSamples = reportInfo.linkedSamples.all()
        reportLinkedEquipment = reportInfo.linkedEquipments.all()
        tagsInReport = reportInfo.reportTags.all()
        reviewers = reportInfo.reportReviewers.all()

        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        context = {
            'reportInfo': reportInfo,
            'reportReagents': reportReagentsList,
            'reportLinkedReports':reportLinkedReports,
            'reportLinkedSOPs' : reportLinkedSOPs,
            'reportattachmentsList':reportattachmentsList,
            'tagList':tagsInReport,
            'reportLinkedSamples':reportLinkedSamples,
            'reportLinkedEquipment' : reportLinkedEquipment,
            'editors':editors,
            'reviewerList':reviewers,
            'projects' : projects,
            'selectedProject': context['projectname'],
            'projectform' : projectform,
        }
        return context
    
    def post(self,response,projectname,id):
        reportInfo = Reports.objects.get(id=id)
        if response.POST.get('delete_report'):
            ReportVersioning(action = 'DELETED', reportModel = reportInfo, user=response.user)
            reportInfo.isEnabled=False
            reportInfo.save()

            return redirect('reportList', projectname=projectname)
        
        if response.POST.get('edit_report'):
            return redirect('editReport', projectname=projectname, id=id)
            
@login_required
def CreateReport(response, projectname):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":response.user.id, 
        "Username":response.user.username,
        "Email": response.user.email,
        "FirstName": response.user.first_name,
        "LastName": response.user.last_name,
        "TimeOfSignature": str(timezone.now())})
    
    reportModel = Reports(title = "Blank Report",
                          reportBody = "",
                          isEnabled=True,
                          project=Projects.objects.get(name=projectname),
                          ownerSignature = esignature,
                          owner=response.user,)
    reportModel.save()
    reportModel.canEditUsers.add(response.user)
    ReportVersioning(action = 'CREATED', reportModel = reportModel, user=response.user)
    return redirect('editReport', projectname=projectname, id=reportModel.id)

@method_decorator(login_required, name='dispatch')
class EditReport(TemplateView):
    template_name='editReport.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        reportInfo = Reports.objects.get(id=context['id'])
    
        if  not reportInfo.isEnabled or not reportInfo.canEditUsers.filter(id=self.request.user.id).exists():
            return redirect('reportList', projectname=context['projectname'])
        
        elif reportInfo.project != Projects.objects.get(name=context['projectname']):
            return redirect('reportList', projectname=context['projectname'])
        
        reportReagents = reportInfo.linkedReagents.all()
        reportReports = reportInfo.linkedReports.all()
        reportSOPs = reportInfo.linkedSOPs.all()
        reportLinkedSamples = reportInfo.linkedSamples.all()
        reportEquipment = reportInfo.linkedEquipments.all()
        reportAttachments = reportInfo.linkedAttachment.all()
        tagsInReport = reportInfo.reportTags.all()
        editors = reportInfo.canEditUsers.exclude(id=reportInfo.owner.id)

        reviewers = reportInfo.reportReviewers.all()

        form = CreateNewReport(initial={'title':reportInfo.title,
                                        'reportBody':reportInfo.reportBody})
        
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        
        context = {
            'form':form,
            'reportInfo': reportInfo,
            'reportReagents': reportReagents,
            'reportReports':reportReports,
            'reportSOPs' : reportSOPs,
            'reportAttachments': reportAttachments,
            'reportLinkedSamples':reportLinkedSamples,
            'reportEquipment' : reportEquipment,
            'tagList':tagsInReport,
            'editorList' : editors,
            'reviewerList':reviewers,
            'id':context['id'],
            'projects' : projects,
            'selectedProject': context['projectname'],
            'projectform' : projectform
            }
        return context
    
    def post(self, response, projectname, id):
        reportInfo = Reports.objects.get(id=id)
        form = CreateNewReport(response.POST, response.FILES)
        if form.is_valid():
            reportTitle = form.cleaned_data['title']
            reportBody = form.cleaned_data['reportBody']
            reportModel = Reports.objects.get(id=id)
            reportModel.title = reportTitle
            reportModel.reportBody = reportBody
            reportModel.save()
            ReportVersioning(action = 'EDITED', reportModel = reportModel, user=response.user)
            return redirect('specificReport', projectname=projectname, id=reportInfo.id)
    
@method_decorator(login_required, name='dispatch')
class CreateReagents(TemplateView):
    template_name='reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachReagentsToReport(),'create-reagents-form')
    
    def post(self,response,id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedReagents,
                            response,
                            'reagentsStockId',
                            'ADDED_REAGENT',
                            'specificReagent',
                            'create-reagents-form',
                            Stock,
                            ReportVersioning
                            )

@login_required
def SpecificReagent(response, id, stockId):
    reportModel = Reports.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        stockId,
        'reagents_detail.html',
        reportModel.linkedReagents,
        'reagent',
        'reportInfo'
    )

@login_required
def DeleteReagent(response, id, stockId):
    reportModel = Reports.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.linkedReagents,
        Stock,
        stockId,
        "REMOVED_REAGENT",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateLinkedReport(TemplateView):
    template_name='reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachReportsToReport(), 'create-linkedreports-form')

    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedReports,
                            response,
                            'report',
                            'ADDED_REPORT',
                            'specificLinkedReport',
                            'create-linkedreports-form',
                            Reports,
                            ReportVersioning
                            )

@login_required
def SpecificLinkedReport(response, id, linkedreportId):
    reportModel = Reports.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        linkedreportId,
        'linkedreport_detail.html',
        reportModel.linkedReports,
        'linkedReport',
        'reportInfo'
    )

@login_required
def DeleteLinkedReport(response, id, linkedreportId):
    reportModel = Reports.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.linkedReports,
        Reports,
        linkedreportId,
        "REMOVED_REPORT",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateLinkedSOP(TemplateView):
    template_name = 'reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachSOPToReport(),'create-linkedsops-form')
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedSOPs,
                            response,
                            'SOP',
                            'ADDED_SOP',
                            'specificLinkedSOP',
                            'create-linkedsops-form',
                            SOP,
                            ReportVersioning
                            )

@login_required
def SpecificLinkedSOP(response, id, linkedsopId):
    reportModel = Reports.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        linkedsopId,
        'linkedsop_detail.html',
        reportModel.linkedSOPs,
        'linkedSOP',
        'reportInfo'
    )

@login_required
def DeleteLinkedSOP(response, id, linkedsopId):

    reportModel = Reports.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.linkedSOPs,
        SOP,
        linkedsopId,
        "REMOVED_SOP",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateAttachment(TemplateView):
    template_name='attachedFiles_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachFilesToReport(), 'create-attachment-form')
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        if response.FILES.get('attachedFile'):
            form = AttachFilesToReport(response.POST, response.FILES)
            if form.is_valid():
                attachmentModel = ReportsAttachments(
                    file = response.FILES['attachedFile'])
                attachmentModel.save()
                reportInfo.linkedAttachment.add(attachmentModel)
                ReportVersioning(action = "ADDED_ATTACHMENT", reportModel = reportInfo, user=response.user)
                return redirect('specificAttachment',reportInfo.id, attachmentModel.id)

        if not response.FILES:
            return redirect('create-attachment-form',id)

@login_required
def SpecificAttachment(response, id, attachmentId):
    reportModel = Reports.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        attachmentId,
        'attachedFiles_detail.html',
        reportModel.linkedAttachment,
        'linkedAttachment',
        'reportInfo'
    )

@login_required
def DeleteAttachment(response, id, attachmentId):
    reportModel = Reports.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.linkedAttachment,
        ReportsAttachments,
        attachmentId,
        "REMOVED_ATTACHMENT",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateTag(TemplateView):
    template_name = 'tag_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        if context['new']:
            form = CreateNewTag()
        else:
            form = AttachTagToReport()
        context= {
            'form':form,
            'documentId':context['id']}
        return context

    def post(self, response, id, new):
        reportInfo = Reports.objects.get(id=id)
        if response.POST.get('newTag'):
            if Tags.objects.filter(name = response.POST.get('newTag').lower()).exists():
                tagModel = Tags.objects.get(name=response.POST.get('newTag').lower())
            
            else:
                tagModel = Tags(name = response.POST.get('newTag').lower())
                tagModel.save()

            reportInfo.reportTags.add(tagModel)
            ReportVersioning(action = "ADDED_TAG", reportModel = reportInfo, user=response.user)
            return redirect('specificTag',reportInfo.id, tagModel.id)
        
        if response.POST.get('newTag') == "":
            return redirect('create-newtag-form', id, 1)
        
        if response.POST.get('attachTag'):
            tagModel = Tags.objects.get(id=response.POST.get('attachTag'))
            reportInfo.reportTags.add(tagModel)
            ReportVersioning(action = "ADDED_TAG", reportModel = reportInfo, user=response.user)
            return redirect('specificTag',reportInfo.id, tagModel.id)
        
        if response.POST.get('attachTag')=="":
            return redirect('create-newtag-form', id, 0)

@login_required
def SpecificTag(response, reportId, tagId):
    reportModel = Reports.objects.get(id=reportId)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        tagId,
        'tag_detail.html',
        reportModel.reportTags,
        'tag',
        'reportInfo'
    )

@login_required
def DeleteTagFromReport(response, reportId, tagId):
    reportModel = Reports.objects.get(id=reportId)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.reportTags,
        Tags,
        tagId,
        "REMOVED_TAG",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateLinkedSample(TemplateView):
    template_name = 'reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachSamplesToReport(), 'create-linkedSamples-form')
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedSamples,
                            response,
                            'linkedSample',
                            'ADDED_SAMPLE',
                            'specificLinkedSample',
                            'create-linkedSamples-form',
                            Sample,
                            ReportVersioning
                            )

@login_required
def SpecificLinkedSample(response, id, sampleId):
    reportModel = Reports.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        sampleId,
        'linkedsamples_detail.html',
        reportModel.linkedSamples,
        'linkedSample',
        'reportInfo'
    )

@login_required
def DeleteLinkedSample(response, id, sampleId):
    reportModel = Reports.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.linkedSamples,
        Sample,
        sampleId,
        "REMOVED_SAMPLE",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateEquipment(TemplateView):
    template_name = 'reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachEquipmentToReport(), 'create-linkedEquipment-form')

    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedEquipments,
                            response,
                            'linkedEquipment',
                            'ADDED_EQUIPMENT',
                            'specificLinkedEquipment',
                            'create-linkedEquipment-form',
                            Equipment,
                            ReportVersioning
                            )

@login_required
def SpecificLinkedEquipment(response, id, equipmentId):
    reportModel = Reports.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        equipmentId,
        'linkedequipment_detail.html',
        reportModel.linkedEquipments,
        'linkedEquipment',
        'reportInfo'
    )

@login_required
def DeleteLinkedEquipment(response, id, equipmentId):
    reportModel = Reports.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.linkedEquipments,
        Equipment,
        equipmentId,
        "REMOVED_EQUIPMENT",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateReportEditor(TemplateView):
    template_name = 'reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AllowEditForm(userId = self.request.user.id), 'create-reporteditor-form')
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.canEditUsers,
                            response,
                            'newEditor',
                            'ADDED_EDITOR',
                            'specificReportEditor',
                            'create-reporteditor-form',
                            User,
                            ReportVersioning
                            )

@login_required       
def SpecificReportEditor(response, reportId, userId):
    reportModel = Reports.objects.get(id=reportId)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        userId,
        'reporteditor_detail.html',
        reportModel.canEditUsers,
        'editor',
        'reportInfo'
    )

@login_required
def DeleteReportEditor(response, reportId, userId):
    reportModel = Reports.objects.get(id=reportId)
    return HTMXDeleteViews(
        response,
        reportModel,
        reportModel.canEditUsers,
        User,
        userId,
        "REMOVED_EDITOR",
        ReportVersioning)

@method_decorator(login_required, name='dispatch')
class CreateReportReviewer(TemplateView):
    template_name = 'reporthtmx_form.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,ReviewerForm(userId = self.request.user.id), 'create-reportreviewer-form')
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
               
        if response.POST.get('newReviewer'):
            newReviewer = User.objects.get(id=response.POST.get('newReviewer'))
            if newReviewer in reportInfo.reportReviewers.all():
                return redirect('create-reportreviewer-form', id)

            reviewerModel = ReportReviewers(
                reviewer = newReviewer,
            )
            reviewerModel.save()
            reportInfo.reportReviewers.add(reviewerModel)
            ReportVersioning(action = "ADDED_REVIEWER", reportModel = reportInfo, user=response.user)
            ReportReviewingVersioning(action="ADDED_REVIEWER", reviewerModel=reviewerModel, user=response.user)
            return redirect('specificReportReviewer',reportInfo.id, reviewerModel.id)
        
        if response.POST.get('newReviewer')=="":
            return redirect('create-reportreviewer-form', id)

@login_required
def SpecificReportReviewer(response, reportId, userId):
    reportModel = Reports.objects.get(id=reportId)
    return HTMXGetSpecificViews(
        response,
        reportModel,
        userId,
        'reportreviewer_detail.html',
        reportModel.reportReviewers,
        'reviewer',
        'reportInfo'
    )

@login_required
def DeleteReportReviewer(response, reportId, userId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=reportId)
        reviewerModel = ReportReviewers.objects.get(id=userId)
        reportModel.reportReviewers.remove(reviewerModel)
        ReportVersioning(action = "REMOVED_REVIEWER", reportModel = reportModel, user=response.user)
        ReportReviewingVersioning(action="REMOVED_REVIEWER", reviewerModel=reviewerModel, user=response.user)
    return HttpResponse('')

@login_required
def ReportReviewDecision(response, userId, decision):
    if response.method == 'POST':
        reviewerModel = ReportReviewers.objects.get(id=userId)
        if response.user.id != reviewerModel.reviewer.id:
            return render(response, 'reportreviewer_detail_specific.html', {'reviewer': reviewerModel})
        
        timestamper = TimestampSigner()
        esignature = timestamper.sign_object({
            "ID":response.user.id, 
            "Username":response.user.username,
            "Email": response.user.email,
            "FirstName": response.user.first_name,
            "LastName": response.user.last_name,
            "TimeOfSignature": str(timezone.now())})
        
        if decision == 1:
            reviewerModel.reviewDecision = 'ACCEPTED'
        else:
            reviewerModel.reviewDecision = 'DECLINED'

        reviewerModel.reviewed = True
        reviewerModel.reviewerSignature = esignature
        reviewerModel.save()
        ReportReviewingVersioning(action="DECISION", reviewerModel=reviewerModel, user=response.user)
        return render(response, 'reportreviewer_detail_specific.html', {'reviewer': reviewerModel})