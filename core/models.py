from django.db import models
from accounts.models import Perfil  # Si quieres vincular al usuario
from django.contrib.auth.models import User

class Supervisor(models.Model):
    nombre = models.CharField(max_length=100)
    base = models.CharField(max_length=50, choices=Perfil.BASE_CHOICES)

    def __str__(self):
        return f"{self.nombre} ({self.base})"

class Conductor(models.Model):
    nombre = models.CharField(max_length=150)
    base = models.CharField(max_length=50, choices=Perfil.BASE_CHOICES)
    perfil = models.OneToOneField(Perfil, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.base})"

class Periodo(models.Model):
    TRIMESTRE_CHOICES = [
        ('Q1', 'Enero-Marzo'),
        ('Q2', 'Abril-Junio'),
        ('Q3', 'Julio-Septiembre'),
        ('Q4', 'Octubre-Diciembre'),
    ]
    trimestre = models.CharField(max_length=2, choices=TRIMESTRE_CHOICES)
    año = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.get_trimestre_display()} {self.año}"

class Entrega(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('entregada', 'Entregada'),
        ('sin_entregar', 'Sin entregar'),
    ]

    FASE_CHOICES = [
        ('no_entregada', 'No entregada por el conductor'),
        ('en_firma', 'En firma del supervisor'),
        ('entregada', 'Entregada'),
        ('desvinculado', 'Desvinculado'),
        ('licencia', 'Licencia médica'),
    ]

    BASE_CHOICES = [
        ('calle_larga', 'Spot Calle Larga'),
        ('lampa', 'Spot Lampa'),
    ]

    numero_registro = models.PositiveIntegerField(unique=True, editable=False, blank=True)
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fase = models.CharField(max_length=20, choices=FASE_CHOICES)
    fecha_entrega = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    base = models.CharField(max_length=50, choices=BASE_CHOICES)  # NUEVO CAMPO

    def __str__(self):
        return f"{self.numero_registro} - {self.conductor.nombre} ({self.periodo})"

    def save(self, *args, **kwargs):
        if not self.numero_registro:
            ultimo = self.__class__.objects.aggregate(max_num=models.Max('numero_registro'))['max_num'] or 0
            self.numero_registro = ultimo + 1
        super().save(*args, **kwargs)