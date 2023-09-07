from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *

# Create your views here.
@login_required
def SOPList(response):
    
    SOPListObjects = SOP.objects.filter(isEnabled=True)
    return render(response, 'SOPList.html', {'SOPList': SOPListObjects})

@login_required
def SpecificSOP(response, id):
    SOPModel = SOP.objects.get(id=id)

    if not SOPModel.isEnabled:
        return HttpResponseRedirect("/SOPs")
    
    elif response.method == "POST":
        if response.POST.get('delete_report'):
            SOPVersioning(action = 'DELETED', SOPModel = SOPModel, user=response.user)
            SOPModel.isEnabled=False
            SOPModel.save()

            return HttpResponseRedirect("/SOPs")
        
        if response.POST.get('edit_report'):
            return HttpResponseRedirect(f"/SOPs/edit/{id}")
    else:
        SOPAttachmentsList = SOPAttachments.objects.filter(SOP = SOPModel)
        return render(response, 'specificSOP.html', {'SOPModel': SOPModel,
                                                    'SOPAttachments': SOPAttachmentsList,})

@login_required
def CreateSOP(response):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":response.user.id, 
        "Username":response.user.username,
        "Email": response.user.email,
        "FirstName": response.user.first_name,
        "LastName": response.user.last_name,
        "TimeOfSignature": str(timezone.now())})
    SOPModel = SOP(title = "Blank SOP",
                          documentBody = "",
                          isEnabled=True,
                          ownerSignature = esignature,
                          owner=response.user)
    SOPModel.save()
    SOPVersioning(action = 'CREATED', SOPModel = SOPModel, user=response.user)
    return HttpResponseRedirect(f"/SOPs/edit/{SOPModel.id}")

@login_required
def EditSOP(response,id):
    
    SOPModel = SOP.objects.get(id=id)
    
    if not SOPModel.isEnabled:
        return HttpResponseRedirect("/SOPs")

    elif response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/SOPs/{id}")
        
        if response.POST.get('save'):

            form = CreateNewSOP(response.POST, response.FILES)

            if form.is_valid():
                SOPModel.title = form.cleaned_data['title']
                SOPModel.documentBody = form.cleaned_data['documentBody']
                
                SOPModel.save()
                SOPVersioning(action = 'EDITED', SOPModel = SOPModel, user=response.user)
                return HttpResponseRedirect(f"/SOPs/{id}")
            
        
        if response.FILES.get('attachedFile'):
            
            form = AttachFilesToSOP(response.POST, response.FILES)
            if form.is_valid():
                SOPAttachmentsModelNew = SOPAttachments(
                    SOP = SOPModel,
                    file = response.FILES['attachedFile'])

                SOPAttachmentsModelNew.save()
                AttachmentsVersioning(action = "ADDED", attachmentsModel = SOPAttachmentsModelNew, user=response.user)
                return redirect('specificAttachment_riskAssessment', SOPAttachmentsModelNew.id)

        if not response.FILES:
            form = AttachFilesToSOP()
            return render(response, 'attachedFiles_form.html', {'form':form,
                                                                'reportId':id})
        

    else:  

        SOPAttachmentsList = SOPAttachments.objects.filter(SOP = SOPModel)

        form = CreateNewSOP(initial={'title':SOPModel.title,
                                    'reportBody':SOPModel.documentBody}
        )
        return render(response, 'editSOP.html', 
                        {'form':form,
                        'SOPModel': SOPModel,
                        'SOPAttachments': SOPAttachmentsList,
                        'id':id})

def SOPVersioning(action = None, SOPModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    newversion = SOP_Versions(  SOP = SOPModel,
                                title = SOPModel.title,
                                documentBody = SOPModel.documentBody,
                                lastAction = action,
                                lastEditedUserSignature = esignature)
    newversion.save()


def CreateAttachmentForm(response, id):
    form = AttachFilesToSOP()
    return render(response, 'attachedFiles_form.html', {'form':form,
                                                        'reportId':id})

def SpecificAttachment(response, id):
    SOPAttachmentModel = SOPAttachments.objects.get(id=id)
    return render(response, 'attachedFiles_detail.html', {'attachedFile':SOPAttachmentModel})

def DeleteAttachment(response, id):
    SOPAttachmentModel = SOPAttachments.objects.get(id=id)
    AttachmentsVersioning(action = "DELETED", attachmentsModel = SOPAttachmentModel, user=response.user)
    SOPAttachmentModel.delete()
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
    newVersion = SOPAttachments_Versions(SOPAttachmentsId = attachmentsModel,
                                            SOP = attachmentsModel.SOP,
                                            fileName = attachmentsModel.file.name,
                                            lastAction = action,
                                            lastEditedUserSignature = esignature)
    newVersion.save()