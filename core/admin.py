
from django.contrib import admin
from .models import Entrega, Supervisor, Conductor, Periodo

admin.site.register(Entrega)
admin.site.register(Supervisor)
admin.site.register(Conductor)
admin.site.register(Periodo)