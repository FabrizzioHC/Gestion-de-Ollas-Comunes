"""
CAPA DE INFRAESTRUCTURA - Implementación de Repositorios
Implementa las interfaces de dominio con SQLite
"""
from typing import List, Optional, Dict
from datetime import datetime
import sqlite3
from domain.repositories import (
    UserRepository, OllaComunRepository, DonacionRepository,
    SolicitudRecursoRepository, EntregaRepository
)
from domain.models import User, OllaComun, Donacion, SolicitudRecurso, Entrega
from .database import Database

class SQLiteUserRepository(UserRepository):
    """Implementación SQLite del repositorio de usuarios"""
    
    def __init__(self, db: Database):
        self.db = db

    def create(self, user: User) -> int:
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (email, password, nombre, role, telefono, activo, fecha_creacion, dni, edad, vulnerabilidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user.email, user.password, user.nombre, user.role, user.telefono, 
                  user.activo, user.fecha_creacion, user.dni, user.edad, user.vulnerabilidad))
            return cursor.lastrowid

    def find_by_id(self, user_id: int) -> Optional[User]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def find_by_email(self, email: str) -> Optional[User]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def find_all(self, role: Optional[str] = None) -> List[User]:
        with self.db.get_cursor() as cursor:
            if role:
                cursor.execute('SELECT * FROM users WHERE role = ?', (role,))
            else:
                cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]

    def update(self, user_id: int, user_data: dict) -> bool:
        with self.db.get_cursor() as cursor:
            fields = ', '.join([f"{k} = ?" for k in user_data.keys()])
            values = list(user_data.values()) + [user_id]
            cursor.execute(f'UPDATE users SET {fields} WHERE id = ?', values)
            return cursor.rowcount > 0

    def delete(self, user_id: int) -> bool:
        with self.db.get_cursor() as cursor:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_user(row) -> User:
        return User(
            id=row['id'],
            email=row['email'],
            password=row['password'],
            nombre=row['nombre'],
            role=row['role'],
            telefono=row['telefono'],
            activo=bool(row['activo']),
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion']),
            dni=row['dni'],
            edad=row['edad'],
            vulnerabilidad=row['vulnerabilidad']
        )


