from django import forms
from .models import GigWork, WeeklyEarning, Payments

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

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payments
        fields = ['date','month','week', 'total', 'revenue']
        
