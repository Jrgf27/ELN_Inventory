from django.db import models
from supplier.models import SuppliersItems
from location.models import Locations
from django.contrib.auth.models import User

# Create your models here.

class Stock(models.Model):
    batchCode = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    hasBatchCode = models.BooleanField()
    locationId = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    itemId = models.ForeignKey(SuppliersItems, on_delete=models.CASCADE, null=True)
    isEnabled=models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.itemId.itemId.name + " - " + self.batchCode
    
class Stock_Versions(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    batchCode = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    hasBatchCode = models.BooleanField()
    locationId = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    itemId = models.ForeignKey(SuppliersItems, on_delete=models.CASCADE, null=True)

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.itemId.itemId.name + " - " + self.batchCode