from django.db import models
from django.contrib.auth.models import User
# Asegúrate de que esta importación sea correcta según la ubicación real de tu modelo Perfil
from accounts.models import Perfil 
# Aunque no está definido aquí, asumimos que BASE_CHOICES existe en Perfil

# --- MODELO SUPERVISOR ---
class Supervisor(models.Model):
    nombre = models.CharField(max_length=100)
    # Usa CharField con choices, es correcto según tu estructura
    base = models.CharField(max_length=50, choices=Perfil.BASE_CHOICES) 

    def __str__(self):
        return f"{self.nombre} ({self.base})"

# --- MODELO CONDUCTOR ---
class Conductor(models.Model):
    nombre = models.CharField(max_length=150)
    # Usa CharField con choices
    base = models.CharField(max_length=50, choices=Perfil.BASE_CHOICES)
    # Relación uno a uno con Perfil (la mantienes)
    perfil = models.OneToOneField(Perfil, on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):
        return f"{self.nombre} ({self.base})"
    
    def get_base_display(self):
        """Método para obtener el nombre legible de la base"""
        return dict(Perfil.BASE_CHOICES).get(self.base, self.base)      

# --- MODELO PERIODO ---
class Periodo(models.Model):
    TRIMESTRE_CHOICES = [
        ('Q1', 'Enero-Marzo'),
        ('Q2', 'Abril-Junio'),
        ('Q3', 'Julio-Septiembre'),
        ('Q4', 'Octubre-Diciembre'),
    ]
    trimestre = models.CharField(max_length=2, choices=TRIMESTRE_CHOICES)
    año = models.PositiveIntegerField()
    # Nota: El Periodo típicamente no necesita el campo 'base' si es global.
    # Si quieres filtrarlo por base, deberías añadir:
    # base = models.CharField(max_length=50, choices=Perfil.BASE_CHOICES, blank=True, null=True) 

    def __str__(self):
        return f"{self.get_trimestre_display()} {self.año}"

# --- MODELO ENTREGA ---
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

    # Mantienes BASE_CHOICES aquí, pero lo ideal es unificarlo con Perfil.BASE_CHOICES
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
    # Usas CharField con choices, es correcto para tu lógica de filtrado por base
    base = models.CharField(max_length=50, choices=BASE_CHOICES) 

    def __str__(self):
        return f"{self.numero_registro} - {self.conductor.nombre} ({self.periodo})"

    def save(self, *args, **kwargs):
        if not self.numero_registro:
            # Lógica para auto-incrementar el número de registro
            ultimo = self.__class__.objects.aggregate(max_num=models.Max('numero_registro'))['max_num'] or 0
            self.numero_registro = ultimo + 1
        super().save(*args, **kwargs)