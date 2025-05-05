from django import forms
from .models import Earning

class EarningForm(forms.ModelForm):
    class Meta:
        model = Earning
        fields = ['date', 'source', 'amount', 'tip']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
