"""Verifica integración sin conectar a MySQL. Ejecutar desde la raíz del proyecto."""
from pathlib import Path
import sys
from html.parser import HTMLParser
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run import app
app.secret_key = app.secret_key or "clave-exclusiva-de-la-prueba-de-plantillas"
from flask import render_template, session
class PanelParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.settings=[]; self.js=0; self.css=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if a.get('data-setting'):self.settings.append(a['data-setting'])
        if a.get('src','').endswith('/accessibility.js'):self.js+=1
        if a.get('href','').endswith('/accessibility.css'):self.css+=1
p=Path(app.root_path)/'frontend/templates'
names=[f.name for f in p.glob('*.html') if not f.name.startswith('_') and f.name!='base.html']
context=dict(datos={},usu={'email':'prueba@example.test','rol':'ADMIN'},usuarios=[],ollas=[],solicitudes=[],donaciones=[],recursos=[],lista_ollas=[],donaciones_globales=[],estadisticas={})
count=0
for role in (None,'ADMIN','DONADOR','LIDERESA'):
    with app.test_request_context('/'):
        if role:session.update(usuario_id=1,rol=role,nombres='Prueba')
        for name in names:
            parser=PanelParser();parser.feed(render_template(name,**context))
            assert parser.ids.count('rc-a11y')==1,(name,role,'panel duplicado/ausente')
            assert parser.ids.count('rc-a11y-panel')==1
            assert parser.js==parser.css==1
            assert set(parser.settings)=={'text','contrast','cursor','mask','dyslexia','line'}
            count+=1
print(f'CORRECTO: {len(names)} páginas × 4 estados de sesión = {count} renderizados. Panel y seis opciones, sin duplicados.')
