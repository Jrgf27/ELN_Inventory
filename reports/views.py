from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.signing import TimestampSigner
from django.core.paginator import Paginator

from .forms import *
from .models import *
from stock.models import Stock
from projects.models import Projects
from projects.forms import CreateNewProject

# Create your views here.
@login_required
def ReportList(response, projectname):
    reportListObjects = Reports.objects.filter(isEnabled=True).filter(project=Projects.objects.get(name=projectname))

    paginator = Paginator(reportListObjects,1)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()

    return render(response, 'reportList.html', {'page_obj' : page_obj,
                                                'projects' : projects,
                                                'selectedProject': projectname,
                                                'projectform' : projectform})

@login_required
def SpecificReport(response, projectname, id):
    reportInfo = Reports.objects.get(id=id)
    editers= reportInfo.canEditUsers.all()

    if not reportInfo.isEnabled:
        return redirect('reportList', projectname=projectname)
    
    elif reportInfo.project != Projects.objects.get(name=projectname):
        return redirect('reportList', projectname=projectname)

    elif response.method == "POST":
        if response.POST.get('delete_report'):
            ReportVersioning(action = 'DELETED', reportModel = reportInfo, user=response.user)
            reportInfo.isEnabled=False
            reportInfo.save()

            return redirect('reportList', projectname=projectname)
        
        if response.POST.get('edit_report'):
            return redirect('editReport', projectname=projectname, id=id)
        
    else:
        reportReagentsList = reportInfo.linkedReagents.all()
        reportattachmentsList = reportInfo.linkedAttachment.all()
        reportLinkedReports = reportInfo.linkedReports.all()
        reportLinkedSOPs = reportInfo.linkedSOPs.all()
        reportLinkedSamples = reportInfo.linkedSamples.all()
        reportLinkedEquipment = reportInfo.linkedEquipments.all()
        tagsInReport = reportInfo.reportTags.all()

        projects=Projects.objects.all()
        projectform = CreateNewProject()
        return render(response, 'specificReport.html', {'reportInfo': reportInfo,
                                                        'reportReagents': reportReagentsList,
                                                        'reportLinkedReports':reportLinkedReports,
                                                        'reportLinkedSOPs' : reportLinkedSOPs,
                                                        'reportattachmentsList':reportattachmentsList,
                                                        'tagList':tagsInReport,
                                                        'reportLinkedSamples':reportLinkedSamples,
                                                        'reportLinkedEquipment' : reportLinkedEquipment,
                                                        'editers':editers,
                                                        'projects' : projects,
                                                        'selectedProject': projectname,
                                                        'projectform' : projectform})

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

