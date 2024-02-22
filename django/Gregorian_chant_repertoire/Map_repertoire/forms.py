"""
Script for form(s) (their fields) definition
"""

from django import forms
from .models import Feasts

class InputForm(forms.Form):
    feast = forms.ChoiceField(choices=[(f[0], f[1]) for f in zip([i for i in range(len(Feasts.objects.all()))], Feasts.objects.values_list('name', flat=True))])
    V = forms.BooleanField(label="V", required=False)
    M = forms.BooleanField(label="M", required=False)
    L = forms.BooleanField(label="L", required=False)
    V2 = forms.BooleanField(label="V2", required=False)