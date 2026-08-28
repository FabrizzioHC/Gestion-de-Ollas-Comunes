/**
 * Lógica del Dashboard
 */

let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticación
    const token = api.getToken();
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const cachedUser = (() => {
            try {
                return JSON.parse(localStorage.getItem('user_data'));
            } catch {
                return null;
            }
        })();

        // Cargar datos del usuario sin forzar una petición que pueda expulsar la sesión
        currentUser = cachedUser;
        if (!currentUser || currentUser.telefono == null) {
            const profile = await api.getProfile();
            currentUser = { ...(currentUser || {}), ...profile };
        }
        if (currentUser) {
            localStorage.setItem('user_data', JSON.stringify(currentUser));
        }

        displayUserInfo(currentUser);
        
        // Mostrar menú según el rol
        setupMenuByRole(currentUser.role);
        
        // Cargar dashboard inicial
        await loadDashboard();
        
        // Event listeners
        setupEventListeners();
        // Inicializar gráficos en la vista principal
        if (window.appCharts && typeof window.appCharts.initDashboardCharts === 'function') {
            window.appCharts.initDashboardCharts(currentUser);
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        api.clearToken();
        window.location.href = 'login.html';
    }
});

function displayUserInfo(user) {
    document.getElementById('userEmail').textContent = user.email;
    document.getElementById('profileEmail').value = user.email;
    document.getElementById('profileNombre').value = user.nombre;
    document.getElementById('profileRole').value = user.role;
    document.getElementById('profileTelefono').value = user.telefono || '';
}

// Enable edit controls for profile inside dashboard
function enableProfileEditing() {
    const profileSection = document.getElementById('profileSection');
    if (!profileSection) return;
    const editBtn = document.createElement('button');
    editBtn.className = 'btn btn-primary mb-3';
    editBtn.textContent = 'Editar Perfil';
    const saveBtn = document.createElement('button');
    saveBtn.className = 'btn btn-success mb-3 ms-2 d-none';
    saveBtn.textContent = 'Guardar';
    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-secondary mb-3 ms-2 d-none';
    cancelBtn.textContent = 'Cancelar';

    const cardBody = profileSection.querySelector('.card-body');
    cardBody.insertBefore(editBtn, cardBody.firstChild);
    cardBody.insertBefore(saveBtn, cardBody.firstChild.nextSibling);
    cardBody.insertBefore(cancelBtn, cardBody.firstChild.nextSibling);

    const inputs = ['profileNombre','profileTelefono'];

    editBtn.addEventListener('click', () => {
        inputs.forEach(id => document.getElementById(id).disabled = false);
        editBtn.classList.add('d-none');
        saveBtn.classList.remove('d-none');
        cancelBtn.classList.remove('d-none');
    });

    cancelBtn.addEventListener('click', () => {
        // reload stored user
        const user = JSON.parse(localStorage.getItem('user_data') || '{}');
        displayUserInfo(user);
        inputs.forEach(id => document.getElementById(id).disabled = true);
        editBtn.classList.remove('d-none');
        saveBtn.classList.add('d-none');
        cancelBtn.classList.add('d-none');
    });

    saveBtn.addEventListener('click', async () => {
        const user = JSON.parse(localStorage.getItem('user_data') || '{}');
        const data = { nombre: document.getElementById('profileNombre').value.trim(), telefono: document.getElementById('profileTelefono').value.trim() };
        try {
            const updated = await api.updateUser(user.id, data);
            localStorage.setItem('user_data', JSON.stringify(updated));
            displayUserInfo(updated);
            inputs.forEach(id => document.getElementById(id).disabled = true);
            editBtn.classList.remove('d-none');
            saveBtn.classList.add('d-none');
            cancelBtn.classList.add('d-none');
            alert('Perfil actualizado');
        } catch (err) {
            alert('Error actualizando perfil: ' + err.message);
        }
    });
}

