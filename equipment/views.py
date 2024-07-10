from django.shortcuts import render, redirect
from django.http.response import HttpResponse

from django.core.paginator import Paginator

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Equipment
from .forms import CreateNewEquipment
from .utils import equipment_versioning


class EquipmentList(LoginRequiredMixin, TemplateView):
    template_name = "equipment/equipmentList.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        equipmentListObjects = Equipment.objects.filter(isEnabled=True).order_by('name')

        paginator = Paginator(equipmentListObjects,20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        equipmentForm=CreateNewEquipment()

        context = {
            'page_obj' : page_obj,
            'form':equipmentForm,
        }

        return context
    
class SpecificEquipment(LoginRequiredMixin, TemplateView):

    def get(self, response, id):
        equipmentModel = Equipment.objects.get(id=id)

        context = {
            'equipmentModel':equipmentModel, 
            'id':id
            }

        return render(response, 'equipment/specificEquipment.html', context)
    
    def post(self, response, id):
        equipmentModel = Equipment.objects.get(id=id)
        equipment_versioning(action = "DELETED", equipmentModel = equipmentModel, user=response.user)
        equipmentModel.isEnabled=False
        equipmentModel.save()
        return redirect("EquipmentList")

class EditEquipment(LoginRequiredMixin, TemplateView):

    def get(self, response, id):
        equipmentModel = Equipment.objects.get(id=id)
        form = CreateNewEquipment(initial={  'name' : equipmentModel.name,
                                            'description' : equipmentModel.description,
                                            'origin' : equipmentModel.origin,
                                            'supportContact' : equipmentModel.supportContact,
                                            'responsibleUser' : equipmentModel.responsibleUser,
                                            'relatedSOP' : equipmentModel.relatedSOP,
                                            'relatedRiskAssessment' : equipmentModel.relatedRiskAssessment,})
        
        return render(response, 'equipment/editEquipment.html', {'form':form})

    def post(self, response, id):
        equipmentModel = Equipment.objects.get(id=id)
        if response.POST.get('exit'):
            return redirect( "specificEquipment", id )
        
        if response.POST.get('save'):

            form = CreateNewEquipment(response.POST)
            if form.is_valid():

                equipmentModel.name = form.cleaned_data['name']
                equipmentModel.description = form.cleaned_data['description']
                equipmentModel.origin = form.cleaned_data['origin']
                equipmentModel.supportContact = form.cleaned_data['supportContact']
                equipmentModel.responsibleUser= form.cleaned_data['responsibleUser']

                equipmentModel.save()
                equipment_versioning(action = "EDITED", equipmentModel = equipmentModel, user=response.user)

                return redirect( "specificEquipment", id )    

class EquipmentHTMX(LoginRequiredMixin, TemplateView):
    def post(self, response):
        form = CreateNewEquipment(response.POST)

        if form.is_valid():

            equipmentModel = Equipment(
                name = form.cleaned_data['name'],
                description= form.cleaned_data['description'],
                origin = form.cleaned_data['origin'],
                supportContact = form.cleaned_data['supportContact'],
                responsibleUser= form.cleaned_data['responsibleUser'],
                )
            equipmentModel.save()
            equipment_versioning(action = "CREATED", equipmentModel = equipmentModel, user=response.user)

            return render(response, 'equipment/partials/equipment_details.html', {'equipment':equipmentModel})

    def delete(self, response, id):
        equipmentModel = Equipment.objects.get(id=id)
        equipmentModel.isEnabled=False
        equipmentModel.save()
        equipment_versioning(action = "DELETED", equipmentModel = equipmentModel, user=response.user)
        return HttpResponse('')