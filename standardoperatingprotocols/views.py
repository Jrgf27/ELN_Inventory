from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from .forms import *
from .models import *
from projects.models import Projects
from projects.forms import CreateNewProject


# Create your views here.

@method_decorator(login_required, name='dispatch')
class SOPList(TemplateView):

    template_name = 'SOPList.html'

    def get_context_data(self):
        context = super().get_context_data()
        
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        SOPListObjects = SOP.objects.filter(isEnabled=True).order_by('-creationDate')
        paginator = Paginator(SOPListObjects,1)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['projects'] = projects
        context['projectform'] = projectform
        return context

@method_decorator(login_required, name='dispatch')
class SpecificSOP(TemplateView):
    template_name = 'specificSOP.html'

    def get_context_data(self,id):
        context = super().get_context_data()
        SOPModel = SOP.objects.get(id=id)

        if not SOPModel.isEnabled:
            return redirect ("SOPList")
        
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        SOPModelAttachments = SOPModel.linkedAttachment.all()
        trainerList = SOPModel.trainer.all()
        traineeList = SOPModel.trainee.all()

        context['SOPModel'] = SOPModel
        context['SOPModelAttachments'] = SOPModelAttachments
        context['trainerList'] = trainerList
        context['traineeList'] = traineeList
        context['projects'] = projects
        context['projectform'] = projectform

        return context

    def post(self, response, id):
        SOPModel = SOP.objects.get(id=id)

        if response.POST.get('delete_report'):
            SOPVersioning(action = 'DELETED', SOPModel = SOPModel, user=response.user)
            SOPModel.isEnabled=False
            SOPModel.save()

            return redirect ("SOPList")
        
        if response.POST.get('edit_report'):
            return redirect('editSOP', id)
        
        if response.POST.get('newTrainee'):
            newTrainee=User.objects.get(id = response.POST.get('newTrainee'))
            if newTrainee in SOPModel.trainee.all():
                return redirect('create-SOPTrainee-form', id)

            SOPModel.trainee.add(newTrainee)
            SOPVersioning(action = "ADDED_TRAINEE", SOPModel = SOPModel, user=response.user)
            return redirect('specificSOPTrainee', SOPModel.id, response.POST.get('newTrainee'))

        if response.POST.get('newTrainee')=="":
            return redirect('create-SOPTrainee-form', id)

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
    SOPModel = SOP(
        title = "Blank SOP",
        documentBody = "",
        isEnabled=True,
        ownerSignature = esignature,
        owner=response.user)
    SOPModel.save()
    SOPVersioning(action = 'CREATED', SOPModel = SOPModel, user=response.user)
    return redirect('editSOP', SOPModel.id)

@method_decorator(login_required, name='dispatch')
class EditSOP(TemplateView):
    template_name = 'editSOP.html'

    def get_context_data(self,id):
        context = super().get_context_data()
        SOPModel = SOP.objects.get(id=id)

        if not SOPModel.isEnabled:
            return redirect ("SOPList")
        
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        form = CreateNewSOP(initial={
            'title':SOPModel.title,
            'reportBody':SOPModel.documentBody
            })
        
        SOPModelAttachments = SOPModel.linkedAttachment.all()
        trainerList = SOPModel.trainer.all()
        traineeList = SOPModel.trainee.all()

        context['form'] = form
        context['SOPModel'] = SOPModel
        context['SOPModelAttachments'] = SOPModelAttachments
        context['trainerList'] = trainerList
        context['traineeList'] = traineeList
        context['id'] = id
        context['projects'] = projects
        context['projectform'] = projectform
        
        return context

    def post(self,response,id):
        SOPModel = SOP.objects.get(id=id)

        if response.POST.get('exit'):
            return redirect ("specificSOP", id)

        if response.POST.get('save'):
            form = CreateNewSOP(response.POST, response.FILES)
            if form.is_valid():
                SOPModel.title = form.cleaned_data['title']
                SOPModel.documentBody = form.cleaned_data['documentBody']
                SOPModel.save()
                SOPVersioning(action = 'EDITED', SOPModel = SOPModel, user=response.user)
                return redirect ("specificSOP", id)

        if response.POST.get('newTrainer'):
            form = TrainerForm(response.POST,response.FILES)
            if form.is_valid():
                newTrainer = User.objects.get(id = response.POST.get('newTrainer'))
                if newTrainer in SOPModel.trainer.all():
                    return redirect('create-SOPTrainer-form', id)
                    
                SOPModel.trainer.add(newTrainer)
                SOPVersioning(action = "ADDED_TRAINER", SOPModel = SOPModel, user=response.user)
                return redirect('specificSOPTrainer',SOPModel.id, response.POST.get('newTrainer'))

        if response.POST.get('newTrainer')=="":
            return redirect('create-SOPTrainer-form', id)

        if response.POST.get('newTrainee'):
            form = TraineeForm(response.POST,response.FILES)
            if form.is_valid():
                newTrainee=User.objects.get(id = response.POST.get('newTrainee'))
                if newTrainee in SOPModel.trainee.all():
                    return redirect('create-SOPTrainee-form', id)

                SOPModel.trainee.add(newTrainee)
                SOPVersioning(action = "ADDED_TRAINEE", SOPModel = SOPModel, user=response.user)
                return redirect('specificSOPTrainee',SOPModel.id, response.POST.get('newTrainee'))

        if response.POST.get('newTrainee')=="":
            return redirect('create-SOPTrainee-form', id)

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
            return redirect('create-attachment-form_SOP',id)

