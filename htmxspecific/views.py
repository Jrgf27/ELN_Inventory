from django.shortcuts import render, redirect
from django.http.response import HttpResponse


def HTMXGetViews(context, form):
    return {
        'form':form,
        'documentId':context['id']
        }

def HTMXGetSpecificViews(response, reportModel,modelId,detailView,linkedModelManager, htmlModelName, htmlDocumentName):
    if response.method == 'GET':
        reportReagentsModel = linkedModelManager.get(id=modelId)
        return render(response, detailView, {
            htmlDocumentName:reportModel,
            htmlModelName:reportReagentsModel})
    else:
        return HttpResponse('')

def HTMXPostViews(reportInfo,linkedModelManager,response,formOption,versioningAction,specificRedirect,formRedirect,modelUsed, versioningFunction):

    if response.POST.get(formOption):
        model = modelUsed.objects.get(id=response.POST.get(formOption))
        linkedModelManager.add(model)
        versioningFunction(action = versioningAction, reportModel = reportInfo, user=response.user)
        return redirect(specificRedirect,reportInfo.id, model.id)
        
    if response.POST.get(formOption) == "":
        return redirect(formRedirect, reportInfo.id)

def HTMXDeleteViews(response, reportModel,linkedModelManager,modelUsed,modelId, versioningAction, versioningFunction):
    if response.method == 'POST':
        linkedModelManager.remove(modelUsed.objects.get(id=modelId))
        versioningFunction(versioningAction, reportModel, response.user)
    return HttpResponse('')
