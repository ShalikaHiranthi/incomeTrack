from django import forms
from .models import Earning, EarningDetail, Weeklypayments, Invoices

class EarningForm(forms.ModelForm):
    class Meta:
        model = Earning
        fields = ['date', 'title','sub_total']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class EarningDetailForm(forms.ModelForm):
    class Meta:
        model = EarningDetail
        fields = ['source', 'amount', 'tip','total']

class ExcelImportForm(forms.Form):
    file = forms.FileField(label='Select Excel file')

class WeeklyPayForm(forms.ModelForm):
    class Meta:
        model = Weeklypayments
        fields = ['month','start', 'ispaid_part1', 'end', 'ispaid_part2']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoices
        fields = ['month','week', 'tips', 'amounts', 'total']
        
