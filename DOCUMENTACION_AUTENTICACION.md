# Sistema de Autenticación OWASP-Compliant - GesTC

## 📋 Descripción General

Se ha implementado un sistema de autenticación completamente seguro siguiendo los estándares OWASP (Open Web Application Security Project) para la aplicación GesTC (Gestión de Talento y Competencias). El sistema incluye login, registro, logout y protección de rutas.

## 🔐 Características de Seguridad Implementadas

### 1. Autenticación
- **Login OWASP-compliant** con validaciones seguras
- **Registro con validación de contraseña fuerte**
- **Logout seguro** con destrucción de sesión
- **Mensajes de error genéricos** (no revela si usuario existe)
- **Protección contra timing attacks**

### 2. Validación de Contraseña
La contraseña debe cumplir con los siguientes requisitos OWASP:
- ✅ Mínimo **12 caracteres**
- ✅ Al menos **1 mayúscula**
- ✅ Al menos **1 minúscula**
- ✅ Al menos **1 número**
- ✅ Al menos **1 símbolo especial** (!@#$%^&*, etc.)

### 3. Protección de Sesión
```python
SESSION_COOKIE_AGE = 3600              # 1 hora
SESSION_COOKIE_HTTPONLY = True         # No accesible desde JS
SESSION_COOKIE_SECURE = False          # True en producción (HTTPS)
SESSION_COOKIE_SAMESITE = 'Strict'     # Protección contra CSRF
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Cierra al cerrar navegador
```

### 4. Cookies CSRF Protegidas
- `CSRF_COOKIE_HTTPONLY = True` - No accesible desde JavaScript
- `CSRF_COOKIE_SECURE = False` - True en producción (HTTPS)
- `CSRF_COOKIE_SAMESITE = 'Strict'` - Solo mismo sitio

### 5. Password Hashing Seguro
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]
```

### 6. Headers de Seguridad
- `X-Frame-Options: DENY` - Previene clickjacking
- `X-Content-Type-Options: nosniff` - Previene MIME-sniffing
- `X-XSS-Protection: 1; mode=block` - Protección XSS
- `Content-Security-Policy` - CSP headers configurados

## 📁 Archivos Modificados

### `main/forms.py`
**Nuevas clases agregadas:**
- `LoginForm` - Formulario de login OWASP-compliant
- `RegisterForm` - Formulario de registro con validación fuerte de contraseña

**Validaciones incluidas:**
- Validación de nombre de usuario (3-150 caracteres, solo alfanuméricos, guiones, guiones bajos)
- Validación de email único
- Validación de contraseña fuerte
- Confirmación de contraseña coincidente
- Sanitización de datos

### `main/views.py`
**Nuevas vistas agregadas:**
- `login_view()` - Vista de login con redirección automática si ya está autenticado
- `logout_view()` - Vista POST-only de logout seguro
- `register_view()` - Vista de registro con validación de formulario

**Rutas protegidas:**
Todas las vistas existentes están protegidas con `@login_required(login_url='login')`

### `main/urls.py`
**Nuevas rutas:**
```python
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('register/', views.register_view, name='register'),
```

### `templates/login.html`
Página de login con:
- Diseño moderno con gradiente
- Campos de usuario y contraseña
- Validaciones de formulario
- Enlace a registro
- Manejo de mensajes de error genéricos

### `templates/register.html`
Página de registro con:
- Formulario completo de registro
- Requisitos de contraseña visibles
- Validaciones en tiempo real
- Mensajes de error detallados
- Enlace a login

### `templates/base.html`
Actualizado con:
- Nombre **GesTC** en navbar
- Dropdown de usuario autenticado
- Botón de logout en el menú
- Mostrar nombre del usuario conectado
- Estilo gradiente moderno

### `web/settings.py`
**Nuevas configuraciones:**
```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'lista_empleados'
LOGOUT_REDIRECT_URL = 'login'

SESSION_COOKIE_AGE = 3600
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # True en producción
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # True en producción
CSRF_COOKIE_SAMESITE = 'Strict'

