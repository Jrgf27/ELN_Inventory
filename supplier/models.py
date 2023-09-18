from django.db import models
from item.models import Items
from django.contrib.auth.models import User
# Create your models here.

class Suppliers(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    website = models.URLField()
    phoneNumber = models.CharField(max_length=20)
    emailAddress = models.CharField(max_length=200)
    contactName = models.CharField(max_length=200)
    isEnabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
class Suppliers_Versions(models.Model):
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    website = models.URLField()
    phoneNumber = models.CharField(max_length=20)
    emailAddress = models.CharField(max_length=200)
    contactName = models.CharField(max_length=200)

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    

class SuppliersItems(models.Model):

    website = models.URLField()
    supplierProductCode = models.CharField(max_length=200)
    supplierId = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, null=True)
    itemId = models.ForeignKey(Items, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    isEnabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        try:
            return self.itemId.name + " from " + self.supplierId.name
        except:
            pass
        return self.supplierProductCode
    
class SuppliersItems_Versions(models.Model):
    supplierItem = models.ForeignKey(SuppliersItems, on_delete=models.SET_NULL, null=True)
    website = models.URLField()
    supplierProductCode = models.CharField(max_length=200)
    supplierId = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, null=True)
    itemId = models.ForeignKey(Items, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        try:
            return self.itemId.name + " from " + self.supplierId.name
        except:
            pass
        return self.supplierProductCode