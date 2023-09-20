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

def HTMXGetViews(context, form):
    return {
        'form':form,
        'reportId':context['id']
        }

def HTMXPostViews(reportInfo,
                  linkedModelManager, 
                  response, 
                  formOption,
                  versioningAction,
                  specificRedirect,
                  formRedirect,
                  modelUsed,
                  ):

    if response.POST.get(formOption):
            model = modelUsed.objects.get(id=response.POST.get(formOption))
            linkedModelManager.add(model)
            ReportVersioning(action = versioningAction, reportModel = reportInfo, user=response.user)
            return redirect(specificRedirect,reportInfo.id, model.id)
        
    if response.POST.get(formOption) == "":
        return redirect(formRedirect, reportInfo.id)

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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
        if response.POST.get('exit'):
            return redirect('specificReport', projectname=projectname, id=reportInfo.id)
        
        if response.POST.get('save'):

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
    template_name='reagents_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachReagentsToReport())
    
    def post(self,response,id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedReagents,
                            response,
                            'reagentsStockId',
                            'ADDED_REAGENT',
                            'specificReagent',
                            'create-reagents-form',
                            Stock
                            )

@login_required
def SpecificReagent(response, id, stockId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=id)
        reportReagentsModel = reportModel.linkedReagents.get(id=stockId)
        return render(response, 'reagents_detail.html', {
            'reportInfo':reportModel,
            'reagent':reportReagentsModel})
    else:
        return HttpResponse('')

@login_required
def DeleteReagent(response, id, stockId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=id)
        reportModel.linkedReagents.remove(Stock.objects.get(id=stockId))
        ReportVersioning(action = "REMOVED_REAGENT", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateLinkedReport(TemplateView):
    template_name='linkedreport_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachReportsToReport())

    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedReports,
                            response,
                            'report',
                            'ADDED_REPORT',
                            'specificLinkedReport',
                            'create-linkedreports-form',
                            Reports
                            )

@login_required
def SpecificLinkedReport(response, id, linkedreportId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=id)
        linkedReport = reportModel.linkedReports.get(id=linkedreportId)
        return render(response, 'linkedreport_detail.html', {
            'reportInfo':reportModel,
            'linkedReport':linkedReport})
    else:
        return HttpResponse('')

@login_required
def DeleteLinkedReport(response, id, linkedreportId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=id)
        reportModel.linkedReports.remove(Reports.objects.get(id=linkedreportId))
        ReportVersioning(action = "REMOVED_REPORT", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateLinkedSOP(TemplateView):
    template_name = 'linkedsop_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachSOPToReport())
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedSOPs,
                            response,
                            'SOP',
                            'ADDED_SOP',
                            'specificLinkedSOP',
                            'create-linkedsops-form',
                            SOP
                            )

@login_required
def SpecificLinkedSOP(response, id, linkedsopId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=id)
        linkedSOP = reportModel.linkedSOPs.get(id=linkedsopId)
        return render(response, 'linkedsop_detail.html', {
            'reportInfo':reportModel,
            'linkedSOP':linkedSOP})
    else:
        return HttpResponse('')

@login_required
def DeleteLinkedSOP(response, id, linkedsopId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=id)
        reportModel.linkedSOPs.remove(SOP.objects.get(id=linkedsopId))
        ReportVersioning(action = "REMOVED_SOP", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateAttachment(TemplateView):
    template_name='attachedFiles_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachFilesToReport())
    
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
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=id)
        linkedAttachment = reportModel.linkedAttachment.get(id=attachmentId)
        return render(response, 'attachedFiles_detail.html', {
            'reportInfo':reportModel,
            'linkedAttachment':linkedAttachment})
    else:
        return HttpResponse('')

@login_required
def DeleteAttachment(response, id, attachmentId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=id)
        reportModel.linkedAttachment.remove(ReportsAttachments.objects.get(id=attachmentId))
        ReportVersioning(action = "REMOVED_ATTACHMENT", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateTag(TemplateView):
    template_name = 'tag_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        if context['new']:
            form = CreateNewTag()
        else:
            form = AttachTagToReport()
        context= {
            'form':form,
            'reportId':context['id']}
        return context

    def post(self, response, id, new):
        reportInfo = Reports.objects.get(id=id)
        if response.POST.get('newTag'):
            if Tags.objects.filter(name = response.POST.get('newTag').lower()).exists():
                tagModel = Tags.objects.get(name=response.POST.get('newTag').lower())
            
            else:
                tagModel = Tags(name = response.POST.get('newTag').lower())
                tagModel.save()

            reportInfo.reportTags.create(tagModel)
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
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=reportId)
        tagModel = Tags.objects.get(id=tagId)
        return render(response, 'tag_detail.html', {
            'reportInfo':reportModel,
            'tag': tagModel})
    else:
        return HttpResponse('')

