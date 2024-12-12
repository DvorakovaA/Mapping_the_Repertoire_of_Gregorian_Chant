from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tool/", views.tool, name="tool"),
    path("help/", views.help, name="help"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("datasets/", views.datasets_view, name="datasets"),
    path("geography/", views.geography, name="geography")
]