from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.dao.solicitud_dao import SolicitudDAO
from backend.dao.olla_dao import OllaDAO  # Importamos el DAO de Olla
from backend.models.solicitud import Solicitud

# Creamos el Blueprint para separar las rutas de las solicitudes
solicitud_bp = Blueprint('solicitud', __name__)

# ==========================================
# VISTA: MOSTRAR MIS SOLICITUDES (GET)
# ==========================================
@solicitud_bp.route('/mis-solicitudes', methods=['GET'])
def gestion_solicitudes_view():
    if session.get('rol') != 'LIDERESA':
        return redirect(url_for('home'))
        
    usuario_id = session.get('usuario_id')
    mi_olla = OllaDAO.obtener_olla_por_lideresa_id(usuario_id)
    mis_solicitudes = []
    
    if mi_olla:
        mis_solicitudes = SolicitudDAO.listar_por_olla(mi_olla.id)
        
    return render_template('gestion_solicitudes.html', mi_olla=mi_olla, mis_solicitudes=mis_solicitudes)

# ==========================================
# FLUJOS DE LA LIDERESA
# ==========================================
@solicitud_bp.route('/solicitudes/crear', methods=['POST'])
def crear_solicitud():
    # 1. Validación de seguridad de rol
    if session.get('rol') != 'LIDERESA':
        return redirect(url_for('home'))
        
    # 2. Obtenemos el ID del usuario directamente de la sesión (100% seguro)
    usuario_id = session.get('usuario_id')
    
    # 3. Buscamos la olla real que le pertenece a esa lideresa
    olla_actual = OllaDAO.obtener_olla_por_lideresa_id(usuario_id)
    
    if not olla_actual:
        flash('Error: No tienes una olla común asignada para hacer solicitudes.', 'error')
        return redirect(url_for('home'))

    # 4. Creamos la solicitud inyectando el ID seguro desde el backend, ignorando el HTML
    nueva = Solicitud(
        olla_id=olla_actual.id, 
        recurso_necesitado=request.form.get('recursoNecesitado'),
        cantidad_necesitada=float(request.form.get('cantidad')),
        unidad_medida=request.form.get('unidadMedida'),
        nivel_urgencia=request.form.get('nivelUrgencia')
    )
    
    if SolicitudDAO.crear_solicitud(nueva):
        flash('Solicitud creada con éxito.', 'success')
    else:
        flash('Error al crear la solicitud.', 'error')
        
    return redirect(url_for('solicitud.gestion_solicitudes_view')) 

@solicitud_bp.route('/solicitudes/actualizar', methods=['POST'])
def actualizar_solicitud():
    if session.get('rol') != 'LIDERESA':
        return redirect(url_for('home'))
        
    editada = Solicitud(
        id=request.form.get('idSolicitud'),
        recurso_necesitado=request.form.get('recursoNecesitado'),
        cantidad_necesitada=float(request.form.get('cantidad')),
        unidad_medida=request.form.get('unidadMedida'),
        nivel_urgencia=request.form.get('nivelUrgencia')
    )
    
    if SolicitudDAO.actualizar_solicitud(editada):
        flash('Solicitud actualizada con éxito.', 'success')
    else:
        flash('Error al actualizar la solicitud.', 'error')
        
    return redirect(url_for('solicitud.gestion_solicitudes_view'))

@solicitud_bp.route('/solicitudes/eliminar', methods=['POST'])
def eliminar_solicitud():
    if session.get('rol') != 'LIDERESA':
        return redirect(url_for('home'))
        
    id_solicitud = request.form.get('idSolicitud')
    
    if SolicitudDAO.eliminar_solicitud(id_solicitud):
        flash('Solicitud eliminada con éxito.', 'success')
    else:
        flash('Error al eliminar la solicitud.', 'error')
        
    return redirect(url_for('solicitud.gestion_solicitudes_view'))

# ==========================================
# FLUJOS DEL ADMINISTRADOR
# ==========================================
@solicitud_bp.route('/admin/solicitudes/estado', methods=['POST'])
def cambiar_estado_solicitud():
    # Validación de seguridad: Solo el Administrador aprueba/rechaza
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    id_solicitud = request.form.get('idSolicitud')
    nuevo_estado = request.form.get('nuevoEstado')
    
    if SolicitudDAO.cambiar_estado_solicitud(id_solicitud, nuevo_estado):
        flash('Estado de la solicitud actualizado correctamente.', 'success')
    else:
        flash('Error al cambiar el estado de la solicitud.', 'error')
        
    # Agregado el prefijo 'solicitud.' para cuando creemos la vista del admin
    return redirect(url_for('solicitud.admin_solicitudes_view'))

# ==========================================
# VISTA: MOSTRAR SOLICITUDES GLOBALES (GET)
# ==========================================
@solicitud_bp.route('/admin/solicitudes', methods=['GET'])
def admin_solicitudes_view():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    # Llamamos al DAO para traer todas las solicitudes
    todas_las_solicitudes = SolicitudDAO.listar_todas_las_solicitudes()
    
    return render_template('admin_solicitudes.html', todas_las_solicitudes=todas_las_solicitudes)