@login_required
def DeleteTagFromReport(response, reportId, tagId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=reportId)
        tagModel = Tags.objects.get(id=tagId)
        reportModel.reportTags.remove(tagModel)
        ReportVersioning(action = "REMOVED_TAG", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateLinkedSample(TemplateView):
    template_name = 'linkedsamples_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachSamplesToReport())
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedSamples,
                            response,
                            'linkedSample',
                            'ADDED_SAMPLE',
                            'specificLinkedSample',
                            'create-linkedSamples-form',
                            Sample
                            )

@login_required
def SpecificLinkedSample(response, id, sampleId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=id)
        reportLinkedSampleModel = reportModel.linkedSamples.get(id=sampleId)
        return render(response, 'linkedsamples_detail.html', {
            'reportInfo':reportModel,
            'linkedSample':reportLinkedSampleModel})
    else:
        return HttpResponse('')

@login_required
def DeleteLinkedSample(response, id, sampleId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=id)
        reportModel.linkedSamples.remove(Sample.objects.get(id=sampleId))
        ReportVersioning(action = "REMOVED_SAMPLE", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateEquipment(TemplateView):
    template_name = 'linkedequipment_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachEquipmentToReport())

    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.linkedEquipments,
                            response,
                            'linkedEquipment',
                            'ADDED_EQUIPMENT',
                            'specificLinkedEquipment',
                            'create-linkedEquipment-form',
                            Equipment
                            )

@login_required
def SpecificLinkedEquipment(response, id, equipmentId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=id)
        reportEquipmentModel = reportModel.linkedEquipments.get(id=equipmentId)
        return render(response, 'linkedequipment_detail.html', {
            'reportInfo':reportModel,
            'linkedEquipment':reportEquipmentModel})
    else:
        return HttpResponse('')

@login_required
def DeleteLinkedEquipment(response, id, equipmentId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=id)
        reportModel.linkedEquipments.remove(Equipment.objects.get(id=equipmentId))
        ReportVersioning(action = "REMOVED_EQUIPMENT", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateReportEditor(TemplateView):
    template_name = 'reporteditor_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,AllowEditForm(userId = self.request.user.id))
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
        return HTMXPostViews(reportInfo,
                            reportInfo.canEditUsers,
                            response,
                            'newEditor',
                            'ADDED_EDITOR',
                            'specificReportEditor',
                            'create-reporteditor-form',
                            User
                            )

@login_required       
def SpecificReportEditor(response, reportId, userId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=reportId)
        editorModel= reportModel.canEditUsers.get(id=userId)
        return render(response, 'reporteditor_detail.html', {
            'reportInfo':reportModel,
            'editor': editorModel})
    else:
        return HttpResponse('')

@login_required
def DeleteReportEditor(response, reportId, userId):
    if response.method == 'POST':
        reportModel = Reports.objects.get(id=reportId)
        reportModel.canEditUsers.remove(User.objects.get(id=userId))
        ReportVersioning(action = "REMOVED_EDITOR", reportModel = reportModel, user=response.user)
    return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class CreateReportReviewer(TemplateView):
    template_name = 'reportreviewer_form.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        return HTMXGetViews(context,ReviewerForm(userId = self.request.user.id))
    
    def post(self, response, id):
        reportInfo = Reports.objects.get(id=id)
               
        if response.POST.get('newReviewer'):
            newReviewer = User.objects.get(id=response.POST.get('newReviewer'))
            if newReviewer in reportInfo.reportReviewers.all():
                form = ReviewerForm(userId = response.user.id)
                return render(response, 'reportreviewer_form.html', {'form':form,
                                                                    'reportId':id})

            reviewerModel = ReportReviewers(
                reviewer = newReviewer,
            )
            reviewerModel.save()
            reportInfo.reportReviewers.add(reviewerModel)
            ReportVersioning(action = "ADDED_REVIEWER", reportModel = reportInfo, user=response.user)
            ReportReviewingVersioning(action="ADDED_REVIEWER", reviewerModel=reviewerModel, user=response.user)
            return redirect('specificReportReviewer',reportInfo.id, reviewerModel.id)
        
        if response.POST.get('newReviewer')=="":
            form = ReviewerForm(userId = response.user.id)
            return render(response, 'reportreviewer_form.html', {'form':form,
                                                                'reportId':id})

@login_required
def SpecificReportReviewer(response, reportId, userId):
    if response.method == 'GET':
        reportModel = Reports.objects.get(id=reportId)
        reviewerModel= reportModel.reportReviewers.get(id=userId)
        return render(response, 'reportreviewer_detail.html', {
            'reportInfo':reportModel,
            'reviewer': reviewerModel})
    else:
        return HttpResponse('')

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