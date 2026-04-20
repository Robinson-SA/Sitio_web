from django.contrib import admin
from .models import Empleado, Certificado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sueldo', 'estado_contrato', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado_contrato',)
    search_fields = ('nombre',)


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empleado')
