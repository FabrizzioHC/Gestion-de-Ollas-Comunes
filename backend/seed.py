"""Script sencillo para poblar la base de datos con datos de ejemplo.

Ejecutar: python backend/seed.py
"""
from werkzeug.security import generate_password_hash
from infrastructure.database import Database
from infrastructure.repositories import (
    SQLiteUserRepository, SQLiteOllaComunRepository, SQLiteDonacionRepository
)
from domain.models import User, OllaComun, Donacion

def seed(db_path='redcomunitaria.db'):
    db = Database(db_path=db_path)
    user_repo = SQLiteUserRepository(db)
    olla_repo = SQLiteOllaComunRepository(db)
    don_repo = SQLiteDonacionRepository(db)

    # Crear usuarios de ejemplo
    try:
        admin = User(email='admin@example.com', password=generate_password_hash('admin123'), nombre='Admin', role='admin')
        admin_id = user_repo.create(admin)
    except Exception:
        admin_id = None

    try:
        donador = User(email='donador@example.com', password=generate_password_hash('donor123'), nombre='Juan Donante', role='donador')
        donador_id = user_repo.create(donador)
    except Exception:
        # intentar obtener existente
        existing = user_repo.find_by_email('donador@example.com')
        donador_id = existing.id if existing else None

    # ensure there's a user to assign as propietario de las ollas
    owner_id = None
    if admin_id:
        owner_id = admin_id
    elif donador_id:
        owner_id = donador_id
    else:
        try:
            olla_owner = User(email='olla_owner@example.com', password=generate_password_hash('owner123'), nombre='Owner Olla', role='olla_comun')
            owner_id = user_repo.create(olla_owner)
        except Exception:
            existing = user_repo.find_by_email('olla_owner@example.com')
            owner_id = existing.id if existing else None

    # Crear algunas ollas de ejemplo con distritos de Lima y necesidades típicas
    samples = [
        ('Olla Común Los Jardines', 'Apoyo alimentario y productos de higiene', 'San Juan de Lurigancho', 120, ['arroz','aceite','leche']),
        ('Olla Común Villa María', 'Raciones diarias y asistencia', 'Villa María del Triunfo', 85, ['arroz','menestras','fideos']),
        ('Olla Común Esperanza', 'Sopa solidaria y leche para niños', 'San Juan de Miraflores', 150, ['leche','sopa','pan']),
        ('Olla Común Unión y Fuerza', 'Apoyo familiar', 'Ate Vitarte', 95, ['arroz','aceite','verduras']),
        ('Olla Común Corazón de Pueblo', 'Raciones para adultos mayores', 'Comas', 70, ['menestras','aceite','azúcar']),
        ('Olla Común Manos Solidarias', 'Alimentos y abrigo', 'San Martín de Porres', 60, ['ropa','manta','alimentos']),
        ('Olla Común Barrio Unido', 'Asistencia interdisciplinaria', 'Los Olivos', 110, ['arroz','fideos','aceite'])
    ]

    created_ids = []
    for nombre, descripcion, direccion, beneficiarios, necesidades in samples:
        try:
            olla = OllaComun(
                nombre=nombre,
                descripcion=descripcion + ' - Necesidades: ' + ', '.join(necesidades),
                direccion=direccion,
                beneficiarios_atendidos=beneficiarios,
                usuario_id=owner_id
            )
            oid = olla_repo.create(olla)
            created_ids.append(oid)
        except Exception:
            pass

    # Crear donaciones de ejemplo
    sample_donaciones = [
        (donador_id, created_ids[0] if created_ids else None, 'arroz', 50, 'kg', 'Arroz para familias'),
        (donador_id, created_ids[1] if len(created_ids)>1 else None, 'aceite', 20, 'l', 'Aceite comestible'),
        (donador_id, created_ids[2] if len(created_ids)>2 else None, 'menestras', 30, 'kg', 'Lentejas y pallares')
    ]

    for d in sample_donaciones:
        try:
            donador_for = d[0] or donador_id or owner_id
            olla_for = d[1]
            if olla_for and donador_for:
                don = Donacion(donador_id=donador_for, olla_comun_id=olla_for, tipo_recurso=d[2], cantidad=d[3], unidad=d[4], descripcion=d[5])
                don_repo.create(don)
        except Exception:
            pass

    print('Seed complete. Created ollas:', created_ids)

if __name__ == '__main__':
    seed()
