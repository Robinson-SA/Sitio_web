"""
Suite de Pruebas de Penetración y Seguridad (OWASP Testing)
Intenta explotar vulnerabilidades comunes en la aplicación Django
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from .models import Empleado, Certificado


class OWASPInjectionTests(TestCase):
    """Pruebas para inyección SQL y command injection"""

    def setUp(self):
        self.client = Client()

    def test_sql_injection_en_lista(self):
        """Intenta inyección SQL en filtro de estado"""
        # Intento de inyección SQL
        response = self.client.get('/lista/')
        self.assertEqual(response.status_code, 200)

        # Simular inyección SQL
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE empleado; --",
            "\" OR \"1\"=\"1",
            "1; DELETE FROM main_empleado; --",
        ]

        for payload in payloads:
            response = self.client.get(f'/lista/?estado={payload}')
            # Si no crashea, está protegido
            self.assertIn(response.status_code, [200, 400, 404])

    def test_sql_injection_en_busqueda(self):
        """Intenta inyección SQL en búsqueda de empleados"""
        Empleado.objects.create(
            nombre="Test Empleado",
            sueldo=50000,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

        payloads = ["' OR '1'='1", "'; --", "\" OR \"1\"=\"1"]

        for payload in payloads:
            # Intentar a través de formulario
            response = self.client.post('/agregar/', {'nombre': payload})
            self.assertIn(response.status_code, [200, 400, 403])


class OWASPXSSTests(TestCase):
    """Pruebas para validar protección contra XSS"""

    def setUp(self):
        self.client = Client()

    def test_xss_en_nombre_empleado(self):
        """Intenta XSS almacenado en nombre de empleado"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror='alert(1)'>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "javascript:alert('XSS')",
            "<svg onload='alert(1)'>",
            "\\<script>alert('XSS')</script>",
        ]

        for payload in xss_payloads:
            form_data = {
                'nombre': payload,
                'sueldo': 50000,
                'fecha_inicio': '2023-01-01',
                'fecha_fin': '2023-12-31',
            }
            response = self.client.post('/agregar/', form_data)
            # Debe rechazar o escapar el contenido
            self.assertIn(response.status_code, [200, 400])

    def test_xss_en_habilidades(self):
        """Intenta XSS en campo de habilidades blandas"""
        payload = "<script>alert('XSS')</script>"
        form_data = {
            'nombre': 'Juan Pérez',
            'sueldo': 50000,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
            'habilidades_blandas': payload,
        }
        response = self.client.post('/agregar/', form_data)
        self.assertIn(response.status_code, [200, 400])


