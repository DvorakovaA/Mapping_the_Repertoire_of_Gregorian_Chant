"""
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import InputForm


def index(request):
    '''
    '''
    #context = {}
    #if request.method == "POST":
    form = InputForm(request.POST or None)
    if form.is_valid():
        request.session['feast'] = form.cleaned_data['feast']
        return HttpResponseRedirect('', request)
    context = {"form": form}
    return render(request, "Map_repertoire/index.html", context)


def help(request):
    return render(request, "Map_repertoire/help.html")