from backend.config.database import get_connection
from backend.models.olla_comun import OllaComun

class DonacionDAO:

    # 1. REGISTRAR DONACIÓN
    @staticmethod
    def registrar_donacion(donacion):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO Donacion (donador_id, olla_id, mensaje, recurso, cantidad, unidad_medida, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente')
                """
                cursor.execute(sql, (
                    donacion.donador_id, donacion.olla_id, donacion.mensaje,
                    donacion.recurso, donacion.cantidad, donacion.unidad_medida
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en registrar_donacion: {e}")
            return False
        finally:
            conexion.close()

    # 2. LISTAR DONACIONES DE UN USUARIO (Devuelve lista de diccionarios)
    @staticmethod
    def listar_mis_donaciones(id_donador):
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT d.id, d.fecha_registro, o.nombre_olla, d.mensaje, d.estado,
                           d.recurso, d.cantidad, d.unidad_medida
                    FROM Donacion d 
                    INNER JOIN Olla_Comun o ON d.olla_id = o.id 
                    WHERE d.donador_id = %s 
                    ORDER BY d.fecha_registro DESC
                """
                cursor.execute(sql, (id_donador,))
                # Devuelve directamente la lista de diccionarios con las claves correctas
                lista = cursor.fetchall()
        except Exception as e:
            print(f"Error en listar_mis_donaciones: {e}")
        finally:
            conexion.close()
        return lista

    # ACTUALIZAR MENSAJE DE DONACIÓN (DONADOR)
    @staticmethod
    def actualizar_donacion(id_donacion, nuevo_mensaje):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE Donacion SET mensaje = %s WHERE id = %s AND estado = 'Pendiente'"
                cursor.execute(sql, (nuevo_mensaje, id_donacion))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en actualizar_donacion: {e}")
            return False
        finally:
            conexion.close()

    # ELIMINAR/CANCELAR DONACIÓN (DONADOR)
    @staticmethod
    def eliminar_donacion(id_donacion):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM Donacion WHERE id = %s AND estado = 'Pendiente'"
                cursor.execute(sql, (id_donacion,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en eliminar_donacion: {e}")
            return False
        finally:
            conexion.close()

    # 3. LISTAR TODAS LAS OLLAS COMUNES (Para llenar el <select> del formulario)
    @staticmethod
    def listar_todas_ollas():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Olla_Comun"
                cursor.execute(sql)
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(OllaComun(**fila))
        except Exception as e:
            print(f"Error en listar_todas_ollas: {e}")
        finally:
            conexion.close()
        return lista

    # 4. LISTAR DONACIONES GLOBALES APROBADAS (Para la vista pública)
    @staticmethod
    def listar_donaciones_aprobadas_globales():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT d.fecha_registro, u.nombres, o.nombre_olla, d.mensaje 
                    FROM Donacion d 
                    INNER JOIN Olla_Comun o ON d.olla_id = o.id 
                    INNER JOIN Usuario u ON d.donador_id = u.id 
                    WHERE d.estado = 'Entregada'
                    ORDER BY d.fecha_registro DESC 
                    LIMIT 15
                """
                cursor.execute(sql)
                lista = cursor.fetchall()
        except Exception as e:
            print(f"Error en listar_donaciones_aprobadas_globales: {e}")
        finally:
            conexion.close()
        return lista

    # 5. LISTAR TODAS LAS DONACIONES (admin)
    @staticmethod
    def listar_todas_las_donaciones_admin():
        lista = []
        conexion = get_connection()
        if not conexion:
            return lista
            
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT d.id, d.fecha_registro, u.nombres, o.nombre_olla, d.mensaje, d.estado,
                           d.recurso, d.cantidad, d.unidad_medida
                    FROM Donacion d 
                    INNER JOIN Olla_Comun o ON d.olla_id = o.id 
                    INNER JOIN Usuario u ON d.donador_id = u.id 
                    ORDER BY d.fecha_registro DESC
                """
                cursor.execute(sql)
                lista = cursor.fetchall()
        except Exception as e:
            print(f"Error en listar_todas_las_donaciones_admin: {e}")
        finally:
            conexion.close()
        return lista

    # 6. CAMBIAR EL ESTADO DE UNA DONACIÓN (Admin)
    @staticmethod
    def cambiar_estado_donacion(id_donacion, nuevo_estado):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                # 1. Leemos la donación (FOR UPDATE la bloquea para no sumar dos veces)
                cursor.execute(
                    "SELECT estado, recurso, cantidad, unidad_medida FROM Donacion WHERE id = %s FOR UPDATE",
                    (id_donacion,)
                )
                don = cursor.fetchone()
                if not don:
                    return False

                # 2. Si pasa a Entregada por primera vez, sumamos al almacén central
                if (nuevo_estado == 'Entregada' and don['estado'] != 'Entregada'
                        and don['recurso'] and don['cantidad']):
                    cursor.execute(
                        """SELECT id FROM recurso
                           WHERE olla_id IS NULL
                             AND LOWER(nombre_recurso) = LOWER(%s)
                             AND unidad_medida = %s
                           LIMIT 1""",
                        (don['recurso'], don['unidad_medida'])
                    )
                    existente = cursor.fetchone()

                    if existente:
                        cursor.execute(
                            """UPDATE recurso
                               SET cantidad = cantidad + %s, fecha_actualizacion = CURRENT_TIMESTAMP
                               WHERE id = %s""",
                            (don['cantidad'], existente['id'])
                        )
                    else:
                        cursor.execute(
                            """INSERT INTO recurso (olla_id, nombre_recurso, cantidad, unidad_medida)
                               VALUES (NULL, %s, %s, %s)""",
                            (don['recurso'], don['cantidad'], don['unidad_medida'])
                        )

                # 3. Cambiamos el estado de la donación
                cursor.execute("UPDATE Donacion SET estado = %s WHERE id = %s", (nuevo_estado, id_donacion))

            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"Error en cambiar_estado_donacion: {e}")
            return False
        finally:
            conexion.close()