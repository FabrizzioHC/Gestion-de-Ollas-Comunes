import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "sistema_ollas_comunes_vs_2"),  # -- es bueno tambien cambiar el nombre aca --
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error de conexión a la Base de Datos: {e}")
        return None

# --- METODO DE PRUEBA ---
if __name__ == "__main__":
    conexion = get_connection()
    if conexion:
        print("¡ÉXITO! Conexión perfecta a la base de datos sistema_ollas_comunes_vs.")
        conexion.close()
    else:
        print("¡ERROR! No se pudo conectar. Revisa tu MySQL y credenciales.")