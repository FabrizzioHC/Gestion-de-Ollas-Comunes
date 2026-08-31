# Red Comunitaria - Sistema de Distribución Equitativa de Recursos

Una plataforma web que conecta donadores con ollas comunes para asegurar que los recursos lleguen a quienes más los necesitan.

## 🎯 Características Principales

- **Autenticación de Usuarios**: Sistema JWT con 3 tipos de usuario (Admin, Donador, Olla Común)
- **Gestión de Ollas Comunes**: CRUD completo para ollas comunes
- **Sistema de Donaciones**: Registrar, aprobar y rechazar donaciones
- **Solicitudes de Recursos**: Las ollas pueden solicitar recursos específicos
- **Dashboard Personalizado**: Interface diferenciada por rol de usuario
- **Panel de Administración**: Aprobación de donaciones y solicitudes
- **Diseño Responsive**: Optimizado para desktop, tablet y móvil con Bootstrap 5
- **Arquitectura Hexagonal**: Separación clara entre capas de dominio, infraestructura e interfaces
- **API REST**: 20+ endpoints REST para todas las operaciones

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: Flask 3.0.0
- **Autenticación**: JWT (Flask-JWT-Extended 4.5.3)
- **Base de Datos**: MySQL
- **Lenguaje**: Python 3.8+
- **ORM**: Nativo con PyMySQL

### Frontend
- **Markup**: HTML5 Semántico
- **Estilos**: CSS3 + Bootstrap 5.3
- **JavaScript**: Vanilla JS (sin frameworks)
- **Comunicación**: Fetch API
- **Gestión de Estado**: localStorage + Client-side

## 📁 Estructura del Proyecto

```text
red-comunitaria/
├── backend/
│   ├── app.py                      # Aplicación Flask principal
│   ├── seed.py                     # Script para inyectar datos de prueba en MySQL
│   ├── config.py                   # Configuración (Dev/Prod)
│   ├── requirements.txt            # Dependencias Python
│   ├── domain/
│   │   ├── models.py              # Entidades de dominio
│   │   ├── repositories.py        # Interfaces de repositorio
│   │   └── services.py            # Servicios de negocio
│   └── infrastructure/
│       ├── database.py            # Gestión de conexión MySQL
│       └── repositories.py        # Implementación de repositorios MySQL
│
└── frontend/
    ├── index.html                 # Landing page
    ├── login.html                 # Página de login
    ├── register.html              # Página de registro
    ├── dashboard.html             # Dashboard principal
    ├── ollas.html                 # Listado de ollas
    ├── donar.html                 # Formulario de donación
    ├── css/
    │   └── styles.css            # Estilos principales
    └── js/
        ├── api.js                # Cliente API HTTP
        └── main.js               # Utilidades globales
```

## ⚡ Instalación y Setup
### Prerrequisitos:
- Python 3.8+
- MySQL Server (XAMPP, MySQL Workbench, etc.)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

### Backend - Instalación
1. Navega a la carpeta del backend:
```
cd backend
```

2. Crea y activa un entorno virtual (recomendado):
```
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
```

3. Instala las dependencias:
```
pip install -r requirements.txt
```

### Configura la base de datos MySQL:

## Abre tu gestor MySQL.

4. Ejecuta el siguiente comando para crear la base de datos vacía:
```
CREATE DATABASE redcomunitaria;
```

5. Ejecuta la aplicación Flask (esto creará las tablas automáticamente):
```
python app.py
```

6. (Opcional) Abre una nueva terminal, activa el entorno virtual e inyecta datos de prueba: (Para agregar datos randoms)
```
python seed.py
```

### Frontend - Instalación

1. Abre una terminal en la carpeta del frontend
   
2. Inicia un servidor HTTP simple:
```bash
# Con Python 3
python -m http.server 8000
# Con Python 2
python -m SimpleHTTPServer 8000
# O con Node.js (si lo tienes instalado)
npx http-server -p 8000
```



3. Abre el navegador en `http://localhost:8000`



## 👤 Credenciales de Prueba


Estas credenciales están preinstaladas en la base de datos:


