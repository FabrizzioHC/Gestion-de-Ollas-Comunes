/**
 * Cliente API para Red Comunitaria
 * Maneja todas las llamadas HTTP a la API backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    /**
     * Establece el token de autenticación
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    /**
     * Obtiene el token actual
     */
    getToken() {
        return localStorage.getItem('auth_token');
    }

    /**
     * Limpia el token (logout)
     */
    clearToken() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        this.token = null;
    }

    /**
     * Realiza una petición HTTP
     */
    async request(method, endpoint, data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        // Agregar token si existe
        const token = this.getToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        // Agregar body si hay datos
        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            const isAuthEndpoint = endpoint.startsWith('/auth/login') || endpoint.startsWith('/auth/register');

            if (response.status === 401 && !isAuthEndpoint) {
                // Token expirado o inválido
                this.clearToken();
                window.location.href = 'login.html';
                return null;
            }

            const json = await response.json();
            
            if (!response.ok) {
                throw new Error(json.error || 'Error en la solicitud');
            }

            return json;
        } catch (error) {
            console.error(`Error en ${method} ${endpoint}:`, error);
            throw error;
        }
    }

    // ========================================================================
    // AUTENTICACIÓN
    // ========================================================================

    async login(email, password) {
        const response = await this.request('POST', '/auth/login', { email, password });
        if (response && response.access_token) {
            this.setToken(response.access_token);
        }
        return response;
    }

    async register(
        email,
        password,
        nombre,
        role,
        telefono = null,
        direccion = null,
        descripcion = null,
        dni = null,
        edad = null,
        vulnerabilidad = null,
        olla_asociada_id = null
    ) {
        const data = { email, password, nombre, role, telefono };
        if (direccion) data.direccion = direccion;
        if (descripcion) data.descripcion = descripcion;
        if (dni) data.dni = dni;
        if (edad !== null && edad !== '' && edad !== undefined) data.edad = Number(edad);
        if (vulnerabilidad) data.vulnerabilidad = vulnerabilidad;
        if (olla_asociada_id !== null && olla_asociada_id !== '' && olla_asociada_id !== undefined) {
            data.olla_asociada_id = Number(olla_asociada_id);
        }
        return await this.request('POST', '/auth/register', data);
    }

    async getProfile() {
        return await this.request('GET', '/auth/profile');
    }

    async updateUser(userId, data) {
        return await this.request('PUT', `/users/${userId}`, data);
    }

    async deleteUser(userId) {
        return await this.request('DELETE', `/users/${userId}`);
    }

    async createUser(email, password, nombre, role, telefono = null) {
        return await this.register(email, password, nombre, role, telefono);
    }

    // ========================================================================
    // OLLAS COMUNES
    // ========================================================================

    async listOllas(estado = null) {
        let endpoint = '/ollas';
        if (estado) {
            endpoint += `?estado=${estado}`;
        }
        return await this.request('GET', endpoint);
    }

    async getOlla(ollaId) {
        return await this.request('GET', `/ollas/${ollaId}`);
    }

    async createOlla(nombre, descripcion, direccion, telefono) {
        return await this.request('POST', '/ollas', {
            nombre,
            descripcion,
            direccion,
            telefono
        });
    }

    async updateOlla(ollaId, data) {
        return await this.request('PUT', `/ollas/${ollaId}`, data);
    }

    async deleteOlla(ollaId) {
        return await this.request('DELETE', `/ollas/${ollaId}`);
    }

    // ========================================================================
    // DONACIONES
    // ========================================================================

    async listDonaciones(estado = null) {
        let endpoint = '/donaciones';
        if (estado) {
            endpoint += `?estado=${estado}`;
        }
        return await this.request('GET', endpoint);
    }

    async listPublicDonaciones(estado = null) {
        let endpoint = '/donaciones/public';
        if (estado) {
            endpoint += `?estado=${estado}`;
        }
        return await this.request('GET', endpoint);
    }

    async getDonacion(donacionId) {
        return await this.request('GET', `/donaciones/${donacionId}`);
    }

    async createDonacion(ollaId, tipoRecurso, cantidad, unidad, descripcion = null) {
        return await this.request('POST', '/donaciones', {
            olla_comun_id: ollaId,
            tipo_recurso: tipoRecurso,
            cantidad,
            unidad,
            descripcion
        });
    }

    async approveDonacion(donacionId) {
        return await this.request('POST', `/donaciones/${donacionId}/approve`);
    }

    async rejectDonacion(donacionId) {
        return await this.request('POST', `/donaciones/${donacionId}/reject`);
    }

    // ========================================================================
    // SOLICITUDES
    // ========================================================================

    async listSolicitudes(estado = null) {
        let endpoint = '/solicitudes';
        if (estado) {
            endpoint += `?estado=${estado}`;
        }
        return await this.request('GET', endpoint);
    }

    async createSolicitud(ollaId, tipoRecurso, cantidad, unidad, urgencia = 'normal', descripcion = null) {
        return await this.request('POST', '/solicitudes', {
            olla_comun_id: ollaId,
            tipo_recurso: tipoRecurso,
            cantidad,
            unidad,
            urgencia,
            descripcion
        });
    }

    async approveSolicitud(solicitudId) {
        return await this.request('POST', `/solicitudes/${solicitudId}/approve`);
    }

    // ========================================================================
    // ADMIN
    // ========================================================================

    async getAdminDashboard() {
        return await this.request('GET', '/admin/dashboard');
    }

    // ========================================================================
    // HEALTH
    // ========================================================================

    async health() {
        return await this.request('GET', '/health');
    }
}

// Instancia global de APIClient
const api = new APIClient();
