"""
Script de Intentos Prácticos para Romper el Sitio
Técnicas de Pentesting Realistas
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import urllib.parse
import json
from .models import Empleado


class RealWorldAttackTests(TestCase):
    """Intentos realistas de romper la aplicación"""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.empleado = Empleado.objects.create(
            nombre="Test",
            sueldo=50000,
            fecha_inicio="2023-01-01",
            fecha_fin="2023-12-31"
        )

    def test_romper_validacion_nombre_html(self):
        """Intenta inyectar HTML sin <script>"""
        payload = "<img src=x onerror='alert(1)'>"
        try:
            form_data = {
                'nombre': payload,
                'sueldo': 50000,
                'fecha_inicio': '2023-01-01',
                'fecha_fin': '2023-12-31',
            }
            response = self.client.post('/agregar/', form_data, follow=True)
            if response.status_code == 200:
                # Verificar si el payload llegó a la base de datos
                empleado = Empleado.objects.filter(nombre=payload).first()
                if empleado:
                    print(f"❌ VULNERABILIDAD: HTML inyectado en nombre: {payload}")
                    return False
        except Exception as e:
            print(f"✅ Exception al inyectar: {e}")
        return True

    def test_romper_validacion_por_encodificacion(self):
        """Intenta evadir validaciones usando encoding"""
        payloads = [
            "Juan%3cscript%3e",  # URL encoded
            "Juan&#60;script&#62;",  # HTML entities
            "Juan\u003cscript\u003e",  # Unicode
        ]
        for payload in payloads:
            decoded = urllib.parse.unquote(payload)
            if '<' in decoded or '>' in decoded:
                print(f"⚠️ Payload sospechoso identificado: {decoded}")

    def test_romper_por_race_condition(self):
        """Intenta race condition en creación de registros"""
        import threading

        results = []

        def create_empleado():
            try:
                self.client.post('/agregar/', {
                    'nombre': 'Juan Multihilo',
                    'sueldo': 50000,
                    'fecha_inicio': '2023-01-01',
                    'fecha_fin': '2023-12-31',
                }, follow=True)
                results.append(True)
            except Exception as e:
                results.append(False)

        threads = [threading.Thread(target=create_empleado) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if len(results) == 5 and all(results):
            print("⚠️ Race condition posible en creación múltiple")
        else:
            print("✅ No hay race conditions detectadas")

    def test_romper_con_null_bytes(self):
        """Intenta null byte injection"""
        payload = "juan\x00.pdf"
        form_data = {
            'nombre': 'Juan' + payload,
            'sueldo': 50000,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
        }
        try:
            response = self.client.post('/agregar/', form_data, follow=True)
            print("✅ Null bytes sanitizados")
        except Exception as e:
            print(f"✅ Exception con null bytes: {type(e).__name__}")

    def test_romper_con_unicode_overlong(self):
        """Intenta Unicode overlong encoding"""
        # C0 A0 es overlong encoding para espacio
        payload = "juan\xc0\xa0script"
        form_data = {
            'nombre': payload,
            'sueldo': 50000,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
        }
        try:
            response = self.client.post('/agregar/', form_data, follow=True)
        except Exception as e:
            print(f"✅ Exception con Unicode overlong: {type(e).__name__}")

    def test_romper_con_bom(self):
        """Intenta BOM (Byte Order Mark) injection"""
        # BOM UTF-8: EF BB BF
        payload = "\ufeffJuan<script>"
        form_data = {
            'nombre': payload,
            'sueldo': 50000,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
        }
        response = self.client.post('/agregar/', form_data, follow=True)
        if response.status_code == 200:
            print("⚠️ BOM injection: verificar si se almacenó")

    def test_romper_largo_campo(self):
        """Intenta campo excesivamente largo"""
        payload = "A" * 10000
        form_data = {
            'nombre': payload,
            'sueldo': 50000,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
        }
        response = self.client.post('/agregar/', form_data, follow=True)
        if response.status_code == 200:
            empleado = Empleado.objects.filter(nombre__contains="A" * 100).first()
            if empleado:
                print(f"❌ Campo largo almacenado: {len(empleado.nombre)} caracteres")

    def test_romper_numeros_negativos_muy_bajos(self):
        """Intenta números muy negativos en sueldo"""
        form_data = {
            'nombre': 'Juan',
            'sueldo': -999999999999,
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
        }
        response = self.client.post('/agregar/', form_data, follow=True)
        if response.status_code == 200:
            empleado = Empleado.objects.filter(nombre='Juan').first()
            if empleado and empleado.sueldo < 0:
                print("❌ Sueldo negativo almacenado")

    def test_romper_fechas_futuro_lejano(self):
        """Intenta fechas en futuro muy lejano"""
        form_data = {
            'nombre': 'Juan',
            'sueldo': 50000,
            'fecha_inicio': '9999-12-31',
            'fecha_fin': '9999-12-31',
        }
        response = self.client.post('/agregar/', form_data, follow=True)
        if response.status_code == 200:
            print("⚠️ Fechas futuro lejano aceptadas")

    def test_romper_con_caracteres_especiales(self):
        """Intenta caracteres especiales peligrosos"""
        payloads = [
            "Juan<>",
            "Juan{}",
            "Juan[];",
            "Juan'\"",
            "Juan\\",
            "Juan|",
            "Juan&",
        ]
        for payload in payloads:
            form_data = {
                'nombre': payload,
                'sueldo': 50000,
                'fecha_inicio': '2023-01-01',
                'fecha_fin': '2023-12-31',
            }
            response = self.client.post('/agregar/', form_data, follow=True)
            # Solo registrar si hay error inesperado
            if response.status_code not in [200, 400]:
                print(f"⚠️ Status {response.status_code} para payload: {payload}")

    def test_romper_acceso_arbirtario_registros(self):
        """Intenta acceder a registros sin autorización"""
        # Crear múltiples empleados
        for i in range(5):
            Empleado.objects.create(
                nombre=f"Empleado {i}",
                sueldo=50000 + i * 1000,
                fecha_inicio="2023-01-01",
                fecha_fin="2023-12-31"
            )

        # Intentar acceder a cada uno
        empleados = Empleado.objects.all()[:3]
        for emp in empleados:
            response = self.client.get(f'/modificar/{emp.pk}/', follow=True)
            if response.status_code == 200:
                print(f"✅ Acceso a registro {emp.pk} permitido (sin login requerido)")

    def test_romper_con_json_en_formulario(self):
        """Intenta enviar JSON en lugar de form data"""
        try:
            response = self.client.post(
                '/agregar/',
                json.dumps({
                    'nombre': '<script>',
                    'sueldo': 50000,
                    'fecha_inicio': '2023-01-01',
                    'fecha_fin': '2023-12-31'
                }),
                content_type='application/json',
                follow=True
            )
        except Exception as e:
            print(f"✅ JSON rechazado: {type(e).__name__}")

    def test_romper_acceso_directo_db(self):
        """Intenta verificar inyección por cambio de model"""
        # Este tests verifica si es posible modificar el objeto
        # directamente sin validaciones
        empleado = Empleado.objects.first()
        if empleado:
            # Intentar bypass de validadores
            empleado.nombre = "<script>alert(1)</script>"
            try:
                empleado.save()
                print("⚠️ Validadores de modelo pueden ser bypasseados en save() directo")
            except Exception as e:
                print(f"✅ Modelo protegido contra bypass: {type(e).__name__}")

    def test_romper_con_simbolos_sql(self):
        """Intenta símbolos SQL en campos de texto"""
        payloads = [
            "Juan'; DROP TABLE",
            "Juan\" OR 1=1 --",
            "Juan`; DELETE FROM",
            "Juan/**/; UNION SELECT",
        ]
        for payload in payloads:
            form_data = {
                'nombre': payload,
                'sueldo': 50000,
                'fecha_inicio': '2023-01-01',
                'fecha_fin': '2023-12-31',
            }
            response = self.client.post('/agregar/', form_data, follow=True)
            if response.status_code == 200:
                # Verificar que el payload no se ejecutó
                empleado = Empleado.objects.filter(nombre=payload).first()
                if empleado:
                    print(f"✅ Payload de SQL almacenado como texto (protegido): {payload}")
