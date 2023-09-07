from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner
from django.contrib.auth.decorators import login_required


from .models import *
from .forms import CreateNewCategory

# Create your views here.
@login_required
def CategoryList(response):

    categoryListObjects = ItemCategory.objects.filter(isEnabled=True)
    categoryForm=CreateNewCategory()
    return render(response, 'categoryList.html', {'categoryList':categoryListObjects,
                                                  'form':categoryForm})

@login_required
def SpecificCategory(response, id):
    categoryInfo = ItemCategory.objects.get(id=id)

    if not categoryInfo.isEnabled:
        return HttpResponseRedirect("/category")
    
    if response.method == "POST":
        if response.POST.get('delete_category'):

            ItemCategoryVersioning(action = "DELETED", itemCategoryModel = categoryInfo, user=response.user)
            categoryInfo.isEnabled=False
            categoryInfo.save()
            return HttpResponseRedirect("/category")
        
        if response.POST.get('edit_category'):
            return HttpResponseRedirect(f"/category/edit/{id}")
        
    else:
        return render(response, 'specificCategory.html', {'categoryInfo':categoryInfo, 
                                                      'id':id})

@login_required
def CreateCategory(response):

    if response.method == "POST":

        form = CreateNewCategory(response.POST)

        if form.is_valid():

            categoryName = form.cleaned_data['name']
            categoryDescription = form.cleaned_data['description']

            categoryModel = ItemCategory(name = categoryName,
                                      description= categoryDescription)
            categoryModel.save()
            ItemCategoryVersioning(action = "CREATED", itemCategoryModel = categoryModel, user=response.user)

            if response.POST.get('save_exit'):
                return HttpResponseRedirect(f"/category/{categoryModel.id}")
            return HttpResponseRedirect("/category/create")

    else:
        form = CreateNewCategory()


        return render(response, 'createCategory.html', {'form':form})

@login_required
def EditCategory(response,id):

    categoryModel = ItemCategory.objects.get(id=id)

    if not categoryModel.isEnabled:
        return HttpResponseRedirect("/category")
    
    if response.method == "POST":

        if response.POST.get('exit'):
                return HttpResponseRedirect(f"/category/{id}")
        
        if response.POST.get('save'):

            form = CreateNewCategory(response.POST)
            if form.is_valid():

                categoryName = form.cleaned_data['name']
                categoryDescription = form.cleaned_data['description']

                categoryModel.name = categoryName
                categoryModel.description = categoryDescription

                categoryModel.save()
                ItemCategoryVersioning(action = "EDITED", itemCategoryModel = categoryModel, user=response.user)

                return HttpResponseRedirect("/category")

    else:
        form = CreateNewCategory(initial={  'name' : categoryModel.name,
                                            'description' : categoryModel.description})
        
        return render(response, 'editCategory.html', {'form':form})

def ItemCategoryVersioning(action = None, itemCategoryModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    itemCategoryVersionModel = ItemCategory_Versions(itemCategory = itemCategoryModel,
                                        name = itemCategoryModel.name,
                                        description= itemCategoryModel.description,
                                        lastAction = action,
                                        lastEditedUserSignature = esignature)
    itemCategoryVersionModel.save()

def CreateCategoryHTMX(response):

    if response.method == "POST":

        form = CreateNewCategory(response.POST)

        if form.is_valid():

            categoryName = form.cleaned_data['name']
            categoryDescription = form.cleaned_data['description']

            categoryModel = ItemCategory(name = categoryName,
                                      description= categoryDescription)
            categoryModel.save()
            ItemCategoryVersioning(action = "CREATED", itemCategoryModel = categoryModel, user=response.user)

            return render(response, 'category_details.html', {'category':categoryModel})

def DeleteCategoryHTMX(response, id):
    categoryModel = ItemCategory.objects.get(id=id)
    categoryModel.isEnabled=False
    categoryModel.save()
    ItemCategoryVersioning(action = "DELETED", itemCategoryModel = categoryModel, user=response.user)
    return HttpResponse('')