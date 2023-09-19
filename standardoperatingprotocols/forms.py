from django import forms
from ckeditor.widgets import CKEditorWidget

from .models import *

class CreateNewSOP(forms.Form):
    title = forms.CharField(label = 'Title', max_length=200, required=True)
    documentBody= forms.CharField(label = '',widget=CKEditorWidget(),required=False)


class AttachFilesToSOP(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachFilesToSOP, self).__init__(*args, **kwargs)

        self.fields['attachedFile'] = forms.FileField(label='Select a file', required=False)


class TrainerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TrainerForm, self).__init__(*args, **kwargs)

        self.fields['newTrainer'] = forms.ModelChoiceField(queryset=User.objects.exclude(is_active=False),
                                    required=True, 
                                    label='Trainer')
        
class TraineeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TraineeForm, self).__init__(*args, **kwargs)

        self.fields['newTrainee'] = forms.ModelChoiceField(queryset=User.objects.exclude(is_active=False),
                                    required=True, 
                                    label='Trainee')