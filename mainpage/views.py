from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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

        item_stockList.append((i,stock_quantity))

    projects = Projects.objects.all()
    projectform = CreateNewProject()

    paginator = Paginator(item_stockList,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(response, 'home.html', {  'categoryList': categoryListObjects,
                                            'page_obj' : page_obj,
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
        item_stockList.append((i,stock_quantity))

    paginator = Paginator(item_stockList,20)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)

    projects = Projects.objects.all()
    projectform = CreateNewProject()
    return render(response, 'lowStock.html', {'categoryList': categoryListObjects,
                                              'page_obj' : page_obj,
                                            'projects' : projects,
                                            'projectform' : projectform})