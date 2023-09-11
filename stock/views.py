from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.signing import TimestampSigner

from .models import *
from reports.models import Reports
from projects.models import Projects
from projects.forms import CreateNewProject


from .forms import *
@login_required
def stockList(response):
    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()
    stockListObjects = Stock.objects.filter(isEnabled=True)
    stockform = CreateNewItemStock(parentItem = 0)
    removeQuantityStockform = RemoveStockQuantity()
    addQuantityStockform = AddStockQuantity()
    return render(response, 'stockList.html', {'stockList':stockListObjects,
                                                'stockform':stockform,
                                                'removeQuantityStockform':removeQuantityStockform,
                                                'addQuantityStockform':addQuantityStockform,
                                                'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def SpecificStock(response,id):

    stockInfo = Stock.objects.get(id=id)

    if not stockInfo.isEnabled:
        return HttpResponseRedirect("/stock")
    
    if response.method == "POST":
        if response.POST.get('delete_stock'):

            StockVersioning(action = "DELETED", stockModel = stockInfo, user=response.user)
            stockInfo.quantity=0
            stockInfo.isEnabled=False
            stockInfo.save()
            return HttpResponseRedirect("/stock")
        
        if response.POST.get('edit_stock'):
            return HttpResponseRedirect(f"/stock/edit/{id}")
        
    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        linkedReports = Reports.objects.filter(linkedReagents=stockInfo)
        return render(response, 'specificStock.html', {'stockInfo':stockInfo, 
                                                      'id':id,
                                                      'linkedReports':linkedReports,
                                                      'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def CreateStock(response):
    
    if response.method == "POST":

        form = CreateNewItemStock(response.POST, parentItem=0)

        if form.is_valid():

            stockBatchCode = form.cleaned_data['batchCode']
            stockQuantity = form.cleaned_data['quantity']
            stockLocation = form.cleaned_data['locationId']
            stockItemID = form.cleaned_data['itemId']

            stockModel = Stock(batchCode = stockBatchCode,
                            quantity= stockQuantity,
                            hasBatchCode = stockBatchCode != "",
                            locationId= stockLocation,
                            itemId= stockItemID)
            
            stockModel.save()
            StockVersioning(action = "CREATED", stockModel = stockModel, user=response.user)
            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/stock/{stockModel.id}")
            return HttpResponseRedirect("/stock/create")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewItemStock(parentItem=0)
        return render(response, 'createStock.html', {'form':form,
                                                     'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def EditStock(response,id):

    stockModel = Stock.objects.get(id=id)

    if not stockModel.isEnabled:
        return HttpResponseRedirect("/stock")
    
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/stock/{id}")
        
        if response.POST.get('save'):

            form = CreateNewItemStock(response.POST, parentItem=0)
            if form.is_valid():

                stockBatchCode = form.cleaned_data['batchCode']
                stockQuantity = form.cleaned_data['quantity']
                stockLocationId = form.cleaned_data['locationId']
                stockItemId = form.cleaned_data['itemId']

                stockModel.batchCode = stockBatchCode
                stockModel.hasBatchCode = (stockModel.batchCode != "")
                stockModel.quantity = stockQuantity
                stockModel.locationId = stockLocationId
                stockModel.itemId = stockItemId
                stockModel.save()

                StockVersioning(action = "EDITED", stockModel = stockModel, user=response.user)

                return HttpResponseRedirect("/stock")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewItemStock(parentItem=0, initial={'batchCode' : stockModel.batchCode,
                                    'quantity' : stockModel.quantity,
                                    'locationId' : stockModel.locationId,
                                    'itemId' : stockModel.itemId})
        
        return render(response, 'editStock.html', {'form':form,
                                                   'projects' : projects,
                                                    'projectform' : projectform})
    

def CreateStockHTMX(response):
    if response.method == "POST":

        form = CreateNewItemStock(response.POST, parentItem=0)
        if form.is_valid():

            stockBatchCode = form.cleaned_data['batchCode']
            stockQuantity = form.cleaned_data['quantity']
            stockLocationId = form.cleaned_data['locationId']
            stockItemId = form.cleaned_data['itemId']

            stockModel = Stock(batchCode = stockBatchCode,
                        quantity= stockQuantity,
                        hasBatchCode = stockBatchCode != "",
                        locationId= stockLocationId,
                        itemId= stockItemId)
    
            stockModel.save()
            StockVersioning(action = "CREATED", stockModel = stockModel, user=response.user)
            
            removeQuantityStockform = RemoveStockQuantity()
            addQuantityStockform = AddStockQuantity()
            return render(response, 'stock_details.html', {'stock':stockModel,
                                                        'removeQuantityStockform':removeQuantityStockform,
                                                        'addQuantityStockform':addQuantityStockform})

def DeleteStockHTMX(response, id):
    stockModel = Stock.objects.get(id=id)
    stockModel.quantity = 0
    stockModel.isEnabled=False
    stockModel.save()
    StockVersioning(action = "DELETED", stockModel = stockModel, user=response.user)
    return HttpResponse('')


def EditStockHTMX(response, id):

    stockModel = Stock.objects.get(id=id)

    if response.method == "POST":

        if response.POST.get('removequantity'):
            form = RemoveStockQuantity(response.POST)
            if form.is_valid():

                stockQuantity = form.cleaned_data['removequantity']

                stockModel.quantity -= stockQuantity
                if stockModel.quantity < 0:
                    stockModel.quantity=0

                stockModel.save()
                StockVersioning(action = "REMOVED_STOCK", stockModel = stockModel, user=response.user)

            removeQuantityStockform = RemoveStockQuantity()
            addQuantityStockform = AddStockQuantity()
            return render(response, 'stock_details.html', {'stock':stockModel,
                                                        'removeQuantityStockform':removeQuantityStockform,
                                                        'addQuantityStockform':addQuantityStockform})
            
        if response.POST.get('addquantity'):
            form = AddStockQuantity(response.POST)
            if form.is_valid():

                stockQuantity = form.cleaned_data['addquantity']

                stockModel.quantity += stockQuantity

                stockModel.save()
                StockVersioning(action = "ADDED_STOCK", stockModel = stockModel, user=response.user)

            removeQuantityStockform = RemoveStockQuantity()
            addQuantityStockform = AddStockQuantity()
            return render(response, 'stock_details.html', {'stock':stockModel,
                                                        'removeQuantityStockform':removeQuantityStockform,
                                                        'addQuantityStockform':addQuantityStockform})
        
def StockVersioning(action = None, stockModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    stockVersionModel = Stock_Versions(
        stock = stockModel,
        batchCode = stockModel.batchCode,
        quantity = stockModel.quantity,
        hasBatchCode = stockModel.hasBatchCode,
        locationId = stockModel.locationId,
        itemId = stockModel.itemId,

        lastAction = action,
        lastEditedUserSignature = esignature)
    
    stockVersionModel.save()
