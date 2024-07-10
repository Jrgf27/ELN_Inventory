from django.db import models

# Create your models here.

class Projects(models.Model):
    name = models.CharField(max_length=200,unique=True)
    isEnabled = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name
