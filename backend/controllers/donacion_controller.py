from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.dao.donacion_dao import DonacionDAO
from backend.models.donacion import Donacion

donacion_bp = Blueprint('donacion', __name__)

# ==========================================
# VISTA: MOSTRAR MIS DONACIONES (GET)
# ==========================================
@donacion_bp.route('/mis-donaciones', methods=['GET'])
def mis_donaciones_view():
    if session.get('rol') != 'DONADOR':
        return redirect(url_for('home'))
        
    usuario_id = session.get('usuario_id')
    lista_donaciones = DonacionDAO.listar_mis_donaciones(usuario_id)
    return render_template('mis_donaciones.html', mis_donaciones=lista_donaciones)

# ==========================================
# FLUJOS DEL DONADOR
# ==========================================
@donacion_bp.route('/donaciones/registrar', methods=['POST'])
def registrar_donacion():
    if session.get('rol') != 'DONADOR':
        return redirect(url_for('home'))
        
    try:
        donador_id = session.get('usuario_id')
        olla_id = int(request.form.get('olla_comun_id'))
        
        tipo = request.form.get('tipo_recurso', '').strip()
        if tipo == 'Otro':
            tipo = request.form.get('tipo_otro', '').strip()
        tipo = tipo.title()
        cantidad = request.form.get('cantidad', '').strip()
        unidad = request.form.get('unidad', '').strip().lower()       # "KG" -> "kg"
        desc = request.form.get('descripcion', '').strip()
        
        if not tipo or not cantidad or not unidad:
            flash('Error: Los campos de tipo, cantidad y unidad son obligatorios.', 'error')
            return redirect(url_for('donacion.mis_donaciones_view'))
        
        cantidad_num = float(cantidad)
        if cantidad_num <= 0:
            flash('Error: La cantidad debe ser mayor a cero.', 'error')
            return redirect(url_for('donacion.mis_donaciones_view'))
        
        mensaje_final = f"{tipo}: {cantidad} {unidad}. Nota: {desc}"
            
        nueva_donacion = Donacion(
            donador_id=donador_id,
            olla_id=olla_id,
            mensaje=mensaje_final,
            recurso=tipo,
            cantidad=cantidad_num,
            unidad_medida=unidad
        )
        
        if DonacionDAO.registrar_donacion(nueva_donacion):
            flash('Donación registrada exitosamente. ¡Gracias por tu aporte!', 'success')
        else:
            flash('Error al registrar la donación.', 'error')
            
    except ValueError:
        flash('Error en los datos enviados. Verifica la cantidad o la olla seleccionada.', 'error')
        
    return redirect(url_for('donacion.mis_donaciones_view'))

@donacion_bp.route('/donaciones/actualizar', methods=['POST'])
def actualizar_donacion():
    if session.get('rol') != 'DONADOR':
        return redirect(url_for('home'))
        
    id_donacion = request.form.get('idDonacion')
    nuevo_mensaje = request.form.get('mensaje')
    
    if DonacionDAO.actualizar_donacion(id_donacion, nuevo_mensaje):
        flash('Mensaje de donación actualizado con éxito.', 'success')
    else:
        flash('Error al actualizar la donación.', 'error')
        
    return redirect(url_for('donacion.mis_donaciones_view'))

@donacion_bp.route('/donaciones/eliminar', methods=['POST'])
def eliminar_donacion():
    if session.get('rol') != 'DONADOR':
        return redirect(url_for('home'))
        
    id_donacion = request.form.get('idDonacion')
    
    if DonacionDAO.eliminar_donacion(id_donacion):
        flash('Donación cancelada y eliminada con éxito.', 'success')
    else:
        flash('Error al eliminar la donación.', 'error')
        
    return redirect(url_for('donacion.mis_donaciones_view'))

# ==========================================
# FLUJOS DEL ADMINISTRADOR
# ==========================================
@donacion_bp.route('/admin/donaciones/estado', methods=['POST'])
def cambiar_estado_donacion():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    id_donacion = request.form.get('idDonacion')
    nuevo_estado = request.form.get('nuevoEstado', '').strip()
    
    # CORREGIDO: Añadido 'Rechazada' a los estados permitidos
    estados_validos = ['Pendiente', 'Aceptada', 'Entregada', 'Rechazada']
    if nuevo_estado not in estados_validos:
        flash('Error: Estado de donación no permitido.', 'error')
        return redirect(url_for('donacion.admin_donaciones_view')) # CORREGIDO con prefijo
    
    if DonacionDAO.cambiar_estado_donacion(id_donacion, nuevo_estado):
        flash('Estado de la donación actualizado.', 'success')
    else:
        flash('Error al cambiar el estado de la donación.', 'error')
        
    return redirect(url_for('donacion.admin_donaciones_view')) # CORREGIDO con prefijo

# ==========================================
# VISTA: MOSTRAR DONACIONES GLOBALES (GET)
# ==========================================
@donacion_bp.route('/admin/donaciones', methods=['GET'])
def admin_donaciones_view():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    lista_donaciones = DonacionDAO.listar_todas_las_donaciones_admin()
    return render_template('admin_donaciones.html', lista_donaciones=lista_donaciones)