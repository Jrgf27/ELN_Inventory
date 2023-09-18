from django import forms
from .models import Suppliers
from item.models import Items

class CreateNewSupplier(forms.Form):
    name = forms.CharField(label = 'Name', max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), required=False)
    website = forms.URLField(label= 'Supplier Website', required=True)
    phoneNumber = forms.CharField(label = 'Phone Number', max_length=200, required=False)
    emailAddress = forms.CharField(label = 'Email Address', max_length=200, required=False)
    contactName = forms.CharField(label = 'Contact Name', max_length=200, required=False)

class CreateNewSupplierItem(forms.Form):

    def __init__(self, *args, **kwargs):
        parentSupplier = kwargs.pop('parentSupplier')
        super(CreateNewSupplierItem, self).__init__(*args, **kwargs)

        if parentSupplier == 0:
            self.fields['supplierId'] = forms.ModelChoiceField(queryset=Suppliers.objects.filter(isEnabled=True), 
                                                            required=True, 
                                                            label='Supplier')
        else:
            self.fields['supplierId'] = forms.ModelChoiceField(queryset=Suppliers.objects.filter(id = parentSupplier).filter(isEnabled=True), 
                                                            required=True, 
                                                            label='Supplier')
        self.fields['website'] = forms.URLField(label= 'Supplier Website', required=False)
        self.fields['supplierProductCode'] =forms.CharField(label = 'Supplier Product Code', max_length=200, required=True)
        self.fields['price'] = forms.DecimalField(label='Item Price', max_digits=10, decimal_places=2)

        self.fields['itemId'] = forms.ModelChoiceField(queryset=Items.objects.filter(isEnabled=True), 
                                                        required=True, 
                                                        label='Item')

class CreateNewItemSupplier(forms.Form):

    def __init__(self, *args, **kwargs):
        parentItem = kwargs.pop('parentItem')
        super(CreateNewItemSupplier, self).__init__(*args, **kwargs)

        self.fields['supplierId'] = forms.ModelChoiceField(queryset=Suppliers.objects.filter(isEnabled=True), 
                                                            required=True, 
                                                            label='Supplier')
        self.fields['website'] = forms.URLField(label= 'Supplier Website', required=False)
        self.fields['supplierProductCode'] =forms.CharField(label = 'Supplier Product Code', max_length=200, required=True)
        self.fields['price'] = forms.DecimalField(label='Item Price', max_digits=10, decimal_places=2)

        self.fields['itemId'] = forms.ModelChoiceField(queryset=Items.objects.filter(id = parentItem).filter(isEnabled=True), 
                                                        required=True, 
                                                        label='Item')
    

    