function setupMenuByRole(role) {
    // Mostrar/ocultar menús según rol
    if (role === 'olla_comun') {
        document.getElementById('menuOllas').style.display = 'block';
        document.getElementById('menuSolicitudes').style.display = 'block';
    } else {
        document.getElementById('menuOllas').style.display = 'none';
        document.getElementById('menuSolicitudes').style.display = 'none';
    }

    const menuAdmin = document.getElementById('menuAdmin');
    const menuGestionUsuarios = document.getElementById('menuGestionUsuarios');
    if (role === 'admin') {
        menuAdmin.style.display = 'block';
        menuAdmin.querySelector('a').textContent = 'Administrador';
        if (menuGestionUsuarios) {
            menuGestionUsuarios.style.display = 'block';
        }
    } else {
        menuAdmin.style.display = 'none';
        if (menuGestionUsuarios) {
            menuGestionUsuarios.style.display = 'none';
        }
    }
}

async function loadDashboard() {
    try {
        if (currentUser.role === 'admin') {
            const stats = await api.getAdminDashboard();
            document.getElementById('statOllasActivas').textContent = stats.ollas_activas;
            document.getElementById('statDonacionesPendientes').textContent = stats.donaciones_pendientes;
            document.getElementById('statSolicitudesPendientes').textContent = stats.solicitudes_pendientes;
            document.getElementById('statTotalUsuarios').textContent = stats.total_usuarios;
            return;
        }

        const [ollas, donaciones, solicitudes] = await Promise.all([
            api.listOllas(),
            api.listDonaciones(),
            api.listSolicitudes()
        ]);

        if (currentUser.role === 'olla_comun') {
            document.getElementById('statOllasActivas').textContent = ollas.length;
            document.getElementById('statDonacionesPendientes').textContent = donaciones.filter(d => d.estado !== 'aprobado').length;
            document.getElementById('statSolicitudesPendientes').textContent = solicitudes.filter(s => s.estado !== 'atendida').length;
            document.getElementById('statTotalUsuarios').textContent = '—';
        } else {
            document.getElementById('statOllasActivas').textContent = ollas.length;
            document.getElementById('statDonacionesPendientes').textContent = donaciones.length;
            document.getElementById('statSolicitudesPendientes').textContent = solicitudes.length;
            document.getElementById('statTotalUsuarios').textContent = '—';
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        document.getElementById('statOllasActivas').textContent = 'N/A';
        document.getElementById('statDonacionesPendientes').textContent = 'N/A';
        document.getElementById('statSolicitudesPendientes').textContent = 'N/A';
        document.getElementById('statTotalUsuarios').textContent = 'N/A';
    }
}

function setupEventListeners() {
    // Navigation links
    document.querySelectorAll('.nav-link[data-section]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = e.target.closest('[data-section]').dataset.section;
            showSection(section);
            closeDashboardMenu();

            if (section === 'gestionUsuarios' && currentUser?.role === 'admin') {
                cargarUsuarios();
            }
        });
    });

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', () => {
        api.clearToken();
        window.location.href = 'index.html';
    });

    // Olla form
    document.getElementById('submitOllaBtn').addEventListener('click', submitOllaForm);

    // Solicitud form
    document.getElementById('submitSolicitudBtn').addEventListener('click', submitSolicitudForm);

    // Load data for sections
    loadDonaciones();
    if (currentUser.role === 'olla_comun') {
        loadOllas();
        loadSolicitudes();
        loadSolicitudOllas();
    }
    if (currentUser.role === 'admin') {
        loadAdminData();
        cargarUsuarios();
        loadPendingOllas();
    }
}

