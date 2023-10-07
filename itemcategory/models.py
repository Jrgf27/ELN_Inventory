"""Item category and versioning models"""

from django.db import models

class ItemCategory(models.Model):
    """Item Category model class"""

    name = models.CharField(max_length=200)
    description = models.TextField()
    isEnabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.name)

class ItemCategoryVersions(models.Model):
    """Item Category versioning model"""

    itemCategory = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)
