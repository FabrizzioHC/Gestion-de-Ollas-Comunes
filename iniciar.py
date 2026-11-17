"""Inicio local de Red Comunitaria. No modifica ni importa datos de MySQL."""
from __future__ import annotations
import hashlib
import importlib.util
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:5000'

def preparar_dependencias():
    requirements = ROOT / 'requirements.txt'
    fingerprint = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = Path(sys.prefix) / '.redcomunitaria-requirements.sha256'
    complete = all(importlib.util.find_spec(name) is not None for name in ('flask','pymysql','dotenv','werkzeug'))
    ready = marker.is_file() and marker.read_text(encoding='ascii').strip() == fingerprint
    if not complete or not ready:
        print('[1/3] Preparando las dependencias. La primera vez necesita Internet.', flush=True)
        result = subprocess.run([sys.executable,'-m','pip','install','-r',str(requirements)],cwd=ROOT)
        if result.returncode:
            print('No se pudieron instalar las dependencias. Revisa la conexion a Internet y vuelve a abrir INICIAR.bat.')
            return False
        marker.write_text(fingerprint,encoding='ascii')
    else:
        print('[1/3] Dependencias listas.',flush=True)
    return True

def preparar_configuracion():
    from dotenv import dotenv_values, load_dotenv, set_key
    env_path = ROOT / '.env'
    if not env_path.exists():
        # Crear solo si falta. Nunca reemplazar las credenciales del usuario.
        env_path.write_bytes((ROOT / '.env.example').read_bytes())
    values = dotenv_values(env_path)
    if not values.get('SECRET_KEY'):
        set_key(str(env_path),'SECRET_KEY',secrets.token_hex(32))
    load_dotenv(dotenv_path=env_path,override=True)
    return env_path

def comprobar_base_datos():
    import pymysql
    try:
        port = int(os.getenv('DB_PORT','3306'))
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError:
        print('DB_PORT debe contener un puerto valido, por ejemplo 3306. Edita el archivo .env.')
        return False
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST','localhost'),port=port,
            user=os.getenv('DB_USER','root'),password=os.getenv('DB_PASSWORD',''),
            database=os.getenv('DB_NAME','sistema_ollas_comunes_vs'),
            charset='utf8mb4',connect_timeout=5,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.execute("SHOW TABLES LIKE 'Usuario'")
                if not cursor.fetchone():
                    print('La conexion funciona, pero faltan las tablas del proyecto.')
                    print('Importa database/ollas_comunes.sql en una base nueva o elige en DB_NAME tu base existente.')
                    return False
        finally:
            connection.close()
    except pymysql.MySQLError as error:
        # No imprimir la cadena de conexion ni la contrasena.
        code = error.args[0] if error.args else 'desconocido'
        print(f'No se pudo conectar a MySQL (codigo {code}).')
        if code in (1045,1698):
            print('Revisa DB_USER y DB_PASSWORD en .env: deben ser tus credenciales de MySQL.')
        elif code == 1049:
            print('No existe la base indicada en DB_NAME. Elige tu base existente o importa el SQL una sola vez.')
        else:
            print('Comprueba que MySQL este encendido y revisa DB_HOST, DB_PORT y DB_NAME en .env.')
        return False
    print('[2/3] Conexion a MySQL lista.',flush=True)
    return True

def puerto_disponible():
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            if os.name == 'nt' and hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
            sock.bind(('127.0.0.1',5000))
    except OSError:
        print('No se puede usar el puerto 5000. Cierra la otra ventana que ejecuta Flask y vuelve a abrir INICIAR.bat.')
        return False
    return True

def abrir_cuando_este_listo(stop):
    # El navegador se abre solo cuando nuestra aplicacion responde.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic()+30
    while not stop.is_set() and time.monotonic()<deadline:
        try:
            with opener.open(URL,timeout=1) as response:
                if response.status==200 and not stop.is_set():
                    webbrowser.open(URL)
                    return
        except (OSError,urllib.error.URLError):
            pass
        stop.wait(.5)

def main():
    if sys.version_info < (3,9):
        print('Se necesita Python 3.9 o superior. Instala una version compatible de Python para Windows.')
        return 1
    if sys.prefix == sys.base_prefix:
        print('Abre INICIAR.bat para usar el entorno virtual del proyecto.')
        return 1
    os.chdir(ROOT)
    if not preparar_dependencias():return 1
    preparar_configuracion()
    if not comprobar_base_datos() or not puerto_disponible():return 1
    print('[3/3] Iniciando Red Comunitaria...',flush=True)
    print(f'Pagina: {URL}\nManten esta ventana abierta. Para detener el proyecto, presiona Ctrl+C.',flush=True)
    stop = threading.Event()
    worker=threading.Thread(target=abrir_cuando_este_listo,args=(stop,),daemon=True)
    worker.start()
    env=os.environ.copy()
    env['FLASK_DEBUG']='0'
    env['FLASK_SKIP_DOTENV']='1'
    process=None
    try:
        # Se usa la aplicacion original sin modificar run.py ni sus rutas.
        process=subprocess.Popen([sys.executable,'-m','flask','--app','run:app','run','--host','127.0.0.1','--port','5000'],cwd=ROOT,env=env)
        return process.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        stop.set()
        if process is not None and process.poll() is None:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

if __name__=='__main__':
    try:
        sys.exit(main())
    except (OSError,subprocess.SubprocessError):
        print('No se pudo completar el inicio. Comprueba que la carpeta este extraida y tengas permisos para escribir en ella.')
        sys.exit(1)