### Administrador
- **Email**: admin@redcomunitaria.com
- **Contraseña**: abc123$
- **Acceso**: Dashboard completo, aprobación de donaciones/solicitudes

### Donador

- **Email**: donador@gmail.com
- **Contraseña**: abc123$
- **Acceso**: Registrar y seguir donaciones



### Olla Común
- **Email**: olla@gmail.com
- **Contraseña**: abc123$
- **Acceso**: Crear ollas, solicitar recursos

## 🔄 Flujos Principales

### 1. Registrarse como Nuevo Usuario
1. Ir a `http://localhost:8000/register.html`
2. Seleccionar tipo de usuario (Donador u Olla Común)
3. Completar email, nombre, contraseña
4. Si es Olla: agregar dirección y descripción
5. Enviar formulario
6. Se redirige automáticamente a login

### 2. Iniciar Sesión
1. Ir a `http://localhost:8000/login.html`
2. Ingresar email y contraseña
3. Click en "Iniciar Sesión"
4. Se redirige al dashboard personalizado por rol

### 3. Donador - Hacer una Donación
1. Iniciar sesión como donador
2. Ir a "Mis Donaciones" en el menú
3. O hacer click en "Donar Ahora" en la landing
4. Seleccionar una olla común
5. Especificar tipo de recurso (alimentos, medicinas, ropa, etc)
6. Ingresar cantidad y unidad
7. Enviar donación
8. Requiere aprobación del admin

### 4. Olla Común - Solicitar Recursos
1. Iniciar sesión como olla común
2. Crear/registrar una olla en "Mis Ollas"
3. Ir a "Solicitudes" para crear una solicitud
4. Especificar tipo de recurso, cantidad y urgencia
5. Enviar solicitud
6. El admin la aprobará


### 5. Admin - Aprobar Solicitudes
1. Iniciar sesión como admin
2. Ir a "Administración" en el menú
3. Ver donaciones pendientes en la sección izquierda
4. Ver solicitudes pendientes en la sección derecha
5. Usar botones ✓ (aprobar) o ✕ (rechazar)

## 📡 API Endpoints


### Autenticación

- `POST /api/auth/login` - Iniciar sesión
  - Body: `{ email, password }`
  - Retorna: JWT access_token + user data

- `POST /api/auth/register` - Registrar nuevo usuario
  - Body: `{ email, password, nombre, role, telefono }`
  - Retorna: user_id

- `GET /api/auth/profile` - Obtener perfil (requiere auth)
  - Retorna: datos del usuario autenticado


### Ollas Comunes
- `GET /api/ollas` - Listar todas las ollas
- `GET /api/ollas/<id>` - Obtener una olla específica
- `POST /api/ollas` - Crear olla (requiere role=olla_comun)
- `PUT /api/ollas/<id>` - Actualizar olla
- `DELETE /api/ollas/<id>` - Eliminar olla

### Donaciones
- `GET /api/donaciones` - Listar donaciones
- `GET /api/donaciones/<id>` - Obtener donación específica
- `POST /api/donaciones` - Crear donación (requiere auth)
- `POST /api/donaciones/<id>/approve` - Aprobar (requiere role=admin)
- `POST /api/donaciones/<id>/reject` - Rechazar (requiere role=admin)

### Solicitudes de Recursos
- `GET /api/solicitudes` - Listar solicitudes
- `POST /api/solicitudes` - Crear solicitud (requiere role=olla_comun)
- `POST /api/solicitudes/<id>/approve` - Aprobar (requiere role=admin)


### Admin
- `GET /api/admin/dashboard` - Estadísticas (requiere role=admin)
- Retorna: total_usuarios, ollas_activas, donaciones_pendientes, solicitudes_pendientes

## 🗄️ Base de Datos

###My SQL con 5 tablas principales:

### users

```sql
id, email, password (hashed), nombre, role, telefono, activo, fecha_creacion
```

### ollas_comunes

```sql
id, nombre, usuario_id, descripcion, direccion, telefono, 
beneficiarios_atendidos, estado (activa/pausada/inactiva), fecha_creacion
```

### donaciones

