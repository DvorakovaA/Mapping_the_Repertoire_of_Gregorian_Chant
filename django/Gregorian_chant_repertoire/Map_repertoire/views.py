"""
Script that contains functions which handle 
displaying of htmls and data transfer between script components
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
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
    #if request.method == "POST":
    form = InputForm(request.POST or None, initial={'feast' : '---'})
    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        request.session['REQUESTED'] = True
        return HttpResponseRedirect('', request)
        

    context = { "form": form }
    if request.session.get('REQUESTED'):
        feast_name = Feasts.objects.values_list('name', flat=True)[int(request.session.get('feast'))]
        context['feast'] = feast_name
        feast_id = Feasts.objects.filter(name = feast_name).values()[0]['feast_id']
        context['feast_id'] = [feast_id]

        communities, edges_info = get_communities([feast_id])
        
        com_map, cen_map = get_maps(communities, edges_info)
        context['com_map'] = com_map._repr_html_()
        context['cen_map'] = cen_map._repr_html_()
        
        context['tab_data'] = get_table(communities, [feast_id])
        request.session['REQUESTED'] = False
    
    return render(request, "map_repertoire/index.html", context)


def help(request):
    """
    Function that manages displaying of help page
    """
    return render(request, "map_repertoire/help.html")