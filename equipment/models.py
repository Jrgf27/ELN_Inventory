from django.db import models
from django.contrib.auth.models import User

from standardoperatingprotocols.models import SOP
from riskassessments.models import RiskAssessment
# Create your models here.


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    origin = models.CharField(max_length=200, null=True)
    supportContact = models.CharField(max_length=200, null=True)
    responsibleUser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    relatedSOP = models.ForeignKey(SOP, on_delete=models.SET_NULL, null=True)
    relatedRiskAssessment = models.ForeignKey(RiskAssessment, on_delete=models.SET_NULL, null=True)
    isEnabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
class Equipment_Versions(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    origin = models.CharField(max_length=200, null=True)
    supportContact = models.CharField(max_length=200, null=True)
    responsibleUser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    relatedSOP = models.ForeignKey(SOP, on_delete=models.SET_NULL, null=True)
    relatedRiskAssessment = models.ForeignKey(RiskAssessment, on_delete=models.SET_NULL, null=True)

    lastAction = models.CharField(max_length=10)
    lastEditedUserSignature = models.CharField(max_length=200)
    lastEditedDate = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name