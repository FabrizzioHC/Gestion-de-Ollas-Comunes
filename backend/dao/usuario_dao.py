from backend.config.database import get_connection
from backend.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

PREFIJO = "scrypt:32768:8:1$"

class UsuarioDAO:

    @staticmethod
    def iniciar_sesion(email, password_plana):
        conexion = get_connection()
        if not conexion:
            return None
        
        try:
            with conexion.cursor() as cursor:
                # Solo buscamos por email y activo. La contraseña se verifica después con el hash.
                sql = "SELECT * FROM Usuario WHERE email = %s AND activo = True"
                cursor.execute(sql, (email,))
                resultado = cursor.fetchone()

                # check_password_hash compara el texto plano con el hash seguro guardado en la BD
                if resultado and check_password_hash(PREFIJO + resultado['password_hash'], password_plana):
                    return Usuario(**resultado) # Desempaqueta el diccionario directamente al modelo
        except Exception as e:
            print(f"Error en iniciar_sesion: {e}")
        finally:
            conexion.close()
            
        return None

    @staticmethod
    def registrar_usuario(usuario):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO Usuario (email, password_hash, nombres, apellidos, rol, telefono, dni) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                # Encriptamos la contraseña antes de guardarla
                hash_seguro = generate_password_hash(usuario.password_hash).replace(PREFIJO, "")
                
                cursor.execute(sql, (
                    usuario.email, hash_seguro, usuario.nombres, 
                    usuario.apellidos, usuario.rol, usuario.telefono, usuario.dni
                ))
            conexion.commit() # Guarda los cambios
            return True
        except Exception as e:
            print(f"Error en registrar_usuario: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def registrar_lideresa_con_olla(usuario, olla):
        conexion = get_connection()
        if not conexion:
            return False
            
        try:
            # Inicia la transacción automáticamente (equivalente a setAutoCommit(false))
            with conexion.cursor() as cursor:
                # PASO 1: Insertar el Usuario
                sql_usuario = "INSERT INTO Usuario (email, password_hash, nombres, apellidos, rol, telefono, dni) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                hash_seguro = generate_password_hash(usuario.password_hash).replace(PREFIJO, "")
                
                cursor.execute(sql_usuario, (
                    usuario.email, hash_seguro, usuario.nombres, 
                    usuario.apellidos, usuario.rol, usuario.telefono, usuario.dni
                ))
                
                # Capturamos el ID autogenerado por MySQL (equivalente a Statement.RETURN_GENERATED_KEYS)
                id_lideresa_generado = cursor.lastrowid
                
                # PASO 2: Insertar la Olla Común
                sql_olla = "INSERT INTO Olla_Comun (usuario_id, nombre_olla, descripcion, direccion) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_olla, (
                    id_lideresa_generado, olla.nombre_olla, 
                    olla.descripcion, olla.direccion
                ))
                
            conexion.commit() # Si todo sale bien, aplicamos commit
            return True
        except Exception as e:
            conexion.rollback() # Si hay un error, revertimos ambas inserciones
            print(f"Error en transacción de Lideresa: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def actualizar_usuario(usuario):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE Usuario SET nombres = %s, apellidos = %s, telefono = %s, dni = %s WHERE id = %s"
                cursor.execute(sql, (usuario.nombres, usuario.apellidos, usuario.telefono, usuario.dni, usuario.id))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en actualizar_usuario: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def buscar_por_id(id_usuario):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Usuario WHERE id = %s"
                cursor.execute(sql, (id_usuario,))
                resultado = cursor.fetchone()
                if resultado:
                    return Usuario(**resultado)
        except Exception as e:
            print(f"Error al buscar usuario: {e}")
        finally:
            conexion.close()
        return None

    @staticmethod
    def listar_todos():
        lista = []
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Usuario ORDER BY fecha_creacion DESC"
                cursor.execute(sql)
                resultados = cursor.fetchall()
                for fila in resultados:
                    lista.append(Usuario(**fila))
        except Exception as e:
            print(f"Error en listar_todos: {e}")
        finally:
            conexion.close()
        return lista

    @staticmethod
    def actualizar_usuario_admin(usuario):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE Usuario SET nombres=%s, apellidos=%s, email=%s, rol=%s, telefono=%s, dni=%s WHERE id=%s"
                cursor.execute(sql, (
                    usuario.nombres, usuario.apellidos, usuario.email, 
                    usuario.rol, usuario.telefono, usuario.dni, usuario.id
                ))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en actualizar_usuario_admin: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def eliminar_usuario_admin(id_usuario):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "DELETE FROM Usuario WHERE id=%s"
                cursor.execute(sql, (id_usuario,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error eliminar_usuario_admin: {e}")
            return False
        finally:
            conexion.close()

        # Comprueba si ya existe un DNI o correo (excluir_id sirve al editar un usuario)
    @staticmethod
    def _existe(campo, valor, excluir_id=None):
        if campo not in ("dni", "email"):
            return False
        conexion = get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                sql = f"SELECT 1 FROM Usuario WHERE {campo} = %s"
                params = [valor]
                if excluir_id:
                    sql += " AND id <> %s"
                    params.append(excluir_id)
                sql += " LIMIT 1"
                cursor.execute(sql, params)
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error en _existe({campo}): {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def existe_dni(dni, excluir_id=None):
        return UsuarioDAO._existe("dni", dni, excluir_id)

    @staticmethod
    def existe_email(email, excluir_id=None):
        return UsuarioDAO._existe("email", email, excluir_id)

    @classmethod
    def registrar_intento_fallido(cls, usuario_id, intentos_actuales=None):
        conexion = get_connection()
        if not conexion:
            raise RuntimeError("No disponible la base de datos")

        try:
            # Garantiza una transacción activa antes del SELECT FOR UPDATE.
            # Necesario para que los intentos simultáneos no pierdan incrementos.
            conexion.begin()
            with conexion.cursor() as cursor:
                # Bloquea la fila para evitar conflictos
                # cuando llegan varias peticiones simultáneas.
                cursor.execute("""
                    SELECT COALESCE(intentos_fallidos, 0) AS intentos,
                        GREATEST(
                            COALESCE(
                                TIMESTAMPDIFF(
                                    SECOND, NOW(), bloqueado_hasta
                                ), 0
                            ), 0
                        ) AS espera
                    FROM Usuario
                    WHERE id = %s
                    FOR UPDATE
                """, (usuario_id,))

                fila = cursor.fetchone()
                if not fila:
                    raise ValueError("Usuario no encontrado")

                intentos = int(fila["intentos"])
                espera = int(fila["espera"])

                # Si sigue bloqueado, no contar otro intento.
                if espera > 0:
                    conexion.commit()
                    return intentos, espera

                intentos += 1

                # Duración progresiva de los bloqueos
                if intentos >= 12:
                    segundos = 86400   # 24 horas
                elif intentos == 9:
                    segundos = 3600    # 1 hora
                elif intentos == 6:
                    segundos = 900     # 15 minutos
                elif intentos == 3:
                    segundos = 180     # 3 minutos
                else:
                    segundos = 0

                cursor.execute("""
                    UPDATE Usuario
                    SET intentos_fallidos = %s,
                        bloqueado_hasta =
                            CASE WHEN %s > 0
                            THEN DATE_ADD(
                                NOW(), INTERVAL %s SECOND
                            )
                            ELSE NULL END
                    WHERE id = %s
                """, (
                    intentos, segundos,
                    segundos, usuario_id
                ))

            conexion.commit()
            return intentos, segundos

        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @classmethod
    def reiniciar_intentos(cls, usuario_id):
        conexion = get_connection()
        if not conexion:
            raise RuntimeError("No disponible la base de datos")
        try:
            with conexion.cursor() as cursor:
                # Se reinicia únicamente tras un inicio de sesión correcto.
                sql = "UPDATE Usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id = %s"
                cursor.execute(sql, (usuario_id,))
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_email(email):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM Usuario WHERE email = %s"
                cursor.execute(sql, (email,))
                resultado = cursor.fetchone()
                if resultado:
                    return Usuario(**resultado)
        except Exception as e:
            print(f"Error al buscar por email: {e}")
        finally:
            if conexion:
                conexion.close()
        return None