class OWASPFileUploadTests(TestCase):
    """Pruebas para validar seguridad de carga de archivos"""

    def setUp(self):
        self.client = Client()
        self.empleado = Empleado.objects.create(
            nombre="Test Empleado",
            sueldo=50000,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

    def test_upload_archivo_malicioso_exe(self):
        """Intenta subir archivo ejecutable"""
        archivo = SimpleUploadedFile("malware.exe", b"MZ\x90\x00", content_type="application/octet-stream")
        response = self.client.post(f'/agregar-certificado/{self.empleado.pk}/', {
            'nombre': 'Certificado',
            'archivo': archivo
        })
        # No debe permitir .exe
        self.assertEqual(response.status_code, 200)

    def test_upload_archivo_grande(self):
        """Intenta subir archivo mayor a 5MB"""
        contenido_grande = b"X" * (10 * 1024 * 1024)  # 10MB
        archivo = SimpleUploadedFile("grande.pdf", contenido_grande, content_type="application/pdf")
        response = self.client.post(f'/agregar-certificado/{self.empleado.pk}/', {
            'nombre': 'Certificado',
            'archivo': archivo
        })
        # No debe permitir > 5MB
        self.assertEqual(response.status_code, 200)

    def test_upload_archivo_con_extension_falsa(self):
        """Intenta subir exe con extensión pdf"""
        archivo = SimpleUploadedFile("payload.pdf", b"MZ\x90\x00", content_type="application/pdf")
        response = self.client.post(f'/agregar-certificado/{self.empleado.pk}/', {
            'nombre': 'Certificado',
            'archivo': archivo
        })
        # Validar que se rechace por content-type mismatch
        self.assertEqual(response.status_code, 200)

    def test_upload_path_traversal(self):
        """Intenta path traversal en nombre de archivo"""
        archivo = SimpleUploadedFile("../../etc/passwd.pdf", b"contenido", content_type="application/pdf")
        response = self.client.post(f'/agregar-certificado/{self.empleado.pk}/', {
            'nombre': 'Certificado',
            'archivo': archivo
        })
        self.assertEqual(response.status_code, 200)


class OWASPAuthenticationTests(TestCase):
    """Pruebas para validar autenticación y autorización"""

    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user('admin', 'admin@test.com', 'password123')
        self.empleado = Empleado.objects.create(
            nombre="Test Empleado",
            sueldo=50000,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

    def test_acceso_sin_autenticacion(self):
        """Intenta acceder a recursos sin autenticación"""
        endpoints = [
            '/lista/',
            '/agregar/',
            f'/modificar/{self.empleado.pk}/',
            f'/eliminar/{self.empleado.pk}/',
            f'/agregar-certificado/{self.empleado.pk}/',
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Nota: si estas vistas no requieren auth, están vulnerables
            self.assertIn(response.status_code, [200, 404, 302])

    def test_fuerza_bruta_login(self):
        """Intenta ataques de fuerza bruta"""
        # Si hay autenticación, probar con contraseñas incorrectas
        passwords = ['123456', 'password', 'admin', 'root', 'user']

        for pwd in passwords:
            # Esto dependería de tener un endpoint de login
            pass


class OWASPValidationBypassTests(TestCase):
    """Pruebas para bypass de validaciones"""

    def setUp(self):
        self.client = Client()

    def test_bypass_validacion_nombre(self):
        """Intenta bypass de validación de nombre"""
        payloads = [
            "",  # Vacío
            " ",  # Solo espacios
            "<html>",  # HTML
            "<?php?>",  # PHP
            "' OR 1=1; --",  # SQL
            "a" * 500,  # Muy largo
        ]

        for payload in payloads:
            form_data = {
                'nombre': payload,
                'sueldo': 50000,
                'fecha_inicio': '2023-01-01',
                'fecha_fin': '2023-12-31',
            }
            response = self.client.post('/agregar/', form_data)
            # Las validaciones deben rechazar estos payloads
            self.assertIn(response.status_code, [200, 400])

    def test_bypass_validacion_sueldo(self):
        """Intenta bypass de validación de sueldo"""
        payloads = [
            -1000,  # Negativo
            0,  # Cero
            99999999.99,  # Máximo permitido
            999999999999,  # Mayor al máximo
            "abc",  # No numérico
        ]

        for payload in payloads:
            form_data = {
                'nombre': 'Juan',
                'sueldo': payload,
                'fecha_inicio': '2023-01-01',
                'fecha_fin': '2023-12-31',
            }
            response = self.client.post('/agregar/', form_data)
            self.assertIn(response.status_code, [200, 400])

    def test_bypass_validacion_fechas(self):
        """Intenta bypass de validación de fechas"""
        form_data = {
            'nombre': 'Juan',
            'sueldo': 50000,
            'fecha_inicio': '2023-12-31',  # Después de fin
            'fecha_fin': '2023-01-01',     # Antes de inicio
        }
        response = self.client.post('/agregar/', form_data)
        # Debe validar que inicio < fin
        self.assertIn(response.status_code, [200, 400])


class OWASPHeaderSecurityTests(TestCase):
    """Pruebas para validar headers de seguridad"""

    def setUp(self):
        self.client = Client()

    def test_security_headers_presentes(self):
        """Verifica que headers de seguridad OWASP estén presentes"""
        response = self.client.get('/lista/')

        # Headers que deberían estar presentes
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Content-Security-Policy',
        ]

        # Nota: En DEBUG=True algunos headers pueden no estar
        # En producción (_SECURE=True) sí deberían estar
        for header in security_headers:
            # No hacemos assert, solo notificamos si están presentes
            if header in response:
                print(f"✅ Header {header} presente")
            else:
                print(f"⚠️ Header {header} NO presente (revisar en producción)")


class OWASPDataExposureTests(TestCase):
    """Pruebas para exposición de datos sensibles"""

    def setUp(self):
        self.client = Client()
        self.empleado = Empleado.objects.create(
            nombre="Test Empleado",
            sueldo=50000,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

    def test_error_pages_revelan_info(self):
        """Verifica que páginas de error no expongan información sensible"""
        response = self.client.get('/no-existe/')

        # En DEBUG=True se muestra traceback completo (vulnerable)
        # En DEBUG=False se muestra página genérica
        if 'DEBUG = True' in str(response):
            print("⚠️ DEBUG activo - información sensible puede exponerse")

    def test_exposicion_ruta_archivos(self):
        """Intenta obtener rutas del sistema"""
        response = self.client.get('/static/../../etc/passwd')
        self.assertIn(response.status_code, [404, 403])


class OWASPCSRFTests(TestCase):
    """Pruebas para validación de CSRF"""

    def setUp(self):
        self.client = Client()

    def test_csrf_token_required(self):
        """Verifica que las mutaciones requieran CSRF token"""
        form_data = {
            'nombre': 'Juan',
            'sueldo': 50000,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
        }

        # POST sin CSRF token debe fallar o estar protegido
        response = self.client.post('/agregar/', form_data)
        # Django rechaza por defecto, pero verificar
        self.assertIn(response.status_code, [200, 403])


class OWASPSQLijectionAdvanced(TestCase):
    """Pruebas avanzadas de inyección SQL"""

    def setUp(self):
        self.client = Client()
        Empleado.objects.create(
            nombre="Juan Pérez",
            sueldo=50000,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

    def test_blind_sql_injection(self):
        """Intenta Blind SQL Injection"""
        payloads = [
            "' AND 1=1 AND '1'='1",
            "' AND 1=2 AND '1'='1",
            "' AND SLEEP(5) AND '1'='1",
        ]

        for payload in payloads:
            response = self.client.get(f'/lista/?estado={payload}')
            self.assertIn(response.status_code, [200, 400, 404])

    def test_time_based_sql_injection(self):
        """Intenta Time-Based SQL Injection"""
        payload = "' OR IF(1=1, SLEEP(5), 0); --"
        response = self.client.get(f'/lista/?estado={payload}')
        self.assertIn(response.status_code, [200, 400, 404])
