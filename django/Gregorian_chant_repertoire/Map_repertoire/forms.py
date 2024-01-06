"""
Script for form(s) (their fields) definition
"""

from django import forms
from .models import Feasts

class InputForm(forms.Form):
    feast = forms.ChoiceField(choices=[(f[0], f[1]) for f in zip([i for i in range(len(Feasts.objects.all()))], Feasts.objects.values_list('name', flat=True))])