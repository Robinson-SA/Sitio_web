from django.db import models


class Empleado(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('finiquitado', 'Finiquitado'),
        ('renovado', 'Renovado'),
    ]
    nombre = models.CharField(max_length=200)
    sueldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    habilidades_blandas = models.TextField(blank=True)
    estado_contrato = models.CharField(max_length=20, choices=ESTADOS, default='activo')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['nombre']


class Certificado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='certificados')
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='certificados/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} — {self.empleado.nombre}"
