let editingUserId = null;
let allUsuarios = [];
let searchListenerAdded = false;

async function cargarUsuarios() {
    try {
        const usuarios = await api.request('GET', '/usuarios');
        if (!usuarios) return;

        allUsuarios = usuarios;
        renderUsuariosTable(usuarios);
        setupSearchListener();
        setupFormListener();
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
    }
}

function renderUsuariosTable(usuarios) {
    const tbody = document.getElementById('usuariosTableBody');
    tbody.innerHTML = '';

    usuarios.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(user.nombre)}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>${escapeHtml(user.rol)}</td>
            <td>${user.activo ? 'Activo' : 'Inactivo'}</td>
            <td>
                <button type="button" class="btn btn-sm btn-warning btn-edit">Editar</button>
                <button type="button" class="btn btn-sm btn-danger btn-delete">Eliminar</button>
            </td>
        `;

        row.querySelector('.btn-edit').addEventListener('click', () => abrirModalUsuario(user));
        row.querySelector('.btn-delete').addEventListener('click', () => eliminarUsuario(user.id, user.nombre));
        tbody.appendChild(row);
    });
}

function setupSearchListener() {
    if (searchListenerAdded) return;
    const searchInput = document.getElementById('buscarUsuario');
    if (!searchInput) return;

    searchInput.addEventListener('input', () => {
        const term = searchInput.value.trim().toLowerCase();
        const filtered = allUsuarios.filter(user =>
            user.nombre.toLowerCase().includes(term) ||
            user.email.toLowerCase().includes(term) ||
            user.rol.toLowerCase().includes(term)
        );
        renderUsuariosTable(filtered);
    });
    searchListenerAdded = true;
}

function setupFormListener() {
    const form = document.getElementById('usuarioForm');
    if (!form) return;
    if (form.dataset.listenerAdded === 'true') return;

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        submitUsuarioForm();
    });
    form.dataset.listenerAdded = 'true';
}

function abrirModalUsuario(user = null) {
    editingUserId = user?.id || null;
    const modal = document.getElementById('usuarioModal');
    const title = document.getElementById('usuarioModalTitle');

    document.getElementById('usuarioId').value = user?.id || '';
    document.getElementById('usuarioEmail').value = user?.email || '';
    document.getElementById('usuarioNombre').value = user?.nombre || '';
    document.getElementById('usuarioRol').value = user?.rol || 'donador';
    document.getElementById('usuarioTelefono').value = user?.telefono || '';
    document.getElementById('usuarioActivo').checked = user ? user.activo : true;
    document.getElementById('usuarioPassword').value = '';

    title.textContent = user ? 'Editar Usuario' : 'Agregar Usuario';
    document.getElementById('usuarioSubmitBtn').textContent = user ? 'Guardar Cambios' : 'Crear Usuario';

    bootstrap.Modal.getOrCreateInstance(modal).show();
}

async function submitUsuarioForm() {
    const email = document.getElementById('usuarioEmail').value.trim();
    const nombre = document.getElementById('usuarioNombre').value.trim();
    const role = document.getElementById('usuarioRol').value;
    const telefono = document.getElementById('usuarioTelefono').value.trim() || null;
    const activo = document.getElementById('usuarioActivo').checked;
    const password = document.getElementById('usuarioPassword').value.trim();
    const modalElement = document.getElementById('usuarioModal');

    if (!email || !nombre || !role) {
        alert('Completa el nombre, el email y el rol.');
        return;
    }

    try {
        if (editingUserId) {
            const data = { nombre, email, role, telefono, activo };
            if (password) {
                data.password = password;
            }
            await api.updateUser(editingUserId, data);
            alert('Usuario actualizado correctamente.');
        } else {
            if (!password) {
                alert('Es necesario establecer una contraseña para el usuario nuevo.');
                return;
            }
            const response = await api.createUser(email, password, nombre, role, telefono);
            if (response && response.user_id) {
                if (!activo) {
                    await api.updateUser(response.user_id, { activo: false });
                }
                alert('Usuario creado correctamente.');
            }
        }

        bootstrap.Modal.getInstance(modalElement).hide();
        cargarUsuarios();
    } catch (error) {
        console.error('Error al guardar usuario:', error);
        alert('Error al guardar usuario. Revisa la consola.');
    }
}

async function eliminarUsuario(userId, userName) {
    if (!confirm(`¿Eliminar al usuario ${userName}? Esta acción es irreversible.`)) {
        return;
    }

    try {
        await api.deleteUser(userId);
        alert('Usuario eliminado correctamente.');
        cargarUsuarios();
    } catch (error) {
        console.error('Error al eliminar usuario:', error);
        alert('No se pudo eliminar el usuario.');
    }
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
