# Cifrado de contraseña en el login y control HTTP

## Cambios
- Frontend: `frontend/static/assets/js/login-encryption.js` usa Web Crypto y RSA-OAEP SHA-256 con clave pública del backend, cifrado aleatorio por petición.
- Formulario: `frontend/templates/login.html` ya NO envía el parámetro `password`. Envía `encrypted_password`.
- Backend: `backend/security/login_crypto.py` descifra en Flask y pasa la clave temporal a `check_password_hash`; no cambia los hashes guardados en MySQL.
- Rate limit: `backend/dao/usuario_dao.py` incrementa el contador de intentos en una instrucción UPDATE atómica para reducir carreras con peticiones simultáneas. En login se mantiene 401 para clave inválida, 429 a partir del tercer fallo, Retry-After 180.

## Cómo ejecutar localmente
1. `pip install -r requirements.txt`
2. Configura el `.env` de base de datos como antes. En localhost se crea una clave RSA temporal al iniciar Flask.
3. `python run.py` y visita `http://127.0.0.1:5000/login` (Web Crypto funciona en localhost).
4. Navega con el navegador lanzado desde ZAP. En `POST /login` mira el cuerpo: debe contener `email=...&encrypted_password=...` y **NO** `password=tu-clave`.
5. Para el bloqueo, haz 3 intentos erróneos **desde el navegador** con una cuenta de prueba existente y sin bloqueo previo: 401, 401, 429. Las peticiones consecutivas deben usar cifrados nuevos, no repetir una petición capturada.

## ¡IMPORTANTE para el Fuzzer!
No puedes reemplazar `encrypted_password` por palabras en claro en el Fuzzer, ni repetir un mismo ciphertext: Flask devolverá 400 cuando falle el descifrado o expire. Para fuzzing automatizado necesitas una secuencia que genere un nuevo cifrado válido con cada palabra, respetando los límites de prueba. Para demostrar 429 es más fácil usar tres intentos manuales seguidos en el navegador de ZAP y examinar Historial.

## Despliegue real / Render
En producción **NO** uses la clave RSA efímera. Genera una única clave RSA privada fuera del repositorio, configura `LOGIN_RSA_PRIVATE_KEY_B64` como variable secreta de entorno común para todos los workers y reinicia el servicio. Para obtenerla en PowerShell con OpenSSL: `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out login-private.pem` y `python -c "import base64;print(base64.b64encode(open('login-private.pem','rb').read()).decode())"`. Copia ese resultado al entorno y elimina el archivo del directorio del proyecto. **Nunca subas el archivo privado a GitHub ni lo incluyas en ZIP distribuidos.**

**Seguridad:** el tráfico HTTPS ya cifra las contraseñas en tránsito. OWASP ZAP puede visualizar el cuerpo original cuando el navegador configura a ZAP como proxy HTTPS; eso por sí solo no demuestra una vulnerabilidad de red. Este cifrado adicional evita que el campo `password` se vea legible en la captura del proxy, pero ZAP aún puede ver y reutilizar el ciphertext: NO reemplaza TLS, CSRF, controles de sesión, ni rate limit. Se aplica solo al login; el registro y demás formularios que recojan claves necesitan evaluación independiente.
