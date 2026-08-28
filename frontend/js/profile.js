document.addEventListener('DOMContentLoaded', async () => {
    const profileForm = document.getElementById('profileForm');
    const emailEl = document.getElementById('profileEmail');
    const nombreEl = document.getElementById('profileNombre');
    const telefonoEl = document.getElementById('profileTelefono');
    const roleEl = document.getElementById('profileRole');
    const roleSelectDiv = document.getElementById('adminRoleDiv');
    const roleSelect = document.getElementById('profileRoleSelect');
    const msg = document.getElementById('profileMsg');

    if (!api.getToken()) {
        window.location.href = 'login.html';
        return;
    }

    if (!profileForm || !emailEl || !nombreEl || !telefonoEl || !roleEl || !msg) {
        console.warn('Perfil no inicializado: faltan elementos en el DOM.');
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

        let user = cachedUser;
        if (!user || user.telefono == null) {
            const profile = await api.getProfile();
            user = { ...(user || {}), ...profile };
            localStorage.setItem('user_data', JSON.stringify(user));
        }

        emailEl.value = user.email || '';
        nombreEl.value = user.nombre || '';
        telefonoEl.value = user.telefono || '';
        roleEl.value = user.role || '';

        // inicializar gráficos en perfil
        if (window.appCharts && typeof window.appCharts.initProfileCharts === 'function') {
            window.appCharts.initProfileCharts(user);
        }

        // if admin, show role select
        if (user.role === 'admin') {
            roleSelectDiv.classList.remove('d-none');
            roleSelect.value = user.role;
        }

        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            msg.textContent = '';
            const data = { nombre: nombreEl.value.trim(), telefono: telefonoEl.value.trim() };
            if (roleSelectDiv && !roleSelectDiv.classList.contains('d-none')) {
                data.role = roleSelect.value;
            }
            try {
                const updated = await api.updateUser(user.id, data);
                msg.textContent = 'Perfil actualizado correctamente.';
                msg.className = 'text-success';
                // update stored user_data
                localStorage.setItem('user_data', JSON.stringify(updated));
                // refresh nav
                if (window.appNav) window.appNav.updateNav();
            } catch (err) {
                msg.textContent = err.message || 'Error actualizando perfil';
                msg.className = 'text-danger';
            }
        });
    } catch (err) {
        console.error('Error cargando perfil:', err);
        api.clearToken();
        window.location.href = 'login.html';
    }
});
