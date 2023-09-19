from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import *
from .models import *
from projects.models import Projects
from projects.forms import CreateNewProject


# Create your views here.
@login_required
def SOPList(response):
    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()

    SOPListObjects = SOP.objects.filter(isEnabled=True).order_by('-creationDate')

    paginator = Paginator(SOPListObjects,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(response, 'SOPList.html', {   'page_obj' : page_obj,
                                                'projects' : projects,
                                                'projectform' : projectform})

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
        
        if response.POST.get('newTrainee'):

            for trainee in SOPModel.trainee.all():
                print(trainee, int(response.POST.get('newTrainee')))
                if trainee.id == int(response.POST.get('newTrainee')):
                    form = TraineeForm()
                    return render(response, 'SOPtrainee_form.html', {'form':form,
                                                        'SOPId':id})

            SOPModel.trainee.add(User.objects.get(id = response.POST.get('newTrainee')))
            SOPVersioning(action = "ADDED_TRAINEE", SOPModel = SOPModel, user=response.user)
            return redirect('specificSOPTrainee',SOPModel.id, response.POST.get('newTrainee'))

        if response.POST.get('newTrainee')=="":
            form = TraineeForm()
            return render(response, 'SOPtrainee_form.html', {'form':form,
                                                            'SOPId':id})
        

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        SOPModelAttachments = SOPModel.linkedAttachment.all()
        trainerList = SOPModel.trainer.all()
        traineeList = SOPModel.trainee.all()
        return render(response, 'specificSOP.html', {'SOPModel': SOPModel,
                                                     'SOPModelAttachments':SOPModelAttachments,
                                                     'trainerList':trainerList,
                                                     'traineeList':traineeList,
                                                     'projects' : projects,
                                                     'projectform' : projectform})

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

        if response.POST.get('newTrainer'):

            for trainer in SOPModel.trainer.all():
                print(trainer, int(response.POST.get('newTrainer')))
                if trainer.id == int(response.POST.get('newTrainer')):
                    form = TrainerForm()
                    return render(response, 'SOPtrainer_form.html', {'form':form,
                                                        'SOPId':id})

            SOPModel.trainer.add(User.objects.get(id = response.POST.get('newTrainer')))
            SOPVersioning(action = "ADDED_TRAINER", SOPModel = SOPModel, user=response.user)
            return redirect('specificSOPTrainer',SOPModel.id, response.POST.get('newTrainer'))

        if response.POST.get('newTrainer')=="":
            form = TrainerForm()
            return render(response, 'SOPtrainer_form.html', {'form':form,
                                                        'SOPId':id})

        if response.POST.get('newTrainee'):

            for trainee in SOPModel.trainee.all():
                print(trainee, int(response.POST.get('newTrainee')))
                if trainee.id == int(response.POST.get('newTrainee')):
                    form = TraineeForm()
                    return render(response, 'SOPtrainee_form.html', {'form':form,
                                                        'SOPId':id})

            SOPModel.trainee.add(User.objects.get(id = response.POST.get('newTrainee')))
            SOPVersioning(action = "ADDED_TRAINEE", SOPModel = SOPModel, user=response.user)
            return redirect('specificSOPTrainee',SOPModel.id, response.POST.get('newTrainee'))

        if response.POST.get('newTrainee')=="":
            form = TraineeForm()
            return render(response, 'SOPtrainee_form.html', {'form':form,
                                                            'SOPId':id})

        if response.FILES.get('attachedFile'):
            
            form = AttachFilesToSOP(response.POST, response.FILES)
            if form.is_valid():
                SOPAttachmentsModelNew = SOPAttachments(
                    file = response.FILES['attachedFile'])

                SOPAttachmentsModelNew.save()
                SOPModel.linkedAttachment.add(SOPAttachmentsModelNew)
                SOPVersioning(action = "ADDED_ATTACHMENT", SOPModel = SOPModel, user=response.user)
                return redirect('specificAttachment_SOP', SOPModel.id, SOPAttachmentsModelNew.id)

        if not response.FILES:
            form = AttachFilesToSOP()
            return render(response, 'attachedFiles_form.html', {'form':form,
                                                                'reportId':id})
        
    else:  
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        form = CreateNewSOP(initial={'title':SOPModel.title,
                                    'reportBody':SOPModel.documentBody})
        SOPModelAttachments = SOPModel.linkedAttachment.all()
        trainerList = SOPModel.trainer.all()
        traineeList = SOPModel.trainee.all()
        

        return render(response, 'editSOP.html', 
                        {'form':form,
                        'SOPModel': SOPModel,
                        'SOPModelAttachments':SOPModelAttachments,
                        'trainerList':trainerList,
                        'traineeList':traineeList,
                        'id':id,
                        'projects' : projects,
                        'projectform' : projectform})

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
    newversion.linkedAttachment.set(SOPModel.linkedAttachment.all())
    newversion.trainer.set(SOPModel.trainer.all())
    newversion.trainee.set(SOPModel.trainee.all())


def CreateAttachmentForm(response, id):
    form = AttachFilesToSOP()
    return render(response, 'attachedFiles_form.html', {'form':form,
                                                        'reportId':id})

def SpecificAttachment(response, id, attachmentId):
    SOPModel = SOP.objects.get(id=id)
    SOPAttachmentModel = SOPModel.linkedAttachment.get(id=attachmentId)
    return render(response, 'attachedFiles_SOP_details.html', {'linkedAttachment':SOPAttachmentModel,
                                                          'SOPModel':SOPModel})

def DeleteAttachment(response, id, attachmentId):
    SOPModel = SOP.objects.get(id=id)
    SOPAttachmentModel = SOPModel.linkedAttachment.get(id=attachmentId)
    SOPModel.linkedAttachment.remove(SOPAttachmentModel)
    SOPVersioning(action = "DELETED_ATTACHMENT", SOPModel = SOPModel, user=response.user)
    return HttpResponse('')


def CreateSOPTrainerForm(response, id):
    form = TrainerForm()
    return render(response, 'SOPtrainer_form.html', {'form':form,
                                                   'SOPId':id})

def SpecificSOPTrainer(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    trainerModel= SOPModel.trainer.get(id=userId)
    return render(response, 'SOPtrainer_detail.html', {'SOPModel':SOPModel,
                                                        'trainer': trainerModel})

def DeleteSOPTrainer(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    trainerModel = User.objects.get(id=userId)
    SOPModel.trainer.remove(trainerModel)
    SOPVersioning(action = "REMOVED_TRAINER", SOPModel = SOPModel, user=response.user)
    return HttpResponse('')


def CreateSOPTraineeForm(response, id):
    form = TraineeForm()
    return render(response, 'SOPtrainee_form.html', {'form':form,
                                                   'SOPId':id})

def SpecificSOPTrainee(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    traineeModel= SOPModel.trainee.get(id=userId)
    return render(response, 'SOPtrainee_detail.html', {'SOPModel':SOPModel,
                                                        'trainee': traineeModel})

def DeleteSOPTrainee(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    traineeModel = User.objects.get(id=userId)
    SOPModel.trainee.remove(traineeModel)
    SOPVersioning(action = "REMOVED_TRAINEE", SOPModel = SOPModel, user=response.user)
    return HttpResponse('')