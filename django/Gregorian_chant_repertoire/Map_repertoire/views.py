"""
Script that contains functions which handle 
displaying of htmls and data transfer between script components
"""

from django.shortcuts import render
from .forms import InputForm
from .models import Feasts

from Map_repertoire.communities import get_communities
from Map_repertoire.table_construct import get_table
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
    Function that manages page of app itself - displays input form and shows results (table and map)
    """
    context = {}

    form = InputForm(request.POST or None, initial={'feast' : '---'})
    context = {"form" : form}
    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        request.session['all'] = form.cleaned_data['all']
        request.session['office'] = form.cleaned_data['office']
        request.session['algo'] = form.cleaned_data['community_detection_algorithm']
        if request.session['algo'] == 'Louvein':
             request.session['add_info_algo'] = form.cleaned_data['metric']
        else:
             request.session['add_info_algo'] = form.cleaned_data['number_of_topics']

        context = {"form" : form}

        feast_names = []
        for id in request.session.get('feast'):
            feast_names.append(Feasts.objects.values_list('name', flat=True)[int(id)])
        context['feasts'] = feast_names
        feast_ids = []
        for feast_name in feast_names:
            feast_ids.append(Feasts.objects.filter(name = feast_name).values()[0]['feast_id'])
        context['feast_id'] = [feast_ids]

        filtering_office = []
        if not request.session.get('all'):
            office_dict = {'V' : 'office_v', 'M' : 'office_m', 'L' : 'office_l', 'V2' : 'office_v2'}
            for off in request.session['office']:
                    filtering_office.append(office_dict[off])
        # else means filtering_office is empty list -> we select All

        communities, edges_info, sig_level = get_communities(feast_ids, filtering_office, request.session['algo'], request.session['add_info_algo'])
        context['sig_level'] = sig_level
        
        context['map_data'] = get_map_data(communities, edges_info)
        context['tab_data'] = get_table(communities, feast_ids, filtering_office)
        
    return render(request, "map_repertoire/tool.html", context)


def help(request):
    """
    Function that manages displaying of help page
    """
    return render(request, "map_repertoire/help.html")