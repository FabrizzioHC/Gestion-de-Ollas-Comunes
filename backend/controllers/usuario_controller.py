from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.dao.usuario_dao import UsuarioDAO
from backend.models.usuario import Usuario
from backend.models.olla_comun import OllaComun
from backend.dao.olla_dao import OllaDAO
from werkzeug.security import check_password_hash
from datetime import datetime

# Creamos el Blueprint para los usuarios. 
# Esto nos permite registrar todas estas rutas en el app principal de forma ordenada.
usuario_bp = Blueprint('usuario', __name__)

# ==========================================
# FLUJO 1: INICIAR SESIÓN Y LOGOUT
# ==========================================
@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = UsuarioDAO.obtener_por_email(email)
        
        if not usuario:
            flash('Correo o contraseña incorrectos.', 'danger') 
            return render_template('login.html')

        # 1. Verificar si el usuario está desactivado permanentemente por un admin
        if not usuario.activo:
            flash('Tu cuenta ha sido suspendida. Contacta al administrador.', 'danger')
            return render_template('login.html')

        # 2. Verificar el bloqueo TEMPORAL de 3 minutos
        if usuario.bloqueado_hasta:
            if usuario.bloqueado_hasta > datetime.now():
                flash('Has superado los intentos permitidos. Intenta de nuevo en 3 minutos.', 'danger')
                return render_template('login.html')
            else:
                # Si el tiempo ya pasó, le reiniciamos los intentos para darle otra oportunidad
                UsuarioDAO.reiniciar_intentos(usuario.id)
                usuario.intentos_fallidos = 0

        # 3. Validar la contraseña
        PREFIJO = "scrypt:32768:8:1$"
        hash_completo = PREFIJO + usuario.password_hash
        
        if check_password_hash(hash_completo, password):
            UsuarioDAO.reiniciar_intentos(usuario.id)
            
            session['usuario_id'] = usuario.id
            session['rol'] = usuario.rol
            session['nombres'] = usuario.nombres

            flash(f'¡Bienvenido, {usuario.nombres}!', 'welcome')
            return redirect(url_for('home'))
        else:
            intentos_actuales = getattr(usuario, 'intentos_fallidos', 0)
            nuevos_intentos = UsuarioDAO.registrar_intento_fallido(usuario.id, intentos_actuales)
            
            if nuevos_intentos >= 3:
                flash('Por seguridad, tu cuenta ha sido bloqueada durante 3 minutos.', 'danger')
            else:
                intentos_restantes = 3 - nuevos_intentos
                flash(f'Contraseña incorrecta. Te quedan {intentos_restantes} intento(s).', 'warning')
                
            return render_template('login.html')
            
    return render_template('login.html')

@usuario_bp.route('/logout')
def logout():
    session.clear() # Destruimos la sesión completa
    return redirect(url_for('home'))

# ==========================================
# FLUJO 2: REGISTRO (DONADOR O LIDERESA)
# ==========================================
# ==========================================
# FLUJO 2: REGISTRO (DONADOR O LIDERESA)
# ==========================================
@usuario_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        datos = request.form
        dni = datos.get('dni', '').strip()
        email = datos.get('email', '').strip().lower()
        rol = datos.get('rol', 'DONADOR')
        nombre_olla = datos.get('nombreOlla', '').strip()

        # 1. VALIDACIONES
        error = None
        if rol not in ('DONADOR', 'LIDERESA'):
            error = 'Rol no válido.'
        elif not (dni.isdigit() and len(dni) == 8):
            error = 'El DNI debe tener exactamente 8 números.'
        elif UsuarioDAO.existe_dni(dni):
            error = 'Ese DNI ya está registrado.'
        elif UsuarioDAO.existe_email(email):
            error = 'Ese correo ya está registrado.'
        elif rol == 'LIDERESA' and not nombre_olla:
            error = 'Debes indicar el nombre de la olla común.'
        elif rol == 'LIDERESA' and OllaDAO.existe_nombre_olla(nombre_olla):
            error = 'Ya existe una olla común con ese nombre.'

        if error:
            flash(error, 'error')
            return render_template('registro.html', datos=datos)

        # 2. Capturamos los datos
        nuevo_usuario = Usuario(
            email=email,
            password_hash=datos.get('password'),
            nombres=datos.get('nombres', '').strip(),
            apellidos=datos.get('apellidos', '').strip(),
            telefono=datos.get('telefono', '').strip(),
            dni=dni,
            rol=rol
        )

        # 3. Evaluamos el rol para decidir cómo guardar
        if rol == 'LIDERESA':
            nueva_olla = OllaComun(
                nombre_olla=nombre_olla,
                direccion=datos.get('direccionOlla', '').strip(),
                descripcion=datos.get('descripcionOlla', '').strip()
            )
            registro_exitoso = UsuarioDAO.registrar_lideresa_con_olla(nuevo_usuario, nueva_olla)
        else:
            registro_exitoso = UsuarioDAO.registrar_usuario(nuevo_usuario)

        # 4. Respuesta
        if registro_exitoso:
            flash('Registro exitoso. ¡Ahora puedes iniciar sesión!', 'success')
            return redirect(url_for('usuario.login'))
        else:
            flash('Error al registrar. Inténtalo de nuevo.', 'error')
            return render_template('registro.html', datos=datos)

    return render_template('registro.html', datos={})

