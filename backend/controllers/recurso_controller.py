from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.dao.recurso_dao import RecursoDAO
from backend.dao.olla_dao import OllaDAO  # Importante para buscar la olla de la Lideresa

# Creamos el Blueprint para los recursos del almacén general y de ollas
recurso_bp = Blueprint('recurso', __name__)

# ==========================================
# FLUJOS DE LA LIDERESA (GESTIÓN DE SU OLLA)
# ==========================================
@recurso_bp.route('/gestion-recursos', methods=['GET'])
def gestion_recursos_view():
    # Validación: Solo lideresas
    if session.get('rol') != 'LIDERESA':
        return redirect(url_for('home'))
        
    usuario_id = session.get('usuario_id')
    
    # 1. Buscamos qué olla le pertenece a esta Lideresa
    mi_olla = OllaDAO.obtener_olla_por_lideresa_id(usuario_id)
    inventario = []
    
    # 2. Si tiene una olla, listamos sus recursos
    if mi_olla:
        inventario = OllaDAO.listar_recursos_por_olla(mi_olla.id)
        
    return render_template('gestion_recursos.html', mi_olla=mi_olla, inventario=inventario)

@recurso_bp.route('/recursos/agregar', methods=['POST'])
def agregar_recurso():
    if session.get('rol') != 'LIDERESA':
        return redirect(url_for('home'))
        
    usuario_id = session.get('usuario_id')
    nombre = request.form.get('nombreRecurso', '').strip().title()
    unidad = request.form.get('unidadMedida')

    try:
        cantidad = float(request.form.get('cantidad', ''))
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash('Error: La cantidad debe ser un número mayor a cero.', 'error')
        return redirect(url_for('recurso.gestion_recursos_view'))
    
    mi_olla = OllaDAO.obtener_olla_por_lideresa_id(usuario_id)
    
    if mi_olla:
        if RecursoDAO.agregar_recurso_olla(mi_olla.id, nombre, cantidad, unidad):
            flash('Recurso agregado correctamente al inventario.', 'success')
        else:
            flash('Error al agregar el recurso.', 'error')
    else:
        flash('Error: No se encontró una Olla Común asociada a tu cuenta.', 'error')
        
    return redirect(url_for('recurso.gestion_recursos_view'))


# ==========================================
# FLUJOS DEL ADMINISTRADOR (ALMACÉN GENERAL)
# ==========================================
@recurso_bp.route('/admin/recursos/agregar', methods=['POST'])
def registrar_almacen_general():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    nombre = request.form.get('nombreRecurso', '').strip().title()
    unidad = request.form.get('unidadMedida')

    try:
        cantidad = float(request.form.get('cantidad', ''))
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash('Error: La cantidad debe ser un número mayor a cero.', 'error')
        return redirect(url_for('recurso.admin_recursos_view'))
    
    if RecursoDAO.agregar_almacen_general(nombre, cantidad, unidad):
        flash('Recurso agregado al almacén general exitosamente.', 'success')
    else:
        flash('Error al agregar el recurso.', 'error')
        
    return redirect(url_for('recurso.admin_recursos_view'))

@recurso_bp.route('/admin/recursos/editar', methods=['POST'])
def editar_almacen_general():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    id_recurso = request.form.get('idRecurso')
    nombre = request.form.get('nombreRecurso')
    cantidad = float(request.form.get('cantidad'))
    unidad = request.form.get('unidadMedida')
    
    if RecursoDAO.actualizar_recurso(id_recurso, nombre, cantidad, unidad):
        flash('Recurso actualizado con éxito.', 'success')
    else:
        flash('Error al actualizar el recurso.', 'error')
        
    return redirect(url_for('recurso.admin_recursos_view'))

@recurso_bp.route('/admin/recursos/eliminar', methods=['POST'])
def eliminar_almacen_general():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    id_recurso = request.form.get('idRecurso')
    
    if RecursoDAO.eliminar_recurso(id_recurso):
        flash('Recurso eliminado del almacén general.', 'success')
    else:
        flash('Error al eliminar el recurso.', 'error')
        
    return redirect(url_for('recurso.admin_recursos_view'))

# ==========================================
# VISTA: MOSTRAR ALMACÉN GENERAL (GET)
# ==========================================
@recurso_bp.route('/admin/recursos', methods=['GET'])
def admin_recursos_view():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    # Consultamos al DAO
    stock_general = RecursoDAO.listar_almacen_general()
    
    return render_template('admin_recursos.html', stock_general=stock_general)