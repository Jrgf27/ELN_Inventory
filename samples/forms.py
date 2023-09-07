from django import forms
from location.models import Locations
from .models import SampleType

class CreateNewSampleType(forms.Form):
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), required=False)


class CreateNewSample(forms.Form):

    sampleType=forms.ModelChoiceField(queryset=SampleType.objects.filter(isEnabled=True), 
                                      required=True, 
                                      label='What\' the Sample Type')
    
    internalId = forms.CharField(label = 'Internal Id', max_length=200, required=True)
    quantity= forms.IntegerField(label='Quantity', required=True)

    locationId=forms.ModelChoiceField(queryset=Locations.objects.filter(isEnabled=True), 
                                      required=False, 
                                      label='Sample Location')
    
    files = forms.FileField(label='Select a file', required=False)
    