from django.db import models
from supplier.models import SuppliersItems
from location.models import Locations

# Create your models here.

class Stock(models.Model):
    """Class representing the Stock Models"""

    batchCode = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    hasBatchCode = models.BooleanField()
    locationId = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    itemId = models.ForeignKey(SuppliersItems, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    isEnabled=models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.itemId.itemId.name + " - " + self.batchCode

class Stock_Versions(models.Model):
    """Class representing the Stock Versions Models"""

    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    batchCode = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    hasBatchCode = models.BooleanField()
    locationId = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    itemId = models.ForeignKey(SuppliersItems, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)
 
    def __str__(self) -> str:
        return self.itemId.itemId.name + " - " + self.batchCode
