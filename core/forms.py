from django import forms
from .models import Entrega, Conductor, Supervisor, Periodo


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
        }


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