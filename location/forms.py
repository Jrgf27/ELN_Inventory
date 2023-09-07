from django import forms
from .models import Locations

class CreateNewLocation(forms.Form):
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), required=False)
    parentID = forms.ModelChoiceField(queryset=Locations.objects.filter(isEnabled=True), 
                                      required=False, 
                                      label='Parent Location')
