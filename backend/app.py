"""
CAPA DE INTERFACES - API REST con Flask
Expone los endpoints HTTP para el frontend
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from werkzeug.security import generate_password_hash

from config import config
from infrastructure.database import Database
from infrastructure.repositories import (
    SQLiteUserRepository, SQLiteOllaComunRepository, SQLiteDonacionRepository,
    SQLiteSolicitudRecursoRepository, SQLiteEntregaRepository
)
from domain.services import (
    AuthService, OllaComunService, DonacionService, SolicitudRecursoService
)

# Inicialización
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"])
jwt = JWTManager(app)

# Base de datos
db = Database()

# Repositorios
user_repo = SQLiteUserRepository(db)
olla_repo = SQLiteOllaComunRepository(db)
donacion_repo = SQLiteDonacionRepository(db)
solicitud_repo = SQLiteSolicitudRecursoRepository(db)
entrega_repo = SQLiteEntregaRepository(db)

# Servicios
auth_service = AuthService(user_repo)
olla_service = OllaComunService(olla_repo)
donacion_service = DonacionService(donacion_repo)
solicitud_service = SolicitudRecursoService(solicitud_repo)


# ============================================================================
# UTILIDADES JWT
# ============================================================================

def get_current_user_id():
    """Obtiene el ID de usuario desde el JWT y lo convierte a entero."""
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


# ============================================================================
# DECORADOR DE AUTORIZACIÓN POR ROL
# ============================================================================
def role_required(*roles):
    """Decorador para verificar roles de usuario"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_current_user_id()
            user = user_repo.find_by_id(user_id)
            if not user or user.role not in roles:
                return jsonify({"error": "Acceso denegado"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registra un nuevo usuario"""
    data = request.get_json()
    
    # Validación básica
    if not all([data.get('email'), data.get('password'), data.get('nombre'), data.get('role')]):
        return jsonify({"error": "Campos requeridos: email, password, nombre, role"}), 400

    olla_asociada_id = data.get('olla_asociada_id')
    if isinstance(olla_asociada_id, str):
        olla_asociada_id = olla_asociada_id.strip()
        if olla_asociada_id.isdigit():
            olla_asociada_id = int(olla_asociada_id)
        elif olla_asociada_id == '':
            olla_asociada_id = None

    if data['role'] == 'beneficiario' and olla_asociada_id is None:
        ollas_disponibles = olla_service.list_ollas()
        if ollas_disponibles:
            primera_olla = ollas_disponibles[0]
            olla_asociada_id = primera_olla.get('id') if isinstance(primera_olla, dict) else getattr(primera_olla, 'id', None)
    
    result = auth_service.register_user(
        email=data['email'],
        password=data['password'],
        nombre=data['nombre'],
        role=data['role'],
        telefono=data.get('telefono'),
        dni=data.get('dni'), #beneficiario
        edad=data.get('edad'),
        vulnerabilidad=data.get('vulnerabilidad'),
        olla_asociada_id=olla_asociada_id
    )
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify({
        "message": "Usuario registrado exitosamente",
        "user_id": result['user_id']
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Autentica un usuario y retorna un JWT token"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email y password requeridos"}), 400
    
    result = auth_service.authenticate(data['email'], data['password'])
    
    if not result['success']:
        return jsonify(result), 401
    
    # Crear token JWT con subject como cadena
    access_token = create_access_token(identity=str(result['user_id']))
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": result['user_id'],
            "email": result['email'],
            "nombre": result['nombre'],
            "role": result['role'],
            "telefono": result.get('telefono')
        }
    }), 200


@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtiene el perfil del usuario autenticado"""
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Token inválido"}), 401
    user_data = auth_service.get_user(user_id)
    
    if not user_data:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    return jsonify(user_data), 200


# ============================================================================
# Gestion de Usuarios
# ============================================================================
@app.route('/api/usuarios', methods=['GET'])
@role_required('admin')
def get_usuarios():
    print("¡Ruta /api/usuarios alcanzada!") # Esto servirá para confirmar en la terminal
    usuarios = user_repo.find_all()
    return jsonify([
        {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "rol": u.role,
            "activo": u.activo,
            "telefono": u.telefono
        } for u in usuarios
    ])


# Endpoint para actualizar perfil de usuario
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current = get_current_user_id()
    if current is None:
        return jsonify({"error": "Token inválido"}), 401
    # solo el usuario o admin puede actualizar
    user = user_repo.find_by_id(current)
    if current != user_id and (not user or user.role != 'admin'):
        return jsonify({"error": "Permiso denegado"}), 403

    data = request.get_json() or {}
    allowed = ['nombre', 'telefono', 'email']
    if user and user.role == 'admin':
        allowed.extend(['role', 'activo'])

    update_data = {k: v for k, v in data.items() if k in allowed}

    if 'activo' in update_data:
        if isinstance(update_data['activo'], str):
            update_data['activo'] = update_data['activo'].lower() in ['true', '1', 'yes', 'on']
        else:
            update_data['activo'] = bool(update_data['activo'])

    if 'password' in data and data.get('password'):
        update_data['password'] = generate_password_hash(data['password'])

    if not update_data:
        return jsonify({"error": "No hay campos para actualizar"}), 400

    success = user_repo.update(user_id, update_data)
    if not success:
        return jsonify({"error": "No se pudo actualizar el usuario"}), 400

    updated = auth_service.get_user(user_id)
    return jsonify(updated), 200


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    if user_id == get_current_user_id():
        return jsonify({"error": "No puedes eliminar tu propia cuenta"}), 400

    success = user_repo.delete(user_id)
    if not success:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"success": True}), 200


