from django.db import models
from django.core.validators import FileExtensionValidator
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone
from django.conf import settings


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
    foto = models.ImageField(
        upload_to='fotos_empleados/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )

    def __str__(self):
        return self.nombre

    def get_foto_url(self):
        if not self.foto:
            return None
        blob_name = self.foto.name
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_ACCOUNT_NAME,
            container_name=settings.AZURE_CONTAINER,
            blob_name=blob_name,
            account_key=settings.AZURE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        return f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER}/{blob_name}?{sas_token}"

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['nombre']


class Certificado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='certificados')
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='certificados/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])

    def __str__(self):
        return f"{self.nombre} — {self.empleado.nombre}"

    def get_url(self):
        if not self.archivo:
            return None
        blob_name = self.archivo.name
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_ACCOUNT_NAME,
            container_name=settings.AZURE_CONTAINER,
            blob_name=blob_name,
            account_key=settings.AZURE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        return f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER}/{blob_name}?{sas_token}"

    def es_imagen(self):
        if not self.archivo:
            return False
        return self.archivo.name.lower().endswith(('.jpg', '.jpeg', '.png'))

    def es_pdf(self):
        if not self.archivo:
            return False
        return self.archivo.name.lower().endswith('.pdf')
