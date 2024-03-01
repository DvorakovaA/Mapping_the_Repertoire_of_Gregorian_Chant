"""
Script for form(s) (their fields) definition
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import Feasts

class InputForm(forms.Form):
    feast = forms.ChoiceField(choices=[(None, '---')]+[(f[0], f[1]) for f in zip([i for i in range(len(Feasts.objects.all()))], Feasts.objects.values_list('name', flat=True))])
    All = forms.BooleanField(label="All", required=False)
    V = forms.BooleanField(label="V", required=False)
    M = forms.BooleanField(label="M", required=False)
    L = forms.BooleanField(label="L", required=False)
    V2 = forms.BooleanField(label="V2", required=False)

    def clean(self):
        cleaned_data = super().clean()
        all = cleaned_data['All']
        v = cleaned_data['V']
        m = cleaned_data['M']
        l = cleaned_data['L']
        v2 = cleaned_data['V2']
        if all and (v or m or l or v2):
            raise ValidationError("Select All option OR something else")
            
        elif not (all or v or m or l or v2):
            raise ValidationError("Something must be selected!")