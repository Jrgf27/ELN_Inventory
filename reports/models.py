from django.db import models
from django.contrib.auth.models import User, Group
from ckeditor.fields import RichTextField
from stock.models import Stock
from samples.models import Sample
from equipment.models import Equipment
from standardoperatingprotocols.models import SOP
from projects.models import Projects
# Create your models here.

class Tags(models.Model):
    name = models.CharField(max_length=200,unique=True)

    def __str__(self) -> str:
        return self.name

class ReportsAttachments(models.Model):

    file=models.FileField(upload_to='documents/%Y/%m/%d',blank=True,null=True)

    def __str__(self) -> str:
        return self.file.name.split("/")[-1]

class ReportReviewers(models.Model):
    reviewer = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    reviewDecision = models.CharField(max_length=10, default="")
    reviewed = models.BooleanField(default=False)
    reviewerSignature = models.CharField(max_length=200, null=True, blank=True, default="")

    def __str__(self) -> str:
        return self.reviewer.username
    
class ReportReviewers_Versions(models.Model):
    reportReviewer = models.ForeignKey(ReportReviewers,on_delete=models.SET_NULL, null=True)
    reviewer = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    reviewDecision = models.CharField(max_length=10, default="")
    reviewed = models.BooleanField(default=False)
    reviewerSignature = models.CharField(max_length=200, null=True, blank=True, default="")

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)
    def __str__(self) -> str:
        return self.reviewer.username

class Reports(models.Model):
    title = models.CharField(max_length=200)
    reportBody = RichTextField(blank=True,null=True)
    reportTags = models.ManyToManyField(Tags)
    isEnabled = models.BooleanField()
    owner = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    ownerSignature = models.CharField(max_length=200)
    creationDate = models.DateField(auto_now_add=True)

    linkedReports = models.ManyToManyField('self')
    linkedSOPs=models.ManyToManyField(SOP, related_name="linkedSOPs")
    linkedReagents=models.ManyToManyField(Stock, related_name="linkedReagents")
    linkedSamples=models.ManyToManyField(Sample, related_name="linkedSamples")
    linkedEquipments=models.ManyToManyField(Equipment, related_name="linkedEquipments")
    linkedAttachment=models.ManyToManyField(ReportsAttachments, related_name="linkedAttachment")

    reportReviewers = models.ManyToManyField(ReportReviewers, related_name="reviewers")
    reviewed = models.BooleanField(default=False)

    project = models.ForeignKey(Projects, on_delete=models.SET_NULL, null=True)

    canEditUsers = models.ManyToManyField(User, related_name="canEditUsers")

    def __str__(self) -> str:
        return self.title

class Reports_Versions(models.Model):

    report = models.ForeignKey(Reports, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True)
    reportBody = RichTextField(blank=True,null=True)
    reportTags = models.ManyToManyField(Tags, related_name="linkedTags_versions")
    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200, default="")
    lastEditedDate = models.DateField(auto_now_add=True)

    linkedReports_versions = models.ManyToManyField(Reports, related_name="linkedReports_versions")
    linkedSOPs=models.ManyToManyField(SOP, related_name="linkedSOPs_versions")
    linkedReagents=models.ManyToManyField(Stock, related_name="linkedReagents_versions")
    linkedSamples=models.ManyToManyField(Sample, related_name="linkedSamples_versions")
    linkedEquipments=models.ManyToManyField(Equipment, related_name="linkedEquipments_versions")
    linkedAttachment=models.ManyToManyField(ReportsAttachments, related_name="linkedAttachment_versions")

    reportReviewers = models.ManyToManyField(ReportReviewers, related_name="reviewers_versions")
    reviewed = models.BooleanField(default=False)

    canEditUsers = models.ManyToManyField(User, related_name="canEditUsers_versions")

    def __str__(self) -> str:
        return self.title
