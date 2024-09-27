"""
Function that handle displaying of html files and data transfer between components
"""

from django.shortcuts import render
from .forms import InputForm, UploadDatasetForm, DeleteDatasetForm
from .models import Feasts
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout

from Map_repertoire.communities import get_communities
from Map_repertoire.table_construct import get_table_data
from Map_repertoire.map_data_construct import get_map_data, get_map_of_all_data

from Map_repertoire.datasets import check_files_validity, integrate_chants_file, delete_dataset 


def index(request):
    """
    Function that manages intro page of the app
    """
    context = {}
    context['map_data_all'] = get_map_of_all_data()
    return render(request, "map_repertoire/index.html", context)



def tool(request):
    """
    Function that manages page with tool - displays request form and shows results (table and map)
    """
    context = {} # back-end and front-end communication variable
    form = InputForm(data=request.POST or None, initial={'feast' : '---'}, user=request.user.username)
    context = {"form" : form}

    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        request.session['all'] = form.cleaned_data['all']
        request.session['office'] = form.cleaned_data['office']
        request.session['algo'] = form.cleaned_data['community_detection_algorithm']
        data_own = form.cleaned_data['datasets_own']
        data_pub = form.cleaned_data['datasets_public']
        request.session['datasets'] = data_own + data_pub

        if request.session['algo'] == 'Louvein' or request.session['algo'] == 'DBSCAN':
             request.session['add_info_algo'] = form.cleaned_data['metric']
        else:
             request.session['add_info_algo'] = form.cleaned_data['number_of_topics']

        if '0' in request.session.get('feast'): # All feasts selected
            context['feasts'] = ['All feasts']
            feast_codes = ['All']
        else:
            feast_names = []
            for id in request.session.get('feast'):
                feast_names.append(Feasts.objects.values_list('name', flat=True)[int(id)-1])
            context['feasts'] = feast_names
            feast_codes = []
            for feast_name in feast_names:
                feast_codes.append(Feasts.objects.filter(name = feast_name).values()[0]['feast_code'])

        filtering_office = []
        if not request.session.get('all'):
            filtering_office = request.session['office']

        communities, edges_info, sig_level = get_communities(feast_codes, filtering_office, request.session['algo'], request.session['add_info_algo'], request.session['datasets'])
        context['sig_level'] = sig_level

        context['map_data'] = get_map_data(communities, edges_info)
        context['tab_data'] = get_table_data(communities, feast_codes, filtering_office, request.session['datasets'])

    return render(request, "map_repertoire/tool.html", context)


def help(request):
    """
    Function that manages displaying of help page
    """
    return render(request, "map_repertoire/help.html")


def register_view(request):
    """
    Function providing page with registration form (and registration) for new users
    """
    reg_form = UserCreationForm(request.POST or None)
    if reg_form.is_valid():
        new_user = reg_form.save()
        return HttpResponseRedirect('/map_repertoire/login/', request)
    
    context = {"form": reg_form}
    return render(request, 'map_repertoire/register.html', context)


def login_view(request):
    """
    Function porvading page with login form for registrated users
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect('/map_repertoire/')
    else:
        form = AuthenticationForm(request)

    context = {"form" : form}
    return render(request, 'map_repertoire/login.html', context)


def logout_view(request):
    """
    Function porvading logout for users (no page, just redirect action)
    """
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/map_repertoire/')
    else:
        return HttpResponseRedirect('/map_repertoire/')
    

def upload_dataset(request):
    add_form = UploadDatasetForm(request.POST, request.FILES)
    delete_form = DeleteDatasetForm(data=request.POST, user=request.user.username)
    context = {"add_form" : add_form, "delete_form" : delete_form}

    # Missing values control
    if request.method == 'POST':

        if 'missing_ok' in request.POST:
            request.session['unknown_values'] = []
            return HttpResponseRedirect("")
        
        # Unknown provenances control
        elif 'geo_yes' in request.POST:
            context['miss_provenance'] =  request.session['miss_provenance']
            context['dataset_name'] = request.session['dataset_name']
            request.session['miss_provenance'] = []
            return render(request, "map_repertoire/geography.html", context)
        
        elif 'geo_no' in request.POST:
            request.session['miss_provenance'] = []
            return HttpResponseRedirect("")

    # Dataset addition
    if add_form.is_valid():
        sources_file = request.FILES.get('sources_file', None)
        request.session['dataset_name'] = add_form.cleaned_data['name']
        validity, error_message = check_files_validity(add_form.cleaned_data['name'], request.user.username, request.FILES['chants_file'], sources_file)
        request.session['error_message'] = error_message

        if validity:
            possible_unknown, miss_provenance = integrate_chants_file(add_form.cleaned_data['name'], request.user.username, request.FILES['chants_file'], sources_file, add_form.cleaned_data['visibility'])
            request.session['unknown_values'] = possible_unknown
            request.session['miss_provenance'] = miss_provenance
        else:
            request.session['unknown_values'] = []
            request.session['miss_provenance'] = []
        return HttpResponseRedirect("")
    

    # Dataset removal
    if delete_form.is_valid():
        datasets = delete_form.cleaned_data['dataset_select']
        for dataset in datasets:
            delete_dataset(dataset)
            
        request.session['error_message'] = ""
        request.session['unknown_values'] = []
        request.session['miss_provenance'] = []
        return HttpResponseRedirect("")
    
    return render(request, "map_repertoire/datasets.html", context)


def geography(request):
    """
    
    """

    #return render(request, "map_repertoire/geography.html", context)