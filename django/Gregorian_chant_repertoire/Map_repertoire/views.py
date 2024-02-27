"""
Script that contains functions which handle 
displaying of htmls and data transfer between script components
"""

from django.shortcuts import render
from .forms import InputForm
from .models import Feasts

from Map_repertoire.communities import get_communities
from Map_repertoire.map_construct import get_maps
from Map_repertoire.table_construct import get_table

def index(request):
    """
    Function that manages main html page of app - displays input form and shows results (table and map)
    """
    context = {}

    form = InputForm(request.POST or None, initial={'feast' : '---'})
    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        request.session['All'] = form.cleaned_data['All']
        request.session['V'] = form.cleaned_data['V']
        request.session['M'] = form.cleaned_data['M']
        request.session['L'] = form.cleaned_data['L']
        request.session['V2'] = form.cleaned_data['V2']

        
    context = {"form" : form}
    feast_name = Feasts.objects.values_list('name', flat=True)[int(request.session.get('feast'))]
    context['feast'] = feast_name
    feast_id = Feasts.objects.filter(name = feast_name).values()[0]['feast_id']
    context['feast_id'] = [feast_id]
    filtering_office = []
    if not request.session.get('All'):
        office_shortcuts = ['V', 'M', 'L', 'V2']
        office_names = ['office_v', 'office_m', 'office_l', 'office_v2']
        for i in range(len(office_shortcuts)):
            if request.session.get(office_shortcuts[i]):
                filtering_office.append(office_names[i])
    # else filtering_office is empty list -> we select All

    communities, edges_info, sig_level = get_communities([feast_id], filtering_office)
    context['sig_level'] = sig_level
    
    com_map, cen_map = get_maps(communities, edges_info)
    context['com_map'] = com_map._repr_html_()
    context['cen_map'] = cen_map._repr_html_()
    
    context['tab_data'] = get_table(communities, [feast_id], filtering_office)
    
    return render(request, "map_repertoire/index.html", context)


def help(request):
    """
    Function that manages displaying of help page
    """
    return render(request, "map_repertoire/help.html")