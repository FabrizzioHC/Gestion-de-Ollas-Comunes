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

⚡ Instalación y Setup
Prerrequisitos:
Python 3.8+

MySQL Server (XAMPP, MySQL Workbench, etc.)

Navegador web moderno (Chrome, Firefox, Safari, Edge)

Backend - Instalación
Navega a la carpeta del backend:

Bash
cd backend
Crea y activa un entorno virtual (recomendado):

Bash
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
Instala las dependencias:

Bash
pip install -r requirements.txt
Configura la base de datos MySQL:

Abre tu gestor MySQL.

Ejecuta el siguiente comando para crear la base de datos vacía:

SQL
CREATE DATABASE redcomunitaria;
Ejecuta la aplicación Flask (esto creará las tablas automáticamente):

Bash
python app.py
(Opcional) Abre una nueva terminal, activa el entorno virtual e inyecta datos de prueba:

Bash
python seed.py
Frontend - Instalación
Abre una terminal en la carpeta del frontend.

Inicia un servidor HTTP simple:

Bash
python -m http.server 8000
Abre el navegador en http://localhost:8000

👤 Credenciales de Prueba
Estas credenciales se generan automáticamente al iniciar el servidor:

Administrador: admin@redcomunitaria.com | Clave: abc123$

Donador: donador@gmail.com | Clave: abc123$

Olla Común: olla@gmail.com | Clave: abc123$

🔄 Flujos Principales
1. Registrarse como Nuevo Usuario
Ir a http://localhost:8000/register.html

Seleccionar tipo de usuario y completar los datos.

Se redirige automáticamente a login tras el registro exitoso.

2. Donador - Hacer una Donación
Iniciar sesión como donador.

Seleccionar una olla común y especificar los recursos.

Enviar donación (quedará pendiente hasta la aprobación del admin).

3. Olla Común - Solicitar Recursos
Iniciar sesión como olla común y registrar una olla en "Mis Ollas".

Crear una solicitud de recursos detallando urgencia y cantidad.

4. Admin - Aprobar Solicitudes
Iniciar sesión como admin y entrar a "Administración".

Aprobar (✓) o rechazar (✕) las solicitudes y donaciones pendientes.

🗄️ Base de Datos
MySQL estructurado en 5 tablas principales:

users
id, email, password, nombre, role, telefono, dni, edad, vulnerabilidad, olla_asociada_id, activo, fecha_creacion

ollas_comunes
id, nombre, usuario_id, descripcion, direccion, telefono, beneficiarios_atendidos, estado, fecha_creacion

donaciones
id, donador_id, olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, estado, fecha_creacion, fecha_entrega

solicitudes_recursos
id, olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, urgencia, estado, fecha_creacion

entregas
id, donacion_id, solicitud_id, olla_comun_id, cantidad_entregada, fecha_entrega, observaciones

🔒 Seguridad
Contraseñas: Hashed con Werkzeug usando SHA256

Autenticación: JWT con expiración de 24 horas

Validación: Inyección prevenida mediante consultas parametrizadas (%s) en PyMySQL.

🐛 Troubleshooting
Error: "Access denied for user" al levantar Flask
Verifica que las credenciales en backend/infrastructure/database.py coincidan con tu MySQL local (usuario root, contraseña correcta, puerto 3306).

Base de datos vacía o con errores de prueba
Para reiniciar todo desde cero, ejecuta en tu gestor MySQL:

SQL
DROP DATABASE redcomunitaria;
CREATE DATABASE redcomunitaria;
Luego, reinicia python app.py y vuelve a correr python seed.py.

📚 Estructura del Código Backend (Arquitectura Hexagonal)
Domain Layer (Dominio)
models.py: Entidades puras sin dependencias

repositories.py: Interfaces (contratos)

services.py: Lógica de negocio pura

Infrastructure Layer (Infraestructura)
database.py: Inicialización de conexión MySQL (PyMySQL)

repositories.py: Implementación concreta de interfaces adaptadas a MySQL

Interface Layer (Interfaces)
app.py: Endpoints Flask REST

Versión: 1.1.0

Última actualización: Agosto 2026

Licencia: MIT
