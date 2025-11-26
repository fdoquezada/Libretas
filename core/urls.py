from django.urls import path
from .views import *

urlpatterns = [
    #DASHBOARD
    path('', inicio, name='inicio'),
    path('dashboard/', dashboard, name='dashboard'),
     #ENTREGAS
    path('crear/', crear_entrega, name='crear_entrega'),
    path('entregas/<int:pk>/editar/', editar_entrega, name='editar_entrega'),
    #CONDUCTORES
    path('conductores/', listar_conductores, name='listar_conductores'),
    path('conductores/nuevo/', crear_conductor, name='crear_conductor'),
    path('conductores/<int:pk>/editar/', editar_conductor, name='editar_conductor'),
    path('conductores/<int:pk>/eliminar/', eliminar_conductor, name='eliminar_conductor'),
    #SUPERVISORES
    path('supervisores/', listar_supervisores, name='listar_supervisores'),
    path('supervisores/nuevo/', crear_supervisor, name='crear_supervisor'),
    path('supervisores/<int:pk>/editar/', editar_supervisor, name='editar_supervisor'),
    path('supervisores/<int:pk>/eliminar/', eliminar_supervisor, name='eliminar_supervisor'),
    #PERIODOS
    path('periodos/', listar_periodos, name='listar_periodos'),
    path('periodos/nuevo/', crear_periodo, name='crear_periodo'),
    path('periodos/<int:pk>/editar/', editar_periodo, name='editar_periodo'),
    path('periodos/<int:pk>/eliminar/', eliminar_periodo, name='eliminar_periodo'),
    #EXPORTAR PERIODOS
    path('periodos/exportar/csv/', exportar_periodos_csv, name='exportar_periodos_csv'),
    path('periodos/exportar/excel/', exportar_periodos_xls, name='exportar_periodos_xls'),
    #EXPORTAR ENTREGAS
    path('entregas/exportar/csv/', exportar_entregas_csv, name='exportar_entregas_csv'),
    path('entregas/exportar/excel/', exportar_entregas_xls, name='exportar_entregas_xls'),

    #entregas edicion y eliminacion
    path('entregas/editar/<int:pk>/', editar_entrega, name='editar_entrega'),
    path('entregas/eliminar/<int:pk>/', eliminar_entrega, name='eliminar_entrega'),

    #CONDUCTORES carga masiva
    path('conductores/carga-masiva/', carga_masiva_conductores, name='carga_masiva_conductores'),
    path('conductores/descargar-plantilla/', descargar_plantilla_conductores, name='descargar_plantilla_conductores'),

]
