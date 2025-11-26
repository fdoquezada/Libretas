
from django.urls import path
from django.contrib.auth import views as auth_views
# Importamos nuestra clase custom
from .views import CustomLogoutView, SignupView

urlpatterns = [
    # Login: Usa la vista estándar con tu template
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    # Logout: Usa nuestra clase CustomLogoutView para añadir los mensajes
    path('logout/', CustomLogoutView.as_view(), name='logout'),


    # Registro: Usa la nueva clase SignupView que creamos
    path('registro/', SignupView.as_view(), name='signup'),
    
    # Registro (Error corregido: ELIMINADO hasta que se implemente correctamente)
    # path('registro/', TuRegistroView.as_view(), name='signup'),
]