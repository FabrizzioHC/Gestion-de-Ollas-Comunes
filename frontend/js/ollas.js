/**
 * Lógica de Ollas Comunes - Página de Listado
 */

let allOllas = [];

document.addEventListener('DOMContentLoaded', async () => {
    const filterEstado = document.getElementById('filterEstado');
    const searchOlla = document.getElementById('searchOlla');
    const ollasList = document.getElementById('ollasList');
    const ollaModal = new bootstrap.Modal(document.getElementById('ollaModal'));

    // Cargar ollas al iniciar
    await loadOllas();

    // Registrar nueva olla
    const registerOllaForm = document.getElementById('registerOllaForm');
    if (registerOllaForm) {
        registerOllaForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const nombre = document.getElementById('newOllaNombre').value.trim();
            const direccion = document.getElementById('newOllaDireccion').value.trim();
            const telefono = document.getElementById('newOllaTelefono').value.trim();
            const descripcion = document.getElementById('newOllaDescripcion').value.trim();

            try {
                const res = await api.createOlla(nombre, descripcion, direccion, telefono);
                if (res && res.olla_id) {
                    // cerrar collapse
                    const collapseEl = document.getElementById('registerOllaCollapse');
                    const bsCollapse = bootstrap.Collapse.getInstance(collapseEl);
                    if (bsCollapse) bsCollapse.hide();
                    // reset form
                    registerOllaForm.reset();
                    await loadOllas();
                } else {
                    alert(res?.error || 'Error al crear la olla');
                }
            } catch (err) {
                console.error('Error creando olla:', err);
                alert('Error creando olla');
            }
        });
    }

    // Eventos de filtrado
    filterEstado.addEventListener('change', filterOllas);
    searchOlla.addEventListener('input', filterOllas);

    async function loadOllas() {
        try {
            const response = await api.listOllas();
            allOllas = response;
            displayOllas(allOllas);
        } catch (error) {
            ollasList.innerHTML = '<div class="col-12"><div class="alert alert-danger">Error cargando ollas</div></div>';
        }
    }

    function displayOllas(ollas) {
        if (!ollas || ollas.length === 0) {
            ollasList.innerHTML = '<div class="col-12"><div class="alert alert-info">No hay ollas comunes disponibles</div></div>';
            return;
        }

        ollasList.innerHTML = ollas.map(olla => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title">${escapeHtml(olla.nombre)}</h5>
                            <span class="badge bg-${olla.estado === 'activa' ? 'success' : 'warning'}">
                                ${olla.estado}
                            </span>
                        </div>
                        <p class="card-text text-muted">${escapeHtml(olla.descripcion || 'Sin descripción')}</p>
                        <div class="mt-3 pt-3 border-top">
                            <small class="text-muted">
                                📍 ${escapeHtml(olla.direccion)}
                            </small>
                            <br>
                            <small class="text-muted">
                                👥 Beneficiarios: ${olla.beneficiarios_atendidos}
                            </small>
                        </div>
                    </div>
                    <div class="card-footer bg-white border-top-0 d-grid gap-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="showOllaModal(${olla.id})">Ver detalles</button>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-secondary flex-grow-1" onclick="editOlla(${olla.id})">Editar</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteOlla(${olla.id})">Eliminar</button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    function filterOllas() {
        const estado = filterEstado.value;
        const searchText = searchOlla.value.toLowerCase();

        let filtered = allOllas.filter(olla => {
            const estadoMatch = !estado || olla.estado === estado;
            const textMatch = olla.nombre.toLowerCase().includes(searchText) ||
                            olla.descripcion?.toLowerCase().includes(searchText);
            return estadoMatch && textMatch;
        });

        displayOllas(filtered);
    }

    window.showOllaModal = async (ollaId) => {
        try {
            const olla = await api.getOlla(ollaId);
            const title = document.getElementById('ollaModalTitle');
            const body = document.getElementById('ollaModalBody');
            const donateBtn = document.getElementById('donateBtn');

            title.textContent = olla.nombre;
            body.innerHTML = `
                <p><strong>Descripción:</strong> ${escapeHtml(olla.descripcion || 'N/A')}</p>
                <p><strong>Dirección:</strong> ${escapeHtml(olla.direccion)}</p>
                <p><strong>Teléfono:</strong> ${escapeHtml(olla.telefono || 'N/A')}</p>
                <p><strong>Beneficiarios Atendidos:</strong> ${olla.beneficiarios_atendidos}</p>
                <p><strong>Estado:</strong> <span class="badge bg-${olla.estado === 'activa' ? 'success' : 'warning'}">${olla.estado}</span></p>
                <p><strong>Fecha de Creación:</strong> ${new Date(olla.fecha_creacion).toLocaleDateString()}</p>
            `;
            donateBtn.href = `donar.html?olla_id=${ollaId}`;
            ollaModal.show();
        } catch (error) {
            console.error('Error loading olla:', error);
        }
    };

    // Editar una olla
    window.editOlla = async (ollaId) => {
        try {
            const olla = await api.getOlla(ollaId);
            const nombre = prompt('Nombre de la olla:', olla.nombre);
            if (nombre === null) return; // cancel
            const descripcion = prompt('Descripción:', olla.descripcion || '');
            if (descripcion === null) return;

            const data = { nombre, descripcion };
            const res = await api.updateOlla(ollaId, data);
            if (res) {
                await loadOllas();
            } else {
                alert('No se pudo actualizar la olla');
            }
        } catch (err) {
            console.error('Error editando olla:', err);
            alert('Error editando olla');
        }
    };

    // Eliminar una olla
    window.deleteOlla = async (ollaId) => {
        if (!confirm('¿Confirma que desea eliminar esta olla? Esta acción no se puede deshacer.')) return;
        try {
            const res = await api.deleteOlla(ollaId);
            if (res) {
                await loadOllas();
            } else {
                alert('No se pudo eliminar la olla');
            }
        } catch (err) {
            console.error('Error eliminando olla:', err);
            alert('Error eliminando olla');
        }
    };

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
