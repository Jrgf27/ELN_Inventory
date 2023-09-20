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

from htmxspecific.views import *

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

@method_decorator(login_required, name='dispatch')
class CreateAttachment(TemplateView):
    template_name = 'attachedFiles_SOP_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return HTMXGetViews(context,AttachFilesToSOP())
    
    def post(self, response, id):
        SOPModel = SOP.objects.get(id=id)
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

@login_required
def SpecificAttachment(response, id, attachmentId):
    SOPModel = SOP.objects.get(id=id)
    return HTMXGetSpecificViews(
        response,
        SOPModel,
        attachmentId,
        'attachedFiles_SOP_details.html',
        SOPModel.linkedAttachment,
        'linkedAttachment',
        'SOPModel'
    )

@login_required
def DeleteAttachment(response, id, attachmentId):
    SOPModel = SOP.objects.get(id=id)
    return HTMXDeleteViews(
        response,
        SOPModel,
        SOPModel.linkedAttachment,
        SOPAttachments,
        attachmentId,
        "DELETED_ATTACHMENT",
        SOPVersioning)

@method_decorator(login_required, name='dispatch')
class CreateSOPTrainer(TemplateView):
    template_name = 'SOPtrainer_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        return HTMXGetViews(context,TrainerForm())

    def post(self,response,id):
        SOPModel = SOP.objects.get(id=id)
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
    
@login_required
def SpecificSOPTrainer(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    return HTMXGetSpecificViews(
        response,
        SOPModel,
        userId,
        'SOPtrainer_detail.html',
        SOPModel.trainer,
        'trainer',
        'SOPModel'
    )

@login_required
def DeleteSOPTrainer(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    return HTMXDeleteViews(
        response,
        SOPModel,
        SOPModel.trainer,
        User,
        userId,
        "REMOVED_TRAINER",
        SOPVersioning)

@method_decorator(login_required, name='dispatch')
class CreateSOPTrainee(TemplateView):
    template_name = 'SOPtrainee_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        return HTMXGetViews(context,TraineeForm())

    def post(self, response, id):
        SOPModel = SOP.objects.get(id=id)
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

@login_required
def SpecificSOPTrainee(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    return HTMXGetSpecificViews(
        response,
        SOPModel,
        userId,
        'SOPtrainee_detail.html',
        SOPModel.trainee,
        'trainee',
        'SOPModel'
    )

@login_required
def DeleteSOPTrainee(response, SOPId, userId):
    SOPModel = SOP.objects.get(id=SOPId)
    return HTMXDeleteViews(
        response,
        SOPModel,
        SOPModel.trainee,
        User,
        userId,
        "REMOVED_TRAINEE",
        SOPVersioning)