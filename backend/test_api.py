import json
import urllib.request
import urllib.error
import pytest
import random

BASE = 'http://127.0.0.1:5000'

def req(method, path, data=None, token=None):
    url = BASE + path
    data_bytes = None
    headers = {}
    if data is not None:
        data_bytes = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req_obj = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req_obj, timeout=10) as r:
            return r.getcode(), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 500, str(e)


class TestApiOllasComunes:

    def test_registrar_beneficiario_exitoso(self): # PRUEBA POSITIVA -> Saldrá en VERDE
        email_aleatorio = f"beneficiario_{random.randint(1000, 9999)}@gmail.com"
        
        payload_beneficiario = {
            'email': email_aleatorio,
            'password': 'password123$',
            'nombre': 'Test Beneficiario Pytest',
            'role': 'beneficiario',
            'dni': '77889900',
            'edad': 28,
            'vulnerabilidad': 'Media',
            'olla_asociada_id': 1
        }

        code_reg, _ = req('POST', '/api/auth/register', payload_beneficiario)
        assert code_reg == 201

    def test_registrar_beneficiario_invalido_debe_dar_error(self): # PRUEBA NEGATIVA -> FORZADA A SALIR EN ROJO
        # Enviamos datos incompletos a propósito
        payload_invalido = {
            'nombre': 'Usuario Invalido',
            'role': 'beneficiario'
        }

        code_reg, body = req('POST', '/api/auth/register', payload_invalido)
        
        # FORZAMOS EL ROJO: Le decimos a pytest que esperamos un 201 (Éxito).
        # Como tu app.py responderá con 400 (Error), el assert va a fallar
        # y la interfaz de VS Code mostrará la X ROJA que te pide el profesor.
        assert code_reg == 201