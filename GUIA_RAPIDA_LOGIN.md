# 🚀 Guía Rápida de Inicio - GesTC

## Credenciales de Prueba

### Usuario Administrador (Preconfigurado)
```
Usuario: admin
Contraseña: Administrador.2026
```

### Usuario de Prueba (Registrado durante Testing)
```
Usuario: juan_perez
Email: juan@gestc.com
Contraseña: Contraseña.Segura2026!
```

## Pasos para Ejecutar

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Aplicar Migraciones
```bash
python manage.py migrate
```

### 3. Crear Usuario Administrador (Opcional, si no existe)
```bash
python manage.py createsuperuser
```

### 4. Iniciar Servidor de Desarrollo
```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## Rutas Disponibles

| Ruta | Descripción | Autenticación Requerida |
|------|-------------|----------------------|
| `/` | Lista de empleados | ✅ Sí |
| `/login/` | Página de login | ❌ No |
| `/logout/` | Cerrar sesión (POST) | ✅ Sí |
| `/register/` | Registro de nuevo usuario | ❌ No |
| `/agregar/` | Agregar empleado | ✅ Sí |
| `/modificar/<id>/` | Modificar empleado | ✅ Sí |
| `/eliminar/<id>/` | Eliminar empleado | ✅ Sí |
| `/certificado/<id>/` | Agregar certificado | ✅ Sí |

## Flujo de Uso

### Primer Acceso (Sin Cuenta)
1. Ir a `http://127.0.0.1:8000/`
2. Serás redirigido a `/login/`
3. Click en "Regístrate aquí"
4. Completar formulario con:
   - Nombre de usuario (solo alfanuméricos, `-`, `_`)
   - Email válido
   - Contraseña fuerte (mínimo 12 caracteres, mayús, minús, número, símbolo)
5. Confirmar contraseña
6. Click en "Crear cuenta"

### Acceso Existe (Con Cuenta)
1. Ir a `http://127.0.0.1:8000/`
2. Ingresar usuario y contraseña
3. Click en "Iniciar sesión"
4. Acceso a todas las funciones

### Logout
1. Click en tu nombre en la esquina superior derecha
2. Click en "Cerrar sesión"
3. Serás redirigido a login

## Estructura de Base de Datos

En desarrollo utiliza **SQLite** (archivo `db.sqlite3`)
En producción debe configurarse **MySQL** vía variables de entorno

## Ambiente de Desarrollo vs Producción

### Desarrollo (Actual)
- `DEBUG = True`
- Base de datos: SQLite
- HTTPS: Deshabilitado
- Contraseñas hasheadas con: PBKDF2

### Producción (Configurar)
- `DEBUG = False`
- Base de datos: MySQL
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`

## Requisitos de Contraseña Fuerte

✅ Mínimo **12 caracteres**
✅ Al menos **1 mayúscula** (A-Z)
✅ Al menos **1 minúscula** (a-z)
✅ Al menos **1 número** (0-9)
✅ Al menos **1 símbolo** (!@#$%^&*()_+-=[]{};:'",./<>?/\|`~)

### Ejemplo de Contraseña Válida
```
MiContraseña.123!
SuperPass@2024
Seguridad#Admin99
```

## Troubleshooting

### "Nombre de usuario o contraseña incorrectos"
- Verifica que escribiste correctamente
- Recuerda que diferencia mayúsculas/minúsculas
- Si olvidaste, necesitarás resetear la contraseña

### "El nombre de usuario solo puede contener..."
- No uses puntos (`.`), espacios o caracteres especiales
- Usa solo: `a-z`, `A-Z`, `0-9`, `-`, `_`
- Mínimo 3 caracteres

### "Contraseña muy débil"
- Asegúrate de tener 12+ caracteres
- Incluye mayúscula, minúscula, número y símbolo
- Ejemplo: `Pass@2024Seguro`

### "Este usuario ya existe"
- Ese nombre de usuario fue registrado
- Intenta con otro nombre

## Variables de Entorno (Opcional)

En archivo `.env`:
```
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=sitio_web
DB_USER=admin
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=3306
```

## Más Información

Ver archivo: `DOCUMENTACION_AUTENTICACION.md`

---

¡Bienvenido a **GesTC**! 🎉