# ============================================================================
# RUTAS DE OLLAS COMUNES
# ============================================================================
@app.route('/api/ollas', methods=['GET'])
def list_ollas():
    """Lista todas las ollas comunes.

    Por defecto no se devuelven las solicitudes pendientes a la vista pública.
    Se puede filtrar por estado enviando el parámetro ?estado=pendiente.
    """
    estado = request.args.get('estado')
    if estado:
        ollas = olla_service.list_ollas(estado)
    else:
        # Excluir solicitudes pendientes en la lista pública
        ollas = [olla for olla in olla_service.list_ollas() if olla.get('estado') != 'pendiente']
    return jsonify(ollas), 200


@app.route('/api/ollas/<int:olla_id>', methods=['GET'])
def get_olla(olla_id):
    """Obtiene una olla común específica"""
    olla = olla_service.get_olla(olla_id)
    if not olla:
        return jsonify({"error": "Olla no encontrada"}), 404
    return jsonify(olla), 200


@app.route('/api/ollas', methods=['POST'])
def create_olla():
    """Crea una nueva olla común.

    Si hay token JWT válido, el usuario debe ser de tipo `olla_comun`.
    Si no hay token, se permite crear la olla en estado 'pendiente' para revisión.
    """
    data = request.get_json() or {}
    if not all([data.get('nombre'), data.get('direccion')]):
        return jsonify({"error": "Campos requeridos: nombre, direccion"}), 400

    user_id = None
    unauthenticated = False
    try:
        identity = get_jwt_identity()
        if identity is not None:
            user_id = int(identity)
            user = user_repo.find_by_id(user_id)
            if not user or user.role != 'olla_comun':
                return jsonify({"error": "Solo las ollas comunes pueden crear registros con este token"}), 403
        else:
            unauthenticated = True
    except Exception:
        unauthenticated = True

    estado = 'pendiente' if unauthenticated else 'activa'
    if user_id is None:
        user_id = 0

    result = olla_service.create_olla(
        nombre=data['nombre'],
        usuario_id=user_id,
        descripcion=data.get('descripcion'),
        direccion=data['direccion'],
        telefono=data.get('telefono'),
        estado=estado
    )

    return jsonify(result), 201


@app.route('/api/ollas/<int:olla_id>', methods=['PUT'])
@role_required('admin', 'olla_comun')
def update_olla(olla_id):
    """Actualiza una olla común"""
    data = request.get_json()
    if olla_service.update_olla(olla_id, data):
        return jsonify({"message": "Olla actualizada"}), 200
    return jsonify({"error": "No se pudo actualizar"}), 400


@app.route('/api/ollas/<int:olla_id>', methods=['DELETE'])
@role_required('admin', 'olla_comun')
def delete_olla(olla_id):
    """Elimina una olla común"""
    if olla_service.delete_olla(olla_id):
        return jsonify({"message": "Olla eliminada"}), 200
    return jsonify({"error": "No se pudo eliminar"}), 400


# ============================================================================
# RUTAS DE DONACIONES
# ============================================================================
@app.route('/api/donaciones', methods=['GET'])
@jwt_required()
def list_donaciones():
    """Lista donaciones del usuario autenticado o, en admin, todas según filtro."""
    user_id = get_current_user_id()
    user = user_repo.find_by_id(user_id) if user_id is not None else None
    estado = request.args.get('estado')
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 401

    if user.role == 'admin':
        donaciones = donacion_service.list_donaciones(estado=estado)
    elif user.role == 'donador':
        donaciones = donacion_service.list_donaciones(estado=estado, donador_id=user.id)
    elif user.role == 'olla_comun':
        olla = olla_repo.find_by_usuario(user.id)
        olla_id = olla[0].id if olla else None
        donaciones = donacion_service.list_donaciones(estado=estado, olla_comun_id=olla_id) if olla_id else []
    else:
        donaciones = []

    return jsonify(donaciones), 200


@app.route('/api/donaciones/public', methods=['GET'])
def list_donaciones_public():
    """Lista pública de donaciones para la vista de donación."""
    estado = request.args.get('estado')
    donaciones = donacion_repo.find_all(estado)

    resultado = []
    for donacion in donaciones:
        donor = user_repo.find_by_id(donacion.donador_id)
        olla = olla_repo.find_by_id(donacion.olla_comun_id) if donacion.olla_comun_id else None

        resultado.append({
            "id": donacion.id,
            "donante": donor.nombre if donor else f"Usuario #{donacion.donador_id}",
            "recurso": donacion.tipo_recurso,
            "cantidad": f"{donacion.cantidad} {donacion.unidad}",
            "destino": olla.nombre if olla else f"Olla #{donacion.olla_comun_id}",
            "estado": donacion.estado,
            "fecha_creacion": donacion.fecha_creacion.isoformat()
        })

    return jsonify(resultado), 200


