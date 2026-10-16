/**
 * Lógica de autenticación - Página de Login
 */

document.addEventListener('DOMContentLoaded', async () => {
    const loginForm = document.getElementById('loginForm');
    const errorAlert = document.getElementById('errorAlert');
    const splashOverlay = document.getElementById('splashOverlay');
    const splashUsername = splashOverlay?.querySelector('.splash-username');

    if (api.getToken()) {
        try {
            const profile = await api.getProfile();
            if (profile && profile.id) {
                window.location.href = 'index.html';
                return;
            }
        } catch (err) {
            api.clearToken();
        }
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value.trim().toLowerCase();
            const password = document.getElementById('password').value.trim();

            errorAlert.classList.add('d-none');

            try {
                const response = await api.login(email, password);
                
                if (response && response.access_token) {
                    localStorage.setItem('user_data', JSON.stringify(response.user));
                    showSplash(response.user.nombre || 'Usuario');
                } else {
                    showError(response?.error || 'Error al iniciar sesión');
                }
            } catch (error) {
                showError(error.message || 'Error de conexión con el servidor');
            }
        });
    }

    function showSplash(nombre) {
        if (!splashOverlay || !splashUsername) {
            window.location.href = 'dashboard.html';
            return;
        }

        splashUsername.textContent = nombre;
        splashOverlay.classList.remove('d-none');
        loginForm.classList.add('d-none');

        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
    }

    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.classList.remove('d-none');
    }
});
