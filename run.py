from flask import Flask, render_template, session, redirect, url_for
import os
from dotenv import load_dotenv

# Importamos los DAOs necesarios para las vistas públicas
from backend.dao.donacion_dao import DonacionDAO
from backend.dao.olla_dao import OllaDAO

# Importamos todos los blueprints de nuestros controladores
from backend.controllers.usuario_controller import usuario_bp
from backend.controllers.olla_controller import olla_bp
from backend.controllers.solicitud_controller import solicitud_bp
from backend.controllers.recurso_controller import recurso_bp
from backend.controllers.donacion_controller import donacion_bp

load_dotenv()

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'una_llave_super_secreta_para_desarrollo')

# Registramos los Blueprints (así Flask conoce todas las rutas)
app.register_blueprint(usuario_bp)
app.register_blueprint(olla_bp)
app.register_blueprint(solicitud_bp)
app.register_blueprint(recurso_bp)
app.register_blueprint(donacion_bp)

# ==========================================
# RUTAS PÚBLICAS Y NAVEGACIÓN PRINCIPAL
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ollas')
def ollas_publicas_view():
    # Asumimos que tienes este método en OllaDAO para listar las activas
    lista_ollas = OllaDAO.listar_todas_las_ollas_publicas() 
    return render_template('ollas.html', lista_ollas=lista_ollas)

@app.route('/donar')
def donar_view():
    # Listas necesarias para los select y la tabla de transparencia
    lista_ollas = DonacionDAO.listar_todas_ollas() 
    donaciones_globales = DonacionDAO.listar_donaciones_aprobadas_globales() 
    return render_template('donar.html', lista_ollas=lista_ollas, donaciones_globales=donaciones_globales)

@app.route('/dashboard')
def dashboard_view():
    # Protegemos el dashboard para que solo entren usuarios logueados
    if not session.get('usuario_id'):
        return redirect(url_for('usuario.login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)