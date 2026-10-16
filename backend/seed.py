"""
Script para poblar la base de datos MySQL con información de prueba.
"""
from infrastructure.database import Database
from werkzeug.security import generate_password_hash
import pymysql

def seed_database():
    db = Database()
    
    with db.get_cursor() as cursor:
        print("Iniciando la inserción de datos de prueba...")
        
        # 1. Insertar 5 Usuarios Donadores adicionales
        donadores = [
            ('juan@gmail.com', 'abc123$', 'Juan Pérez', 'donador', '987654321', '76543210'),
            ('maria@gmail.com', 'abc123$', 'María Gómez', 'donador', '912345678', '87654321'),
            ('carlos@gmail.com', 'abc123$', 'Carlos Ruiz', 'donador', '923456789', '12345678'),
            ('ana@gmail.com', 'abc123$', 'Ana Torres', 'donador', '934567890', '23456789'),
            ('luis@gmail.com', 'abc123$', 'Luis Flores', 'donador', '945678901', '34567890')
        ]
        
        for email, pwd, nombre, rol, tel, dni in donadores:
            try:
                hashed_pwd = generate_password_hash(pwd)
                cursor.execute(
                    "INSERT INTO users (email, password, nombre, role, telefono, dni) VALUES (%s, %s, %s, %s, %s, %s)",
                    (email, hashed_pwd, nombre, rol, tel, dni)
                )
            except pymysql.err.IntegrityError:
                pass # El usuario ya existe
                
        # 2. Insertar 10 Ollas Comunes (Asociadas al usuario olla@gmail.com que tiene id=3)
        ollas = [
            ('Olla Común Esperanza', 3, 'Atención a 50 familias', 'Av. Próceres de la Independencia 1234, SJL', '999111222', 50),
            ('Olla Fe y Alegría', 3, 'Comedor del sector', 'Quebrada Canto Grande Mz A Lt 5, SJL', '999222333', 80),
            ('Olla Las Mercedes', 3, 'Desayunos y almuerzos', 'Campoy Calle 4, SJL', '999333444', 45),
            ('Olla Solidaria Huáscar', 3, 'Apoyo a madres solteras', 'AA.HH Huáscar Grupo 2, SJL', '999444555', 60),
            ('Olla Mangomarca', 3, 'Comidas nutritivas', 'Mangomarca Baja Mz B, SJL', '999555666', 40),
            ('Olla Zárate Unido', 3, 'Almuerzos solidarios', 'Zárate Av. Gran Chimú 456, SJL', '999666777', 75),
            ('Olla Corazón de Jesús', 3, 'Atención niños y ancianos', 'Jicamarca Sector Sur, SJL', '999777888', 55),
            ('Olla 10 de Octubre', 3, 'Comedor vecinal', '10 de Octubre 3ra etapa, SJL', '999888999', 90),
            ('Olla Santa María', 3, 'Raciones diarias', 'Mariscal Cáceres Mz D, SJL', '999123123', 65),
            ('Olla Virgen del Carmen', 3, 'Alimentación comunitaria', 'Bayóvar Sector 2, SJL', '999321321', 70)
        ]
        
        cursor.execute("SELECT count(*) as count FROM ollas_comunes")
        if cursor.fetchone()['count'] == 0:
            for n, uid, desc, dir, tel, ben in ollas:
                cursor.execute(
                    "INSERT INTO ollas_comunes (nombre, usuario_id, descripcion, direccion, telefono, beneficiarios_atendidos) VALUES (%s, %s, %s, %s, %s, %s)",
                    (n, uid, desc, dir, tel, ben)
                )

        # 3. Insertar 5 Donaciones (Por el usuario donador@gmail.com con ID 2)
        donaciones = [
            (2, 1, 'Alimentos', 50.0, 'kg', 'Sacos de arroz y azúcar', 'aprobada'),
            (2, 2, 'Vegetales', 20.0, 'kg', 'Papas y cebollas', 'aprobada'),
            (2, 3, 'Insumos', 15.0, 'litros', 'Aceite vegetal', 'pendiente'),
            (2, 4, 'Proteínas', 10.0, 'kg', 'Pollo y conservas de atún', 'pendiente'),
            (2, 5, 'Menestras', 25.0, 'kg', 'Lentejas y frijoles', 'rechazada')
        ]
        
        cursor.execute("SELECT count(*) as count FROM donaciones")
        if cursor.fetchone()['count'] == 0:
            for did, oid, tipo, cant, uni, desc, est in donaciones:
                cursor.execute(
                    "INSERT INTO donaciones (donador_id, olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (did, oid, tipo, cant, uni, desc, est)
                )

        # 4. Insertar 5 Solicitudes
        solicitudes = [
            (1, 'Agua potable', 100.0, 'litros', 'Necesitamos agua para cocinar', 'crítica', 'pendiente'),
            (2, 'Gas', 1.0, 'balón', 'Balón de gas de 10kg', 'alta', 'aprobada'),
            (3, 'Carnes', 15.0, 'kg', 'Menudencia o pollo', 'normal', 'pendiente'),
            (4, 'Verduras', 20.0, 'kg', 'Zanahoria, tomate, zapallo', 'normal', 'completada'),
            (5, 'Menestras', 10.0, 'kg', 'Arvejas o pallares', 'alta', 'pendiente')
        ]
        
        cursor.execute("SELECT count(*) as count FROM solicitudes_recursos")
        if cursor.fetchone()['count'] == 0:
            for oid, tipo, cant, uni, desc, urg, est in solicitudes:
                cursor.execute(
                    "INSERT INTO solicitudes_recursos (olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, urgencia, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (oid, tipo, cant, uni, desc, urg, est)
                )

        print("¡Datos de prueba insertados exitosamente en MySQL!")

if __name__ == '__main__':
    seed_database()