from backend.config.database import get_connection
from backend.models.recurso import Recurso

class RecursoDAO:

    # 1. Obtener los recursos centrales (donde olla_id es NULL o 0)
    @staticmethod
    def listar_almacen_general():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM recurso WHERE olla_id IS NULL OR olla_id = 0"
                cursor.execute(sql)
                resultados = cursor.fetchall()
                
                for fila in resultados:
                    lista.append(Recurso(**fila))
        except Exception as e:
            print(f"Error al listar almacén central: {e}")
        finally:
            if conexion:
                conexion.close()
                
        return lista

    # 2. Agregar al almacén general (suma si ya existe)
    @staticmethod
    def agregar_almacen_general(nombre, cantidad, unidad):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """SELECT id FROM recurso
                       WHERE olla_id IS NULL
                         AND LOWER(nombre_recurso) = LOWER(%s)
                         AND unidad_medida = %s
                       LIMIT 1""",
                    (nombre, unidad)
                )
                existente = cursor.fetchone()

                if existente:
                    cursor.execute(
                        """UPDATE recurso
                           SET cantidad = cantidad + %s, fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s""",
                        (cantidad, existente['id'])
                    )
                else:
                    cursor.execute(
                        """INSERT INTO recurso (olla_id, nombre_recurso, cantidad, unidad_medida)
                           VALUES (NULL, %s, %s, %s)""",
                        (nombre, cantidad, unidad)
                    )
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"Error al registrar en almacén: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    # 3. Actualizar recurso
    @staticmethod
    def actualizar_recurso(id_recurso, nombre, cantidad, unidad):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    UPDATE recurso 
                    SET nombre_recurso = %s, cantidad = %s, unidad_medida = %s, fecha_actualizacion = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """
                cursor.execute(sql, (nombre, cantidad, unidad, id_recurso))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar recurso: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    # 4. Eliminar recurso
    @staticmethod
    def eliminar_recurso(id_recurso):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM recurso WHERE id = %s"
                cursor.execute(sql, (id_recurso,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar recurso: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    # 5. Agregar recurso al inventario de una olla (suma si ya existe)
    @staticmethod
    def agregar_recurso_olla(olla_id, nombre, cantidad, unidad):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """SELECT id FROM recurso
                       WHERE olla_id = %s
                         AND LOWER(nombre_recurso) = LOWER(%s)
                         AND unidad_medida = %s
                       LIMIT 1""",
                    (olla_id, nombre, unidad)
                )
                existente = cursor.fetchone()

                if existente:
                    cursor.execute(
                        """UPDATE recurso
                           SET cantidad = cantidad + %s, fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id = %s""",
                        (cantidad, existente['id'])
                    )
                else:
                    cursor.execute(
                        """INSERT INTO recurso (olla_id, nombre_recurso, cantidad, unidad_medida)
                           VALUES (%s, %s, %s, %s)""",
                        (olla_id, nombre, cantidad, unidad)
                    )
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"Error al agregar recurso a la olla: {e}")
            return False
        finally:
            if conexion:
                conexion.close()