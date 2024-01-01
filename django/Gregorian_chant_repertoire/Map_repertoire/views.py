"""
Script that contains functions which handle 
displaying of htmls and data transfer between script components
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import InputForm


def index(request):
    """
    Function that manages main html page of app - displays input form and shows results (table and map)
    """
    #context = {}
    #if request.method == "POST":
    form = InputForm(request.POST or None)
    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        return HttpResponseRedirect('', request)
    context = {"form": form}
    return render(request, "Map_repertoire/index.html", context)


def help(request):
    """
    Function that manages displaying of help page
    """
    return render(request, "Map_repertoire/help.html")