@login_required
def EditReport(response, projectname, id):

    reportInfo = Reports.objects.get(id=id)
    
    if  not reportInfo.isEnabled or not reportInfo.canEditUsers.filter(id=response.user.id).exists():
        return redirect('reportList', projectname=projectname)
    
    elif reportInfo.project != Projects.objects.get(name=projectname):
        return redirect('reportList', projectname=projectname)

    elif response.method == "POST":

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
            
        if response.POST.get('reagentsStockId'):
            
            stockModel = Stock.objects.get(id=response.POST.get('reagentsStockId'))
            reportInfo.linkedReagents.add(stockModel)
            ReportVersioning(action = "ADDED_REAGENT", reportModel = reportInfo, user=response.user)
            return redirect('specificReagent',reportInfo.id, stockModel.id)
        
        if response.POST.get('reagentsStockId') == "":
            form = AttachReagentsToReport()
            return render(response, 'reagents_form.html', { 'form':form,
                                                            'reportId':id})
        
        if response.POST.get('linkedSample'):

            sampleModel = Sample.objects.get(id=response.POST.get('linkedSample'))
            reportInfo.linkedSamples.add(sampleModel)
            ReportVersioning(action = "ADDED_SAMPLE", reportModel = reportInfo, user=response.user)
            return redirect('specificLinkedSample',reportInfo.id, sampleModel.id)
        
        if response.POST.get('linkedSample')=="":
            
            form = AttachSamplesToReport()
            return render(response, 'linkedsamples_form.html', { 'form':form,
                                                                'reportId':id})

        if response.POST.get('report'):
            
            linkedReportModel = Reports.objects.get(id=response.POST.get('report'))
            reportInfo.linkedReports.add(linkedReportModel)
            ReportVersioning(action = "ADDED_REPORT", reportModel = reportInfo, user=response.user)
            return redirect('specificLinkedReport',reportInfo.id, linkedReportModel.id)
        
        if response.POST.get('report') == "":
            form = AttachReportsToReport()
            return render(response, 'linkedreport_form.html', { 'form':form,
                                                            'reportId':id})
        
        if response.POST.get('linkedEquipment'):
            
            equipmentModel = Equipment.objects.get(id=response.POST.get('linkedEquipment'))
            reportInfo.linkedEquipments.add(equipmentModel)
            ReportVersioning(action = "ADDED_EQUIPMENT", reportModel = reportInfo, user=response.user)
            return redirect('specificLinkedEquipment',reportInfo.id, equipmentModel.id)
        
        if response.POST.get('linkedEquipment') == "":
            form = AttachEquipmentToReport()
            return render(response, 'linkedequipment_form.html', { 'form':form,
                                                                'reportId':id})
        
        if response.POST.get('SOP'):
            linkedSOPModel = SOP.objects.get(id=response.POST.get('SOP'))
            reportInfo.linkedSOPs.add(linkedSOPModel)
            ReportVersioning(action = "ADDED_SOP", reportModel = reportInfo, user=response.user)
            return redirect('specificLinkedSOP',reportInfo.id, linkedSOPModel.id)
        
        if response.POST.get('SOP') == "":
            form = AttachSOPToReport()
            return render(response, 'linkedsop_form.html', { 'form':form,
                                                                'reportId':id})

        if response.POST.get('newTag'):
            if Tags.objects.filter(name = response.POST.get('newTag').lower()).exists():
                tagModel = Tags.objects.get(name=response.POST.get('newTag').lower())
                reportInfo.reportTags.add(tagModel)
                ReportVersioning(action = "ADDED_TAG", reportModel = reportInfo, user=response.user)
                return redirect('specificTag',reportInfo.id, tagModel.id)
            
            else:
                tagModel = Tags(name = response.POST.get('newTag').lower())
                tagModel.save()
                reportInfo.reportTags.add(tagModel)
                ReportVersioning(action = "ADDED_TAG", reportModel = reportInfo, user=response.user)
                return redirect('specificTag',reportInfo.id, tagModel.id)
        
        if response.POST.get('newTag') == "":
            form = CreateNewTag()
            return render(response, 'tag_form.html', {'form':form,
                                                        'reportId':id})
        
        if response.POST.get('attachTag'):
            tagModel = Tags.objects.get(id=response.POST.get('attachTag'))
            reportInfo.reportTags.add(tagModel)
            ReportVersioning(action = "ADDED_TAG", reportModel = reportInfo, user=response.user)
            return redirect('specificTag',reportInfo.id, tagModel.id)
        
        if response.POST.get('attachTag')=="":
            form = AttachTagToReport()
            return render(response, 'tag_form.html', {'form':form,
                                                        'reportId':id})

        if response.POST.get('newEditor'):
            editorModel = User.objects.get(id=response.POST.get('newEditor'))
            reportInfo.canEditUsers.add(editorModel)
            ReportVersioning(action = "ADDED_EDITOR", reportModel = reportInfo, user=response.user)
            return redirect('specificReportEditor',reportInfo.id, editorModel.id)
        
        if response.POST.get('newEditor')=="":
            form = AllowEditForm(userId = response.user.id)
            return render(response, 'reporteditor_form.html', {'form':form,
                                                        'reportId':id})

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
            form = AttachFilesToReport()
            return render(response, 'attachedFiles_form.html', {'form':form,
                                                                'reportId':id})

    elif response.method == "GET": 

        reportReagents = reportInfo.linkedReagents.all()
        reportReports = reportInfo.linkedReports.all()
        reportSOPs = reportInfo.linkedSOPs.all()
        reportLinkedSamples = reportInfo.linkedSamples.all()
        reportEquipment = reportInfo.linkedEquipments.all()
        reportAttachments = reportInfo.linkedAttachment.all()
        tagsInReport = reportInfo.reportTags.all()
        editors = reportInfo.canEditUsers.exclude(id=reportInfo.owner.id)


        form = CreateNewReport(initial={'title':reportInfo.title,
                                        'reportBody':reportInfo.reportBody})
        
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        
        return render(response, 'editReport.html', {'form':form,
                                                    'reportInfo': reportInfo,
                                                    'reportReagents': reportReagents,
                                                    'reportReports':reportReports,
                                                    'reportSOPs' : reportSOPs,
                                                    'reportAttachments': reportAttachments,
                                                    'reportLinkedSamples':reportLinkedSamples,
                                                    'reportEquipment' : reportEquipment,
                                                    'tagList':tagsInReport,
                                                    'editorList' : editors,
                                                    'id':id,
                                                    'projects' : projects,
                                                    'selectedProject': projectname,
                                                    'projectform' : projectform})

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

