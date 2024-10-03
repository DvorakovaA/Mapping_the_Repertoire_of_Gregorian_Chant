"""
Class definition of form(s) (their fields and their behaviour)
"""

from django import forms

from .models import Feasts, Datasets
from django.db.models import Q


OFFICE_CHOICES = {"V": "V", "M": "M", "L": "L", "V2": "V2"}
ALGO_CHOICES = {"Louvein": "Louvein algorithm", "DBSCAN": "DBSCAN clustering - DO NOT USE (no meaningful results, only for replication)", "Topic": "Topic model"}
METRIC_CHOICES = {"Jaccard": "Jaccard metric", "Topic model": "Comparison based on topic model (no research results for this option)"}
TOPIC_CHOICES = {"2": "2", "5": "5", "10": "10", "20":"20"}
ALL_CHOICE = 0


class InputForm(forms.Form):
    """ 
    Request form on tool page
    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(InputForm, self).__init__(*args, **kwargs)
        self.fields['datasets_own'].choices = [("admin_CI_base", "Basic CI dataset")]+list(Datasets.objects.filter(owner=user).values_list('dataset_id', 'name')) #[f for f in zip(Datasets.objects.filter(owner=user).values_list('dataset_id', flat=True), Datasets.objects.filter(owner=user).values_list('name', flat=True))]
        self.fields['datasets_public'].choices = [(f[0], f[1]+" (owner: "+f[2]+")") for f in list(Datasets.objects.filter(~Q(owner=user) & Q(public=True)).values_list('dataset_id', 'name', 'owner'))]


    feast = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'form-control'}), 
                                    choices=[(None, '---'), (ALL_CHOICE, 'All')]+[(f[0], f[1]) for f in zip([i for i in range(1, len(Feasts.objects.all())+1)], Feasts.objects.values_list('name', flat=True))])
    all = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices={"All": "All"}, required=False, initial=True)
    office = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OFFICE_CHOICES, required=False)
    
    community_detection_algorithm = forms.ChoiceField(widget=forms.RadioSelect, choices=ALGO_CHOICES, initial="Louvein")
    metric = forms.ChoiceField(widget=forms.RadioSelect, choices=METRIC_CHOICES, initial="Jaccard")
    number_of_topics = forms.ChoiceField(widget=forms.RadioSelect, choices=TOPIC_CHOICES, initial="5")
    datasets_own = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=None, initial=True, required=False)
    datasets_public = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=None, required=False)


class UploadDatasetForm(forms.Form):
    """
    Form for upload of own data sets
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
    Form for updates in georaphz data
    Used for matching same provenances with different 
    """
    def __init__(self, suggestions, *args, **kwargs):
        self.suggestions = suggestions
        super().__init__(*args, **kwargs)
        self.fields['matched_info'].choices = [ch for ch in zip(suggestions, suggestions)]

    matched_info = forms.ChoiceField(widget=forms.RadioSelect, choices=None, required=False)
    new_coords = forms.ChoiceField(widget=forms.RadioSelect, choices={'new_geo': 'Add new coordinates (Use decimal format!)'}, required=False)
    lat = forms.CharField(max_length=15, required=False)
    long = forms.CharField(max_length=15, required=False)