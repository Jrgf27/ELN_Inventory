# pylint: disable=relative-beyond-top-level
# pylint: disable=import-error
"""Views and logic required for Item Category Application"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView


from .models import ItemCategory
from .forms import CreateNewCategory
from .utils import item_category_versioning


# Create your views here.

class ListCategory(LoginRequiredMixin, TemplateView):
    """List view class for Item Category;
    returns all enabled categories in the database;
    only has GET method"""

    template_name = 'itemcategory/categoryList.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_list_objects = ItemCategory.objects.filter(
            isEnabled=True).order_by('name')
        paginator = Paginator(category_list_objects, 20)

        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        category_form = CreateNewCategory()

        context = {
            'page_obj': page_obj,
            'form': category_form}
        return context


class DetailCategory(LoginRequiredMixin, TemplateView):
    """Detail view of item category, returns 
    category based on provided id in url path;
    has GET and POST methods"""
    template_name = 'itemcategory/specificCategory.html'

    def get(self, request, category_id):
        category_model = get_object_or_404(
            ItemCategory, id=category_id)
        context = {
            'categoryInfo': category_model,
            'id': category_id}
        return render(request, self.template_name, context)

    def post(self, response, category_id):
        """POST method for detail view, either disable model or redirect to edit"""
        category_model = get_object_or_404(ItemCategory, pk=category_id)
        if response.POST.get('delete_category'):
            item_category_versioning(
                action="DELETED",
                item_category_model=category_model,
                user=response.user
            )

            category_model.isEnabled = False
            category_model.save()
            return redirect('CategoryList')

        if response.POST.get('edit_category'):
            return redirect('editCategory', category_id=category_id)

        return redirect('CategoryList')

class EditCategory(LoginRequiredMixin, TemplateView):
    """View logic for category editing url"""
    template_name = 'itemcategory/editCategory.html'

    def get(self, request, category_id):
        context = self.get_context_data(category_id=category_id)
        category_model = get_object_or_404(
            ItemCategory, id=context['category_id'])

        form = CreateNewCategory(initial={
            'name': category_model.name,
            'description': category_model.description
        })
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

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
                    action="EDITED",
                    item_category_model=category_model,
                    user=response.user)

        return redirect("CategoryList")


class CategoryHTMX(LoginRequiredMixin, TemplateView):
    """Logic for category creation thought HTMX"""

    def post(self, response):
        """POST method for item category creation through HTMX"""
        form = CreateNewCategory(response.POST)
        if form.is_valid():
            category_model = ItemCategory(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'])
            category_model.save()
            item_category_versioning(
                action="CREATED",
                item_category_model=category_model,
                user=response.user)
            context = {'category': category_model}
            return render(response, 'itemcategory/partials/category_details.html', context)
        return HttpResponse('')

    def delete(self, response, category_id):
        """POST method for item category deletion through HTMX"""
        category_model = get_object_or_404(ItemCategory, pk=category_id)
        category_model.isEnabled = False
        category_model.save()
        item_category_versioning(
            action="DELETED",
            item_category_model=category_model,
            user=response.user)
        return HttpResponse('')
