"""Pruebas HTTP del login, sin conexión a MySQL. Ejecutar: python -m unittest discover -s pruebas/http -v"""
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask
import base64
import json
import time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from backend.security.login_crypto import clave_publica_pem
from backend.controllers.usuario_controller import usuario_bp


class PruebasCodigosLogin(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__, template_folder='../../frontend/templates')
        # La plantilla se busca a partir de la raíz de trabajo, no del paquete del test.
        from pathlib import Path
        app.template_folder = str(Path(__file__).resolve().parents[2] / 'frontend' / 'templates')
        app.secret_key = 'solo-pruebas'
        app.register_blueprint(usuario_bp)
        app.add_url_rule('/', 'home', lambda: 'Inicio')
        app.testing = True
        self.cliente = app.test_client()
        self.usuario = SimpleNamespace(
            id=1, email='test@example.com', password_hash='hash-ficticio',
            nombres='Prueba', rol='DONADOR', activo=True,
            bloqueado_hasta=None, intentos_fallidos=0,
        )

    def enviar(self, password='incorrecta'):
        publica = serialization.load_pem_public_key(clave_publica_pem().encode())
        payload = json.dumps({'password':password, 'timestamp':time.time()}).encode()
        cifrado = publica.encrypt(payload, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        return self.cliente.post('/login', data={
            'email':'test@example.com',
            'encrypted_password':base64.b64encode(cifrado).decode()
        })

    def test_plaintext_no_se_acepta(self):
        respuesta = self.cliente.post('/login', data={'email':'test@example.com', 'password':'secreto'})
        self.assertEqual(respuesta.status_code, 400)

    def test_clave_publica_disponible(self):
        r = self.cliente.get('/login/clave-publica')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'BEGIN PUBLIC KEY', r.data)

    def test_get_ok(self):
        self.assertEqual(self.cliente.get('/login').status_code, 200)

    @patch('backend.controllers.usuario_controller.UsuarioDAO.obtener_por_email', return_value=None)
    def test_correo_desconocido_401(self, _):
        self.assertEqual(self.enviar().status_code, 401)

    def test_formulario_incompleto_400(self):
        self.assertEqual(self.cliente.post('/login', data={'email': '', 'password': ''}).status_code, 400)

    @patch('backend.controllers.usuario_controller.UsuarioDAO.obtener_por_email')
    def test_cuenta_suspendida_403(self, buscar):
        self.usuario.activo = False
        buscar.return_value = self.usuario
        self.assertEqual(self.enviar().status_code, 403)

    @patch('backend.controllers.usuario_controller.UsuarioDAO.obtener_por_email')
    def test_bloqueo_activo_429(self, buscar):
        self.usuario.bloqueado_hasta = datetime.now() + timedelta(seconds=90)
        buscar.return_value = self.usuario
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 429)
        self.assertGreater(int(respuesta.headers['Retry-After']), 0)

    @patch('backend.controllers.usuario_controller.UsuarioDAO.registrar_intento_fallido', return_value=1)
    @patch('backend.controllers.usuario_controller.check_password_hash', return_value=False)
    @patch('backend.controllers.usuario_controller.UsuarioDAO.obtener_por_email')
    def test_clave_incorrecta_401(self, buscar, _hash, _registro):
        buscar.return_value = self.usuario
        self.assertEqual(self.enviar().status_code, 401)

    @patch('backend.controllers.usuario_controller.UsuarioDAO.registrar_intento_fallido', return_value=3)
    @patch('backend.controllers.usuario_controller.check_password_hash', return_value=False)
    @patch('backend.controllers.usuario_controller.UsuarioDAO.obtener_por_email')
    def test_tercer_intento_429(self, buscar, _hash, _registro):
        buscar.return_value = self.usuario
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 429)
        self.assertEqual(respuesta.headers['Retry-After'], '180')

    @patch('backend.controllers.usuario_controller.UsuarioDAO.reiniciar_intentos')
    @patch('backend.controllers.usuario_controller.check_password_hash', return_value=True)
    @patch('backend.controllers.usuario_controller.UsuarioDAO.obtener_por_email')
    def test_acceso_correcto_302(self, buscar, _hash, _reiniciar):
        buscar.return_value = self.usuario
        self.assertEqual(self.enviar(password='correcta').status_code, 302)


if __name__ == '__main__':
    unittest.main()
