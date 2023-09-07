from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from location.models import Locations
from supplier.models import SuppliersItems

   
class RemoveStockQuantity(forms.Form):
    def __init__(self, *args, **kwargs):

        super(RemoveStockQuantity, self).__init__(*args, **kwargs)
        self.fields['removequantity']= forms.IntegerField(label="",
                                                          required=True,
                                                          validators=[MinValueValidator(0)])

class AddStockQuantity(forms.Form):
    def __init__(self, *args, **kwargs):

        super(AddStockQuantity, self).__init__(*args, **kwargs)
        self.fields['addquantity']= forms.IntegerField(label="",
                                                       required=True,
                                                       validators=[MinValueValidator(0)])

class CreateNewItemStock(forms.Form):

    def __init__(self, *args, **kwargs):
        parentItem = kwargs.pop('parentItem')
        super(CreateNewItemStock, self).__init__(*args, **kwargs)
        if parentItem == 0:
            self.fields['itemId'] = forms.ModelChoiceField(queryset=SuppliersItems.objects.filter(isEnabled=True), 
                                        required=True, 
                                        label='What\' the Item')
        else:
            self.fields['itemId'] = forms.ModelChoiceField(queryset=SuppliersItems.objects.filter(itemId_id = parentItem).filter(isEnabled=True), 
                                        required=True, 
                                        label='What\' the Item')
        self.fields['batchCode'] = forms.CharField(label = 'Batch/Lot Code', max_length=200, required=True)
        self.fields['quantity'] = forms.IntegerField(label='Quantity', required=True)
        self.fields['locationId'] =forms.ModelChoiceField(queryset=Locations.objects.filter(isEnabled=True), 
                                      required=True, 
                                      label='Stock Location')