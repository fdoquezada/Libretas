from django.contrib.auth.views import LogoutView
from django.contrib import messages
# --- NUEVAS IMPORTACIONES ---
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

# Heredamos de la vista estándar de Django
class CustomLogoutView(LogoutView):
    next_page = 'inicio'
    # Sobreescribimos el método post para añadir el mensaje antes de redirigir
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'Sesión cerrada correctamente.')
        return response
        
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# --- VISTA DE REGISTRO FALTANTE ---
class SignupView(CreateView):
    """
    Vista genérica para crear un nuevo usuario (registro).
    """
    # Usamos el formulario personalizado que incluye el campo 'email'.
    form_class = CustomUserCreationForm 
    
    # URL a la que redirigir después de un registro exitoso.
    success_url = reverse_lazy('login')  
    
    # Template que renderizará el formulario.
    template_name = 'accounts/registro.html'


