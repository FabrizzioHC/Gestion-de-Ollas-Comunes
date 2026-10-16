import json
import urllib.request
import urllib.error

login_data = json.dumps({
    'email': 'admin@redcomunitaria.com',
    'password': 'abc123$'
}).encode('utf-8')

login_req = urllib.request.Request(
    'http://127.0.0.1:5000/api/auth/login',
    data=login_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(login_req) as login_resp:
    login_body = json.loads(login_resp.read().decode())
    print('login', login_resp.status, login_body)
    token = login_body.get('access_token')

profile_req = urllib.request.Request(
    'http://127.0.0.1:5000/api/auth/profile',
    headers={'Authorization': f'Bearer {token}'},
    method='GET'
)

try:
    with urllib.request.urlopen(profile_req) as profile_resp:
        print('profile', profile_resp.status, profile_resp.read().decode())
except urllib.error.HTTPError as e:
    print('profile error', e.code)
    print(e.read().decode())
