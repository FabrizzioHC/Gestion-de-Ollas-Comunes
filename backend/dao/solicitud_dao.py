from backend.config.database import get_connection
from backend.models.solicitud import Solicitud

class SolicitudDAO:

    # 1. LEER - Listar solicitudes por el ID de la Olla (Para la Lideresa)
    @staticmethod
    def listar_por_olla(id_olla):
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Solicitud WHERE olla_id = %s ORDER BY fecha_solicitud DESC"
                cursor.execute(sql, (id_olla,))
                resultados = cursor.fetchall()
                
                for fila in resultados:
                    # Python convierte automáticamente toda la fila de la BD al objeto Solicitud
                    lista.append(Solicitud(**fila)) 
        except Exception as e:
            print(f"Error en listar_por_olla: {e}")
        finally:
            conexion.close()
            
        return lista

    # 2. CREAR - Registrar una nueva solicitud
    @staticmethod
    def crear_solicitud(solicitud):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO Solicitud 
                    (olla_id, recurso_necesitado, cantidad_necesitada, unidad_medida, nivel_urgencia, estado) 
                    VALUES (%s, %s, %s, %s, %s, 'Pendiente')
                """
                cursor.execute(sql, (
                    solicitud.olla_id, solicitud.recurso_necesitado, 
                    solicitud.cantidad_necesitada, solicitud.unidad_medida, 
                    solicitud.nivel_urgencia
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en crear_solicitud: {e}")
            return False
        finally:
            conexion.close()

    # 3. ACTUALIZAR - Modificar una solicitud existente desde el Modal
    @staticmethod
    def actualizar_solicitud(solicitud):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    UPDATE Solicitud 
                    SET recurso_necesitado=%s, cantidad_necesitada=%s, unidad_medida=%s, nivel_urgencia=%s 
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    solicitud.recurso_necesitado, solicitud.cantidad_necesitada, 
                    solicitud.unidad_medida, solicitud.nivel_urgencia, 
                    solicitud.id
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en actualizar_solicitud: {e}")
            return False
        finally:
            conexion.close()

    # 4. ELIMINAR - Borrar una solicitud
    @staticmethod
    def eliminar_solicitud(id_solicitud):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM Solicitud WHERE id=%s"
                cursor.execute(sql, (id_solicitud,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en eliminar_solicitud: {e}")
            return False
        finally:
            conexion.close()

    # 5. LISTAR TODAS LAS SOLICITUDES (Para el Administrador)
    @staticmethod
    def listar_todas_las_solicitudes():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                # El INNER JOIN trae la columna 'nombre_olla'
                sql = """
                    SELECT s.*, o.nombre_olla 
                    FROM Solicitud s 
                    INNER JOIN Olla_Comun o ON s.olla_id = o.id 
                    ORDER BY s.fecha_solicitud DESC
                """
                cursor.execute(sql)
                resultados = cursor.fetchall()
                
                for fila in resultados:
                    # Como en nuestro modelo `solicitud.py` pusimos `nombre_olla=""` en el __init__,
                    # al hacer **fila, Python detecta la columna del JOIN y la asigna mágicamente.
                    lista.append(Solicitud(**fila))
        except Exception as e:
            print(f"Error en listar_todas_las_solicitudes: {e}")
        finally:
            conexion.close()
            
        return lista

    # 6. CAMBIAR EL ESTADO (Aceptar o Rechazar por el Admin)
    @staticmethod
    def cambiar_estado_solicitud(id_solicitud, nuevo_estado):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE Solicitud SET estado = %s WHERE id = %s"
                cursor.execute(sql, (nuevo_estado, id_solicitud))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en cambiar_estado_solicitud: {e}")
            return False
        finally:
            conexion.close()