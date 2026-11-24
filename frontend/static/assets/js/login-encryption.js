/* Cifrado RSA-OAEP SHA-256 antes del POST /login. TLS sigue siendo obligatorio en producción. */
(() => {
  'use strict';
  const form = document.getElementById('loginForm');
  if (!form) return;
  const campo = document.getElementById('inputPassword');
  const destino = document.getElementById('encryptedPassword');
  const boton = document.getElementById('loginSubmit');
  const error = document.getElementById('loginCryptoError');
  let enviando = false;

  const b64 = (bytes) => {
    let texto = '';
    for (const byte of new Uint8Array(bytes)) texto += String.fromCharCode(byte);
    return btoa(texto);
  };
  const importarPublica = async (pem) => {
    const raw = atob(pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s/g, ''));
    const bytes = Uint8Array.from(raw, c => c.charCodeAt(0));
    return crypto.subtle.importKey('spki', bytes, {name:'RSA-OAEP', hash:'SHA-256'}, false, ['encrypt']);
  };
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (enviando || !form.reportValidity()) return;
    error.hidden = true;
    boton.disabled = true;
    try {
      if (!window.crypto || !window.crypto.subtle) throw new Error('Se necesita HTTPS o localhost para Web Crypto.');
      const respuesta = await fetch(form.dataset.publicKeyUrl, {cache:'no-store', credentials:'same-origin'});
      if (!respuesta.ok) throw new Error('No se pudo consultar la clave pública.');
      const clave = await importarPublica(await respuesta.text());
      // La marca de tiempo impide reutilizar peticiones antiguas (no evita replay dentro de 60 s).
      const contenido = JSON.stringify({password:campo.value, timestamp: Date.now()/1000});
      const cifrado = await crypto.subtle.encrypt({name:'RSA-OAEP'}, clave, new TextEncoder().encode(contenido));
      destino.value = b64(cifrado);
      // No transmitir la contraseña original; no tiene name y se limpia antes del envío.
      campo.value = '';
      enviando = true;
      form.submit();
    } catch (exc) {
      error.textContent = 'No se pudo proteger la contraseña. ' + (exc.message || 'Actualiza la página e inténtalo de nuevo.');
      error.hidden = false;
      boton.disabled = false;
    }
  });
})();
