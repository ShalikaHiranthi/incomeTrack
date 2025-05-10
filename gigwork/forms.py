from django import forms
from .models import GigWork, WeeklyEarning

class ExcelImportForm(forms.Form):
    file = forms.FileField(label='Select Excel file')

class GigWorkForm(forms.ModelForm):
    class Meta:
        model = GigWork
        fields = ['date','duration', 'distance_km']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class WeeklyEarningForm(forms.ModelForm):
    class Meta:
        model = WeeklyEarning
        fields = ['month','start', 'ispaid_part1', 'end', 'ispaid_part2']
        
