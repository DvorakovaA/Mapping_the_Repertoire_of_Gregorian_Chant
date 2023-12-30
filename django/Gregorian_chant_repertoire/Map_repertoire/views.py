from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, "Map_repertoire/index.html")


def help(request):
    return render(request, "Map_repertoire/help.html")