```sql
id, donador_id, olla_comun_id, tipo_recurso, cantidad, unidad,
descripcion, estado (pendiente/aprobada/entregada/rechazada), 
fecha_creacion, fecha_entrega
```

### solicitudes_recursos
```sql
id, olla_comun_id, tipo_recurso, cantidad, unidad, descripcion,
urgencia (baja/normal/alta/crítica), estado (pendiente/aprobada/completada/rechazada),
fecha_creacion
```

### entregas
```sql
id, donacion_id, solicitud_id, olla_comun_id, cantidad_entregada,
fecha_entrega, observaciones
```

## 🔒 Seguridad
- **Contraseñas**: Hashed con Werkzeug usando SHA256
- **Autenticación**: JWT con expiración de 24 horas
- **Autorización**: Validación de roles por endpoint
- **CORS**: Habilitado para desarrollo
- **Validación**: Input validation en frontend y backend
- **Sesiones**: Basadas en JWT (stateless)


## 📱 Características del Diseño

### Responsive Design
- Mobile-first approach
- Breakpoints: xs, sm (576px), md (768px), lg (992px), xl (1200px)
- Bootstrap 5 grid system
- Flexbox layouts

### Paleta de Colores
- Primario: #007BFF (Azul)
- Secundario: #FF6B6B (Rojo)
- Success: #28a745
- Warning: #ffc107
- Danger: #dc3545


### Tipografía
- Font principal: Segoe UI, Tahoma, Geneva, Verdana
- Heading: Pesos 700-800
- Body: Peso 400, line-height 1.6


## 🚀 Deploy a Producción

Antes de desplegar:

1. **Cambiar configuración**:
```python
# config.py
FLASK_ENV = 'production'
SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@host/db'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Generar una segura
```

2. **Generar JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **Usar servidor WSGI** (no Flask development):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. **Servir frontend desde CDN o servidor web**:
- Usar Nginx/Apache para archivos estáticos
- HTTPS obligatorio
- Minificar CSS/JS

## 🐛 Troubleshooting

### Error: "Connection refused" en API calls
- Verifica que el backend esté corriendo: `python backend/app.py`
- Frontend debe estar en `http://localhost:8000`
- Backend debe estar en `http://localhost:5000`

### CORS errors
- Flask-CORS está configurado, pero verifica que la URL sea correcta
- En producción, especificar `CORS_ORIGINS`

### Token expirado
- El token expira después de 24 horas
- Usuario debe volver a iniciar sesión



### Base de datos no se inicializa
- Elimina `backend/redcomunitaria.db`
- Reinicia el backend para regenerarla con usuarios por defecto

## 📚 Estructura del Código Backend (Arquitectura Hexagonal)

### Domain Layer (Dominio)

- `models.py`: Entidades puras sin dependencias
- `repositories.py`: Interfaces (contratos)
- `services.py`: Lógica de negocio pura

### Infrastructure Layer (Infraestructura)
- `database.py`: Inicialización SQLite
- `repositories.py`: Implementación concreta de interfaces

### Interface Layer (Interfaces)
- `app.py`: Endpoints Flask REST


## 🔗 Integración Frontend-Backend

El cliente API (`frontend/js/api.js`) maneja:
- Autenticación con JWT
- Manejo automático de errores 401
- Requests HTTP RESTful
- Gestión de tokens en localStorage

## 📋 Tipos de Usuarios y Permisos
| Acción | Admin | Donador | Olla Común |
|--------|-------|---------|-----------|
| Ver ollas | ✓ | ✓ | ✓ |
| Crear olla | ✓ | ✗ | ✓ |
| Crear donación | ✗ | ✓ | ✗ |
| Crear solicitud | ✗ | ✗ | ✓ |
| Aprobar donación | ✓ | ✗ | ✗ |
| Aprobar solicitud | ✓ | ✗ | ✗ |
| Ver dashboard admin | ✓ | ✗ | ✗ |



## 📞 Soporte

Para reportar bugs o sugerencias, crea un issue en el repositorio.

---

**Versión**: 1.0.0  
**Última actualización**: Junio 2024  
**Licencia**: MIT 
