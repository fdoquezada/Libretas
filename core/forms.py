from django import forms
from .models import *
import pandas as pd
import os



class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = [
            'conductor',
            'estado',
            'supervisor',
            'fase',
            'fecha_entrega',
            'notas',
            'periodo'
        ]
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

class EntregaEstadoForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = [
            'estado',
            'fase',
            'fecha_entrega',
            'notas',
        ]
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }


class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['nombre', 'base', 'perfil']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'base': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        
        # FILTRAR EL CAMPO 'PERFIL'
        if 'perfil' in self.fields and user_profile:
            base_del_usuario = user_profile.base
            self.fields['perfil'].queryset = Perfil.objects.filter(base=base_del_usuario)
        
        # Controlar la visibilidad del campo base según permisos
        if user_profile:
            # Si el usuario tiene un perfil específico, limitar las opciones de base
            # o mostrar solo su base dependiendo de tus reglas de negocio
            
            # Opción A: Mostrar todas las bases pero solo para usuarios con permisos
            # Opción B: Mostrar solo la base del usuario (más restrictivo)
            
            # Ejemplo: Mostrar solo la base del usuario en edición
            if self.instance.pk:  # Edición
                self.fields['base'].queryset = Conductor.objects.filter(
                    base=user_profile.base
                ).values_list('base', 'base').distinct()
            else:  # Creación
                self.instance.base = user_profile.base
                self.fields['base'].initial = user_profile.base

class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ['nombre', 'base']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
        }


class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['trimestre', 'año']
        widgets = {
            'año': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
        }


class CargaMasivaConductoresForm(forms.Form):
    archivo_excel = forms.FileField(
        label='Seleccionar archivo Excel',
        help_text='Formatos soportados: .xlsx, .xls',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )
    
    def clean_archivo_excel(self):
        archivo = self.cleaned_data['archivo_excel']
        
        # Validar extensión
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in ['.xlsx', '.xls']:
            raise forms.ValidationError('Solo se permiten archivos Excel (.xlsx, .xls)')
        
        # Validar tamaño (max 5MB)
        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError('El archivo no puede ser mayor a 5MB')
        
        return archivo        