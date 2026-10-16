/**
 * Lógica de registro - Página de Registro
 */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const direccionField = document.getElementById('direccionField');
    const descripcionField = document.getElementById('descripcionField');
    const nombreOllaField = document.getElementById('nombreOllaField');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    const beneficiarioFields = document.getElementById('beneficiarioFields');
    const dniInput = document.getElementById('dni');
    const edadInput = document.getElementById('edad');
    const vulnerabilidadInput = document.getElementById('vulnerabilidad');
    const ollaSelect = document.getElementById('olla_asociada_id');

    function updateRoleFields() {
        const selectedRole = document.querySelector('input[name="role"]:checked')?.value;

        const isOllaComun = selectedRole === 'olla_comun';
        const isBeneficiario = selectedRole === 'beneficiario';

        direccionField.style.display = isOllaComun ? 'block' : 'none';
        descripcionField.style.display = isOllaComun ? 'block' : 'none';
        if (nombreOllaField) nombreOllaField.style.display = isOllaComun ? 'block' : 'none';
        beneficiarioFields.style.display = isBeneficiario ? 'block' : 'none';

        document.getElementById('direccion').required = isOllaComun;
        dniInput.required = isBeneficiario;
        edadInput.required = isBeneficiario;
        vulnerabilidadInput.required = isBeneficiario;
        if (ollaSelect) {
            ollaSelect.required = isBeneficiario;
            if (!isBeneficiario) {
                ollaSelect.value = '';
            }
        }
    }

    // Mostrar/ocultar campos según el rol seleccionado
    roleRadios.forEach(radio => {
        radio.addEventListener('change', updateRoleFields);
    });

    updateRoleFields();

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const nombre = document.getElementById('nombre').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const telefono = document.getElementById('telefono').value;
            const role = document.querySelector('input[name="role"]:checked').value;
            const direccion = document.getElementById('direccion').value;
            const descripcion = document.getElementById('descripcion').value;
            const nombreOlla = document.getElementById('nombreOlla') ? document.getElementById('nombreOlla').value : null;
            const olla_asociada_id = document.getElementById('olla_asociada_id').value;
            const dni = document.getElementById('dni').value;
            const edad = document.getElementById('edad').value;
            const vulnerabilidad = document.getElementById('vulnerabilidad').value;

            // Limpiar alertas
            errorAlert.classList.add('d-none');
            successAlert.classList.add('d-none');

            // Validaciones
            if (password !== confirmPassword) {
                showError('Las contraseñas no coinciden');
                return;
            }

            if (password.length < 6) {
                showError('La contraseña debe tener al menos 6 caracteres');
                return;
            }

            try {
                const response = await api.register(
                    email,
                    password,
                    nombre,
                    role,
                    telefono,
                    direccion,
                    descripcion,
                    dni,
                    edad,
                    vulnerabilidad,
                    olla_asociada_id
                );

                if (response && response.user_id) {
                    showSuccess('Usuario registrado exitosamente. Redirigiendo al login...');
                    
                    // If role is olla_comun, create an olla request (pendiente) so admin can review
                    if (role === 'olla_comun') {
                        try {
                            await api.createOlla(nombreOlla || ('Olla ' + nombre), descripcion, direccion, telefono);
                        } catch (err) {
                            console.error('Error creando solicitud de olla:', err);
                        }
                    }

                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 2000);
                } else {
                    showError(response?.error || 'Error al registrar usuario');
                }
            } catch (error) {
                showError(error.message || 'Error de conexión con el servidor');
            }
        });
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

    async function cargarOllasAlSelect() {
        if (!ollaSelect) {
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/ollas');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const ollas = await response.json();
            
            // Limpiar opciones previas
            ollaSelect.innerHTML = '<option value="">Seleccione una Olla Común</option>';
            
            ollas.forEach(olla => {
                const option = document.createElement('option');
                option.value = olla.id;
                option.textContent = olla.nombre;
                ollaSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error al cargar ollas:", error);
        }
    }

    cargarOllasAlSelect();
});
