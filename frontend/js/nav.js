// nav.js - Maneja visibilidad del menú según autenticación y logout

(function(){
    const loginBtn = document.getElementById('navLogin');
    const profileLink = document.getElementById('navProfile');
    const logoutBtn = document.getElementById('navLogout');
    const ollasLink = document.getElementById('navOllas');
    const donarLink = document.getElementById('navDonar');

    function updateNav() {
        const token = localStorage.getItem('auth_token');
        if (token) {
            if (loginBtn) loginBtn.classList.add('d-none');
            if (profileLink) profileLink.classList.remove('d-none');
            if (logoutBtn) logoutBtn.classList.remove('d-none');
        } else {
            if (loginBtn) loginBtn.classList.remove('d-none');
            if (profileLink) profileLink.classList.add('d-none');
            if (logoutBtn) logoutBtn.classList.add('d-none');
        }
    }

    function logout() {
        if (window.api && typeof api.clearToken === 'function') {
            api.clearToken();
        } else {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
        }
        // small delay then redirect to login
        setTimeout(() => { window.location.href = 'login.html'; }, 150);
    }

    function getThemeToggle() {
        return document.getElementById('themeToggle');
    }

    function applyTheme(theme) {
        const body = document.body;
        body.classList.toggle('dark-mode', theme === 'dark');
        localStorage.setItem('theme', theme);

        const themeBtn = getThemeToggle();
        if (themeBtn) {
            themeBtn.textContent = theme === 'dark' ? '☀️ Modo claro' : '🌙 Modo oscuro';
            themeBtn.classList.toggle('btn-outline-light', theme === 'dark');
            themeBtn.classList.toggle('btn-outline-primary', theme !== 'dark');
        }
    }

    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        applyTheme(savedTheme);
    }

    function toggleTheme() {
        const newTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        applyTheme(newTheme);
    }

    if (logoutBtn) logoutBtn.addEventListener('click', logout);

    function initPage() {
        const themeBtn = getThemeToggle();
        if (themeBtn) {
            themeBtn.addEventListener('click', toggleTheme);
        }
        updateNav();
        initTheme();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPage);
    } else {
        initPage();
    }

    // Expose for console if needed
    window.appNav = { updateNav, logout, applyTheme };
})();
