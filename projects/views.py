from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils import timezone
from django.core.signing import TimestampSigner

from .models import *
from .forms import CreateNewProject


def CreateProjectHTMX(response):

    if response.method == "POST":

        form = CreateNewProject(response.POST)

        if form.is_valid():

            categoryName = form.cleaned_data['name']

            projectModel = Projects(name = categoryName)
            projectModel.save()

            return render(response, 'project_details.html', {'project':projectModel})

def DeleteProjectHTMX(response, id):
    projectModel = Projects.objects.get(id=id)
    projectModel.isEnabled=False
    projectModel.save()
    return HttpResponse('')