# ==========================================
# VISTA: MOSTRAR MI PERFIL (GET)
# ==========================================
@usuario_bp.route('/perfil', methods=['GET'])
def perfil_view():
    # 1. Validamos que el usuario esté logueado
    if 'usuario_id' not in session:
        return redirect(url_for('usuario.login'))
        
    # 2. Buscamos toda la información fresca del usuario en la Base de Datos
    usuario_actual = UsuarioDAO.buscar_por_id(session['usuario_id'])
    
    # 3. Renderizamos el HTML pasándole la variable 'usu' que espera Jinja2
    return render_template('perfil.html', usu=usuario_actual)

# ==========================================
# FLUJO 3: ACTUALIZAR PERFIL (MI PERFIL)
# ==========================================
@usuario_bp.route('/perfil/actualizar', methods=['POST'])
def actualizar_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('usuario.login'))
        
    # CAMBIO: Primero buscamos al usuario completo en la BD
    usuario = UsuarioDAO.buscar_por_id(session['usuario_id'])
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('home'))
        
    # Actualizamos solo los campos permitidos
    usuario.nombres = request.form.get('nombres')
    usuario.apellidos = request.form.get('apellidos')
    usuario.telefono = request.form.get('telefono')
    usuario.dni = request.form.get('dni')
    
    if UsuarioDAO.actualizar_usuario(usuario):
        session['nombres'] = usuario.nombres # Actualizamos el nombre en la sesión
        flash('Perfil actualizado correctamente', 'success')
    else:
        flash('Error al actualizar el perfil', 'error')
        
    return redirect(url_for('usuario.perfil_view')) # Ruta de la edit


# ==========================================
# VISTA: MOSTRAR GESTIÓN DE USUARIOS (GET)
# ==========================================
@usuario_bp.route('/admin/usuarios', methods=['GET'])
def admin_usuarios_view():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    lista_usuarios = UsuarioDAO.listar_todos()
    return render_template('admin_usuarios.html', lista_usuarios=lista_usuarios)

# ==========================================
# FLUJOS 4: ADMINISTRACIÓN DE USUARIOS (ADMIN)
# ==========================================
@usuario_bp.route('/admin/usuarios/agregar', methods=['POST'])
def admin_agregar_usuario():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    nuevo = Usuario(
        nombres=request.form.get('nombres'),
        apellidos=request.form.get('apellidos'),
        email=request.form.get('email'),
        dni=request.form.get('dni'),
        telefono=request.form.get('telefono'),
        rol=request.form.get('rol'),
        password_hash=request.form.get('password')
    )
    
    if UsuarioDAO.registrar_usuario(nuevo):
        flash('Usuario agregado exitosamente.', 'success')
    else:
        flash('Error al agregar usuario (Email/DNI duplicado).', 'error')
        
    return redirect(url_for('usuario.admin_usuarios_view'))

@usuario_bp.route('/admin/usuarios/editar', methods=['POST'])
def admin_editar_usuario():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    usuario = UsuarioDAO.buscar_por_id(request.form.get('idUsuario'))
    if usuario:
        usuario.nombres = request.form.get('nombres')
        usuario.apellidos = request.form.get('apellidos')
        usuario.email = request.form.get('email')
        usuario.rol = request.form.get('rol')
        usuario.telefono = request.form.get('telefono')
        usuario.dni = request.form.get('dni')
        
        if UsuarioDAO.actualizar_usuario_admin(usuario):
            flash('Usuario actualizado con éxito.', 'success')
        else:
            flash('Error al actualizar usuario.', 'error')
    else:
        flash('Usuario no encontrado.', 'error')
        
    return redirect(url_for('usuario.admin_usuarios_view'))

@usuario_bp.route('/admin/usuarios/eliminar', methods=['POST'])
def admin_eliminar_usuario():
    if session.get('rol') != 'ADMIN':
        return redirect(url_for('home'))
        
    id_usu = request.form.get('idUsu')
    
    if UsuarioDAO.eliminar_usuario_admin(id_usu):
        flash('Usuario desactivado con éxito.', 'success') 
    else:
        flash('Error al procesar la baja del usuario.', 'error')
        
    return redirect(url_for('usuario.admin_usuarios_view'))