def CreateReagentsForm(response, id):
    form = AttachReagentsToReport()
    return render(response, 'reagents_form.html', {'form':form,
                                                   'reportId':id})

def SpecificReagent(response, id, stockId):
    reportModel = Reports.objects.get(id=id)
    reportReagentsModel = reportModel.linkedReagents.get(id=stockId)
    return render(response, 'reagents_detail.html', {'reportInfo':reportModel,
                                                     'reagent':reportReagentsModel})

def DeleteReagent(response, id, stockId):
    reportModel = Reports.objects.get(id=id)
    reportModel.linkedReagents.remove(Stock.objects.get(id=stockId))
    ReportVersioning(action = "REMOVED_REAGENT", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateLinkedReportForm(response, id):

    form = AttachReportsToReport()
    return render(response, 'linkedreport_form.html', {'form':form,
                                                   'reportId':id})

def SpecificLinkedReport(response, id, linkedreportId):

    reportModel = Reports.objects.get(id=id)
    linkedReport = reportModel.linkedReports.get(id=linkedreportId)
    return render(response, 'linkedreport_detail.html', {'reportInfo':reportModel,
                                                            'linkedReport':linkedReport})

def DeleteLinkedReport(response, id, linkedreportId):
    reportModel = Reports.objects.get(id=id)
    reportModel.linkedReports.remove(Reports.objects.get(id=linkedreportId))
    ReportVersioning(action = "REMOVED_REPORT", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateLinkedSOPForm(response, id):

    form = AttachSOPToReport()
    return render(response, 'linkedsop_form.html', {'form':form,
                                                   'reportId':id})

def SpecificLinkedSOP(response, id, linkedsopId):

    reportModel = Reports.objects.get(id=id)
    linkedSOP = reportModel.linkedSOPs.get(id=linkedsopId)
    return render(response, 'linkedsop_detail.html', {'reportInfo':reportModel,
                                                        'linkedSOP':linkedSOP})

def DeleteLinkedSOP(response, id, linkedsopId):
    reportModel = Reports.objects.get(id=id)
    reportModel.linkedSOPs.remove(SOP.objects.get(id=linkedsopId))
    ReportVersioning(action = "REMOVED_SOP", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateAttachmentForm(response, id):
    form = AttachFilesToReport()
    return render(response, 'attachedFiles_form.html', {'form':form,
                                                   'reportId':id})

def SpecificAttachment(response, id, attachmentId):
    reportModel = Reports.objects.get(id=id)
    linkedAttachment = reportModel.linkedAttachment.get(id=attachmentId)
    return render(response, 'attachedFiles_detail.html', {'reportInfo':reportModel,
                                                        'linkedAttachment':linkedAttachment})

def DeleteAttachment(response, id, attachmentId):

    reportModel = Reports.objects.get(id=id)
    reportModel.linkedAttachment.remove(ReportsAttachments.objects.get(id=attachmentId))
    ReportVersioning(action = "REMOVED_ATTACHMENT", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateNewTagForm(response, id):
    form = CreateNewTag()
    return render(response, 'tag_form.html', {'form':form,
                                                   'reportId':id})

def AddExistingTagForm(response,id):
    form = AttachTagToReport()
    return render(response, 'tag_form.html', {'form':form,
                                                   'reportId':id})

def SpecificTag(response, reportId, tagId):
    reportModel = Reports.objects.get(id=reportId)
    tagModel = Tags.objects.get(id=tagId)
    return render(response, 'tag_detail.html', {'reportInfo':reportModel,
                                                'tag': tagModel})

def DeleteTagFromReport(response, reportId, tagId):
    reportModel = Reports.objects.get(id=reportId)
    tagModel = Tags.objects.get(id=tagId)
    reportModel.reportTags.remove(tagModel)
    ReportVersioning(action = "REMOVED_TAG", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateLinkedSampleForm(response, id):
    form = AttachSamplesToReport()
    return render(response, 'linkedsamples_form.html', {'form':form,
                                                        'reportId':id})

def SpecificLinkedSample(response, id, sampleId):

    reportModel = Reports.objects.get(id=id)
    reportLinkedSampleModel = reportModel.linkedSamples.get(id=sampleId)
    return render(response, 'linkedsamples_detail.html', {'reportInfo':reportModel,
                                                        'linkedSample':reportLinkedSampleModel})

def DeleteLinkedSample(response, id, sampleId):
    reportModel = Reports.objects.get(id=id)
    reportModel.linkedSamples.remove(Sample.objects.get(id=sampleId))
    ReportVersioning(action = "REMOVED_SAMPLE", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateEquipmentForm(response, id):
    form = AttachEquipmentToReport()
    return render(response, 'linkedequipment_form.html', {'form':form,
                                                        'reportId':id})

def SpecificLinkedEquipment(response, id, equipmentId):
    reportModel = Reports.objects.get(id=id)
    reportEquipmentModel = reportModel.linkedEquipments.get(id=equipmentId)
    return render(response, 'linkedequipment_detail.html', {'reportInfo':reportModel,
                                                            'linkedEquipment':reportEquipmentModel})

def DeleteLinkedEquipment(response, id, equipmentId):
    reportModel = Reports.objects.get(id=id)
    reportModel.linkedEquipments.remove(Equipment.objects.get(id=equipmentId))
    ReportVersioning(action = "REMOVED_EQUIPMENT", reportModel = reportModel, user=response.user)
    return HttpResponse('')


def CreateReportEditorForm(response, id):
    form = AllowEditForm(userId = response.user.id)
    return render(response, 'reporteditor_form.html', {'form':form,
                                                   'reportId':id})

def SpecificReportEditor(response, reportId, userId):
    reportModel = Reports.objects.get(id=reportId)
    editorModel= reportModel.canEditUsers.get(id=userId)
    return render(response, 'reporteditor_detail.html', {'reportInfo':reportModel,
                                                        'editor': editorModel})

def DeleteReportEditor(response, reportId, userId):
    reportModel = Reports.objects.get(id=reportId)
    reportModel.canEditUsers.remove(User.objects.get(id=userId))
    ReportVersioning(action = "REMOVED_EDITOR", reportModel = reportModel, user=response.user)
    return HttpResponse('')
