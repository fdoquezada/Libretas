from django.contrib import admin
from .models import Contacto

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ['nombre', 'email', 'asunto', 'creado_en', 'mensaje_corto']
    
    # Campos por los que se puede filtrar
    list_filter = ['creado_en']
    
    # Campos por los que se puede buscar
    search_fields = ['nombre', 'email', 'asunto', 'mensaje']
    
    # Campos de solo lectura (generalmente fechas)
    readonly_fields = ['creado_en']
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = [
        ('Información Personal', {
            'fields': ['nombre', 'email']
        }),
        ('Mensaje', {
            'fields': ['asunto', 'mensaje']
        }),
        ('Metadata', {
            'fields': ['creado_en'],
            'classes': ['collapse']  # Se puede colapsar
        })
    ]
    
    # Ordenamiento por defecto
    ordering = ['-creado_en']  # Más recientes primero
    
    # Paginación
    list_per_page = 20
    
    # Método personalizado para mostrar un extracto del mensaje
    def mensaje_corto(self, obj):
        """Muestra los primeros 50 caracteres del mensaje"""
        if len(obj.mensaje) > 50:
            return f"{obj.mensaje[:50]}..."
        return obj.mensaje
    mensaje_corto.short_description = 'Mensaje (extracto)'
    
    # Opcional: Deshabilitar la capacidad de agregar nuevos contactos desde el admin
    def has_add_permission(self, request):
        return False  # Los contactos solo se crean desde el formulario público
    
    # Opcional: Deshabilitar la edición desde el admin
    def has_change_permission(self, request, obj=None):
        return False  # Los contactos son de solo lectura
    
    # Opcional: Permitir eliminar contactos
    def has_delete_permission(self, request, obj=None):
        return True
