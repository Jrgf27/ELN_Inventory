from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.signing import TimestampSigner

from .forms import *
from .models import *

# Create your views here.
@login_required
def RiskAssessmentList(response):
    riskAssessmentListObjects = RiskAssessment.objects.filter(isEnabled=True)

    return render(response, 'riskAssessmentList.html', {'riskAssessmentList': riskAssessmentListObjects})

@login_required
def SpecificRiskAssessment(response, id):
    riskAssessmentInfo = RiskAssessment.objects.get(id=id)

    if not riskAssessmentInfo.isEnabled:
        return HttpResponseRedirect("/riskassessments")
    
    elif response.method == "POST":
        if response.POST.get('delete_report'):
            RiskAssessmentVersioning(action = 'DELETED', riskAssessmentModel = riskAssessmentInfo, user=response.user)
            riskAssessmentInfo.isEnabled=False
            riskAssessmentInfo.save()

            return HttpResponseRedirect("/riskassessments")
        
        if response.POST.get('edit_report'):
            return HttpResponseRedirect(f"/riskassessments/edit/{id}")
    else:
        riskAssessmentAttachments = RiskAssessmentAttachments.objects.filter(riskAssessment = riskAssessmentInfo)
        return render(response, 'specificRiskAssessment.html', {'riskAssessmentInfo': riskAssessmentInfo,
                                                                'riskAssessmentAttachments': riskAssessmentAttachments,})

@login_required
def CreateRiskAssessment(response):
    timestamper = TimestampSigner()
    timestamper.timestamp()
    esignature = timestamper.sign_object({
        "ID":response.user.id, 
        "Username":response.user.username,
        "Email": response.user.email,
        "FirstName": response.user.first_name,
        "LastName": response.user.last_name,
        "TimeOfSignature": str(timezone.now())})
    riskAssessmentModel = RiskAssessment(title = "Blank Risk Assessment",
                          documentBody = "",
                          isEnabled=True,
                          ownerSignature = esignature,
                          owner = response.user)
    riskAssessmentModel.save()
    RiskAssessmentVersioning(action = 'CREATED', riskAssessmentModel = riskAssessmentModel, user=response.user)
    return HttpResponseRedirect(f"/riskassessments/edit/{riskAssessmentModel.id}")

@login_required
def EditRiskAssessment(response,id):
    
    riskAssessmentInfo = RiskAssessment.objects.get(id=id)
    
    if not riskAssessmentInfo.isEnabled:
        return HttpResponseRedirect("/riskassessments")

    elif response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/riskassessments/{id}")
        
        if response.POST.get('save'):

            form = CreateNewRiskAssessment(response.POST, response.FILES)

            if form.is_valid():
                riskAssessmentModel = RiskAssessment.objects.get(id=id)
                riskAssessmentModel.title = form.cleaned_data['title']
                riskAssessmentModel.documentBody = form.cleaned_data['documentBody']
                
                riskAssessmentModel.save()
                RiskAssessmentVersioning(action = 'EDITED', riskAssessmentModel = riskAssessmentModel, user=response.user)
                return HttpResponseRedirect(f"/riskassessments/{id}")
            
        
        if response.FILES.get('attachedFile'):
            
            form = AttachFilesToRiskAssessment(response.POST, response.FILES)
            if form.is_valid():
                riskAssessmentAttachmentsModelNew = RiskAssessmentAttachments(
                    riskAssessment = riskAssessmentInfo,
                    file = response.FILES['attachedFile'])

                riskAssessmentAttachmentsModelNew.save()
                AttachmentsVersioning(action = "ADDED", attachmentsModel = riskAssessmentAttachmentsModelNew, user=response.user)
                return redirect('specificAttachment_riskAssessment', riskAssessmentAttachmentsModelNew.id)

        if not response.FILES:
            form = AttachFilesToRiskAssessment()
            return render(response, 'attachedFiles_form.html', {'form':form,
                                                                'reportId':id})
        

    else:  

        riskAssessmentAttachments = RiskAssessmentAttachments.objects.filter(riskAssessment = riskAssessmentInfo)

        form = CreateNewRiskAssessment(initial={'title':riskAssessmentInfo.title,
                                                'reportBody':riskAssessmentInfo.documentBody}
        )
        return render(response, 'editRiskAssessment.html', 
                        {'form':form,
                        'riskAssessmentInfo': riskAssessmentInfo,
                        'riskAssessmentAttachments': riskAssessmentAttachments,
                        'id':id})

def RiskAssessmentVersioning(action = None, riskAssessmentModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    riskAssessmentVersionModel = RiskAssessment_Versions(
        riskAssessment = riskAssessmentModel,
        title = riskAssessmentModel.title,
        documentBody = riskAssessmentModel.documentBody,
        lastAction = action,
        lastEditedUserSignature = esignature)
    riskAssessmentVersionModel.save()


def CreateAttachmentForm(response, id):
    form = AttachFilesToRiskAssessment()
    return render(response, 'attachedFiles_form.html', {'form':form,
                                                        'reportId':id})

def SpecificAttachment(response, id):
    reportAttachmentModel = RiskAssessmentAttachments.objects.get(id=id)
    return render(response, 'attachedFiles_detail.html', {'attachedFile':reportAttachmentModel})

def DeleteAttachment(response, id):
    reportAttachmentModel = RiskAssessmentAttachments.objects.get(id=id)
    AttachmentsVersioning(action = "DELETED", attachmentsModel = reportAttachmentModel, user=response.user)
    reportAttachmentModel.delete()
    return HttpResponse('')

def AttachmentsVersioning(action = None, attachmentsModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    newVersion = RiskAssessmentAttachments_Versions(
        reportAttachmentsId = attachmentsModel,
        riskAssessment = attachmentsModel.riskAssessment,
        fileName = attachmentsModel.file.name,
        lastAction = action,
        lastEditedUserSignature = esignature)
    newVersion.save()