"""
Class definition of form(s) (their fields and their behaviour)
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import Feasts


OFFICE_CHOICES = {"V": "V", "M": "M", "L": "L", "V2": "V2"}
ALGO_CHOICES = {"Louvein": "Louvein algorithm", "DBSCAN": "DBSCAN clustering - DO NOT USE (no meaningful results, only for replication)", "Topic": "Topic model"}
METRIC_CHOICES = {"Jaccard": "Jaccard metric", "Topic model": "Comparison based on topic model (no research results for this option)"}
TOPIC_CHOICES = {"2": "2", "5": "5", "10": "10", "20":"20"}
ALL_CHOICE = 0


class InputForm(forms.Form):
    """ 
    Request form on tool page
    """
    feast = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'form-control'}), 
                                      choices=[(None, '---'), (ALL_CHOICE, 'All')]+[(f[0], f[1]) for f in zip([i for i in range(1, len(Feasts.objects.all())+1)], Feasts.objects.values_list('name', flat=True))])
    all = forms.MultipleChoiceField(label="Select complete repertoire for feast:", widget=forms.CheckboxSelectMultiple, choices={"All": "All"}, required=False, initial=True)
    office = forms.MultipleChoiceField(label="or select only particular office:", widget=forms.CheckboxSelectMultiple, choices=OFFICE_CHOICES, required=False)
    
    community_detection_algorithm = forms.ChoiceField(widget=forms.RadioSelect, choices=ALGO_CHOICES, initial="Louvein")
    metric = forms.ChoiceField(widget=forms.RadioSelect, choices=METRIC_CHOICES, initial="Jaccard")
    number_of_topics = forms.ChoiceField(widget=forms.RadioSelect, choices=TOPIC_CHOICES, initial="5")