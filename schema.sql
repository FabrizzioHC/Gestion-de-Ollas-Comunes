CREATE DATABASE redcomunitaria;

-- 1. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'donador',
    telefono VARCHAR(20),
    dni VARCHAR(20),
    edad INT,
    vulnerabilidad VARCHAR(100),
    olla_asociada_id INT,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (olla_asociada_id) REFERENCES ollas_comunes(id)
);

-- 2. Tabla de Ollas Comunes
CREATE TABLE IF NOT EXISTS ollas_comunes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    usuario_id INT NOT NULL,
    descripcion TEXT,
    direccion TEXT NOT NULL,
    telefono VARCHAR(20),
    beneficiarios_atendidos INT DEFAULT 0,
    estado VARCHAR(50) DEFAULT 'activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES users(id)
);

-- 3. Tabla de Donaciones
CREATE TABLE IF NOT EXISTS donaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donador_id INT NOT NULL,
    olla_comun_id INT,
    tipo_recurso VARCHAR(100) NOT NULL,
    cantidad FLOAT NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (donador_id) REFERENCES users(id),
    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
);

-- 4. Tabla de Solicitudes de Recursos
CREATE TABLE IF NOT EXISTS solicitudes_recursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    olla_comun_id INT NOT NULL,
    tipo_recurso VARCHAR(100) NOT NULL,
    cantidad FLOAT NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    descripcion TEXT,
    urgencia VARCHAR(50) DEFAULT 'normal',
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
);

-- 5. Tabla de Entregas
CREATE TABLE IF NOT EXISTS entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donacion_id INT,
    solicitud_id INT,
    olla_comun_id INT NOT NULL,
    cantidad_entregada FLOAT NOT NULL,
    fecha_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (donacion_id) REFERENCES donaciones(id),
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes_recursos(id),
    FOREIGN KEY (olla_comun_id) REFERENCES ollas_comunes(id)
);

-- ================================================================================
-- Tambien puedes usar seed.py en vez de agregar estos pocos datos (!IMPORTANTE¡)
-- ================================================================================

USE redcomunitaria;

-- Insertar Ollas Comunes (Asociadas al usuario olla con ID 3)
INSERT INTO ollas_comunes (nombre, usuario_id, descripcion, direccion, telefono, beneficiarios_atendidos, estado) VALUES 
('Olla Común La Esperanza', 3, 'Atendiendo a madres solteras y niños', 'Av. Próceres de la Independencia 1234, SJL', '987654321', 45, 'activa'),
('Olla Común Fe y Solidaridad', 3, 'Comedor popular del sector alto', 'Quebrada Canto Grande Mz A Lote 5, SJL', '912345678', 80, 'activa');

-- Insertar Donaciones (Realizadas por el donador con ID 2)
INSERT INTO donaciones (donador_id, olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, estado) VALUES 
(2, 1, 'Alimentos', 50.5, 'kg', 'Sacos de arroz, avena y azúcar', 'aprobada'),
(2, 2, 'Insumos', 20.0, 'litros', 'Botellas de aceite vegetal', 'pendiente');

-- Insertar Solicitudes de Recursos (Requeridas por las ollas 1 y 2)
INSERT INTO solicitudes_recursos (olla_comun_id, tipo_recurso, cantidad, unidad, descripcion, urgencia, estado) VALUES 
(1, 'Vegetales', 30.0, 'kg', 'Necesitamos papas y cebollas para el menú de la semana', 'alta', 'pendiente'),
(2, 'Gas', 1.0, 'balón', 'Balón de gas de 10kg para cocinar', 'crítica', 'aprobada');

-- Insertar Entregas (Relacionadas a la donación 1 y olla 1)
INSERT INTO entregas (donacion_id, olla_comun_id, cantidad_entregada, observaciones) VALUES 
(1, 1, 50.5, 'Entrega realizada exitosamente por la mañana en el local principal');