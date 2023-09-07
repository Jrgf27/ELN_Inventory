from django import forms
from ckeditor.widgets import CKEditorWidget

from itemcategory.models import ItemCategory
from location.models import Locations
from supplier.models import SuppliersItems, Suppliers
from .models import Items


class CreateNewItem(forms.Form):
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), required=False)
    minimumStock= forms.IntegerField(label='Minimum Stock', required=True)
    
    itemCategoryId=forms.ModelChoiceField(queryset=ItemCategory.objects.filter(isEnabled=True), 
                                      required=True, 
                                      label='Category')



