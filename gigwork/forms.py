from django import forms
from .models import GigWork

class ExcelImportForm(forms.Form):
    file = forms.FileField(label='Select Excel file')

class GigWorkForm(forms.ModelForm):
    class Meta:
        model = GigWork
        fields = ['date','duration', 'distance_km']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