class SQLiteOllaComunRepository(OllaComunRepository):
    """Implementación SQLite del repositorio de ollas comunes"""
    
    def __init__(self, db: Database):
        self.db = db

    def create(self, olla: OllaComun) -> int:
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO ollas_comunes 
                (nombre, usuario_id, descripcion, direccion, telefono, beneficiarios_atendidos, estado, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (olla.nombre, olla.usuario_id, olla.descripcion, olla.direccion,
                  olla.telefono, olla.beneficiarios_atendidos, olla.estado, olla.fecha_creacion))
            return cursor.lastrowid

    def find_by_id(self, olla_id: int) -> Optional[OllaComun]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM ollas_comunes WHERE id = ?', (olla_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_olla(row)

    def find_all(self, estado: Optional[str] = None) -> List[OllaComun]:
        with self.db.get_cursor() as cursor:
            if estado:
                cursor.execute('SELECT * FROM ollas_comunes WHERE estado = ?', (estado,))
            else:
                cursor.execute('SELECT * FROM ollas_comunes')
            rows = cursor.fetchall()
            return [self._row_to_olla(row) for row in rows]

    def find_by_usuario(self, usuario_id: int) -> List[OllaComun]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM ollas_comunes WHERE usuario_id = ?', (usuario_id,))
            rows = cursor.fetchall()
            return [self._row_to_olla(row) for row in rows]

    def update(self, olla_id: int, olla_data: dict) -> bool:
        with self.db.get_cursor() as cursor:
            fields = ', '.join([f"{k} = ?" for k in olla_data.keys()])
            values = list(olla_data.values()) + [olla_id]
            cursor.execute(f'UPDATE ollas_comunes SET {fields} WHERE id = ?', values)
            return cursor.rowcount > 0

    def delete(self, olla_id: int) -> bool:
        with self.db.get_cursor() as cursor:
            cursor.execute('DELETE FROM ollas_comunes WHERE id = ?', (olla_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_olla(row) -> OllaComun:
        return OllaComun(
            id=row['id'],
            nombre=row['nombre'],
            usuario_id=row['usuario_id'],
            descripcion=row['descripcion'],
            direccion=row['direccion'],
            telefono=row['telefono'],
            beneficiarios_atendidos=row['beneficiarios_atendidos'],
            estado=row['estado'],
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion'])
        )


class SQLiteDonacionRepository(DonacionRepository):
    """Implementación SQLite del repositorio de donaciones"""
    
    def __init__(self, db: Database):
        self.db = db

    def create(self, donacion: Donacion) -> int:
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO donaciones 
                (donador_id, olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, estado, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (donacion.donador_id, donacion.olla_comun_id, donacion.tipo_recurso,
                  donacion.cantidad, donacion.unidad, donacion.descripcion, donacion.estado,
                  donacion.fecha_creacion))
            return cursor.lastrowid

    def find_by_id(self, donacion_id: int) -> Optional[Donacion]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM donaciones WHERE id = ?', (donacion_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_donacion(row)

    def find_all(self, estado: Optional[str] = None) -> List[Donacion]:
        with self.db.get_cursor() as cursor:
            if estado:
                cursor.execute('SELECT * FROM donaciones WHERE estado = ?', (estado,))
            else:
                cursor.execute('SELECT * FROM donaciones')
            rows = cursor.fetchall()
            return [self._row_to_donacion(row) for row in rows]

    def find_by_donador(self, donador_id: int) -> List[Donacion]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM donaciones WHERE donador_id = ?', (donador_id,))
            rows = cursor.fetchall()
            return [self._row_to_donacion(row) for row in rows]

    def find_by_olla(self, olla_id: int) -> List[Donacion]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM donaciones WHERE olla_comun_id = ?', (olla_id,))
            rows = cursor.fetchall()
            return [self._row_to_donacion(row) for row in rows]

    def update(self, donacion_id: int, donacion_data: dict) -> bool:
        with self.db.get_cursor() as cursor:
            fields = ', '.join([f"{k} = ?" for k in donacion_data.keys()])
            values = list(donacion_data.values()) + [donacion_id]
            cursor.execute(f'UPDATE donaciones SET {fields} WHERE id = ?', values)
            return cursor.rowcount > 0

    def delete(self, donacion_id: int) -> bool:
        with self.db.get_cursor() as cursor:
            cursor.execute('DELETE FROM donaciones WHERE id = ?', (donacion_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_donacion(row) -> Donacion:
        return Donacion(
            id=row['id'],
            donador_id=row['donador_id'],
            olla_comun_id=row['olla_comun_id'],
            tipo_recurso=row['tipo_recurso'],
            cantidad=row['cantidad'],
            unidad=row['unidad'],
            descripcion=row['descripcion'],
            estado=row['estado'],
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion']),
            fecha_entrega=datetime.fromisoformat(row['fecha_entrega']) if row['fecha_entrega'] else None
        )


class SQLiteSolicitudRecursoRepository(SolicitudRecursoRepository):
    """Implementación SQLite del repositorio de solicitudes"""
    
    def __init__(self, db: Database):
        self.db = db

    def create(self, solicitud: SolicitudRecurso) -> int:
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO solicitudes_recursos 
                (olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, urgencia, estado, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (solicitud.olla_comun_id, solicitud.tipo_recurso, solicitud.cantidad,
                  solicitud.unidad, solicitud.descripcion, solicitud.urgencia, solicitud.estado,
                  solicitud.fecha_creacion))
            return cursor.lastrowid

    def find_by_id(self, solicitud_id: int) -> Optional[SolicitudRecurso]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM solicitudes_recursos WHERE id = ?', (solicitud_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_solicitud(row)

    def find_all(self, estado: Optional[str] = None) -> List[SolicitudRecurso]:
        with self.db.get_cursor() as cursor:
            if estado:
                cursor.execute('SELECT * FROM solicitudes_recursos WHERE estado = ?', (estado,))
            else:
                cursor.execute('SELECT * FROM solicitudes_recursos')
            rows = cursor.fetchall()
            return [self._row_to_solicitud(row) for row in rows]

    def find_by_olla(self, olla_id: int) -> List[SolicitudRecurso]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM solicitudes_recursos WHERE olla_comun_id = ?', (olla_id,))
            rows = cursor.fetchall()
            return [self._row_to_solicitud(row) for row in rows]

    def update(self, solicitud_id: int, solicitud_data: dict) -> bool:
        with self.db.get_cursor() as cursor:
            fields = ', '.join([f"{k} = ?" for k in solicitud_data.keys()])
            values = list(solicitud_data.values()) + [solicitud_id]
            cursor.execute(f'UPDATE solicitudes_recursos SET {fields} WHERE id = ?', values)
            return cursor.rowcount > 0

    def delete(self, solicitud_id: int) -> bool:
        with self.db.get_cursor() as cursor:
            cursor.execute('DELETE FROM solicitudes_recursos WHERE id = ?', (solicitud_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_solicitud(row) -> SolicitudRecurso:
        return SolicitudRecurso(
            id=row['id'],
            olla_comun_id=row['olla_comun_id'],
            tipo_recurso=row['tipo_recurso'],
            cantidad=row['cantidad'],
            unidad=row['unidad'],
            descripcion=row['descripcion'],
            urgencia=row['urgencia'],
            estado=row['estado'],
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion'])
        )


class SQLiteEntregaRepository(EntregaRepository):
    """Implementación SQLite del repositorio de entregas"""
    
    def __init__(self, db: Database):
        self.db = db

    def create(self, entrega: Entrega) -> int:
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO entregas 
                (donacion_id, solicitud_id, olla_comun_id, cantidad_entregada, fecha_entrega, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entrega.donacion_id, entrega.solicitud_id, entrega.olla_comun_id,
                  entrega.cantidad_entregada, entrega.fecha_entrega, entrega.observaciones))
            return cursor.lastrowid

    def find_by_id(self, entrega_id: int) -> Optional[Entrega]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM entregas WHERE id = ?', (entrega_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_entrega(row)

    def find_all(self) -> List[Entrega]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM entregas')
            rows = cursor.fetchall()
            return [self._row_to_entrega(row) for row in rows]

    def find_by_olla(self, olla_id: int) -> List[Entrega]:
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM entregas WHERE olla_comun_id = ?', (olla_id,))
            rows = cursor.fetchall()
            return [self._row_to_entrega(row) for row in rows]

    def update(self, entrega_id: int, entrega_data: dict) -> bool:
        with self.db.get_cursor() as cursor:
            fields = ', '.join([f"{k} = ?" for k in entrega_data.keys()])
            values = list(entrega_data.values()) + [entrega_id]
            cursor.execute(f'UPDATE entregas SET {fields} WHERE id = ?', values)
            return cursor.rowcount > 0

    def delete(self, entrega_id: int) -> bool:
        with self.db.get_cursor() as cursor:
            cursor.execute('DELETE FROM entregas WHERE id = ?', (entrega_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_entrega(row) -> Entrega:
        return Entrega(
            id=row['id'],
            donacion_id=row['donacion_id'],
            solicitud_id=row['solicitud_id'],
            olla_comun_id=row['olla_comun_id'],
            cantidad_entregada=row['cantidad_entregada'],
            fecha_entrega=datetime.fromisoformat(row['fecha_entrega']),
            observaciones=row['observaciones']
        )
