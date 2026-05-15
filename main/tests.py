from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Empleado, Certificado
from .forms import EmpleadoForm, CertificadoForm


class EmpleadoModelTest(TestCase):
    def test_crear_empleado(self):
        empleado = Empleado.objects.create(
            nombre="Juan Pérez",
            sueldo=50000.00,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31",
            habilidades_blandas="Trabajo en equipo"
        )
        self.assertEqual(empleado.nombre, "Juan Pérez")
        self.assertEqual(str(empleado), "Juan Pérez")


class CertificadoModelTest(TestCase):
    def setUp(self):
        self.empleado = Empleado.objects.create(
            nombre="Ana García",
            sueldo=60000.00,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

    def test_crear_certificado(self):
        certificado = Certificado.objects.create(
            empleado=self.empleado,
            nombre="Certificado Python"
        )
        self.assertEqual(certificado.nombre, "Certificado Python")
        self.assertEqual(str(certificado), "Certificado Python — Ana García")


class EmpleadoFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'nombre': 'Carlos López',
            'sueldo': 45000.00,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
            'habilidades_blandas': 'Liderazgo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido_nombre_caracteres(self):
        form_data = {
            'nombre': 'Carlos123',
            'sueldo': 45000.00,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_form_invalido_sueldo_negativo(self):
        form_data = {
            'nombre': 'Carlos López',
            'sueldo': -1000.00,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('sueldo', form.errors)


class CertificadoFormTest(TestCase):
    def test_form_valido_con_archivo(self):
        archivo = SimpleUploadedFile("cert.pdf", b"contenido del archivo", content_type="application/pdf")
        form_data = {'nombre': 'Certificado Django'}
        form = CertificadoForm(data=form_data, files={'archivo': archivo})
        self.assertTrue(form.is_valid())

    def test_form_invalido_tipo_archivo(self):
        archivo = SimpleUploadedFile("cert.exe", b"contenido", content_type="application/octet-stream")
        form_data = {'nombre': 'Certificado'}
        form = CertificadoForm(data=form_data, files={'archivo': archivo})
        self.assertFalse(form.is_valid())
        self.assertIn('archivo', form.errors)
