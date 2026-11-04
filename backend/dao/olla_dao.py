from backend.config.database import get_connection
from backend.models.olla_comun import OllaComun
from backend.models.recurso import Recurso
from backend.models.usuario import Usuario

class OllaDAO:

    # 1. OBTENER LA OLLA COMÚN DE UNA LIDERESA
    @staticmethod
    def obtener_olla_por_lideresa_id(id_lideresa):
        conexion = get_connection()
        if not conexion:
            return None
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Olla_Comun WHERE usuario_id = %s"
                cursor.execute(sql, (id_lideresa,))
                resultado = cursor.fetchone()
                if resultado:
                    return OllaComun(**resultado)
        except Exception as e:
            print(f"Error en obtener_olla_por_lideresa_id: {e}")
        finally:
            conexion.close()
        return None

    # 2. AGREGAR UN NUEVO RECURSO AL INVENTARIO
    @staticmethod
    def registrar_recurso(recurso):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO Recurso (olla_id, nombre_recurso, cantidad, unidad_medida) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (
                    recurso.olla_id, recurso.nombre_recurso, 
                    recurso.cantidad, recurso.unidad_medida
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en registrar_recurso: {e}")
            return False
        finally:
            conexion.close()

    # 3. LISTAR TODOS LOS RECURSOS DE UNA OLLA
    @staticmethod
    def listar_recursos_por_olla(olla_id):
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Recurso WHERE olla_id = %s ORDER BY fecha_actualizacion DESC"
                cursor.execute(sql, (olla_id,))
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(Recurso(**fila))
        except Exception as e:
            print(f"Error en listar_recursos_por_olla: {e}")
        finally:
            conexion.close()
        return lista

    # 4. LISTAR TODAS LAS OLLAS PARA LA VISTA PÚBLICA
    @staticmethod
    def listar_todas_las_ollas_publicas():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Olla_Comun WHERE estado = 'ACTIVA' ORDER BY fecha_creacion DESC"
                cursor.execute(sql)
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(OllaComun(**fila))
        except Exception as e:
            print(f"Error en listar_todas_las_ollas_publicas: {e}")
        finally:
            conexion.close()
        return lista
        
    # 5. LISTAR TODAS LAS OLLAS PARA EL ADMIN
    @staticmethod
    def listar_todas_admin():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Olla_Comun ORDER BY id DESC"
                cursor.execute(sql)
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(OllaComun(**fila))
        except Exception as e:
            print(f"Error en listar_todas_admin: {e}")
        finally:
            conexion.close()
        return lista

    # 6. ACTUALIZAR OLLA (ADMIN)
    @staticmethod
    def actualizar_olla_admin(olla):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    UPDATE Olla_Comun 
                    SET nombre_olla=%s, direccion=%s, descripcion=%s, beneficiarios_atendidos=%s, estado=%s 
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    olla.nombre_olla, olla.direccion, olla.descripcion, 
                    olla.beneficiarios_atendidos, olla.estado, olla.id
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en actualizar_olla_admin: {e}")
            return False
        finally:
            conexion.close()

    # 7. ELIMINAR OLLA (ADMIN) - Implementando Borrado Lógico
    @staticmethod
    def eliminar_olla_admin(id_olla):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                # En lugar de DELETE, cambiamos el estado a 'INACTIVA'
                sql = "UPDATE Olla_Comun SET estado = 'INACTIVA' WHERE id=%s"
                cursor.execute(sql, (id_olla,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en eliminar_olla_admin (Borrado lógico): {e}")
            return False
        finally:
            conexion.close()
            
    # NUEVO: LIDERESAS ACTIVAS QUE TODAVÍA NO TIENEN OLLA ASIGNADA
    @staticmethod
    def listar_lideresas_sin_olla():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT u.id, u.nombres, u.apellidos, u.email 
                    FROM Usuario u 
                    WHERE u.rol = 'LIDERESA' AND u.activo = 1 
                    AND NOT EXISTS (SELECT 1 FROM Olla_Comun o WHERE o.usuario_id = u.id) 
                    ORDER BY u.nombres, u.apellidos
                """
                cursor.execute(sql)
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(Usuario(**fila))
        except Exception as e:
            print(f"Error en listar_lideresas_sin_olla: {e}")
        finally:
            conexion.close()
        return lista

    # READ: buscar ollas comunes en MySQL por nombre, dirección, estado o beneficiarios.
    @staticmethod
    def buscar_ollas_admin(texto):
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT * FROM Olla_Comun WHERE 
                    nombre_olla LIKE %s OR direccion LIKE %s OR estado LIKE %s 
                    OR CAST(beneficiarios_atendidos AS CHAR) LIKE %s 
                    ORDER BY id DESC
                """
                patron = f"%{texto}%"
                cursor.execute(sql, (patron, patron, patron, patron))
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(OllaComun(**fila))
        except Exception as e:
            print(f"Error en buscar_ollas_admin: {e}")
        finally:
            conexion.close()
        return lista

    # NUEVO: REGISTRAR UNA OLLA DESDE ADMINISTRACIÓN EN MYSQL
    @staticmethod
    def registrar_olla_admin(olla):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO Olla_Comun 
                    (usuario_id, nombre_olla, descripcion, direccion, beneficiarios_atendidos, estado) 
                    SELECT u.id, %s, %s, %s, %s, %s 
                    FROM Usuario u 
                    WHERE u.id = %s AND u.rol = 'LIDERESA' AND u.activo = 1 
                    AND NOT EXISTS (SELECT 1 FROM Olla_Comun o WHERE o.usuario_id = u.id)
                """
                cursor.execute(sql, (
                    olla.nombre_olla, olla.descripcion, olla.direccion, 
                    olla.beneficiarios_atendidos, olla.estado, olla.usuario_id
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en registrar_olla_admin: {e}")
            return False
        finally:
            conexion.close()

        # Comprueba si ya existe una olla con ese nombre
    @staticmethod
    def existe_nombre_olla(nombre, excluir_id=None):
        conexion = get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT 1 FROM Olla_Comun WHERE LOWER(TRIM(nombre_olla)) = LOWER(TRIM(%s))"
                params = [nombre]
                if excluir_id:
                    sql += " AND id <> %s"
                    params.append(excluir_id)
                sql += " LIMIT 1"
                cursor.execute(sql, params)
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error en existe_nombre_olla: {e}")
            return False
        finally:
            conexion.close()