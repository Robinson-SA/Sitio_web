from django import forms
from .models import Empleado, Certificado


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'sueldo', 'fecha_inicio', 'fecha_fin', 'habilidades_blandas']
        labels = {
            'nombre': 'Nombre',
            'sueldo': 'Sueldo',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'habilidades_blandas': 'Habilidades blandas',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
            }),
            'sueldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sueldo',
                'step': '0.01',
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'habilidades_blandas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Habilidades blandas',
                'rows': 3,
            }),
        }


class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ['nombre', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del certificado',
            }),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FiltroEstadoForm(forms.Form):
    OPCIONES = [('', 'Todos')] + Empleado.ESTADOS
    estado = forms.ChoiceField(choices=OPCIONES, required=False, label='Estado de contrato',
                               widget=forms.Select(attrs={'class': 'form-select'}))
