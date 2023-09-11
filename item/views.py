from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import *
from stock.models import Stock
from stock.forms import RemoveStockQuantity, CreateNewItemStock, AddStockQuantity
from supplier.models import SuppliersItems
from supplier.forms import CreateNewItemSupplier
from projects.models import Projects
from projects.forms import CreateNewProject


from .forms import *

@login_required
def ItemList(response):

    itemListObjects = Items.objects.filter(isEnabled=True).order_by('name')
    stockListObjects = Stock.objects.filter(isEnabled=True)

    form = CreateNewItem()
    item_stockList = []
    for i in itemListObjects:
        stock_quantity = 0
        for j in stockListObjects:
            if j.itemId.itemId == None:
                continue
            if j.itemId.itemId.id == i.id:
                stock_quantity += j.quantity
        item_stockList.append((i,stock_quantity))

    projects=Projects.objects.filter(isEnabled=True)
    projectform = CreateNewProject()

    paginator = Paginator(item_stockList,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(response, 'itemList.html', {'page_obj':page_obj,
                                                'form': form,
                                                'projects' : projects,
                                                'projectform' : projectform})

@login_required
def SpecificItem(response, id):

    itemInfo = Items.objects.get(id=id)

    if not itemInfo.isEnabled:
        return HttpResponseRedirect("/item")

    if response.method == "POST":

        if response.POST.get('delete_item'):

            ItemVersioning(action="DELETED", itemModel=itemInfo,
                           user=response.user)
            itemInfo.isEnabled = False
            itemInfo.save()

            return HttpResponseRedirect("/item")

        if response.POST.get('edit_item'):
            return HttpResponseRedirect(f"/item/edit/{id}")

    else:
        if response.GET.get("page")==None:
            page_number_supplierItem = None
            page_number_stock = None
        else:
            page_numbers=response.GET.get("page").split(",")
            page_number_stock = page_numbers[0]
            page_number_supplierItem = page_numbers[1]

        supplierItemObjects = SuppliersItems.objects.filter(itemId=id)
        paginator_supplierItem = Paginator(supplierItemObjects,1)
        page_obj_supplierItem = paginator_supplierItem.get_page(page_number_supplierItem)

        stockListObjects = []
        for item in supplierItemObjects:
            stockList = Stock.objects.filter(itemId=item).filter(isEnabled=True)
            for stock in stockList:
                stockListObjects.append(stock)

        paginator_stock = Paginator(stockListObjects,1)
        page_obj_stock = paginator_stock.get_page(page_number_stock)

        stockform = CreateNewItemStock(initial={'itemId': id}, parentItem=id)
        supplierItemform = CreateNewItemSupplier(initial={'itemId': id}, parentItem=id)
        removeQuantityStockform = RemoveStockQuantity()
        addQuantityStockform = AddStockQuantity()

        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        return render(response, 'specificItem.html', {'itemInfo': itemInfo,
                                                      'page_obj_stock': page_obj_stock,
                                                      'page_obj_supplierItem': page_obj_supplierItem,
                                                      'id': id,
                                                      'supplierItemform': supplierItemform,
                                                      'stockform': stockform,
                                                      'removeQuantityStockform': removeQuantityStockform,
                                                      'addQuantityStockform': addQuantityStockform,
                                                      'projects' : projects,
                                                        'projectform' : projectform})

@login_required
def CreateItem(response):

    if response.method == "POST":

        form = CreateNewItem(response.POST)

        if form.is_valid():

            itemName = form.cleaned_data['name']
            itemDescription = form.cleaned_data['description']
            itemMinimumStock = form.cleaned_data['minimumStock']
            itemCategoryId = form.cleaned_data['itemCategoryId']

            itemModel = Items(name=itemName,
                              description=itemDescription,
                              minimumStock=itemMinimumStock,
                              isEnabled=True,
                              itemCategoryId=itemCategoryId)
            itemModel.save()
            ItemVersioning(action="CREATED",
                           itemModel=itemModel, user=response.user)

            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/item/{itemModel.id}")
            return HttpResponseRedirect("/item/create")

    else:
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewItem()
        return render(response, 'createItem.html', {'form': form,
                                                    'projects' : projects,
                                                    'projectform' : projectform})

@login_required
def EditItem(response, id):

    itemObject = Items.objects.get(id=id)
    if not itemObject.isEnabled:
        return HttpResponseRedirect("/item")

    if response.method == "POST":

        if response.POST.get('exit'):
            return HttpResponseRedirect(f"/item/{id}")

        if response.POST.get('save'):

            form = CreateNewItem(response.POST)
            if form.is_valid():

                itemName = form.cleaned_data['name']
                itemDescription = form.cleaned_data['description']
                itemMinimumStock = form.cleaned_data['minimumStock']
                itemCategoryId = form.cleaned_data['itemCategoryId']

                itemModel = Items.objects.get(id=id)
                itemModel.name = itemName
                itemModel.description = itemDescription
                itemModel.minimumStock = itemMinimumStock
                itemModel.itemCategoryId = itemCategoryId

                itemModel.save()
                ItemVersioning(action="EDITED",
                               itemModel=itemModel, user=response.user)

                return HttpResponseRedirect("/item")

    else:
        itemObject = Items.objects.get(id=id)
        form = CreateNewItem(initial={'name': itemObject.name,
                                      'description': itemObject.description,
                                      'minimumStock': itemObject.minimumStock,
                                      'itemCategoryId': itemObject.itemCategoryId.id})
        
        projects=Projects.objects.filter(isEnabled=True)
        projectform = CreateNewProject()

        return render(response, 'editItem.html', {'form': form,
                                                  'projects' : projects,
                                                    'projectform' : projectform})

def ItemVersioning(action=None, itemModel=None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID": user.id,
        "Username": user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    itemVersionModel = Items_Versions(item=itemModel,
                                      name=itemModel.name,
                                      description=itemModel.description,
                                      minimumStock=itemModel.minimumStock,
                                      itemCategoryId=itemModel.itemCategoryId,
                                      lastAction=action,
                                      lastEditedUserSignature=esignature)
    itemVersionModel.save()

def CreateItemHTMX(response):

    if response.method == "POST":

        form = CreateNewItem(response.POST)

        if form.is_valid():

            itemName = form.cleaned_data['name']
            itemDescription = form.cleaned_data['description']
            itemMinimumStock = form.cleaned_data['minimumStock']
            itemCategoryId = form.cleaned_data['itemCategoryId']

            itemModel = Items(name=itemName,
                              description=itemDescription,
                              minimumStock=itemMinimumStock,
                              isEnabled=True,
                              itemCategoryId=itemCategoryId)
            itemModel.save()
            ItemVersioning(action="CREATED",
                           itemModel=itemModel, user=response.user)
            stockQuantity = 0
            return render(response, 'item_details.html', {'item': itemModel,
                                                          'stockQuantity': stockQuantity})

def DeleteItemHTMX(response, id):
    itemModel = Items.objects.get(id=id)
    itemModel.isEnabled = False
    itemModel.save()
    ItemVersioning(action="DELETED", itemModel=itemModel, user=response.user)
    return HttpResponse('')
