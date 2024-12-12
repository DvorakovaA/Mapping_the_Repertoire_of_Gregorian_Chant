"""
Class definition of form(s) (their fields and their behaviour)
"""

from django import forms

from .models import Feasts, Datasets
from django.db.models import Q


OFFICE_CHOICES = {"V": "V", "M": "M", "L": "L", "V2": "V2"}
ALGO_CHOICES = {"Louvain": "Louvain algorithm", "CAT" : "Complete agreement principle (aka Cantus Analysis Tool)", "Topic": "Topic model"}
METRIC_CHOICES = {"Jaccard": "Jaccard metric", "Topic model": "Comparison based on topic model (no research results for this option)"}
TOPIC_CHOICES = {"2": "2", "5": "5", "10": "10", "20":"20"}
OFFICE_POLICY_CHOICES = {"ignore" : "Treat day as one whole (ignore to which office chant belongs)", "preserve" : "Include office usage into comparison"}
ALL_CHOICE = 0


class InputForm(forms.Form):
    """ 
    Request form on tool page -> collecting data for community detection
    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(InputForm, self).__init__(*args, **kwargs)
        self.fields['datasets_own'].choices = [("admin_CI_base", "Basic CI dataset")]+list(Datasets.objects.filter(owner=user).values_list('dataset_id', 'name')) #[f for f in zip(Datasets.objects.filter(owner=user).values_list('dataset_id', flat=True), Datasets.objects.filter(owner=user).values_list('name', flat=True))]
        self.fields['datasets_public'].choices = [(f[0], f[1]+" (owner: "+f[2]+")") for f in list(Datasets.objects.filter(~Q(owner=user) & Q(public=True)).values_list('dataset_id', 'name', 'owner'))]


    number_of_feasts = len(Feasts.objects.all().values_list('name', flat=True))
    feast = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'feasts_select', 'style': 'width: 100%;'}), 
                                    choices=[(None, '---'), (ALL_CHOICE, 'All')]+[(f[0], f[1]) for f in zip([i for i in range(1, number_of_feasts+1)], Feasts.objects.values_list('name', flat=True))],)
    all = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices={"All": "All"}, required=False, initial=True)
    office = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OFFICE_CHOICES, required=False)
    
    community_detection_algorithm = forms.ChoiceField(widget=forms.RadioSelect, choices=ALGO_CHOICES, initial="Louvain")
    metric = forms.ChoiceField(widget=forms.RadioSelect, choices=METRIC_CHOICES, initial="Jaccard")
    number_of_topics = forms.ChoiceField(widget=forms.RadioSelect, choices=TOPIC_CHOICES, initial="5")
    office_policy = forms.ChoiceField(widget=forms.RadioSelect, choices=OFFICE_POLICY_CHOICES, initial="ignore")
    datasets_own = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=None, required=False, initial="admin_CI_base")
    datasets_public = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=None, required=False)


class UploadDatasetForm(forms.Form):
    """
    Form for upload of own datasets
    """
    name = forms.CharField(max_length=50)
    chants_file = forms.FileField()
    sources_file = forms.FileField(required=False)
    visibility = forms.ChoiceField(widget=forms.RadioSelect, choices={"private" : "private", "public" : "public"}, initial="private")


class DeleteDatasetForm(forms.Form):
    """
    Form for dataset removal
    """
    dataset_select = forms.MultipleChoiceField(choices=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['dataset_select'].choices = [(f[0], f[1]) for f in zip(Datasets.objects.filter(owner=user).values_list('dataset_id', flat=True), Datasets.objects.filter(owner=user).values_list('name', flat=True))]



class AddGeographyInfoForm(forms.Form):
    """
    Form for updates in georaphy data
    Used for matching same provenances with different or coordinates addition
    """
    def __init__(self, suggestions, *args, **kwargs):
        self.suggestions = suggestions
        super().__init__(*args, **kwargs)
        self.fields['matched_info'].choices = [ch for ch in zip(suggestions, suggestions)]

    matched_info = forms.ChoiceField(widget=forms.RadioSelect, choices=None, required=False)
    new_coords = forms.ChoiceField(widget=forms.RadioSelect, choices={'new_geo': 'Add new coordinates (Use decimal format, e. g. London is [51.507222, -0.1275].)'}, required=False)
    lat = forms.CharField(max_length=15, required=False)
    long = forms.CharField(max_length=15, required=False)