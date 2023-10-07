# pylint: disable=relative-beyond-top-level
# pylint: disable=import-error
"""Views and logic required for Item Category Application"""

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http.response import HttpResponse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from projects.models import Projects
from projects.forms import CreateNewProject

from .models import ItemCategory
from .forms import CreateNewCategory
from .utils import item_category_versioning


# Create your views here.

@method_decorator(login_required, name='dispatch')
class ListCategory(TemplateView):
    """List view class for Item Category;
    returns all enabled categories in the database;
    only has GET method"""
    template_name = 'itemcategory/categoryList.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_list_objects = get_list_or_404(ItemCategory, isEnabled=True)
        category_form=CreateNewCategory()

        paginator = Paginator(category_list_objects,20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        projects=get_list_or_404(Projects, isEnabled=True)
        project_form = CreateNewProject()

        context = {
            'page_obj':page_obj,
            'form':category_form,
            'projects' : projects,
            'projectform' : project_form}
        return context

@method_decorator(login_required, name='dispatch')
class DetailCategory(TemplateView):
    """Detail view of item category, returns 
    category based on provided id in url path;
    has GET and POST methods"""
    template_name = 'itemcategory/specificCategory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_model = get_object_or_404(ItemCategory, id=context['category_id'])

        if not category_model.isEnabled:
            return redirect('CategoryList')

        projects=get_list_or_404(Projects, isEnabled=True)
        projectform = CreateNewProject()
        context = {
            'categoryInfo':category_model,
            'id':context['category_id'],
            'projects' : projects,
            'projectform' : projectform}
        return context

    def post(self, response, category_id):
        """POST method for detail view, either disable model or redirect to edit"""
        category_model = get_object_or_404(ItemCategory, pk=category_id)
        if response.POST.get('delete_category'):
            item_category_versioning(
                action = "DELETED",
                item_category_model = category_model,
                user=response.user
                )

            category_model.isEnabled=False
            category_model.save()
            return redirect('CategoryList')

        if response.POST.get('edit_category'):
            return redirect('editCategory', category_id=category_id)

        return redirect('CategoryList')

@method_decorator(login_required, name='dispatch')
class CreateCategory(TemplateView):
    """Form page for category creation, 
    provides form class and saves the model if inputs are valid"""
    template_name = 'itemcategory/createCategory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects=get_list_or_404(Projects, isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewCategory()
        context = {
            'form':form,
            'projects' : projects,
            'projectform' : projectform
            }
        return context

    def post(self, response):
        """POST method for create category;
        checks if form is valid and if user wants to add more entries"""
        form = CreateNewCategory(response.POST)
        if form.is_valid():
            category_model = ItemCategory(
                name = form.cleaned_data['name'],
                description= form.cleaned_data['description']
                )
            category_model.save()
            item_category_versioning(
                action = "CREATED",
                item_category_model = category_model,
                user=response.user
                )

            if response.POST.get('save_exit'):
                return redirect('specificCategory', category_id=category_model.pk)

        return redirect('createCategory')

@method_decorator(login_required, name='dispatch')
class EditCategory(TemplateView):
    """View logic for category editing url"""
    template_name = 'itemcategory/editCategory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_model = get_object_or_404(ItemCategory, id=context['category_id'])

        if not category_model.isEnabled:
            return redirect('CategoryList')

        projects=get_list_or_404(Projects, isEnabled=True)
        projectform = CreateNewProject()
        form = CreateNewCategory(initial={
            'name' : category_model.name,
            'description' : category_model.description
            })
        context = {
            'form':form,
            'projects' : projects,
            'projectform' : projectform
            }
        return context

    def post(self, response, category_id):
        """POST method for category editing"""
        category_model = get_object_or_404(ItemCategory, pk=category_id)
        if response.POST.get('exit'):
            return redirect('specificCategory', category_id=category_id)

        if response.POST.get('save'):

            form = CreateNewCategory(response.POST)
            if form.is_valid():

                category_model.name = form.cleaned_data['name']
                category_model.description = form.cleaned_data['description']
                category_model.save()
                item_category_versioning(
                    action = "EDITED",
                    item_category_model = category_model,
                    user=response.user)

        return HttpResponseRedirect("/category")

@method_decorator(login_required, name='dispatch')
class CreateCategoryHTMX(TemplateView):
    """Logic for category creation thought HTMX"""

    def post(self, response):
        """POST method for item category creation through HTMX"""
        form = CreateNewCategory(response.POST)
        if form.is_valid():
            category_model = ItemCategory(
                name = form.cleaned_data['name'],
                description= form.cleaned_data['description'])
            category_model.save()
            item_category_versioning(
                action = "CREATED",
                item_category_model = category_model,
                user=response.user)
            context = {'category':category_model}
            return render(response, 'itemcategory/partials/category_details.html', context)
        return HttpResponse('')

@method_decorator(login_required, name='dispatch')
class DeleteCategoryHTMX(TemplateView):
    """Logic for category deletion thought HTMX"""

    def post(self, response, category_id):
        """POST method for item category deletion through HTMX"""
        category_model = get_object_or_404(ItemCategory, pk=category_id)
        category_model.isEnabled=False
        category_model.save()
        item_category_versioning(
            action = "DELETED",
            item_category_model = category_model,
            user=response.user)
        return HttpResponse('')
