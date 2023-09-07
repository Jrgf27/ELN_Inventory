from django.db import models
from itemcategory.models import ItemCategory
from django.contrib.auth.models import User
# Create your models here.


class Items(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    minimumStock = models.IntegerField()
    isEnabled = models.BooleanField(default=True)
    itemCategoryId = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.name
    
class Items_Versions(models.Model):
    item = models.ForeignKey(Items, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    minimumStock = models.IntegerField()
    itemCategoryId = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name