-- ==========================================================
-- SISTEMA DE OLLAS COMUNES - RED COMUNITARIA
-- Estructura + datos de prueba
--
--
-- Si lo ejecutas a mano en MySQL Workbench, primero selecciona la base:
--   USE sistema_ollas_comunes_vs;
--
-- Todos los usuarios de prueba tienen la contrasena: abc123$
--  el UsuarioDAO lo agrega al verificar el login)
-- ==========================================================

CREATE DATABASE sistema_ollas_comunes_vs;

USE sistema_ollas_comunes_vs;

-- ==========================================================
-- 1. ESTRUCTURA
-- ==========================================================

-- Usuarios (Admin, Lideresa, Donador)
CREATE TABLE Usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    rol ENUM('ADMIN', 'LIDERESA', 'DONADOR') NOT NULL,
    telefono VARCHAR(20),
    dni VARCHAR(15) UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ollas comunes (perfil de la organización)
CREATE TABLE Olla_Comun (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,                       -- Lideresa a cargo
    nombre_olla VARCHAR(150) NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(255) NOT NULL,
    beneficiarios_atendidos INT DEFAULT 0,
    estado ENUM('ACTIVA', 'PAUSADA', 'INACTIVA') DEFAULT 'ACTIVA',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_nombre_olla UNIQUE (nombre_olla),
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id) ON DELETE CASCADE
);

-- Solicitudes (lo que la lideresa pide cuando hay escasez)
CREATE TABLE Solicitud (
    id INT AUTO_INCREMENT PRIMARY KEY,
    olla_id INT NOT NULL,
    recurso_necesitado VARCHAR(100) NOT NULL,
    cantidad_necesitada DECIMAL(10,2) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    nivel_urgencia VARCHAR(20) DEFAULT 'Normal',   -- Normal, Alta, Crítica
    estado VARCHAR(20) DEFAULT 'Pendiente',        -- Pendiente, Aceptada, Completada, Rechazada
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (olla_id) REFERENCES Olla_Comun(id) ON DELETE CASCADE
);

-- Donaciones (aporte que registra el donador)
CREATE TABLE Donacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donador_id INT NOT NULL,
    olla_id INT NOT NULL,
    mensaje VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'Pendiente',        -- Pendiente, Aceptada, Entregada, Rechazada
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recurso VARCHAR(100),                          -- Ej: Arroz
    cantidad DECIMAL(10,2),                        -- Ej: 50
    unidad_medida VARCHAR(20),                     -- Ej: kg
    FOREIGN KEY (donador_id) REFERENCES Usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (olla_id) REFERENCES Olla_Comun(id) ON DELETE CASCADE
);

-- Recursos (inventario de cada olla; olla_id NULL = almacén central)
CREATE TABLE recurso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    olla_id INT NULL,
    nombre_recurso VARCHAR(100) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (olla_id) REFERENCES Olla_Comun(id) ON DELETE CASCADE
);

-- ==========================================================
-- 2. DATOS DE PRUEBA
-- ==========================================================

-- USUARIOS (1 Admin, 10 Lideresas, 15 Donadores)
-- id 1 = admin | ids 2-11 = lideresas | ids 12-26 = donadores
INSERT INTO Usuario (email, password_hash, nombres, apellidos, rol, telefono, dni, activo) VALUES
('admin.redcomunitaria@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Carlos Alberto', 'Mendoza Rojas', 'ADMIN', '987654321', '45123678', TRUE),

