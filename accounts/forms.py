# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

# Obtenemos el modelo de usuario activo (django.contrib.auth.models.User por defecto)
User = get_user_model() 

class CustomUserCreationForm(UserCreationForm):
    """
    Un formulario de creación de usuario que incluye el campo de email.
    """
    class Meta:
        # Hereda todos los campos de UserCreationForm (username, password, etc.)
        model = User 
        # Añadimos 'email' a los campos que se deben mostrar
        fields = ('username', 'email') 
        # Nota: Por defecto, Django marca el campo email como opcional. 
        # Si quieres que sea obligatorio, deberías sobreescribir el campo email:
        # email = forms.EmailField(required=True, label='Correo Electrónico')