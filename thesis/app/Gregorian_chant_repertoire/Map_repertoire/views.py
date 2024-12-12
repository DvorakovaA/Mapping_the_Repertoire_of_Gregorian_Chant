"""
Functions that handle displaying of html files as pages 
and data transfer between backend and frontend components
"""

from django.shortcuts import render
from .forms import InputForm, UploadDatasetForm, DeleteDatasetForm, AddGeographyInfoForm
from .models import Feasts
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout

from Map_repertoire.communities import get_communities
from Map_repertoire.table_construct import get_table_data
from Map_repertoire.map_data_construct import get_map_data, get_map_of_all_data_informed, get_map_of_all_data_basic

from Map_repertoire.datasets import check_files_validity, integrate_chants_file, delete_dataset
from Map_repertoire.datasets import get_provenance_sugestions, get_unknown_provenances, add_new_coordinates, add_matched_provenance


def index(request):
    """
    Function that manages intro (home) page of the app
    """
    request.session['upload_error_message'] = '' # clean datasets errors with page change

    context = {}
    context['map_data_all_informed'] = get_map_of_all_data_informed()
    return render(request, "map_repertoire/index.html", context)



def tool(request):
    """
    Function that manages page with tool - displays request form and shows results (table and map)
    """
    context = {} # back-end and front-end communication variable
    form = InputForm(data=request.POST or None, initial={'feast' : '---'}, user=request.user.username)
    context = {"form" : form}

    request.session['upload_error_message'] = '' # clean datasets errors with page change

    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        request.session['all'] = form.cleaned_data['all']
        request.session['office'] = form.cleaned_data['office']
        request.session['algo'] = form.cleaned_data['community_detection_algorithm']
        data_own = form.cleaned_data['datasets_own']
        data_pub = form.cleaned_data['datasets_public']
        if data_pub + data_own == []:
            request.session['dataset_error_message'] = 'Please, select at least one dataset!'
            return HttpResponseRedirect("")
        else:
            request.session['dataset_error_message'] = ''
        request.session['datasets'] = data_own + data_pub

        if request.session['algo'] == 'Louvain' or request.session['algo'] == 'DBSCAN':
             request.session['add_info_algo'] = form.cleaned_data['metric']
        elif request.session['algo'] == 'CAT':
            request.session['add_info_algo'] = form.cleaned_data['office_policy']
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


def contact(request):
    """
    Function that manages displaying of page with contact info
    """
    return render(request, "map_repertoire/contact.html")


def register_view(request):
    """
    Function providing page with registration form (and registration) for new users
    """
    reg_form = UserCreationForm(request.POST)

    if request.method == 'POST':
        if reg_form.is_valid():
            request.session['reg_error'] = ""
            reg_form.save()
            return HttpResponseRedirect('/map_repertoire/login/', request)
        else:
            request.session['reg_error'] = ""
            request.session['reg_error'] = reg_form.errors
    else:
        request.session['reg_error'] = ""
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
    Function porvading logout for users (no page, just redirect action causing log out)
    """
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/map_repertoire/')
    else:
        return HttpResponseRedirect('/map_repertoire/')
    

def datasets_view(request):
    """
    Page for upload and delete datasets -> two django forms
    Also displays various warnings
    """
    add_form = UploadDatasetForm(request.POST, request.FILES)
    delete_form = DeleteDatasetForm(data=request.POST, user=request.user.username)
    context = {"add_form" : add_form, "delete_form" : delete_form}

    # Missing values control
    if request.method == 'POST':
        if 'missing_ok' in request.POST:
            request.session['unknown_values'] = []
            return HttpResponseRedirect("")
        
        # Unknown provenances controls
        elif 'geo_yes' in request.POST:
            request.session['miss_provenance'] = []
            return HttpResponseRedirect("/map_repertoire/geography", request)
            
        
        elif 'geo_no' in request.POST:
            request.session['miss_provenance'] = []
            return HttpResponseRedirect("")

    # Dataset addition
    if add_form.is_valid():
        sources_file = request.FILES.get('sources_file', None)
        request.session['dataset_name'] = add_form.cleaned_data['name'].strip()
        validity, error_message = check_files_validity(add_form.cleaned_data['name'], request.user.username, request.FILES['chants_file'], sources_file)
        request.session['upload_error_message'] = error_message

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
            
        request.session['upload_error_message'] = ""
        request.session['unknown_values'] = []
        request.session['miss_provenance'] = []
        return HttpResponseRedirect("")
    
    return render(request, "map_repertoire/datasets.html", context)


def geography(request):
    """
    Provides page with updates in geography data of app
    especially geography data updating form control
    """
    try:
        if request.session['list_missed'] == []:
            list_all_general_missed = get_unknown_provenances(request.user.username)
            request.session['list_missed'] = list_all_general_missed
    except: # request.session['list_missed'] does not exist -> create it
        list_all_general_missed = get_unknown_provenances(request.user.username)
        request.session['list_missed'] = list_all_general_missed


    context = {}
    context['map_data_all_basic'] = get_map_of_all_data_basic()
    if request.session['list_missed'] != []:
         context['actual_prov'] = request.session['list_missed'][0]
         suggestions = get_provenance_sugestions(request.session['list_missed'][0])
         prov_form = AddGeographyInfoForm(data=request.POST, suggestions=suggestions)
         context['prov_form'] = prov_form
         
    else:
        context['prov_form'] = []
    
    # Resolving forms
    if request.method == 'POST':
        if context['prov_form'] != []:
            # 
            if context['prov_form'].is_valid():
                # Check what submit button was pressed
                if 'add' in request.POST:
                    # Check if something was selected while Add pressed
                    if context['prov_form'].cleaned_data['matched_info'] != '' or context['prov_form'].cleaned_data['new_coords'] != '':
                        if context['prov_form'].cleaned_data['new_coords'] == 'new_geo':
                            lat = context['prov_form'].cleaned_data['lat']
                            long = context['prov_form'].cleaned_data['long']
                            try:
                                lat = float(lat)
                                long = float(long)
                            except:
                                context['error_message'] = 'Please, use decimal format of coordinates!'
                                return render(request, "map_repertoire/geography.html", context)
                            add_new_coordinates(request.session['list_missed'][0], lat, long)
                        else:    
                            add_matched_provenance(request.session['list_missed'][0], context['prov_form'].cleaned_data['matched_info'])
                        request.session['list_missed'].pop(0)
                    else: # empty form and Add pressed
                        context['error_message'] = 'Please for Add option choose something.'
                        return render(request, "map_repertoire/geography.html", context)
                elif 'next' in request.POST:
                    request.session['list_missed'].pop(0)

                request.session.modified = True
                return HttpResponseRedirect("", request)
            

    return render(request, "map_repertoire/geography.html", context)