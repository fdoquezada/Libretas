from django.db import models
from django.contrib.auth.models import User
class Perfil(models.Model):
    BASE_CHOICES = [
        ('calle_larga', 'Spot Calle Larga'),
        ('lampa', 'Spot Lampa'),
    ]

    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('conductor', 'Conductor'),
        ('externo', 'Usuario externo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    base = models.CharField(max_length=50, choices=BASE_CHOICES)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

    conductor_relacionado = models.OneToOneField(
        'core.Conductor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_relacionado'
    )
    supervisor_relacionado = models.OneToOneField('core.Supervisor', on_delete=models.SET_NULL, null=True, blank=True)
