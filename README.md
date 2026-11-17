# Sistema de Ollas Comunes - Red Comunitaria

Sistema web para la gestión integral de Ollas Comunes, que conecta a Lideresas, Donadores y Administradores. Está construido con Python (Flask), Jinja2, Bootstrap 5 y MySQL, y fue migrado desde una arquitectura Java/JSP.

## Requisitos previos

- Python 3.8 o superior
- MySQL Server 8.x y MySQL Workbench (o cualquier cliente SQL)
- Git
- VS Code (recomendado)

## Instalación y configuración local

Todos los comandos se ejecutan en la terminal de VS Code, desde la **raíz del proyecto**.

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd <carpeta-del-proyecto>
```

### 2. Crear el entorno virtual

El entorno virtual aísla las librerías de este proyecto para que no interfieran con otros en tu computadora.

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

Git Bash:

```bash
source venv/Scripts/activate
```

PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea el script, ejecuta primero:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

Sabrás que funcionó porque aparece `(venv)` al inicio de la línea de la terminal.

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Crear la base de datos

En MySQL Workbench, ejecuta en este orden:

1. `database/schema.sql`: crea la base `sistema_ollas_comunes_vs` y sus tablas.
2. `database/seed.sql`: carga datos de prueba (usuarios, ollas, recursos, solicitudes y donaciones).

> Ejecútalos sobre una base **vacía**. Los datos de prueba dependen de que los IDs empiecen en 1.

### 6. Configurar las variables de entorno

El archivo `.env` contiene datos privados (contraseña de la base de datos), por eso **no se sube al repositorio**. Cada persona crea el suyo a partir de la plantilla `.env.example`.

Git Bash:

```bash
cp .env.example .env
```

PowerShell:

```powershell
copy .env.example .env
```

Abre el `.env` y completa tus datos:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD='tu_contraseña_de_mysql'
DB_NAME=sistema_ollas_comunes_vs
SECRET_KEY=una_clave_larga_y_aleatoria
```

Notas importantes:

- `DB_PASSWORD` es la contraseña de **tu** MySQL. Si contiene símbolos como `$`, escríbela entre comillas simples.
- `DB_PORT` es normalmente `3306`. Si tu MySQL usa otro puerto (por ejemplo `3307`), cámbialo aquí.
- `SECRET_KEY` es la llave con la que Flask firma las sesiones de inicio de sesión. Puede ser cualquier texto largo y difícil de adivinar. Para generar una:

  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

  No tiene que ser la misma para todos los integrantes: cada quien usa la suya en su propia computadora.
- No dejes espacios alrededor del `=`.

### 7. Probar la conexión a la base de datos

```bash
python backend/config/database.py
```

Debe mostrar: `¡ÉXITO! Conexión perfecta a la base de datos sistema_ollas_comunes_vs.`

### 8. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

## Usuarios de prueba

Todos los usuarios de prueba usan la contraseña `abc123$` (solo para desarrollo).

| Rol | Correo |
|---|---|
| Administrador | admin.redcomunitaria@gmail.com |
| Lideresa | rosa.gomez@gmail.com |
| Donador | luis.torres@gmail.com |

## Problemas comunes

| Mensaje | Causa probable |
|---|---|
| `Access denied for user 'root'` | La contraseña del `.env` no coincide con la de tu MySQL. |
| `Can't connect to MySQL server` | MySQL no está iniciado o el `DB_PORT` es incorrecto. |
| `Unknown database` | Falta ejecutar `database/schema.sql`. |
| `ModuleNotFoundError` | El entorno virtual no está activo o faltó `pip install -r requirements.txt`. |
| Las tildes se ven mal (`Ã±`) | Revisa que la base de datos use `utf8mb4`. |

## Estructura del proyecto

```
backend/
  config/       Conexión a la base de datos
  controllers/  Rutas de Flask (Blueprints)
  dao/          Acceso a datos (consultas SQL)
  models/       Clases del dominio
frontend/
  static/       CSS e imágenes
  templates/    Plantillas HTML (Jinja2)
database/       Scripts SQL (schema y seed)
run.py          Punto de entrada de la aplicación
```

## Inicio rapido con accesibilidad

1. Extrae el ZIP completo en una carpeta nueva.
2. Abre `.env` y configura DB_HOST, DB_PORT, DB_USER, DB_PASSWORD y DB_NAME
   con los datos de tu MySQL. Si ya tienes una base con los datos del proyecto,
   escribe su nombre en DB_NAME. El nombre debe coincidir exactamente.
3. Enciende MySQL y haz doble clic en `INICIAR.bat`.

El iniciador prepara un entorno virtual (venv; tambien reconoce .venv), instala
las dependencias la primera vez, genera una clave local de sesion si falta,
comprueba la conexion y la tabla Usuario, y abre http://127.0.0.1:5000 cuando la
aplicacion responde. Python 3.9 o superior debe estar instalado. La primera
instalacion necesita Internet. No necesitas activar PowerShell ni editar
backend/config/database.py. Conserva abierta la ventana para usar el sistema;
Ctrl+C lo detiene. Si el puerto 5000 esta ocupado, detiene la otra instancia.

Si aun no existe la base, importa `database/ollas_comunes.sql` una sola vez
con MySQL Workbench. Este es el archivo incluido en este ZIP; reemplaza las
referencias antiguas a schema.sql y seed.sql de la guia original. El archivo
INICIAR.bat no importa SQL, no elimina registros y no cambia contrasenas de MySQL.
No reemplaces tu `.env` al actualizar una instalacion que ya esta configurada.

### Panel de accesibilidad

El boton azul inferior derecho aparece en las 15 paginas. Incluye texto al
125 %, 150 % y 200 %; tres contrastes; cursor grande y extra grande; mascara
de lectura; fuente y espaciado de lectura; interlineado; perfiles y restablecer.
Las preferencias se guardan en este navegador para el mismo host y puerto.
El panel admite teclado, Escape, retorno del foco y avisos para lectores de
pantalla. La mascara respeta campos y controles que utilizan flechas. El texto
se recalcula al cambiar el ancho de la ventana. El idioma disponible es espanol.

Los archivos originales de backend, SQL, dependencias, estilos generales y
run.py se conservan. En base.html y cinco paginas independientes se agregaron
solo las inclusiones del panel. Sus archivos estan separados en los fragmentos
_accessibility*.html y los recursos accessibility.css y accessibility.js.

### Verificacion

`python pruebas/accesibilidad/verificar_plantillas.py` comprueba 60 renderizados
(15 paginas con cuatro estados de sesion) sin consultar MySQL.
`node pruebas/accesibilidad/verificar_logica.cjs` comprueba la logica del panel
con un DOM simulado. Node es opcional y solo se usa para estas pruebas; no es
necesario para ejecutar el proyecto.

La ejecucion visual en Windows y la lectura con NVDA deben comprobarse en tu
equipo. No se presenta la simulacion como una certificacion de accesibilidad.
