from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.dao.olla_dao import OllaDAO
from backend.models.olla_comun import OllaComun

olla_bp = Blueprint('olla', __name__)

# ==========================================
# VISTA Y BÚSQUEDA DEL ADMIN (GET)
# ==========================================
@olla_bp.route('/admin/ollas', methods=['GET'])
def admin_ollas_view():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    # Recibimos el parámetro de búsqueda 'q' de la URL de forma segura
    q = request.args.get('q', '').strip()
    if len(q) > 100:
        q = q[:100]
        
    # Si hay texto de búsqueda usamos el DAO correspondiente
    if q:
        lista_ollas = OllaDAO.buscar_ollas_admin(q)
    else:
        lista_ollas = OllaDAO.listar_todas_admin()
        
    lideresas_disponibles = OllaDAO.listar_lideresas_sin_olla()
    
    # Ajustado a snake_case para coincidir con admin_ollas.html
    return render_template(
        'admin_ollas.html', 
        lista_ollas=lista_ollas, 
        lideresas_disponibles=lideresas_disponibles, 
        termino_busqueda=q
    )

# ==========================================
# FLUJOS DEL ADMINISTRADOR (POST)
# ==========================================
@olla_bp.route('/admin/ollas/agregar', methods=['POST'])
def admin_agregar_olla():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    try:
        nombre = request.form.get('nombre_olla', '').strip()
        direccion = request.form.get('direccion', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        estado = request.form.get('estado', '').strip()
        lideresa_id = int(request.form.get('usuario_id', 0))
        beneficiarios = int(request.form.get('beneficiarios', 0))
        
        estado_valido = estado in ["ACTIVA", "PAUSADA", "INACTIVA"]
        
        if (lideresa_id <= 0 or not nombre or len(nombre) > 150 or
            not direccion or len(direccion) > 255 or len(descripcion) > 2000 or
            beneficiarios < 0 or beneficiarios > 1000000 or not estado_valido):
            flash('Error de validación: Datos incorrectos o exceden el límite de caracteres.', 'error')
            return redirect(url_for('olla.admin_ollas_view'))
            
        nueva_olla = OllaComun(
            usuario_id=lideresa_id,
            nombre_olla=nombre,
            direccion=direccion,
            descripcion=descripcion,
            beneficiarios_atendidos=beneficiarios,
            estado=estado
        )
        
        if OllaDAO.registrar_olla_admin(nueva_olla):
            flash('Olla común registrada correctamente.', 'success')
        else:
            flash('Error al registrar la olla común.', 'error')
            
    except ValueError:
        flash('Error: Verifica que los valores numéricos sean correctos.', 'error')
        
    return redirect(url_for('olla.admin_ollas_view'))

@olla_bp.route('/admin/ollas/editar', methods=['POST'])
def admin_editar_olla():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    olla_editada = OllaComun(
        id=request.form.get('idOlla'),
        nombre_olla=request.form.get('nombre_olla'),
        direccion=request.form.get('direccion'),
        descripcion=request.form.get('descripcion'),
        beneficiarios_atendidos=int(request.form.get('beneficiarios', 0)),
        estado=request.form.get('estado')
    )
    
    if OllaDAO.actualizar_olla_admin(olla_editada):
        flash('Olla común actualizada con éxito.', 'success')
    else:
        flash('Error al actualizar la olla común.', 'error')
        
    return redirect(url_for('olla.admin_ollas_view'))

@olla_bp.route('/admin/ollas/eliminar', methods=['POST'])
def admin_eliminar_olla():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    id_olla = request.form.get('idOlla')
    
    if OllaDAO.eliminar_olla_admin(id_olla):
        flash('Olla común inactiva con éxito.', 'success')
    else:
        flash('Error al eliminar. La olla puede tener recursos, donaciones o solicitudes asociadas.', 'error')
        
    return redirect(url_for('olla.admin_ollas_view'))