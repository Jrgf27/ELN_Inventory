from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import *
from .forms import CreateNewEquipment
from projects.models import Projects
from projects.forms import CreateNewProject



# Create your views here.
@login_required
def EquipmentList(response):

    equipmentListObjects = Equipment.objects.filter(isEnabled=True).order_by('name')

    paginator = Paginator(equipmentListObjects,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    equipmentForm=CreateNewEquipment()

    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()

    return render(response, 'equipmentList.html', {'page_obj' : page_obj,
                                                    'form':equipmentForm,
                                                    'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def SpecificEquipment(response, id):
    equipmentModel = Equipment.objects.get(id=id)

    if not equipmentModel.isEnabled:
        return HttpResponseRedirect("/equipment")
    
    if response.method == "POST":
        if response.POST.get('delete_category'):

            EquipmentVersioning(action = "DELETED", equipmentModel = equipmentModel, user=response.user)
            equipmentModel.isEnabled=False
            equipmentModel.save()
            return HttpResponseRedirect("/equipment")
        
        if response.POST.get('edit_category'):
            return HttpResponseRedirect(f"/equipment/edit/{id}")
        
    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        return render(response, 'specificEquipment.html', {
            'equipmentModel':equipmentModel, 
            'id':id,
            'projects' : projects,
            'projectform' : projectform
            })

@login_required
def CreateEquipment(response):

    if response.method == "POST":

        form = CreateNewEquipment(response.POST)

        if form.is_valid():

            equipmentModel = Equipment(
                name = form.cleaned_data['name'],
                description= form.cleaned_data['description'],
                origin = form.cleaned_data['origin'],
                supportContact = form.cleaned_data['supportContact'],
                responsibleUser= form.cleaned_data['responsibleUser'],
                )
            equipmentModel.save()
            EquipmentVersioning(action = "CREATED", equipmentModel = equipmentModel, user=response.user)


            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/equipment/{equipmentModel.id}")
            return HttpResponseRedirect("/equipment/create")

    else:
        form = CreateNewEquipment()

        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        return render(response, 'createEquipment.html', {'form':form,
                                                         'projects' : projects,
                                                        'projectform' : projectform})

@login_required
def EditEquipment(response,id):

    equipmentModel = Equipment.objects.get(id=id)

    if not equipmentModel.isEnabled:
        return HttpResponseRedirect("/equipment")
    
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/equipment/{id}")
        
        if response.POST.get('save'):

            form = CreateNewEquipment(response.POST)
            if form.is_valid():

                equipmentModel.name = form.cleaned_data['name']
                equipmentModel.description = form.cleaned_data['description']
                equipmentModel.origin = form.cleaned_data['origin']
                equipmentModel.supportContact = form.cleaned_data['supportContact']
                equipmentModel.responsibleUser= form.cleaned_data['responsibleUser']

                equipmentModel.save()
                EquipmentVersioning(action = "EDITED", equipmentModel = equipmentModel, user=response.user)

                return HttpResponseRedirect(f"/equipment/{id}")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        form = CreateNewEquipment(initial={  'name' : equipmentModel.name,
                                            'description' : equipmentModel.description,
                                            'origin' : equipmentModel.origin,
                                            'supportContact' : equipmentModel.supportContact,
                                            'responsibleUser' : equipmentModel.responsibleUser,
                                            'relatedSOP' : equipmentModel.relatedSOP,
                                            'relatedRiskAssessment' : equipmentModel.relatedRiskAssessment,})
        
        return render(response, 'editEquipment.html', {'form':form,
                                                       'projects' : projects,
                                                        'projectform' : projectform})

def EquipmentVersioning(action = None, equipmentModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    newversion = Equipment_Versions(
        equipment = equipmentModel,
        name = equipmentModel.name,
        description= equipmentModel.description,
        origin = equipmentModel.origin,
        supportContact = equipmentModel.supportContact,
        responsibleUser= equipmentModel.responsibleUser,
        lastAction = action,
        relatedSOP = equipmentModel.relatedSOP,
        relatedRiskAssessment = equipmentModel.relatedRiskAssessment,
        lastEditedUserSignature = esignature)
    newversion.save()

def CreateEquipmentHTMX(response):

    if response.method == "POST":

        form = CreateNewEquipment(response.POST)

        if form.is_valid():

            equipmentModel = Equipment(
                name = form.cleaned_data['name'],
                description= form.cleaned_data['description'],
                origin = form.cleaned_data['origin'],
                supportContact = form.cleaned_data['supportContact'],
                responsibleUser= form.cleaned_data['responsibleUser'],
                )
            equipmentModel.save()
            EquipmentVersioning(action = "CREATED", equipmentModel = equipmentModel, user=response.user)

            return render(response, 'equipment_details.html', {'equipment':equipmentModel})

def DeleteEquipmentHTMX(response, id):
    equipmentModel = Equipment.objects.get(id=id)
    equipmentModel.isEnabled=False
    equipmentModel.save()
    EquipmentVersioning(action = "DELETED", equipmentModel = equipmentModel, user=response.user)
    return HttpResponse('')