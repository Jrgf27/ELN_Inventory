from django.db import models
from django.contrib.auth.models import User, Group
from ckeditor.fields import RichTextField

# Create your models here.

class RiskAssessment(models.Model):
    title = models.CharField(max_length=200)
    documentBody = RichTextField(blank=True,null=True)
    isEnabled = models.BooleanField(default=True)
    owner = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    ownerSignature = models.CharField(max_length=200, default="")
    creationDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

class RiskAssessment_Versions(models.Model):

    riskAssessment = models.ForeignKey(RiskAssessment, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True)
    documentBody = RichTextField(blank=True,null=True)
    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class RiskAssessmentAttachments(models.Model):

    riskAssessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, null=True)
    file=models.FileField(upload_to='documents/%Y/%m/%d',blank=True,null=True)

    def __str__(self) -> str:
        return self.file.name.split("/")[-1]
    
class RiskAssessmentAttachments_Versions(models.Model):

    reportAttachmentsId = models.ForeignKey(RiskAssessmentAttachments, on_delete=models.SET_NULL, null=True)
    riskAssessment = models.ForeignKey(RiskAssessment, on_delete=models.SET_NULL, null=True)
    fileName=models.CharField(max_length=200)
    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.fileName
    