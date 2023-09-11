from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.signing import TimestampSigner

from .models import *
from .forms import CreateNewSupplier, CreateNewSupplierItem
from projects.models import Projects
from projects.forms import CreateNewProject


@login_required
def SupplierList(response):

    supplierListObjects = Suppliers.objects.filter(isEnabled=True)
    form = CreateNewSupplier()
    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()
    return render(response, 'supplierList.html', {'supplierList':supplierListObjects,
                                                  'form':form,
                                                  'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def SpecificSupplier(response, id):
    supplierInfo = Suppliers.objects.get(id=id)
    supplierItemInfo = SuppliersItems.objects.filter(isEnabled=True).filter(supplierId=supplierInfo)

    supplierItemform = CreateNewSupplierItem(initial={'supplierId' : supplierInfo},
                                        parentSupplier =supplierInfo.id)
    if not supplierInfo.isEnabled:
        return HttpResponseRedirect("/supplier")
    
    if response.method == "POST":
        if response.POST.get('delete_supplier'):
            SupplierVersioning(action = "DELETED", supplierModel = supplierInfo, user=response.user)
            supplierInfo.isEnabled=False
            supplierInfo.save()
            return HttpResponseRedirect("/supplier")
        
        if response.POST.get('edit_supplier'):
            return HttpResponseRedirect(f"/supplier/edit/{id}")
        
        if response.POST.get('save_supplier_Item'):
            form = CreateNewSupplierItem(response.POST, parentSupplier = id)

            if form.is_valid():

                supplierItemWebsite = form.cleaned_data['website']
                supplierItemProductCode = form.cleaned_data['supplierProductCode']
                supplierItemSupplierId = form.cleaned_data['supplierId']
                supplierItemItemId = form.cleaned_data['itemId']

                supplierItemModel = SuppliersItems(website = supplierItemWebsite,
                                        supplierProductCode= supplierItemProductCode,
                                        supplierId= supplierItemSupplierId,
                                        itemId= supplierItemItemId)
                supplierItemModel.save()
                SupplierItemVersioning(action = "CREATED", supplierItemModel = supplierItemModel, user=response.user)
                return HttpResponseRedirect(f"/supplier/{id}")
        
    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        return render(response, 'specificSupplier.html', {  'supplierInfo':supplierInfo,
                                                            'supplierItemList': supplierItemInfo,
                                                            'id':id,
                                                            'supplierItemform':supplierItemform,
                                                            'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def CreateSupplier(response):

    if response.method == "POST":

        form = CreateNewSupplier(response.POST)

        if form.is_valid():

            supplierName = form.cleaned_data['name']
            supplierDescription = form.cleaned_data['description']
            supplierWebsite = form.cleaned_data['website']
            supplierPhoneNumber = form.cleaned_data['phoneNumber']
            supplierEmailAddress = form.cleaned_data['emailAddress']
            supplierContactName = form.cleaned_data['contactName']

            supplierModel = Suppliers(name = supplierName,
                                      description= supplierDescription,
                                      website= supplierWebsite,
                                      phoneNumber= supplierPhoneNumber,
                                      emailAddress= supplierEmailAddress,
                                      contactName=supplierContactName)
            supplierModel.save()
            SupplierVersioning(action = "CREATED", supplierModel = supplierModel, user=response.user)

            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/supplier/{supplierModel.id}")
            return HttpResponseRedirect("/supplier/create")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewSupplier()


        return render(response, 'createSupplier.html', {'form':form,
                                                        'projects' : projects,
                                                        'projectform' : projectform})

@login_required
def EditSupplier(response,id):

    supplierInfo = Suppliers.objects.get(id=id)

    if not supplierInfo.isEnabled:
        return HttpResponseRedirect("/supplier")
    
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/supplier/{id}")
        
        if response.POST.get('save'):

            form = CreateNewSupplier(response.POST)
            if form.is_valid():

                supplierName = form.cleaned_data['name']
                supplierDescription = form.cleaned_data['description']
                supplierWebsite = form.cleaned_data['website']
                supplierPhoneNumber = form.cleaned_data['phoneNumber']
                supplierEmailAddress = form.cleaned_data['emailAddress']
                supplierContactName = form.cleaned_data['contactName']

                supplierInfo.name = supplierName
                supplierInfo.description = supplierDescription
                supplierInfo.website = supplierWebsite
                supplierInfo.phoneNumber = supplierPhoneNumber
                supplierInfo.emailAddress = supplierEmailAddress
                supplierInfo.contactName = supplierContactName

                supplierInfo.save()
                SupplierVersioning(action = "EDITED", supplierModel = supplierInfo, user=response.user)
                return HttpResponseRedirect("/supplier")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewSupplier(initial={'name' : supplierInfo.name,
                                        'description' : supplierInfo.description,
                                        'website' : supplierInfo.website,
                                        'phoneNumber' : supplierInfo.phoneNumber,
                                        'emailAddress' : supplierInfo.emailAddress,
                                        'contactName' : supplierInfo.contactName})
        
        return render(response, 'editSupplier.html', {'form':form,
                                                      'projects' : projects,
                                                    'projectform' : projectform})

def SupplierVersioning(action = None, supplierModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    supplierVersionModel = Suppliers_Versions(supplier = supplierModel,
                                        name = supplierModel.name,
                                        description= supplierModel.description,
                                        website = supplierModel.website,
                                        phoneNumber = supplierModel.phoneNumber,
                                        emailAddress = supplierModel.emailAddress,
                                        contactName = supplierModel.contactName,

                                        lastAction = action,
                                        lastEditedUserSignature = esignature)
    supplierVersionModel.save()

def CreateSupplierHTMX(response):
    if response.method == "POST":

        form = CreateNewSupplier(response.POST)

        if form.is_valid():

            supplierName = form.cleaned_data['name']
            supplierDescription = form.cleaned_data['description']
            supplierWebsite = form.cleaned_data['website']
            supplierPhoneNumber = form.cleaned_data['phoneNumber']
            supplierEmailAddress = form.cleaned_data['emailAddress']
            supplierContactName = form.cleaned_data['contactName']

            supplierModel = Suppliers(name = supplierName,
                                      description= supplierDescription,
                                      website= supplierWebsite,
                                      phoneNumber= supplierPhoneNumber,
                                      emailAddress= supplierEmailAddress,
                                      contactName=supplierContactName)
            supplierModel.save()
            SupplierVersioning(action = "CREATED", supplierModel = supplierModel, user=response.user)
 
            return render(response, 'supplier_details.html', {'supplier':supplierModel})

def DeleteSupplierHTMX(response, id):
    supplierModel = Suppliers.objects.get(id=id)
    supplierModel.isEnabled=False
    supplierModel.save()
    SupplierVersioning(action = "DELETED", supplierModel = supplierModel, user=response.user)
    return HttpResponse('')


@login_required
def SpecificSupplierItem(response, id):
    supplierInfo = SuppliersItems.objects.get(id=id)

    if response.method == "POST":
        if response.POST.get('delete_supplier'):
            SupplierItemVersioning(action = "DELETED", supplierItemModel = supplierInfo, user=response.user)
            supplierInfo.isEnabled=False
            supplierInfo.save()
            return HttpResponseRedirect(f"/supplier/{supplierInfo.supplierId.id}")
        
        if response.POST.get('edit_supplier'):
            return HttpResponseRedirect(f"/supplier/part/edit/{id}")
        
    else:
        return render(response, 'specificSupplier.html', {'supplierInfo':supplierInfo, 
                                                        'id':id})

@login_required
def EditSupplierItem(response,id):
    supplierInfo = SuppliersItems.objects.get(id=id)
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/supplier/{supplierInfo.supplierId.id}")
        
        elif response.POST.get('save'):

            form = CreateNewSupplierItem(response.POST, parentSupplier =0)
            if form.is_valid():

                supplierItemWebsite = form.cleaned_data['website']
                supplierItemProductCode = form.cleaned_data['supplierProductCode']
                supplierItemSupplierId = form.cleaned_data['supplierId']
                supplierItemItemId = form.cleaned_data['itemId']

                supplierItemModel = SuppliersItems.objects.get(id=id)
                supplierItemModel.website = supplierItemWebsite
                supplierItemModel.supplierProductCode = supplierItemProductCode
                supplierItemModel.supplierId = supplierItemSupplierId
                supplierItemModel.itemId = supplierItemItemId

                supplierItemModel.save()
                SupplierItemVersioning(action = "EDITED", supplierItemModel = supplierItemModel, user=response.user)

                return HttpResponseRedirect(f"/supplier/{supplierInfo.supplierId.id}")

    else:
        supplierItemObject = SuppliersItems.objects.get(id=id)
        form = CreateNewSupplierItem(initial={'supplierId' : supplierItemObject.supplierId,
                                        'website' : supplierItemObject.website,
                                        'supplierProductCode' : supplierItemObject.supplierProductCode,
                                        'itemId' : supplierItemObject.itemId},
                                        parentSupplier =0)
        
        return render(response, 'editSupplier.html', {'form':form})
    
def SupplierItemVersioning(action = None, supplierItemModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    supplierItemVersionModel = SuppliersItems_Versions(
        supplierItem = supplierItemModel,
        website = supplierItemModel.website,
        supplierProductCode = supplierItemModel.supplierProductCode,
        supplierId = supplierItemModel.supplierId,
        itemId = supplierItemModel.itemId,

        lastAction = action,
        lastEditedUserSignature = esignature)
    
    supplierItemVersionModel.save()

def CreateSupplierItemHTMX(response):
    if response.method == "POST":
        
        if response.POST.get('supplierProductCode'):

            supplierItemWebsite =  response.POST.get('website')
            supplierItemProductCode =  response.POST.get('supplierProductCode')
            supplierItemSupplierId = Suppliers.objects.get(id=response.POST.get('supplierId'))
            supplierItemItemId = Items.objects.get(id=response.POST.get('itemId'))

            supplierItemModel = SuppliersItems(website = supplierItemWebsite,
                                    supplierProductCode= supplierItemProductCode,
                                    supplierId= supplierItemSupplierId,
                                    itemId= supplierItemItemId)
            supplierItemModel.save()
            SupplierItemVersioning(action = "CREATED", supplierItemModel = supplierItemModel, user=response.user)
 
            return render(response, 'supplieritem_details.html', {'supplierItem':supplierItemModel})

def DeleteSupplierItemHTMX(response, id):
    supplierItemModel = SuppliersItems.objects.get(id=id)
    supplierItemModel.isEnabled=False
    supplierItemModel.save()
    SupplierItemVersioning(action = "DELETED", supplierItemModel = supplierItemModel, user=response.user)
    return HttpResponse('')