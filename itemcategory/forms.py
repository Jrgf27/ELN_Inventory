"""Form used to create Item Categories"""
from django import forms

class CreateNewCategory(forms.Form):
    """Class with Item Category form"""
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}),
                                  required=False)
    