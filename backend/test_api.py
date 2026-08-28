import json
import urllib.request
import urllib.error

BASE='http://127.0.0.1:5000'

def req(method, path, data=None, token=None):
    url = BASE + path
    data_bytes = None
    headers = {}
    if data is not None:
        data_bytes = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8')
            print(f"{method} {path} -> {r.getcode()}\n{body}\n")
            return r.getcode(), body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"{method} {path} -> HTTPERR {e.code}\n{body}\n")
        return e.code, body
    except Exception as e:
        print(f"{method} {path} -> ERR {e}\n")
        return None, str(e)

if __name__ == '__main__':
    # admin login
    code, body = req('POST','/api/auth/login', {'email':'admin@redcomunitaria.com','password':'abc123$'})
    admin_token = None
    try:
        admin_token = json.loads(body).get('access_token')
    except:
        pass

    # create olla without token
    req('POST','/api/ollas', {'nombre':'Olla Prueba UI','descripcion':'Crear desde UI sin token','direccion':'Lince','beneficiarios_atendidos':20})

    # create olla with admin token
    code, body = req('POST','/api/ollas', {'nombre':'Olla Prueba Admin','descripcion':'Crear desde UI con admin token','direccion':'Miraflores','beneficiarios_atendidos':30}, token=admin_token)
    new_id = None
    try:
        j = json.loads(body)
        new_id = j.get('id') or j.get('olla_id')
    except:
        new_id = None

    if new_id:
        # try PUT
        req('PUT', f'/api/ollas/{new_id}', {'nombre':'Olla Prueba Admin Edit','descripcion':'Editada via script'}, token=admin_token)
        # delete
        req('DELETE', f'/api/ollas/{new_id}', token=admin_token)

    # donador login
    code, body = req('POST','/api/auth/login', {'email':'donador@gmail.com','password':'abc123$'})
    donor_token = None
    try:
        donor_token = json.loads(body).get('access_token')
    except:
        donor_token = None

    # create donation
    req('POST','/api/donaciones', {'olla_comun_id':1,'tipo_recurso':'alimentos','cantidad':5,'unidad':'kg','descripcion':'Prueba donacion'}, token=donor_token)
