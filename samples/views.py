from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import *
from .models import *

from reports.models import Reports
from projects.models import Projects
from projects.forms import CreateNewProject

# Create your views here.
@login_required
def sampleTypeList(response):
    sampletypeform = CreateNewSampleType()
    sampleTypeList = SampleType.objects.filter(isEnabled=True)

    paginator = Paginator(sampleTypeList,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()
    return render(response, 'sampleTypeList.html', {'page_obj':page_obj,
                                                  'sampletypeform':sampletypeform,
                                                  'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def CreateSampleType(response):

    if response.method == "POST":

        form = CreateNewSampleType(response.POST)

        if form.is_valid():

            sampleTypeName = form.cleaned_data['name']
            sampleTypeDescription = form.cleaned_data['description']

            sampleTypeModel = SampleType(name = sampleTypeName,
                                      description= sampleTypeDescription)
            sampleTypeModel.save()
            SampleTypeVersioning(action = "CREATED", sampleTypeModel = sampleTypeModel, user=response.user)

            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/sampletype/{sampleTypeModel.id}")
            return HttpResponseRedirect("/sampletype/create")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewSampleType()


        return render(response, 'createSampleType.html', {'form':form,
                                                          'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def SpecificSampleType(response, id):
    
    sampleTypeModel = SampleType.objects.get(id=id)
    

    if not sampleTypeModel.isEnabled:
        return HttpResponseRedirect("/sampletype")
    
    if response.method == "POST":
        if response.POST.get('delete_sampleType'):

            SampleTypeVersioning(action = "DELETED", sampleTypeModel = sampleTypeModel, user=response.user)
            sampleTypeModel.isEnabled=False
            sampleTypeModel.save()
            return HttpResponseRedirect("/sampletype")
        
        if response.POST.get('edit_sampleType'):
            return HttpResponseRedirect(f"/sampletype/edit/{id}")
        
    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        sampleList = Sample.objects.filter(isEnabled=True).filter(sampleType = sampleTypeModel)
        sampleform = CreateNewSample(initial={'sampleType' : sampleTypeModel})

        paginator = Paginator(sampleList,20)
        page_number = response.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(response, 'specificSampleType.html', {'sampleTypeModel':sampleTypeModel, 
                                                            'id':id,
                                                            'sampleform':sampleform,
                                                            'page_obj':page_obj,
                                                            'projects' : projects,
                                                            'projectform' : projectform})

@login_required
def EditSampleType(response,id):
    sampleTypeModel = SampleType.objects.get(id=id)

    if not sampleTypeModel.isEnabled:
        return HttpResponseRedirect("/sampletype")
    
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/sampletype/{id}")
        
        if response.POST.get('save'):

            form = CreateNewSampleType(response.POST)
            if form.is_valid():

                categoryName = form.cleaned_data['name']
                categoryDescription = form.cleaned_data['description']

                sampleTypeModel.name = categoryName
                sampleTypeModel.description = categoryDescription

                sampleTypeModel.save()
                SampleTypeVersioning(action = "EDITED", sampleTypeModel = sampleTypeModel, user=response.user)

                return HttpResponseRedirect("/sampletype")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewSampleType(initial={  'name' : sampleTypeModel.name,
                                            'description' : sampleTypeModel.description})
        
        return render(response, 'editSampleType.html', {'form':form,
                                                        'projects' : projects,
                                                    'projectform' : projectform})
    
def SampleTypeVersioning(action = None, sampleTypeModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    sampleTypeVersionModel = SampleType_Versions(sampleType = sampleTypeModel,
                                        name = sampleTypeModel.name,
                                        description= sampleTypeModel.description,
                                        lastAction = action,
                                        lastEditedUserSignature = esignature)
    sampleTypeVersionModel.save()


def DeleteSampleTypeHTMX(response, id):
    sampleTypeModel = SampleType.objects.get(id=id)
    sampleTypeModel.isEnabled=False
    sampleTypeModel.save()
    SampleTypeVersioning(action = "DELETED", sampleTypeModel = sampleTypeModel, user=response.user)
    return HttpResponse('')

def CreateSampleTypeHTMX(response):
    if response.method == "POST":

        form = CreateNewSampleType(response.POST)

        if form.is_valid():

            sampleTypeName = form.cleaned_data['name']
            sampleTypeDescription = form.cleaned_data['description']

            sampleTypeModel = SampleType(name = sampleTypeName,
                                      description= sampleTypeDescription)
            sampleTypeModel.save()
            SampleTypeVersioning(action = "CREATED", sampleTypeModel = sampleTypeModel, user=response.user)

            return render(response, 'sampleType_details.html', {'sampleType':sampleTypeModel})

@login_required
def SpecificSample(response, id):
    
    sampleModel = Sample.objects.get(id=id)
    reportsLinked = Reports.objects.filter(linkedSamples=sampleModel)
    if not sampleModel.isEnabled:
        return HttpResponseRedirect("/sampletype")
    
    if response.method == "POST":
        if response.POST.get('delete_sample'):

            SampleVersioning(action = "DELETED", sampleModel = sampleModel, user=response.user)
            sampleModel.isEnabled=False
            sampleModel.save()
            return HttpResponseRedirect(f"/sampletype/{sampleModel.sampleType.id}")
        
        if response.POST.get('edit_sample'):
            return HttpResponseRedirect(f"/sampletype/sample/edit/{id}")
        
    else:
        return render(response, 'specificSample.html', {'sample':sampleModel,
                                                        'reportsLinked':reportsLinked, 
                                                        'id':id})

@login_required
def EditSample(response,id):

    sampleModel = Sample.objects.get(id=id)

    if not sampleModel.isEnabled:
        return HttpResponseRedirect("/sampletype")
    
    if response.method == "POST":
        print(response.POST)
        print(response.FILES)
        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/sampletype/sample/{id}")
        
        if response.POST.get('save'):

            form = CreateNewSample(response.POST, response.FILES)
            if form.is_valid():

                sampleInternalId = form.cleaned_data['internalId']
                sampleQuantity = form.cleaned_data['quantity']
                sampleLocationId = form.cleaned_data['locationId']
                sampleType = form.cleaned_data['sampleType']
                sampleFile= form.cleaned_data['files']

                sampleModel.internalId = sampleInternalId
                sampleModel.hasInternalId = (sampleModel.internalId != "")
                sampleModel.quantity = sampleQuantity
                sampleModel.locationId = sampleLocationId
                sampleModel.sampleType = sampleType
                sampleModel.file = sampleFile
                sampleModel.save()

                SampleVersioning(action = "EDITED", sampleModel = sampleModel, user=response.user)

                return HttpResponseRedirect(f"/sampletype/sample/{id}")

    else:
        form = CreateNewSample(initial={'internalId' : sampleModel.internalId,
                                    'quantity' : sampleModel.quantity,
                                    'locationId' : sampleModel.locationId,
                                    'sampleType' : sampleModel.sampleType,
                                    'files' : sampleModel.file})
        
        return render(response, 'editSample.html', {'form':form})
   
def SampleVersioning(action = None, sampleModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    sampleVersionModel = Sample_Versions(sample = sampleModel,
                                        internalId = sampleModel.internalId,
                                        quantity= sampleModel.quantity,
                                        locationId= sampleModel.locationId,
                                        sampleType= sampleModel.sampleType,
                                        hasInternalId = sampleModel.hasInternalId,

                                        lastAction = action,
                                        lastEditedUserSignature = esignature)
    sampleVersionModel.save()


def DeleteSampleHTMX(response, id):
    sampleModel = Sample.objects.get(id=id)
    sampleModel.isEnabled=False
    sampleModel.save()
    SampleVersioning(action = "DELETED", sampleModel = sampleModel, user=response.user)
    return HttpResponse('')

def CreateSampleHTMX(response):
    if response.method == "POST":

        form = CreateNewSample(response.POST, response.FILES)

        if form.is_valid():

            sampleInternalId = form.cleaned_data['internalId']
            sampleQuantity = form.cleaned_data['quantity']
            sampleLocationId = form.cleaned_data['locationId']
            sampleType = form.cleaned_data['sampleType']
            sampleFile= form.cleaned_data['files']

            sampleModel = Sample(internalId = sampleInternalId,
                                quantity= sampleQuantity,
                                hasInternalId = sampleInternalId != "",
                                locationId = sampleLocationId,
                                sampleType = sampleType,
                                file = sampleFile)
            sampleModel.save()
            SampleVersioning(action = "CREATED", sampleModel = sampleModel, user=response.user)

            return render(response, 'sample_details.html', {'sample':sampleModel})
