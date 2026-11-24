# Corrección de códigos HTTP — autenticación

## Archivo modificado
`backend/controllers/usuario_controller.py` (ruta `/login`).

| Caso | Estado HTTP esperado |
| --- | --- |
| GET /login | 200 OK |
| POST con campos vacíos | 400 Bad Request |
| POST con usuario inexistente | 401 Unauthorized |
| POST con contraseña incorrecta (primer y segundo intento) | 401 Unauthorized |
| POST con cuenta suspendida | 403 Forbidden |
| POST con tercera contraseña incorrecta | 429 Too Many Requests |
| POST mientras existe bloqueo temporal | 429 Too Many Requests |
| POST con credenciales válidas sin bloqueo | 302 Found, redirección al inicio |

En los bloqueos `429` se devuelve además `Retry-After` (segundos hasta reintentar) y `Cache-Control: no-store`.

## Comprobación con OWASP ZAP
1. Actualiza la aplicación desplegada en Render con este código (subiendo al repositorio conectado al servicio). El ZIP corregido por sí solo no modifica el servicio en internet.
2. Abre una **sesión de pruebas** en una cuenta propia. Accede a `/login` y captura el POST con ZAP.
3. Envía contraseñas incorrectas: intenta 1 -> 401; intento 2 -> 401; intento 3 -> 429. El sistema sigue mostrando sus mensajes de error.
4. Durante los siguientes 3 minutos vuelve a intentar iniciar sesión: 429 y encabezado `Retry-After`.
5. Una vez finalizado el bloqueo, verifica que las credenciales correctas generen 302.
6. Para las capturas del informe, comprueba el **código de respuesta del POST /login**, no el GET de la página, que legítimamente puede devolver 200.

Los resultados de un Fuzzer pueden depender del contador previo de intentos y del orden de las solicitudes; cada carga no tiene necesariamente un estado fijo. La implementación preserva las reglas de bloqueo existentes y cambia solo los códigos de respuesta.

## Pruebas automatizadas (con dependencias instaladas)
Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
python -m unittest discover -s pruebas/http -v
```

## Seguridad
Los códigos 429 reflejan el bloqueo **por cuenta que ya existía**. Esto no es un limitador global por IP. Un `401` HTML puede seguir mostrando el formulario al usuario aunque el navegador indique un error HTTP en la pestaña Red: es el comportamiento esperado.

La conexión HTTPS ya cifra el transporte; utilizar un hash estático de contraseña desde JavaScript no sustituye TLS ni proporciona por sí mismo seguridad adicional frente a reutilización del hash.
