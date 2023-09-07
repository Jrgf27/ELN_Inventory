from django.db import models
from django.contrib.auth.models import User, Group
from ckeditor.fields import RichTextField

# Create your models here.

class SOP(models.Model):
    title = models.CharField(max_length=200)
    documentBody = RichTextField(blank=True,null=True)
    isEnabled = models.BooleanField(default=True)
    owner = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    ownerSignature = models.CharField(max_length=200,default="")
    creationDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

class SOP_Versions(models.Model):

    SOP = models.ForeignKey(SOP, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True)
    documentBody = RichTextField(blank=True,null=True)
    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class SOPAttachments(models.Model):

    SOP = models.ForeignKey(SOP, on_delete=models.CASCADE, null=True)
    file=models.FileField(upload_to='documents/%Y/%m/%d',blank=True,null=True)

    def __str__(self) -> str:
        return self.file.name.split("/")[-1]
    
class SOPAttachments_Versions(models.Model):

    SOPAttachmentsId = models.ForeignKey(SOPAttachments, on_delete=models.SET_NULL, null=True)
    SOP = models.ForeignKey(SOP, on_delete=models.SET_NULL, null=True)
    fileName=models.CharField(max_length=200)
    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.fileName
    