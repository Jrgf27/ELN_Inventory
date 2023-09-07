from django import forms
from django.contrib.auth.models import User

from standardoperatingprotocols.models import SOP
from riskassessments.models import RiskAssessment

class CreateNewEquipment(forms.Form):
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), required=False)
    origin = forms.CharField(label = 'Origin/Supplier', max_length=200, required=False)
    supportContact = forms.CharField(label = 'Support Contact', max_length=200, required=False)
    responsibleUser = forms.ModelChoiceField(label = 'Responsible',queryset=User.objects.all(), required=True)