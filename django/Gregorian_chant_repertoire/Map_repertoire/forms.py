"""
Script for form(s) (their fields) definition and little validation
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import Feasts


OFFICE_CHOICES = {"V": "V", "M": "M", "L": "L", "V2": "V2"}
ALGO_CHOICES = {"Louvein": "Louvein algorithm", "DBSCAN": "DBSCAN clustering", "Topic": "Topic model"}
METRIC_CHOICES = {"Jaccard": "Jaccard metric", "Topic model": "Comparison based on topic model"}
TOPIC_CHOICES = {"5": "5", "10": "10", "20":"20"}


class InputForm(forms.Form):
    feast = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'form-control'}), 
                                      choices=[(None, '---')]+[(f[0], f[1]) for f in zip([i for i in range(len(Feasts.objects.all()))], Feasts.objects.values_list('name', flat=True))])
    all = forms.MultipleChoiceField(label="Select complete repertoire for feast:", widget=forms.CheckboxSelectMultiple, choices={"All": "All"}, required=False)
    office = forms.MultipleChoiceField(label="or select only particular office:", widget=forms.CheckboxSelectMultiple, choices=OFFICE_CHOICES, required=False)
    
    community_detection_algorithm = forms.ChoiceField(widget=forms.RadioSelect, choices=ALGO_CHOICES, initial="Louvein")
    metric = forms.ChoiceField(widget=forms.RadioSelect, choices=METRIC_CHOICES, initial="Jaccard")
    number_of_topics = forms.ChoiceField(widget=forms.RadioSelect, choices=TOPIC_CHOICES, initial="5")


    def clean(self):
        cleaned_data = super().clean()
        all = cleaned_data['all']
        office = cleaned_data['office']

        if all and (office):
            raise ValidationError("Select All option OR something else")
            
        elif not (all or office):
            raise ValidationError("Something must be selected!")