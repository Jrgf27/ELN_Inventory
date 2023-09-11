from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from stock.models import Stock
from item.models import Items
from itemcategory.models import ItemCategory

from projects.models import Projects
from projects.forms import CreateNewProject

# Create your views here.
@login_required
def homePage(response):

    itemListObjects = Items.objects.filter(isEnabled=True)
    stockListObjects = Stock.objects.filter(isEnabled=True)
    categoryListObjects = ItemCategory.objects.filter(isEnabled=True)

    item_stockList=[]
    for i in itemListObjects:
        stock_quantity=0
        for j in stockListObjects:
            if j.itemId.itemId == None:
                continue
            if j.itemId.itemId.id == i.id:
                stock_quantity += j.quantity

        item_stockList.append(stock_quantity)

    projects = Projects.objects.all()
    projectform = CreateNewProject()

    return render(response, 'home.html', {  'categoryList': categoryListObjects,
                                            'item_stockList' : zip(itemListObjects,
                                                                 item_stockList),
                                            'projects' : projects,
                                            'projectform' : projectform})
@login_required
def LowStock(response):

    itemListObjects = Items.objects.filter(isEnabled=True)
    stockListObjects = Stock.objects.filter(isEnabled=True)
    categoryListObjects = ItemCategory.objects.filter(isEnabled=True)

    item_stockList=[]
    for i in itemListObjects:
        stock_quantity=0
        for j in stockListObjects:
            if j.itemId.itemId == None:
                continue
            if j.itemId.itemId.id == i.id:
                stock_quantity += j.quantity
        item_stockList.append(stock_quantity)

    projects = Projects.objects.all()
    projectform = CreateNewProject()
    return render(response, 'lowStock.html', {'categoryList': categoryListObjects,
                                              'item_stockList' : zip(itemListObjects,
                                                                     item_stockList),
                                            'projects' : projects,
                                            'projectform' : projectform})