def SOPVersioning(action = None, SOPModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    newversion = SOP_Versions(  
        SOP = SOPModel,
        title = SOPModel.title,
        documentBody = SOPModel.documentBody,
        lastAction = action,
        lastEditedUserSignature = esignature)
    newversion.save()
    newversion.linkedAttachment.set(SOPModel.linkedAttachment.all())
    newversion.trainer.set(SOPModel.trainer.all())
    newversion.trainee.set(SOPModel.trainee.all())

@login_required
def CreateAttachmentForm(response, id):
    if response.method == 'GET':
        form = AttachFilesToSOP()
        return render(response, 'attachedFiles_form.html', {
            'form':form,
            'reportId':id})
    else:
        return HttpResponse('')

@login_required
def SpecificAttachment(response, id, attachmentId):
    if response.method == 'GET':
        SOPModel = SOP.objects.get(id=id)
        SOPAttachmentModel = SOPModel.linkedAttachment.get(id=attachmentId)
        return render(response, 'attachedFiles_SOP_details.html', {
            'linkedAttachment':SOPAttachmentModel,
            'SOPModel':SOPModel
            })
    else:
        return HttpResponse('')

@login_required
def DeleteAttachment(response, id, attachmentId):
    if response.method == 'POST':
        SOPModel = SOP.objects.get(id=id)
        SOPAttachmentModel = SOPModel.linkedAttachment.get(id=attachmentId)
        SOPModel.linkedAttachment.remove(SOPAttachmentModel)
        SOPVersioning(action = "DELETED_ATTACHMENT", SOPModel = SOPModel, user=response.user)
    return HttpResponse('')

@login_required
def CreateSOPTrainerForm(response, id):
    if response.method == 'GET':
        form = TrainerForm()
        return render(response, 'SOPtrainer_form.html', {
            'form':form,
            'SOPId':id
            })
    else:
        return HttpResponse('')

@login_required
def SpecificSOPTrainer(response, SOPId, userId):
    if response.method == 'GET':
        SOPModel = SOP.objects.get(id=SOPId)
        trainerModel= SOPModel.trainer.get(id=userId)
        return render(response, 'SOPtrainer_detail.html', {
            'SOPModel':SOPModel,
            'trainer': trainerModel
            })
    else:
        return HttpResponse('')

@login_required
def DeleteSOPTrainer(response, SOPId, userId):
    if response.method == 'POST':
        SOPModel = SOP.objects.get(id=SOPId)
        trainerModel = User.objects.get(id=userId)
        SOPModel.trainer.remove(trainerModel)
        SOPVersioning(action = "REMOVED_TRAINER", SOPModel = SOPModel, user=response.user)
    return HttpResponse('')

@login_required
def CreateSOPTraineeForm(response, id):
    if response.method == 'GET':
        form = TraineeForm()
        return render(response, 'SOPtrainee_form.html', {
            'form':form,
            'SOPId':id
            })
    else:
        return HttpResponse('')

@login_required
def SpecificSOPTrainee(response, SOPId, userId):
    if response.method == 'GET':
        SOPModel = SOP.objects.get(id=SOPId)
        traineeModel= SOPModel.trainee.get(id=userId)
        return render(response, 'SOPtrainee_detail.html', {
            'SOPModel':SOPModel,
            'trainee': traineeModel
            })
    else:
        return HttpResponse('')

@login_required
def DeleteSOPTrainee(response, SOPId, userId):
    if response.method == 'POST':
        SOPModel = SOP.objects.get(id=SOPId)
        traineeModel = User.objects.get(id=userId)
        SOPModel.trainee.remove(traineeModel)
        SOPVersioning(action = "REMOVED_TRAINEE", SOPModel = SOPModel, user=response.user)
    return HttpResponse('')