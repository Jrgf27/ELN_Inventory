from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ItemCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    isEnabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
class ItemCategory_Versions(models.Model):
    itemCategory = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name