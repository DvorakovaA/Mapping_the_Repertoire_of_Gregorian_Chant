from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tool/", views.tool, name="tool"),
    path("help/", views.help, name="help")
]