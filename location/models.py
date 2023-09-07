from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Locations(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    parentLocation=models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='_parentLocation')

    isEnabled=models.BooleanField(default=True)

    def __str__(self) -> str:
        if self.parentLocation==None:
            return self.name
        return self.parentLocation.__str__() + '/' + self.name
    

class Locations_Versions(models.Model):
    location=models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    parentLocation=models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True, related_name='_parentLocation_versions')

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        if self.parentLocation==None:
            return self.name
        return self.parentLocation.__str__() + '/' + self.name