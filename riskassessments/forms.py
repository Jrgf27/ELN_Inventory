from django import forms
from ckeditor.widgets import CKEditorWidget

from .models import *

class CreateNewRiskAssessment(forms.Form):
    title = forms.CharField(label = 'Title', max_length=200, required=True)
    documentBody= forms.CharField(label = '',widget=CKEditorWidget(),required=False)


class AttachFilesToRiskAssessment(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachFilesToRiskAssessment, self).__init__(*args, **kwargs)

        self.fields['attachedFile'] = forms.FileField(label='Select a file', required=False)