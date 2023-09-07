from django import forms

class CreateNewProject(forms.Form):
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    