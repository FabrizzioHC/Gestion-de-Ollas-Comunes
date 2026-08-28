"""
CAPA DE INFRAESTRUCTURA - Base de Datos
Implementación SQLAlchemy para persistencia de datos
"""
import sqlite3
from datetime import datetime
import json
from typing import List, Optional, Dict
from contextlib import contextmanager

class Database:
    """Gestor de conexión a la base de datos SQLite"""
    
    def __init__(self, db_path: str = 'redcomunitaria.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'donador',
                    telefono TEXT,
                    dni TEXT,
                    edad INTEGER,
                    vulnerabilidad TEXT,
                    olla_asociada_id INTEGER,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (olla_asociada_id) REFERENCES ollas_comunes(id)
                )
            ''')

            # Tabla de ollas comunes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ollas_comunes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    descripcion TEXT,
                    direccion TEXT NOT NULL,
                    telefono TEXT,
                    beneficiarios_atendidos INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'activa',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES users(id)
                )
            ''')

            # Tabla de donaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS donaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donador_id INTEGER NOT NULL,
                    olla_comun_id INTEGER,
                    tipo_recurso TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    unidad TEXT NOT NULL,
                    descripcion TEXT,
                    estado TEXT DEFAULT 'pendiente',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_entrega TIMESTAMP,
                    FOREIGN KEY (donador_id) REFERENCES users(id),
                    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
                )
            ''')

            # Tabla de solicitudes de recursos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solicitudes_recursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    olla_comun_id INTEGER NOT NULL,
                    tipo_recurso TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    unidad TEXT NOT NULL,
                    descripcion TEXT,
                    urgencia TEXT DEFAULT 'normal',
                    estado TEXT DEFAULT 'pendiente',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
                )
            ''')

            # Tabla de entregas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entregas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donacion_id INTEGER,
                    solicitud_id INTEGER,
                    olla_comun_id INTEGER NOT NULL,
                    cantidad_entregada REAL NOT NULL,
                    fecha_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT,
                    FOREIGN KEY (donacion_id) REFERENCES donaciones(id),
                    FOREIGN KEY (solicitud_id) REFERENCES solicitudes_recursos(id),
                    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
                )
            ''')

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
                    cursor.execute('''
                        INSERT INTO users (email, password, nombre, role, telefono)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (email, hashed_pwd, nombre, role, telefono))
                except sqlite3.IntegrityError:
                    # El usuario ya existe
                    pass