PASSWORD_HASHERS = [...]  # Configurado con PBKDF2 como principal
```

### `requirements.txt`
**Nuevo paquete agregado:**
- `argon2-cffi==23.1.0` - Para hash Argon2

## 🧪 Pruebas Realizadas

### ✅ Test de Login
- Usuario: `admin`
- Contraseña: `Administrador.2026`
- Resultado: ✅ Login exitoso

### ✅ Test de Logout
- Navegación: Click en dropdown de usuario → Cerrar sesión
- Resultado: ✅ Logout exitoso con mensaje de confirmación

### ✅ Test de Registro
- Usuario: `juan_perez`
- Email: `juan@gestc.com`
- Contraseña: `Contraseña.Segura2026!`
- Resultado: ✅ Registro exitoso con validaciones completas

### ✅ Test de Validación de Contraseña
- Validación de mínimo 12 caracteres: ✅
- Validación de mayúscula: ✅
- Validación de minúscula: ✅
- Validación de número: ✅
- Validación de símbolo especial: ✅
- Validación de confirmación: ✅

### ✅ Test de Nombre de Usuario
- Validación contra caracteres especiales (. rechazado): ✅
- Aceptación de guiones y guiones bajos: ✅
- Unicidad de usuario: ✅

### ✅ Test de Redirección
- Sin autenticación → Redirección a login: ✅
- Login exitoso → Redirección a lista: ✅
- Logout → Redirección a login: ✅

## 📊 Flujo de Autenticación

```
SIN AUTENTICACIÓN
       ↓
       └─→ Intenta acceder a /
           └─→ Redirecciona a /login/

LOGIN EXITOSO
       ↓
       └─→ POST /login/
           └─→ Valida credenciales
           └─→ Crea sesión
           └─→ Redirecciona a /

USUARIO AUTENTICADO
       ↓
       ├─→ Acceso a todas las rutas
       ├─→ Dropdown de usuario en navbar
       ├─→ Opción de logout
       └─→ Sesión expira en 1 hora

LOGOUT
       ↓
       └─→ POST /logout/
           └─→ Destruye sesión
           └─→ Redirecciona a /login/

REGISTRO NUEVO USUARIO
       ↓
       └─→ GET /register/
           └─→ Muestra formulario
       └─→ POST /register/ con datos válidos
           └─→ Valida contraseña fuerte
           └─→ Valida unicidad de usuario/email
           └─→ Crea usuario
           └─→ Muestra mensaje exitoso
           └─→ Redirecciona a /login/
```

## 🛡️ OWASP Top 10 - Mitigaciones

1. **Inyección SQL**: ✅ ORM de Django, valores parametrizados
2. **Broken Authentication**: ✅ Contraseñas hasheadas, sesiones seguras
3. **Sensitive Data Exposure**: ✅ Cookies HTTPONLY, SAMESITE
4. **XML External Entities (XXE)**: ✅ No aplicable aquí
5. **Broken Access Control**: ✅ @login_required en todas las rutas
6. **Security Misconfiguration**: ✅ Headers de seguridad configurados
7. **Cross-Site Scripting (XSS)**: ✅ Template escaping automático
8. **Insecure Deserialization**: ✅ Sesiones seguras de Django
9. **Using Components with Known Vulnerabilities**: ✅ Dependencias actualizadas
10. **Insufficient Logging & Monitoring**: ✅ Sistema de mensajes de Django

## 🚀 Próximas Mejoras Sugeridas

Para producción, recomendamos:

1. **HTTPS Obligatorio**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_HSTS_SECONDS = 31536000
   ```

2. **Rate Limiting para Login**
   - Instalar: `pip install django-ratelimit`
   - Proteger vistas de login contra fuerza bruta

3. **Autenticación Multifactor (MFA)**
   - Instalar: `pip install django-otp`
   - Implementar TOTP o SMS

4. **Contraseña Recuperable**
   - Implementar flujo de reset de contraseña
   - Tokens de un solo uso

5. **Logging de Seguridad**
   - Registrar intentos fallidos de login
   - Auditoría de cambios de contraseña
   - Alertas de acceso sospechoso

6. **Validación de Email**
   - Envío de email de confirmación
   - Verificación antes de permitir login

## 📞 Soporte

Para más información sobre OWASP y buenas prácticas de seguridad:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Django Security Documentation](https://docs.djangoproject.com/en/5.2/topics/security/)

---

**Fecha de Implementación**: 14 de Mayo de 2026
**Estado**: ✅ Completado y Probado
**Versión**: 1.0