@app.route('/api/donaciones', methods=['POST'])
@jwt_required()
def create_donacion():
    """Crea una nueva donación"""
    user_id = get_jwt_identity()
    user = user_repo.find_by_id(user_id)
    
    if user.role != "donador":
        return jsonify({"error": "Solo los donadores pueden crear donaciones"}), 403
    
    data = request.get_json()
    if not all([data.get('olla_comun_id'), data.get('tipo_recurso'), 
                data.get('cantidad'), data.get('unidad')]):
        return jsonify({"error": "Campos requeridos incompletos"}), 400
    
    result = donacion_service.create_donacion(
        donador_id=user_id,
        olla_comun_id=data['olla_comun_id'],
        tipo_recurso=data['tipo_recurso'],
        cantidad=data['cantidad'],
        unidad=data['unidad'],
        descripcion=data.get('descripcion')
    )
    
    return jsonify(result), 201


@app.route('/api/donaciones/<int:donacion_id>', methods=['GET'])
@jwt_required()
def get_donacion(donacion_id):
    """Obtiene una donación específica"""
    donacion = donacion_service.get_donacion(donacion_id)
    if not donacion:
        return jsonify({"error": "Donación no encontrada"}), 404
    return jsonify(donacion), 200


@app.route('/api/donaciones/<int:donacion_id>/approve', methods=['POST'])
@role_required('admin')
def approve_donacion(donacion_id):
    """Aprueba una donación"""
    if donacion_service.approve_donacion(donacion_id):
        return jsonify({"message": "Donación aprobada"}), 200
    return jsonify({"error": "No se pudo aprobar"}), 400


@app.route('/api/donaciones/<int:donacion_id>/reject', methods=['POST'])
@role_required('admin')
def reject_donacion(donacion_id):
    """Rechaza una donación"""
    if donacion_service.reject_donacion(donacion_id):
        return jsonify({"message": "Donación rechazada"}), 200
    return jsonify({"error": "No se pudo rechazar"}), 400


# ============================================================================
# RUTAS DE SOLICITUDES DE RECURSOS
# ============================================================================
@app.route('/api/solicitudes', methods=['GET'])
@jwt_required()
def list_solicitudes():
    """Lista solicitudes de recursos"""
    estado = request.args.get('estado')
    solicitudes = solicitud_service.list_solicitudes(estado)
    return jsonify(solicitudes), 200


@app.route('/api/solicitudes', methods=['POST'])
@jwt_required()
def create_solicitud():
    """Crea una nueva solicitud de recurso"""
    user_id = get_jwt_identity()
    user = user_repo.find_by_id(user_id)
    
    if user.role != "olla_comun":
        return jsonify({"error": "Solo las ollas comunes pueden solicitar recursos"}), 403
    
    data = request.get_json()
    if not all([data.get('olla_comun_id'), data.get('tipo_recurso'), 
                data.get('cantidad'), data.get('unidad')]):
        return jsonify({"error": "Campos requeridos incompletos"}), 400
    
    result = solicitud_service.create_solicitud(
        olla_comun_id=data['olla_comun_id'],
        tipo_recurso=data['tipo_recurso'],
        cantidad=data['cantidad'],
        unidad=data['unidad'],
        urgencia=data.get('urgencia', 'normal'),
        descripcion=data.get('descripcion')
    )
    
    return jsonify(result), 201


@app.route('/api/solicitudes/<int:solicitud_id>/approve', methods=['POST'])
@role_required('admin')
def approve_solicitud(solicitud_id):
    """Aprueba una solicitud"""
    if solicitud_service.approve_solicitud(solicitud_id):
        return jsonify({"message": "Solicitud aprobada"}), 200
    return jsonify({"error": "No se pudo aprobar"}), 400


# ============================================================================
# RUTAS ADMIN
# ============================================================================
@app.route('/api/admin/dashboard', methods=['GET'])
@role_required('admin')
def admin_dashboard():
    """Obtiene estadísticas para el dashboard admin"""
    with db.get_cursor() as cursor:
        cursor.execute('SELECT COUNT(*) as total FROM users')
        total_users = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM ollas_comunes WHERE estado = "activa"')
        ollas_activas = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM donaciones WHERE estado = "pendiente"')
        donaciones_pendientes = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM solicitudes_recursos WHERE estado = "pendiente"')
        solicitudes_pendientes = cursor.fetchone()['total']
    
    return jsonify({
        "total_usuarios": total_users,
        "ollas_activas": ollas_activas,
        "donaciones_pendientes": donaciones_pendientes,
        "solicitudes_pendientes": solicitudes_pendientes
    }), 200


# ============================================================================
# RUTAS DE SALUD
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health():
    """Verifica el estado de la API"""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)

