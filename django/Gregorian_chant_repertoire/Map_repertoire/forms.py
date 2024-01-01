"""
Script for form(s) (their fields) definition
"""

from django import forms
from .models import Feasts

class InputForm(forms.Form):
    feast = forms.ModelChoiceField(queryset=Feasts.objects.values_list('name', flat=True))