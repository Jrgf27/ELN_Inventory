from django.shortcuts import render, redirect
from django.http.response import HttpResponse

from django.core.paginator import Paginator


from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Items
from stock.models import Stock
from stock.forms import RemoveStockQuantity, CreateNewItemStock, AddStockQuantity
from supplier.models import SuppliersItems
from supplier.forms import CreateNewItemSupplier

from .forms import CreateNewItem
from .utils import item_versioning

class ItemList(LoginRequiredMixin, TemplateView):
    def get(self, response):
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


        paginator = Paginator(item_stockList,20)
        page_number = response.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(response, 'item/itemList.html', { 'page_obj':page_obj,
                                                        'form': form})

class SpecificItem(LoginRequiredMixin, TemplateView):
    def get(self, response, id):

        itemInfo = Items.objects.get(id=id)

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

        context = { 'itemInfo': itemInfo,
                    'page_obj_stock': page_obj_stock,
                    'page_obj_supplierItem': page_obj_supplierItem,
                    'id': id,
                    'supplierItemform': supplierItemform,
                    'stockform': stockform,
                    'removeQuantityStockform': removeQuantityStockform,
                    'addQuantityStockform': addQuantityStockform}

        return render(response, 'item/specificItem.html',context )

    def post(self, response, id):
        itemInfo = Items.objects.get(id=id)
        item_versioning(action="DELETED", itemModel=itemInfo,
                        user=response.user)
        itemInfo.isEnabled = False
        itemInfo.save()
        return redirect("ItemList")

class EditItem(LoginRequiredMixin, TemplateView):
    def get(self, response, id):
        itemObject = Items.objects.get(id=id)
        form = CreateNewItem(initial={'name': itemObject.name,
                                      'description': itemObject.description,
                                      'minimumStock': itemObject.minimumStock,
                                      'itemCategoryId': itemObject.itemCategoryId.id})
        

        return render(response, 'item/editItem.html', {'form': form})

    def post(self, response, id):
        if response.POST.get('exit'):
            return redirect("specificItem", id)

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
                item_versioning(action="EDITED",
                               itemModel=itemModel, user=response.user)

                return redirect("ItemList")

        
class ItemHTMX(LoginRequiredMixin, TemplateView):
    def post(self, response):
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
            item_versioning(action="CREATED",
                           itemModel=itemModel, user=response.user)
            stockQuantity = 0
            return render(response, 'item/partials/item_details.html', {'item': itemModel,
                                                          'stockQuantity': stockQuantity})

    def delete(self, response, id):
        itemModel = Items.objects.get(id=id)
        itemModel.isEnabled = False
        itemModel.save()
        item_versioning(action="DELETED", itemModel=itemModel, user=response.user)
        return HttpResponse('')
