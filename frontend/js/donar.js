/**
 * Lógica de Donaciones - Página de Donación
 */

document.addEventListener('DOMContentLoaded', async () => {
    const donationForm = document.getElementById('donationForm');
    const ollaComunSelect = document.getElementById('olla_comun_id');
    const authAlert = document.getElementById('authAlert');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    const donacionesTableBody = document.getElementById('donacionesTableBody');

    let ollasById = {};
    const hasToken = Boolean(api.getToken());

    // Verificar si el usuario está autenticado
    if (!hasToken) {
        authAlert.classList.remove('d-none');
        if (donationForm) {
            donationForm.style.display = 'none';
        }
    }

    // Cargar ollas y donaciones
    const loadTasks = [loadDonaciones()];
    if (hasToken) {
        loadTasks.unshift(loadOllas());
    }
    await Promise.all(loadTasks);

    // Verificar si hay una olla seleccionada en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const ollaId = urlParams.get('olla_id');
    if (ollaId) {
        ollaComunSelect.value = ollaId;
    }

    if (donationForm && hasToken) {
        donationForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const ollaId = document.getElementById('olla_comun_id').value;
            const tipoRecurso = document.getElementById('tipo_recurso').value;
            const cantidad = parseFloat(document.getElementById('cantidad').value);
            const unidad = document.getElementById('unidad').value;
            const descripcion = document.getElementById('descripcion').value;

            errorAlert.classList.add('d-none');
            successAlert.classList.add('d-none');

            try {
                const response = await api.createDonacion(
                    ollaId,
                    tipoRecurso,
                    cantidad,
                    unidad,
                    descripcion
                );

                if (response && response.donacion_id) {
                    showSuccess('¡Donación registrada exitosamente! Los administradores la revisarán pronto.');
                    donationForm.reset();
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 2000);
                } else {
                    showError(response?.error || 'Error al registrar la donación');
                }
            } catch (error) {
                showError(error.message || 'Error de conexión con el servidor');
            }
        });
    }

    async function loadOllas() {
        try {
            const ollas = await api.listOllas('activa');
            ollasById = (ollas || []).reduce((accumulator, olla) => {
                accumulator[String(olla.id)] = olla;
                return accumulator;
            }, {});
            
            if (ollas && ollas.length > 0) {
                const options = ollas.map(olla => `
                    <option value="${olla.id}">${escapeHtml(olla.nombre)}</option>
                `).join('');
                ollaComunSelect.innerHTML += options;
            } else {
                showError('No hay ollas comunes disponibles en este momento');
            }
        } catch (error) {
            showError('Error cargando ollas comunes');
        }
    }

    async function loadDonaciones() {
        if (!donacionesTableBody) {
            return;
        }

        try {
            const donaciones = await api.listPublicDonaciones();

            if (!donaciones || donaciones.length === 0) {
                donacionesTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No hay donaciones registradas aún.</td></tr>';
                return;
            }

            donacionesTableBody.innerHTML = donaciones.map(donacion => {
                const destino = donacion.destino || ollasById[String(donacion.olla_comun_id)]?.nombre || `Olla #${donacion.olla_comun_id}`;
                const donante = donacion.donante || 'Donante';
                const estadoInfo = normalizeEstado(donacion.estado);

                return `
                    <tr>
                        <td>${escapeHtml(donante)}</td>
                        <td>${escapeHtml(donacion.recurso || donacion.tipo_recurso || 'Sin recurso')}</td>
                        <td>${escapeHtml(donacion.cantidad || formatCantidad(donacion.cantidad, donacion.unidad))}</td>
                        <td>${escapeHtml(destino)}</td>
                        <td><span class="badge ${estadoInfo.badgeClass}">${estadoInfo.label}</span></td>
                        <td>${escapeHtml(formatDate(donacion.fecha_creacion))}</td>
                    </tr>
                `;
            }).join('');
        } catch (error) {
            console.error('Error loading donations:', error);
            donacionesTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No se pudieron cargar las donaciones.</td></tr>';
        }
    }

    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.classList.remove('d-none');
        successAlert.classList.add('d-none');
    }

    function showSuccess(message) {
        successAlert.textContent = message;
        successAlert.classList.remove('d-none');
        errorAlert.classList.add('d-none');
    }

    function normalizeEstado(estado) {
        const normalized = String(estado || '').toLowerCase();

        if (['aprobada', 'aprobado', 'entregada', 'entregado'].includes(normalized)) {
            return { label: 'Aprobado', badgeClass: 'text-bg-success' };
        }

        if (['rechazada', 'rechazado', 'cancelada', 'cancelado'].includes(normalized)) {
            return { label: 'Cancelado', badgeClass: 'text-bg-danger' };
        }

        return { label: 'Pendiente', badgeClass: 'text-bg-warning' };
    }

    function formatCantidad(cantidad, unidad) {
        if (cantidad === null || cantidad === undefined || cantidad === '') {
            return '-';
        }

        const numeric = Number(cantidad);
        const value = Number.isFinite(numeric) ? numeric.toString() : String(cantidad);
        return unidad ? `${value} ${unidad}` : value;
    }

    function formatDate(dateString) {
        if (!dateString) {
            return '-';
        }

        const date = new Date(dateString);
        if (Number.isNaN(date.getTime())) {
            return '-';
        }

        return date.toLocaleDateString('es-ES');
    }

    function escapeHtml(text) {
        return String(text)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }
});
