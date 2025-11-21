from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('crear/', crear_entrega, name='crear_entrega'),
    path('entregas/<int:pk>/editar/', editar_entrega, name='editar_entrega'),

    path('conductores/', listar_conductores, name='listar_conductores'),
    path('conductores/nuevo/', crear_conductor, name='crear_conductor'),
    path('conductores/<int:pk>/editar/', editar_conductor, name='editar_conductor'),
    path('conductores/<int:pk>/eliminar/', eliminar_conductor, name='eliminar_conductor'),

    path('supervisores/', listar_supervisores, name='listar_supervisores'),
    path('supervisores/nuevo/', crear_supervisor, name='crear_supervisor'),
    path('supervisores/<int:pk>/editar/', editar_supervisor, name='editar_supervisor'),
    path('supervisores/<int:pk>/eliminar/', eliminar_supervisor, name='eliminar_supervisor'),

    path('periodos/', listar_periodos, name='listar_periodos'),
    path('periodos/nuevo/', crear_periodo, name='crear_periodo'),
    path('periodos/<int:pk>/editar/', editar_periodo, name='editar_periodo'),
    path('periodos/<int:pk>/eliminar/', eliminar_periodo, name='eliminar_periodo'),
]
