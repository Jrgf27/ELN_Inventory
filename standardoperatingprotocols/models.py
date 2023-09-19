from django.db import models
from django.contrib.auth.models import User, Group
from ckeditor.fields import RichTextField

# Create your models here.

class SOPAttachments(models.Model):

    file=models.FileField(upload_to='documents/%Y/%m/%d',blank=True,null=True)

    def __str__(self) -> str:
        return self.file.name.split("/")[-1]

class SOP(models.Model):
    title = models.CharField(max_length=200)
    documentBody = RichTextField(blank=True,null=True)
    isEnabled = models.BooleanField(default=True)
    owner = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    ownerSignature = models.CharField(max_length=200,default="")
    creationDate = models.DateField(auto_now_add=True)

    linkedAttachment=models.ManyToManyField(SOPAttachments, related_name="linkedAttachment")

    trainer = models.ManyToManyField(User, related_name="trainer")
    trainee = models.ManyToManyField(User, related_name="trainee")

    def __str__(self) -> str:
        return self.title

class SOP_Versions(models.Model):

    SOP = models.ForeignKey(SOP, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True)
    documentBody = RichTextField(blank=True,null=True)

    linkedAttachment=models.ManyToManyField(SOPAttachments, related_name="linkedAttachment_versions")

    trainer = models.ManyToManyField(User, related_name="trainer_versions")
    trainee = models.ManyToManyField(User, related_name="trainee_versions")

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title



    
    