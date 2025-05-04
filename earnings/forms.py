from django import forms
from .models import Earning

class EarningForm(forms.ModelForm):
    class Meta:
        model = Earning
        fields = '__all__'
