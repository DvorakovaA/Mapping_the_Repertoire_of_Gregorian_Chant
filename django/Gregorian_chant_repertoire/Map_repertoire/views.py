"""
Script that contains functions which handle 
displaying of htmls and data transfer between script components
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import InputForm
from .models import Feasts

from Map_repertoire.map_construct import get_map
from Map_repertoire.communities import get_communities

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
        context['feast_id'] = feast_id
        communities = get_communities(feast_id)
        context['map'] = get_map(communities)._repr_html_()
        
        context['sources'] = [{'drupal_path' : source} for com in communities for source in com]
        request.session['REQUESTED'] = False
    
    return render(request, "Map_repertoire/index.html", context)


def help(request):
    """
    Function that manages displaying of help page
    """
    return render(request, "Map_repertoire/help.html")