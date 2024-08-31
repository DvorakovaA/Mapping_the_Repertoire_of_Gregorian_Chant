"""
Function that handle displaying of html files and data transfer between components
"""

from django.shortcuts import render
from .forms import InputForm
from .models import Feasts
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout

from Map_repertoire.communities import get_communities
from Map_repertoire.table_construct import get_table_data
from Map_repertoire.map_data_construct import get_map_data, get_map_of_all_data


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

    form = InputForm(request.POST or None, initial={'feast' : '---'})
    context = {"form" : form}
    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        request.session['all'] = form.cleaned_data['all']
        request.session['office'] = form.cleaned_data['office']
        request.session['algo'] = form.cleaned_data['community_detection_algorithm']
        if request.session['algo'] == 'Louvein' or request.session['algo'] == 'DBSCAN':
             request.session['add_info_algo'] = form.cleaned_data['metric']
        else:
             request.session['add_info_algo'] = form.cleaned_data['number_of_topics']

        context = {"form" : form}

        if '0' in request.session.get('feast'): # All feasts selected
            context['feasts'] = ['All feasts']
            feast_ids = ['All']
        else:
            feast_names = []
            for id in request.session.get('feast'):
                feast_names.append(Feasts.objects.values_list('name', flat=True)[int(id)-1])
            context['feasts'] = feast_names
            feast_ids = []
            for feast_name in feast_names:
                feast_ids.append(Feasts.objects.filter(name = feast_name).values()[0]['feast_id'])

        filtering_office = []
        if not request.session.get('all'):
            office_dict = {'V' : 'office_v', 'M' : 'office_m', 'L' : 'office_l', 'V2' : 'office_v2'}
            for off in request.session['office']:
                    filtering_office.append(office_dict[off])
        # else means filtering_office is empty list -> we select All offices

        communities, edges_info, sig_level = get_communities(feast_ids, filtering_office, request.session['algo'], request.session['add_info_algo'])
        context['sig_level'] = sig_level

        context['map_data'] = get_map_data(communities, edges_info)
        context['tab_data'] = get_table_data(communities, feast_ids, filtering_office)
        
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