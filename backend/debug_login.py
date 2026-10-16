import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from infrastructure.database import Database
from infrastructure.repositories import SQLiteUserRepository
from werkzeug.security import check_password_hash

db = Database(db_path='redcomunitaria.db')
repo = SQLiteUserRepository(db)
users = repo.find_all()
print('USERS:', len(users))
for u in users:
    print(u.id, u.email, u.role, u.activo)
    if u.email == 'admin@redcomunitaria.com':
        print('admin password ok', check_password_hash(u.password, 'abc123$'))