async function loadPendingOllas() {
    try {
        const ollas = await api.listOllas('pendiente');
        const container = document.getElementById('adminPendingOllas');
        if (!ollas || ollas.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No hay solicitudes pendientes</div>';
            return;
        }

        container.innerHTML = ollas.map(o => `
            <div class="card mb-3 p-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6>${escapeHtml(o.nombre)}</h6>
                        <p class="mb-1"><strong>Dirección:</strong> ${escapeHtml(o.direccion)}</p>
                        <p class="mb-1"><strong>Descripción:</strong> ${escapeHtml(o.descripcion || '')}</p>
                    </div>
                    <div>
                        <button class="btn btn-success btn-sm" onclick="approveOlla(${o.id})">Aprobar</button>
                        <button class="btn btn-danger btn-sm ms-2" onclick="rejectOlla(${o.id})">Rechazar</button>
                        <button class="btn btn-outline-secondary btn-sm ms-2" onclick="editOlla(${o.id})">Editar</button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error cargando solicitudes de ollas:', err);
    }
}

async function approveOlla(ollaId) {
    try {
        await api.updateOlla(ollaId, { estado: 'activa' });
        loadPendingOllas();
        alert('Olla aprobada');
    } catch (err) {
        alert('Error aprobando: ' + err.message);
    }
}

async function rejectOlla(ollaId) {
    try {
        await api.updateOlla(ollaId, { estado: 'rechazada' });
        loadPendingOllas();
        alert('Olla rechazada');
    } catch (err) {
        alert('Error rechazando: ' + err.message);
    }
}

function editOlla(ollaId) {
    // abrir ventana de edición rápida
    const name = prompt('Nuevo nombre para la olla (dejar vacío para no cambiar):');
    const direccion = prompt('Nueva dirección (vacío para no cambiar):');
    const descripcion = prompt('Nueva descripción (vacío para no cambiar):');
    const data = {};
    if (name) data.nombre = name;
    if (direccion) data.direccion = direccion;
    if (descripcion) data.descripcion = descripcion;
    if (Object.keys(data).length === 0) return;
    api.updateOlla(ollaId, data).then(()=>{
        alert('Olla actualizada');
        loadPendingOllas();
    }).catch(err=>alert('Error al actualizar: '+err.message));
}

async function loadSolicitudOllas() {
    try {
        const ollas = await api.listOllas();
        const select = document.getElementById('solicitudOllaId');
        if (!ollas || ollas.length === 0) {
            select.innerHTML = '<option value="">No hay ollas disponibles</option>';
            return;
        }
        select.innerHTML = '<option value="">-- Selecciona una olla --</option>' + ollas.map(olla => `
            <option value="${olla.id}">${escapeHtml(olla.nombre)}</option>
        `).join('');
    } catch (error) {
        console.error('Error cargando ollas para solicitud:', error);
    }
}

function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Mostrar sección seleccionada
    const section = document.getElementById(sectionName + 'Section');
    section.style.display = 'block';

    // si se muestra el perfil, inicializar gráficos específicos del perfil
    if (sectionName === 'profile' && window.appCharts && typeof window.appCharts.initProfileCharts === 'function') {
        window.appCharts.initProfileCharts(currentUser);
    }

    if (sectionName === 'gestionUsuarios' && currentUser?.role === 'admin') {
        cargarUsuarios();
    }

    section.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Actualizar nav activo
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // initialize charts for dashboard or profile when visible
    if (sectionName === 'dashboard' && window.appCharts && typeof window.appCharts.initDashboardCharts === 'function') {
        window.appCharts.initDashboardCharts(currentUser);
    }
    if (sectionName === 'profile') {
        if (window.appCharts && typeof window.appCharts.initProfileCharts === 'function') {
            window.appCharts.initProfileCharts(currentUser);
        }
        // enable inline editing
        enableProfileEditing();
    }
}

function closeDashboardMenu() {
    const menu = document.getElementById('dashboardMenu');
    if (!menu || typeof bootstrap === 'undefined') {
        return;
    }

    const offcanvas = bootstrap.Offcanvas.getInstance(menu) || bootstrap.Offcanvas.getOrCreateInstance(menu);
    offcanvas.hide();
}

async function loadOllas() {
    try {
        const ollas = await api.listOllas();
        const container = document.getElementById('ollasListContainer');
        
        if (!ollas || ollas.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No tienes ollas registradas</div>';
            return;
        }

        container.innerHTML = ollas.map(olla => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${escapeHtml(olla.nombre)}</h5>
                        <p class="card-text">${escapeHtml(olla.descripcion || 'Sin descripción')}</p>
                        <small class="text-muted">📍 ${escapeHtml(olla.direccion)}</small><br>
                        <small class="text-muted">👥 ${olla.beneficiarios_atendidos} beneficiarios</small>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading ollas:', error);
    }
}

async function loadDonaciones() {
    try {
        const donaciones = await api.listDonaciones();
        const tbody = document.getElementById('donacionesTableBody');
        
        if (!donaciones || donaciones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay donaciones</td></tr>';
            return;
        }

        tbody.innerHTML = donaciones.map(d => `
            <tr>
                <td>${d.olla_comun_id}</td>
                <td>${d.tipo_recurso}</td>
                <td>${d.cantidad_str || (d.cantidad)}</td>
                <td><span class="badge bg-info">${d.estado}</span></td>
                <td>${new Date(d.fecha_creacion).toLocaleDateString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading donaciones:', error);
    }
}

async function loadSolicitudes() {
    try {
        const solicitudes = await api.listSolicitudes();
        const tbody = document.getElementById('solicitudesTableBody');
        
        if (!solicitudes || solicitudes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay solicitudes</td></tr>';
            return;
        }

        tbody.innerHTML = solicitudes.map(s => `
            <tr>
                <td>${s.tipo_recurso}</td>
                <td>${s.cantidad}</td>
                <td><span class="badge bg-warning">${s.urgencia}</span></td>
                <td>${s.estado}</td>
                <td>${new Date(s.fecha_creacion).toLocaleDateString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading solicitudes:', error);
    }
}

async function loadAdminData() {
    try {
        const donaciones = await api.listDonaciones('pendiente');
        const solicitudes = await api.listSolicitudes('pendiente');

        const donacionesContainer = document.getElementById('adminDonacionesContainer');
        const solicitudesContainer = document.getElementById('adminSolicitudesContainer');

        if (donaciones && donaciones.length > 0) {
            donacionesContainer.innerHTML = donaciones.map(d => `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h6>${d.tipo_recurso}</h6>
                            <small class="text-muted">${d.cantidad}</small>
                        </div>
                        <div>
                            <button class="btn btn-success btn-sm" onclick="approveDonacion(${d.id})">✓</button>
                            <button class="btn btn-danger btn-sm" onclick="rejectDonacion(${d.id})">✕</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        if (solicitudes && solicitudes.length > 0) {
            solicitudesContainer.innerHTML = solicitudes.map(s => `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h6>${s.tipo_recurso}</h6>
                            <small class="text-muted">Urgencia: ${s.urgencia}</small>
                        </div>
                        <button class="btn btn-success btn-sm" onclick="approveSolicitud(${s.id})">✓</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading admin data:', error);
    }
}

async function submitOllaForm() {
    const nombre = document.getElementById('ollaNombre').value;
    const direccion = document.getElementById('ollaDireccion').value;
    const telefono = document.getElementById('ollaTelefono').value;
    const descripcion = document.getElementById('ollaDescripcion').value;

    try {
        const response = await api.createOlla(nombre, descripcion, direccion, telefono);
        if (response && response.olla_id) {
            alert('Olla creada exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('ollaModal')).hide();
            loadOllas();
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function submitSolicitudForm() {
    const ollaId = document.getElementById('solicitudOllaId').value;
    const tipo = document.getElementById('solicitudTipo').value;
    const cantidad = document.getElementById('solicitudCantidad').value;
    const urgencia = document.getElementById('solicitudUrgencia').value;
    const descripcion = document.getElementById('solicitudDescripcion').value;

    if (!ollaId) {
        alert('Selecciona una olla común antes de enviar la solicitud.');
        return;
    }

    try {
        const response = await api.createSolicitud(
            ollaId,
            tipo,
            cantidad,
            'unidades',
            urgencia,
            descripcion
        );
        if (response && response.solicitud_id) {
            alert('Solicitud creada exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('solicitudModal')).hide();
            loadSolicitudes();
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function approveDonacion(donacionId) {
    try {
        await api.approveDonacion(donacionId);
        loadAdminData();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function rejectDonacion(donacionId) {
    try {
        await api.rejectDonacion(donacionId);
        loadAdminData();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function approveSolicitud(solicitudId) {
    try {
        await api.approveSolicitud(solicitudId);
        loadAdminData();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
