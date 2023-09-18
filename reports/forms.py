from django import forms
from ckeditor.widgets import CKEditorWidget

from django.contrib.auth.models import User
from stock.models import Stock
from standardoperatingprotocols.models import SOP
from .models import *

class CreateNewReport(forms.Form):
    title = forms.CharField(label = 'Title', max_length=200, required=True)
    reportBody= forms.CharField(label = '',widget=CKEditorWidget(),required=False)

class AttachTagToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachTagToReport, self).__init__(*args, **kwargs)

        self.fields['attachTag'] = forms.ModelChoiceField(queryset=Tags.objects.all(), 
                                    required=True, 
                                    label='Chose Tag')

class CreateNewTag(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CreateNewTag, self).__init__(*args, **kwargs)

        self.fields['newTag'] = forms.CharField(label = 'New Tag', max_length=200, required=True)

class AttachReagentsToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachReagentsToReport, self).__init__(*args, **kwargs)

        self.fields['reagentsStockId'] = forms.ModelChoiceField(queryset=Stock.objects.filter(hasBatchCode = True).exclude(isEnabled=False), 
                                    required=True, 
                                    label='What\' the Stock')

class AttachReportsToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachReportsToReport, self).__init__(*args, **kwargs)

        self.fields['report'] = forms.ModelChoiceField(queryset=Reports.objects.exclude(isEnabled=False), 
                                    required=True, 
                                    label='Linked report')
        
class AttachSOPToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachSOPToReport, self).__init__(*args, **kwargs)

        self.fields['SOP'] = forms.ModelChoiceField(queryset=SOP.objects.exclude(isEnabled=False), 
                                    required=True, 
                                    label='Linked SOP')

class AttachSamplesToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachSamplesToReport, self).__init__(*args, **kwargs)

        self.fields['linkedSample'] = forms.ModelChoiceField(queryset=Sample.objects.exclude(isEnabled=False), 
                                    required=True, 
                                    label='What\' the Sample')

class AttachEquipmentToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachEquipmentToReport, self).__init__(*args, **kwargs)

        self.fields['linkedEquipment'] = forms.ModelChoiceField(queryset=Equipment.objects.exclude(isEnabled=False), 
                                    required=True, 
                                    label='What\' the Equipment')
        
class AllowEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        userId = kwargs.pop('userId')
        super(AllowEditForm, self).__init__(*args, **kwargs)

        self.fields['newEditor'] = forms.ModelChoiceField(queryset=User.objects.exclude(is_active=False).exclude(id=userId),
                                    required=True, 
                                    label='Editor')

class ReviewerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        userId = kwargs.pop('userId')
        super(ReviewerForm, self).__init__(*args, **kwargs)

        self.fields['newReviewer'] = forms.ModelChoiceField(queryset=User.objects.exclude(is_active=False).exclude(id=userId),
                                    required=True, 
                                    label='Reviewer')

class AttachFilesToReport(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AttachFilesToReport, self).__init__(*args, **kwargs)

        self.fields['attachedFile'] = forms.FileField(label='Select a file', required=False)