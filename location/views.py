from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import *
from .forms import CreateNewLocation

from stock.models import Stock
from stock.forms import RemoveStockQuantity, AddStockQuantity, CreateNewItemStock
from projects.models import Projects
from projects.forms import CreateNewProject


@login_required
def LocationList(response):
    locationlistobjects = Locations.objects.filter(parentLocation=None).filter(isEnabled=True)

    paginator = Paginator(locationlistobjects,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    locationform=CreateNewLocation()
    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()
    return render(response, 'locationList.html', {'page_obj':page_obj,
                                                  'locationform':locationform,
                                                  'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def SpecificLocation(response, id):

    locationObject = Locations.objects.get(id=id)

    if not locationObject.isEnabled:
        return redirect('LocationList')

    if response.method == "POST":
        if response.POST.get('delete_location'):
            locationObject.isEnabled=False
            locationObject.save()
            LocationVersioning(action = "DELETED", locationModel = locationObject, user=response.user)
            return redirect('LocationList')
        
        if response.POST.get('edit_location'):
            return redirect('editLocation', id=id)
        
    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        if response.GET.get("page")==None:
            page_number_location = None
            page_number_stock = None
        else:
            page_numbers=response.GET.get("page").split(",")
            page_number_stock = page_numbers[0]
            page_number_location = page_numbers[1]

        locationlistobjects = Locations.objects.filter(parentLocation = locationObject).filter(isEnabled=True)

        paginator_location = Paginator(locationlistobjects,20)
        page_obj_location = paginator_location.get_page(page_number_location)

        stockListObjects = Stock.objects.filter(isEnabled=True).filter(locationId=locationObject)

        paginator_stock = Paginator(stockListObjects,20)
        page_obj_stock = paginator_stock.get_page(page_number_stock)

        stockform = CreateNewItemStock(initial={'locationId' : locationObject}, parentItem = 0)
        locationform=CreateNewLocation(initial={'parentID' : locationObject})
        removeQuantityStockform = RemoveStockQuantity()
        addQuantityStockform = AddStockQuantity()
        return render(response, 'specificLocation.html', {'page_obj_location':page_obj_location,
                                                          'page_obj_stock':page_obj_stock, 
                                                          'locationObject':locationObject,
                                                          'stockform':stockform,
                                                          'removeQuantityStockform':removeQuantityStockform,
                                                          'addQuantityStockform':addQuantityStockform,
                                                          'locationform':locationform,
                                                          'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def CreateLocation(response):

    if response.method == "POST":

        form = CreateNewLocation(response.POST)

        if form.is_valid():

            locationName = form.cleaned_data['name']
            locationDescription = form.cleaned_data['description']
            parentLocation = form.cleaned_data['parentID']

            if parentLocation == None:
                locationModel = Locations(name=locationName, 
                                        description = locationDescription)
            else:
                locationModel = Locations(name=locationName, 
                                        description = locationDescription,
                                        parentLocation = parentLocation)
            
            locationModel.save()
            LocationVersioning(action = "CREATED", locationModel = locationModel, user=response.user)
            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/location/{locationModel.id}")
            return HttpResponseRedirect("/location/create")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewLocation()
        return render(response, 'createLocation.html', {'form':form,
                                                        'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def EditLocation(response,id):

    locationModel = Locations.objects.get(id=id)

    if not locationModel.isEnabled:
        return redirect('LocationList')
    
    if response.method == "POST":

        if response.POST.get('exit'):
            return redirect('specificLocation', id=id)
        
        if response.POST.get('save'):

            form = CreateNewLocation(response.POST)
            if form.is_valid():
                
                locationModel.name = form.cleaned_data['name']
                locationModel.description = form.cleaned_data['description']
                
                currentLocationQuery = form.cleaned_data['parentID']
                while currentLocationQuery:
                    if currentLocationQuery == locationModel:
                        locationModel.save()
                        LocationVersioning(action = "EDITED", locationModel = locationModel, user=response.user)
                        print("Recursivness Detected")
                        return redirect('specificLocation', id=id)
                    currentLocationQuery = currentLocationQuery.parentLocation

                locationModel.parentLocation = form.cleaned_data['parentID']
                print("Not Recursive")

                locationModel.save()
                LocationVersioning(action = "EDITED", locationModel = locationModel, user=response.user)

                return redirect('specificLocation', id=id)

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewLocation(initial={'name' : locationModel.name,
                                        'description' : locationModel.description,
                                        'parentID' : locationModel.parentLocation})
        
        return render(response, 'editLocation.html', {'form':form,
                                                      'projects' : projects,
                                                    'projectform' : projectform})

def LocationVersioning(action = None, locationModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    
    locationVersionModel = Locations_Versions(
        location = locationModel,
        name = locationModel.name,
        description = locationModel.description,
        parentLocation = locationModel.parentLocation,

        lastAction = action,
        lastEditedUserSignature = esignature)
    
    locationVersionModel.save()

def CreateLocationHTMX(response):

    if response.method == "POST":

        form = CreateNewLocation(response.POST)

        if form.is_valid():

            locationName = form.cleaned_data['name']
            locationDescription = form.cleaned_data['description']
            parentLocation = form.cleaned_data['parentID']

            if parentLocation == None:
                locationModel = Locations(name=locationName, 
                                        description = locationDescription)
            
            else:
                locationModel = Locations(name=locationName, 
                                        description = locationDescription,
                                        parentLocation = parentLocation)
            
            locationModel.save()
            LocationVersioning(action = "CREATED", locationModel = locationModel, user=response.user)
            return render(response, 'location_details.html', {'location':locationModel})

def DeleteLocationHTMX(response, id):
    locationModel = Locations.objects.get(id=id)
    locationModel.isEnabled=False
    locationModel.save()
    LocationVersioning(action = "DELETED", locationModel = locationModel, user=response.user)
    return HttpResponse('')