"""
CAPA DE INFRAESTRUCTURA - Base de Datos
Implementación PyMySQL para persistencia de datos
"""
import pymysql
import pymysql.cursors
from datetime import datetime
import json
from contextlib import contextmanager

class Database:
    """Gestor de conexión a la base de datos MySQL"""
    
    def __init__(self, host='127.0.0.1', user='root', password='abc123$', db='redcomunitaria', port=3306):
            self.host = host
            self.user = user
            self.password = password
            self.db = db
            self.port = port
            self.init_db()

    def get_connection(self):
            """Obtiene una conexión a la base de datos MySQL"""
            return pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor
            )

    @contextmanager
    def get_cursor(self):
        """Context manager para manejo de cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def init_db(self):
        """Inicializa las tablas de la base de datos"""
        with self.get_cursor() as cursor:
            # MySQL es estricto con las llaves foráneas. 
            # Apagamos la revisión temporalmente por la dependencia circular entre users y ollas_comunes
            cursor.execute('SET FOREIGN_KEY_CHECKS=0;')

            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'donador',
                    telefono VARCHAR(20),
                    dni VARCHAR(20),
                    edad INT,
                    vulnerabilidad VARCHAR(100),
                    olla_asociada_id INT,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (olla_asociada_id) REFERENCES ollas_comunes(id)
                )
            ''')

            # Tabla de ollas comunes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ollas_comunes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    usuario_id INT NOT NULL,
                    descripcion TEXT,
                    direccion TEXT NOT NULL,
                    telefono VARCHAR(20),
                    beneficiarios_atendidos INT DEFAULT 0,
                    estado VARCHAR(50) DEFAULT 'activa',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES users(id)
                )
            ''')

            # Tabla de donaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS donaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    donador_id INT NOT NULL,
                    olla_comun_id INT,
                    tipo_recurso VARCHAR(100) NOT NULL,
                    cantidad FLOAT NOT NULL,
                    unidad VARCHAR(50) NOT NULL,
                    descripcion TEXT,
                    estado VARCHAR(50) DEFAULT 'pendiente',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_entrega TIMESTAMP NULL DEFAULT NULL,
                    FOREIGN KEY (donador_id) REFERENCES users(id),
                    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
                )
            ''')

            # Tabla de solicitudes de recursos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solicitudes_recursos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    olla_comun_id INT NOT NULL,
                    tipo_recurso VARCHAR(100) NOT NULL,
                    cantidad FLOAT NOT NULL,
                    unidad VARCHAR(50) NOT NULL,
                    descripcion TEXT,
                    urgencia VARCHAR(50) DEFAULT 'normal',
                    estado VARCHAR(50) DEFAULT 'pendiente',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
                )
            ''')

            # Tabla de entregas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entregas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    donacion_id INT,
                    solicitud_id INT,
                    olla_comun_id INT NOT NULL,
                    cantidad_entregada FLOAT NOT NULL,
                    fecha_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT,
                    FOREIGN KEY (donacion_id) REFERENCES donaciones(id),
                    FOREIGN KEY (solicitud_id) REFERENCES solicitudes_recursos(id),
                    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
                )
            ''')

            cursor.execute('SET FOREIGN_KEY_CHECKS=1;')
            
            # Insertar usuarios predefinidos
            self._insert_default_users()

    def _insert_default_users(self):
        """Inserta los usuarios predefinidos en la base de datos"""
        from werkzeug.security import generate_password_hash
        
        users_data = [
            ('admin@redcomunitaria.com', 'abc123$', 'Admin Red Comunitaria', 'admin', '+1234567890'),
            ('donador@gmail.com', 'abc123$', 'Usuario Donador', 'donador', '+0987654321'),
            ('olla@gmail.com', 'abc123$', 'Olla Común Centro', 'olla_comun', '+5551234567')
        ]

        with self.get_cursor() as cursor:
            for email, password, nombre, role, telefono in users_data:
                try:
                    hashed_pwd = generate_password_hash(password)
                    # En MySQL se usa %s en lugar de ? para los parámetros
                    cursor.execute('''
                        INSERT INTO users (email, password, nombre, role, telefono)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (email, hashed_pwd, nombre, role, telefono))
                except pymysql.err.IntegrityError:
                    # El usuario ya existe
                    pass