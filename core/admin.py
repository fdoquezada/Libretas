from django.contrib import admin
from .models import Supervisor, Conductor, Periodo, Entrega

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'base', 'get_base_display']
    list_filter = ['base']
    search_fields = ['nombre']
    list_per_page = 20
    
    def get_base_display(self, obj):
        return obj.get_base_display()
    get_base_display.short_description = 'Base'

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'base', 'get_base_display', 'perfil', 'tiene_perfil']
    list_filter = ['base']
    search_fields = ['nombre', 'perfil__user__username']
    # ELIMINA readonly_fields ya que Conductor no tiene 'creado_en'
    list_per_page = 20
    
    def get_base_display(self, obj):
        return obj.get_base_display()
    get_base_display.short_description = 'Base'
    
    def tiene_perfil(self, obj):
        return obj.perfil is not None
    tiene_perfil.boolean = True
    tiene_perfil.short_description = 'Tiene Perfil'

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ['trimestre', 'año', 'get_trimestre_display', 'periodo_completo']
    list_filter = ['año', 'trimestre']
    search_fields = ['año']
    ordering = ['-año', 'trimestre']
    list_per_page = 20
    
    def periodo_completo(self, obj):
        return str(obj)
    periodo_completo.short_description = 'Periodo'

@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = [
        'numero_registro', 
        'conductor', 
        'supervisor', 
        'estado', 
        'fase', 
        'periodo',
        'base',
        'fecha_entrega'
    ]
    list_filter = [
        'estado', 
        'fase', 
        'base', 
        'periodo',
        'fecha_entrega'
    ]
    search_fields = [
        'numero_registro',
        'conductor__nombre',
        'supervisor__nombre',
        'notas'
    ]
    readonly_fields = ['numero_registro']  # Este SÍ existe en Entrega
    list_select_related = ['conductor', 'supervisor', 'periodo']
    list_per_page = 25
    
    fieldsets = [
        ('Información Principal', {
            'fields': [
                'numero_registro',
                'conductor', 
                'supervisor', 
                'periodo',
                'base'
            ]
        }),
        ('Estado y Fase', {
            'fields': [
                'estado',
                'fase'
            ]
        }),
        ('Fechas y Observaciones', {
            'fields': [
                'fecha_entrega',
                'notas'
            ]
        })
    ]
    
    def get_estado_display(self, obj):
        return obj.get_estado_display()
    get_estado_display.short_description = 'Estado'
    
    def get_fase_display(self, obj):
        return obj.get_fase_display()
    get_fase_display.short_description = 'Fase'
