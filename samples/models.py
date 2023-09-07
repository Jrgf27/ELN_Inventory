from django.db import models
from django.contrib.auth.models import User

from location.models import Locations

# Create your models here.

class SampleType(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    isEnabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
class SampleType_Versions(models.Model):
    sampleType = models.ForeignKey(SampleType, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    

class Sample(models.Model):
    internalId = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    hasInternalId = models.BooleanField()
    locationId = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    sampleType = models.ForeignKey(SampleType, on_delete=models.CASCADE, null=True)
    file=models.FileField(upload_to=f'samplesDocs/%Y/%m/%d',blank=True,null=True)
    isEnabled=models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.sampleType.name + " - " + self.internalId
    
class Sample_Versions(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True)
    internalId = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    hasInternalId = models.BooleanField()
    locationId = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True)
    sampleType = models.ForeignKey(SampleType, on_delete=models.CASCADE, null=True)

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.sampleType.name + " - " + self.internalId