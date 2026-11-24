"""Cifrado opcional adicional a TLS para el POST /login (RSA-OAEP SHA-256).
La llave privada del servidor NUNCA se entrega al navegador.
Para despliegues multiproceso configure LOGIN_RSA_PRIVATE_KEY_B64 en el entorno.
"""
import base64
import json
import os
import time
from functools import lru_cache
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

MAX_EDAD_SEGUNDOS = 60

@lru_cache(maxsize=1)
def _clave_privada():
    valor = os.environ.get('LOGIN_RSA_PRIVATE_KEY_B64', '').strip()
    if valor:
        pem = base64.b64decode(valor, validate=True)
        return serialization.load_pem_private_key(pem, password=None)
    # Solo para desarrollo local: se crea una clave al iniciar cada proceso.
    # En un servidor con varios workers es OBLIGATORIO definir la clave en el entorno.
    if os.environ.get('RENDER') or os.environ.get('LOGIN_REQUIRE_PERSISTENT_KEY') == '1':
        raise RuntimeError('Configure LOGIN_RSA_PRIVATE_KEY_B64 para el despliegue.')
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def clave_publica_pem():
    return _clave_privada().public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('ascii')

def descifrar_password(cadena):
    if not cadena or len(cadena) > 4096:
        raise ValueError('Contenido cifrado ausente o excesivo')
    try:
        cifrado = base64.b64decode(cadena, validate=True)
        claro = _clave_privada().decrypt(
            cifrado,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                         algorithm=hashes.SHA256(), label=None),
        )
        datos = json.loads(claro.decode('utf-8'))
        clave = datos['password']
        marca = datos['timestamp']
        if not isinstance(clave, str) or not clave or len(clave) > 128:
            raise ValueError('Contraseña inválida')
        if not isinstance(marca, (float, int)) or abs(time.time() - marca) > MAX_EDAD_SEGUNDOS:
            raise ValueError('Petición expirada')
        return clave
    except (ValueError, TypeError, KeyError, UnicodeDecodeError, OverflowError) as exc:
        raise ValueError('No se pudo validar la petición cifrada') from exc
    except Exception as exc:
        raise ValueError('No se pudo descifrar la petición') from exc
