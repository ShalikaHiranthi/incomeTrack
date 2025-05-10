from django import forms
from .models import Earning, EarningDetail

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
        fields = ['source', 'amount', 'tip']
        
