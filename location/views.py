from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import CreateNewLocation

from stock.models import Stock
from stock.forms import RemoveStockQuantity, AddStockQuantity, CreateNewItemStock


@login_required
def LocationList(response):
    locationlistobjects = Locations.objects.filter(parentLocation=None).filter(isEnabled=True)
    locationform=CreateNewLocation()
    return render(response, 'locationList.html', {'locationlist':locationlistobjects,
                                                  'locationform':locationform})

@login_required
def SpecificLocation(response, id):

    locationObject = Locations.objects.get(id=id)

    if not locationObject.isEnabled:
        return HttpResponseRedirect("/location")

    if response.method == "POST":
        if response.POST.get('delete_location'):
            locationObject.isEnabled=False
            locationObject.save()
            LocationVersioning(action = "DELETED", locationModel = locationObject, user=response.user)
            return HttpResponseRedirect("/location")
        
        if response.POST.get('edit_location'):
            return HttpResponseRedirect(f"/location/edit/{id}")
        
    else:
        locationlistobjects = Locations.objects.filter(parentLocation = locationObject).filter(isEnabled=True)
        stockListObjects = Stock.objects.filter(isEnabled=True).filter(locationId=locationObject)
        stockform = CreateNewItemStock(initial={'locationId' : locationObject}, parentItem = 0)
        locationform=CreateNewLocation(initial={'parentID' : locationObject})
        removeQuantityStockform = RemoveStockQuantity()
        addQuantityStockform = AddStockQuantity()
        return render(response, 'specificLocation.html', {'locationlist':locationlistobjects,
                                                          'stockList':stockListObjects, 
                                                          'locationObject':locationObject,
                                                          'stockform':stockform,
                                                          'removeQuantityStockform':removeQuantityStockform,
                                                          'addQuantityStockform':addQuantityStockform,
                                                          'locationform':locationform})

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
        form = CreateNewLocation()
        return render(response, 'createLocation.html', {'form':form})

@login_required
def EditLocation(response,id):

    locationModel = Locations.objects.get(id=id)

    if not locationModel.isEnabled:
        return HttpResponseRedirect("/location")
    
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/location/{id}")
        
        if response.POST.get('save'):

            form = CreateNewLocation(response.POST)
            if form.is_valid():
                
                locationModel.name = form.cleaned_data['name']
                locationModel.description = form.cleaned_data['description']
                locationModel.parentLocation = form.cleaned_data['parentID']

                locationModel.save()
                LocationVersioning(action = "EDITED", locationModel = locationModel, user=response.user)

                return HttpResponseRedirect("/location")

    else:

        form = CreateNewLocation(initial={'name' : locationModel.name,
                                        'description' : locationModel.description,
                                        'parentID' : locationModel.parentLocation})
        
        return render(response, 'editLocation.html', {'form':form})

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
                locationModel.save()
                LocationVersioning(action = "CREATED", locationModel = locationModel, user=response.user)
                return render(response, 'location_details.html', {'location':locationModel})
            
            else:
                locationModel = Locations(name=locationName, 
                                        description = locationDescription,
                                        parentLocation = parentLocation)
                locationModel.save()
                LocationVersioning(action = "CREATED", locationModel = locationModel, user=response.user)
                return HttpResponse('')

def DeleteLocationHTMX(response, id):
    locationModel = Locations.objects.get(id=id)
    locationModel.isEnabled=False
    locationModel.save()
    LocationVersioning(action = "DELETED", locationModel = locationModel, user=response.user)
    return HttpResponse('')