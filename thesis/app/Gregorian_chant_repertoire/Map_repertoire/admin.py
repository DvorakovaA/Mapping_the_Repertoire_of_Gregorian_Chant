from django.contrib import admin

# Register your models here.

from .models import Feasts, Sources, Data_Chant, Geography

admin.site.register(Feasts)
admin.site.register(Sources)
admin.site.register(Data_Chant)
admin.site.register(Geography)