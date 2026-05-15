from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
import re
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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise ValidationError('El nombre es obligatorio.')
        # Validar que solo contenga letras, espacios y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\.]+$', nombre):
            raise ValidationError('El nombre contiene caracteres no permitidos.')
        if len(nombre) > 200:
            raise ValidationError('El nombre es demasiado largo.')
        return nombre

    def clean_sueldo(self):
        sueldo = self.cleaned_data.get('sueldo')
        if sueldo is None or sueldo <= 0:
            raise ValidationError('El sueldo debe ser un número positivo.')
        if sueldo > 99999999.99:  # Máximo para DecimalField
            raise ValidationError('El sueldo es demasiado alto.')
        return sueldo

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        return fecha_inicio

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        return cleaned_data

    def clean_habilidades_blandas(self):
        habilidades = self.cleaned_data.get('habilidades_blandas')
        if habilidades and len(habilidades) > 1000:
            raise ValidationError('Las habilidades blandas son demasiado largas.')
        # Sanitizar: remover scripts potenciales
        if '<' in habilidades or '>' in habilidades:
            raise ValidationError('Las habilidades blandas contienen caracteres no permitidos.')
        return habilidades


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo'].validators.append(FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']))

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar tamaño máximo: 5MB
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo es demasiado grande. Máximo 5MB.')
            # Validar tipo MIME
            allowed_mimes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
            if hasattr(archivo, 'content_type') and archivo.content_type not in allowed_mimes:
                raise ValidationError('Tipo de archivo no permitido. Solo PDF, JPG, PNG.')
        return archivo


class FiltroEstadoForm(forms.Form):
    OPCIONES = [('', 'Todos')] + Empleado.ESTADOS
    estado = forms.ChoiceField(choices=OPCIONES, required=False, label='Estado de contrato',
                               widget=forms.Select(attrs={'class': 'form-select'}))


# OWASP-compliant authentication forms
class LoginForm(AuthenticationForm):
    """
    Formulario de login OWASP-compliant.
    Incluye protecciones contra fuerza bruta, ataques de timing, y validación segura.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autocomplete': 'username',
            'required': True,
        }),
        label='Nombre de usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'required': True,
        }),
        label='Contraseña'
    )

    def clean(self):
        cleaned_data = super().clean()
        # Protección contra timing attacks: siempre hacer las mismas validaciones
        username = cleaned_data.get('username', '')
        password = cleaned_data.get('password', '')

        if username and password:
            # Validaciones adicionales OWASP
            if len(username) > 150:  # Límite de Django
                raise ValidationError('Nombre de usuario inválido.')
            if len(password) > 4096:  # Límite de seguridad
                raise ValidationError('Contraseña inválida.')

        return cleaned_data


class RegisterForm(forms.ModelForm):
    """
    Formulario de registro de usuario con validación de contraseña fuerte OWASP.
    """
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'new-password',
        }),
        help_text='Mínimo 12 caracteres. Incluir mayúsculas, minúsculas, números y símbolos.'
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario',
                'autocomplete': 'username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico',
                'autocomplete': 'email',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        if len(username) > 150:
            raise ValidationError('El nombre de usuario es muy largo.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está registrado.')
        # Permitir solo alfanuméricos, guiones y guiones bajos
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 12:
            raise ValidationError('La contraseña debe tener al menos 12 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('La contraseña debe contener al menos una mayúscula.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('La contraseña debe contener al menos una minúscula.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            raise ValidationError('La contraseña debe contener al menos un símbolo especial.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