('rosa.gomez@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Rosa Elvira', 'Gómez Palomino', 'LIDERESA', '912345678', '08234561', TRUE),
('maria.quispe@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'María Isabel', 'Quispe Huamán', 'LIDERESA', '923456789', '09345672', TRUE),
('carmen.flores@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Carmen Rosa', 'Flores Chávez', 'LIDERESA', '934567890', '10456783', TRUE),
('juana.mamani@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Juana Luz', 'Mamani Condori', 'LIDERESA', '945678901', '41567894', TRUE),
('teresa.vargas@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Teresa Aurora', 'Vargas Ccoa', 'LIDERESA', '956789012', '07678905', TRUE),
('luz.rojas@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Luz Marina', 'Rojas Villanueva', 'LIDERESA', '967890123', '42789016', TRUE),
('elena.huaman@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Elena Victoria', 'Huamán Anccasi', 'LIDERESA', '978901234', '09890127', TRUE),
('doris.condori@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Doris Milagros', 'Condori Apaza', 'LIDERESA', '989012345', '40901238', TRUE),
('gladys.ramos@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Gladys Nelly', 'Ramos Salazar', 'LIDERESA', '990123456', '10012349', TRUE),
('norma.cardenas@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Norma Beatriz', 'Cárdenas Yupanqui', 'LIDERESA', '901234567', '43123450', TRUE),

('luis.torres@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Luis Fernando', 'Torres Aguilar', 'DONADOR', '955444331', '70123451', TRUE),
('jorge.salas@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Jorge Armando', 'Salas Medina', 'DONADOR', '955444332', '70234562', TRUE),
('miguel.vega@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Miguel Ángel', 'Vega Paredes', 'DONADOR', '955444333', '71345673', TRUE),
('sofia.luna@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Sofía Alejandra', 'Luna Ríos', 'DONADOR', '955444334', '72456784', TRUE),
('raul.castro@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Raúl Eduardo', 'Castro Bendezú', 'DONADOR', '955444335', '70567895', TRUE),
('lucia.rios@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Lucía Fernanda', 'Ríos Delgado', 'DONADOR', '955444336', '73678906', TRUE),
('pedro.cruz@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Pedro Pablo', 'Cruz Valdivia', 'DONADOR', '955444337', '71789017', TRUE),
('diana.silva@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Diana Carolina', 'Silva Ortiz', 'DONADOR', '955444338', '72890128', TRUE),
('victor.paz@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Víctor Hugo', 'Paz Espinoza', 'DONADOR', '955444339', '70901239', TRUE),
('laura.soto@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Laura Patricia', 'Soto Mendívil', 'DONADOR', '955444340', '74012340', TRUE),
('andres.ledesma@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Andrés Felipe', 'Ledesma Cano', 'DONADOR', '955444341', '71123452', TRUE),
('katherine.ugarte@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Katherine Milagros', 'Ugarte Ruiz', 'DONADOR', '955444342', '72234563', TRUE),
('renzo.bustamante@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Renzo Alonso', 'Bustamante Gil', 'DONADOR', '955444343', '73345674', TRUE),
('patricia.zevallos@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Patricia del Pilar', 'Zevallos Arana', 'DONADOR', '955444344', '70456785', FALSE),
('marco.guerra@gmail.com', 'c6v38A5bjfvbCw7J$90756b59534860acbbff8d14efb405a3e6b92bde2290c8061543bfc2f4ee9a5f38baae8d57329936ba349b25fcceec91786ce9d3e950dfa03496e798a8d5c820', 'Marco Antonio', 'Guerra Tello', 'DONADOR', '955444345', '71567896', TRUE);

-- OLLAS COMUNES (10 ollas -> lideresas con id 2 al 11)
INSERT INTO Olla_Comun (usuario_id, nombre_olla, descripcion, direccion, beneficiarios_atendidos, estado) VALUES
(2,  'Olla Solidaria SJL', 'Apoyo diario para familias vulnerables del distrito', 'Av. Próceres de la Independencia 1234, San Juan de Lurigancho', 120, 'ACTIVA'),
(3,  'Esperanza de La Molina', 'Atención para adultos mayores y niños', 'Sector Musa Mz H Lt 5, La Molina', 85, 'ACTIVA'),
(4,  'Corazón de Ate', 'Almuerzos comunitarios de lunes a viernes', 'Huaycán Zona Z, Ate Vitarte', 150, 'ACTIVA'),
(5,  'Fuerza Trujillo', 'Comedor autogestionado por madres de familia', 'Barrio El Porvenir, Trujillo', 200, 'ACTIVA'),
(6,  'Unidos por El Agustino', 'Brindamos desayunos y almuerzos solidarios', 'Cerro El Pino Alto, El Agustino', 95, 'PAUSADA'),
(7,  'Manos a la Olla VES', 'Apoyo a familias de escasos recursos', 'Sector 3 Grupo 14, Villa El Salvador', 110, 'ACTIVA'),
(8,  'Luz y Esperanza', 'Comedor solidario para niños en edad escolar', 'Lomas de Carabayllo, Carabayllo', 180, 'ACTIVA'),
(9,  'Ollita Milagrosa', 'Iniciativa vecinal para tiempos de crisis', 'AA.HH. Los Constructores, San Juan de Lurigancho', 70, 'ACTIVA'),
(10, 'Santa Rosa de Comas', 'Comedor popular con más de 10 años de servicio', 'Jr. Los Girasoles 450, Collique, Comas', 130, 'ACTIVA'),
(11, 'Nuevo Amanecer Pachacámac', 'Olla en reorganización por falta de local', 'Mz C Lt 9, Manchay, Pachacámac', 60, 'INACTIVA');

-- RECURSOS: inventario de cada olla (olla_id 1 al 10)
INSERT INTO recurso (olla_id, nombre_recurso, cantidad, unidad_medida) VALUES
(1,  'Arroz Costeño', 50.00, 'kg'),
(1,  'Aceite Vegetal', 6.00, 'litros'),
(2,  'Aceite Vegetal', 12.50, 'litros'),
(2,  'Azúcar Rubia', 18.00, 'kg'),
(3,  'Fideos Tallarín', 20.00, 'kg'),
(3,  'Sal de Mesa', 8.00, 'kg'),
(4,  'Lentejas', 15.00, 'kg'),
(4,  'Arroz Costeño', 40.00, 'kg'),
(5,  'Avena', 10.00, 'kg'),
(5,  'Leche Evaporada', 12.00, 'unidades'),
(6,  'Atún en conservas', 48.00, 'unidades'),
(6,  'Frejol Canario', 22.00, 'kg'),
(7,  'Azúcar Rubia', 25.00, 'kg'),
(7,  'Harina de Trigo', 30.00, 'kg'),
(8,  'Papas', 100.00, 'kg'),
(8,  'Cebolla Roja', 35.00, 'kg'),
(9,  'Arroz Costeño', 75.00, 'kg'),
(9,  'Pollo', 18.00, 'kg'),
(10, 'Garbanzos', 9.00, 'kg'),
(10, 'Fideos Spaghetti', 14.00, 'kg');

-- RECURSOS: almacén central (olla_id NULL)
INSERT INTO recurso (olla_id, nombre_recurso, cantidad, unidad_medida) VALUES
(NULL, 'Arroz', 115.00, 'kg'),
(NULL, 'Aceite', 60.00, 'litros'),
(NULL, 'Fideos', 80.00, 'kg'),
(NULL, 'Lentejas', 45.00, 'kg'),
(NULL, 'Azúcar', 70.00, 'kg'),
(NULL, 'Leche Evaporada', 96.00, 'unidades'),
(NULL, 'Atún', 120.00, 'unidades'),
(NULL, 'Harina', 8.00, 'sacos');

-- SOLICITUDES (peticiones de las lideresas)
INSERT INTO Solicitud (olla_id, recurso_necesitado, cantidad_necesitada, unidad_medida, nivel_urgencia, estado) VALUES
(1,  'Aceite', 20.00, 'litros', 'Alta', 'Pendiente'),
(2,  'Arroz', 100.00, 'kg', 'Crítica', 'Pendiente'),
(3,  'Fideos', 50.00, 'kg', 'Normal', 'Completada'),
(4,  'Pollo', 30.00, 'kg', 'Crítica', 'Pendiente'),
(5,  'Leche Evaporada', 48.00, 'unidades', 'Alta', 'Aceptada'),
(6,  'Verduras surtidas', 50.00, 'kg', 'Normal', 'Completada'),
(7,  'Balón de Gas', 2.00, 'unidades', 'Crítica', 'Pendiente'),
(8,  'Menestras', 30.00, 'kg', 'Alta', 'Pendiente'),
(9,  'Huevos', 15.00, 'kg', 'Normal', 'Pendiente'),
(10, 'Ollas grandes de 40 litros', 2.00, 'unidades', 'Alta', 'Rechazada'),
(1,  'Sal', 10.00, 'kg', 'Normal', 'Completada'),
(3,  'Aceite', 15.00, 'litros', 'Alta', 'Aceptada'),
(4,  'Carne de res', 25.00, 'kg', 'Alta', 'Completada'),
(7,  'Pan', 200.00, 'unidades', 'Normal', 'Pendiente'),
(9,  'Balón de Gas', 3.00, 'unidades', 'Crítica', 'Pendiente');

-- DONACIONES (donadores con id 12 al 26 hacia diferentes ollas)
INSERT INTO Donacion (donador_id, olla_id, mensaje, estado, recurso, cantidad, unidad_medida) VALUES
(12, 1,  'Llevo 20 litros de aceite este viernes', 'Aceptada', 'Aceite', 20.00, 'litros'),
(13, 2,  'Donación de 2 sacos de arroz (100kg total)', 'Entregada', 'Arroz', 100.00, 'kg'),
(14, 3,  'Compré 50kg de fideos para la olla', 'Entregada', 'Fideos', 50.00, 'kg'),
(15, 4,  'Transferencia para comprar pollo coordinada por WhatsApp', 'Pendiente', 'Pollo', 30.00, 'kg'),
(16, 5,  'Llevaré 2 cajas de leche evaporada', 'Aceptada', 'Leche Evaporada', 24.00, 'unidades'),
(17, 6,  'Aporte de verduras del mercado mayorista', 'Entregada', 'Verduras', 50.00, 'kg'),
(18, 7,  'Pagaré la recarga de 2 balones de gas', 'Pendiente', 'Balón De Gas', 2.00, 'unidades'),
(19, 8,  'Dejaré 30 kilos de lentejas el fin de semana', 'Pendiente', 'Lentejas', 30.00, 'kg'),
(20, 9,  'Puedo llevar 10 kilos de huevos el sábado por la mañana', 'Aceptada', 'Huevos', 10.00, 'kg'),
(21, 10, 'Donaré 2 ollas grandes que ya no uso en mi negocio', 'Pendiente', 'Ollas Grandes', 2.00, 'unidades'),
(22, 1,  'Llevaré 10 kg de sal', 'Entregada', 'Sal', 10.00, 'kg'),
(23, 3,  'Compraré 15 litros de aceite el lunes', 'Aceptada', 'Aceite', 15.00, 'litros'),
(24, 4,  'Traigo 25 kg de carne de res de mi carnicería', 'Entregada', 'Carne De Res', 25.00, 'kg'),
(25, 7,  'Coordinaré la entrega de 200 panes con la panadería del barrio', 'Pendiente', 'Pan', 200.00, 'unidades'),
(26, 9,  'Pagaré 3 balones de gas, avisen cuándo recogerlos', 'Aceptada', 'Balón De Gas', 3.00, 'unidades'),
(12, 2,  'Segunda donación: 50 kg de arroz adicionales', 'Pendiente', 'Arroz', 50.00, 'kg'),
(14, 8,  'Llevo 20 kg de papas amarillas de mi chacra', 'Entregada', 'Papas', 20.00, 'kg'),
(16, 10, 'Apoyo con 10 kg de fideos para la reapertura', 'Pendiente', 'Fideos', 10.00, 'kg'),
(18, 5,  'Donaré avena para los desayunos', 'Aceptada', 'Avena', 10.00, 'kg'),
(21, 6,  'Ayuda con víveres para los niños del comedor', 'Entregada', 'Víveres Surtidos', 15.00, 'kg');