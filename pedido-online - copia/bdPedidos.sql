CREATE DATABASE pedido_online_db;
USE pedido_online_db;

-- 1. Roles de usuario
CREATE TABLE roles (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre_rol VARCHAR(50) NOT NULL
);

-- 2. Usuarios (clientes y administradores)
CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  id_rol INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- 3. Proveedores
CREATE TABLE proveedores (
  id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
  nombre_proveedor VARCHAR(150) NOT NULL,
  contacto VARCHAR(100),
  telefono VARCHAR(20),
  email VARCHAR(150),
  direccion VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Productos
CREATE TABLE productos (
  id_producto INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  descripcion TEXT,
  precio_unitario DECIMAL(10,2) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
ALTER TABLE productos 
ADD imagen VARCHAR(255) AFTER precio_unitario;


-- 5. Inventario (control de stock)
CREATE TABLE inventario (
  id_inventario INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  cantidad_actual INT NOT NULL,
  cantidad_minima INT NOT NULL DEFAULT 0,
  ubicacion VARCHAR(100),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 6. Compras (ingreso de stock)
CREATE TABLE compras (
  id_compra INT AUTO_INCREMENT PRIMARY KEY,
  id_proveedor INT NOT NULL,
  fecha_compra DATE NOT NULL,
  total_compra DECIMAL(12,2),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

-- 7. Detalle de compras
CREATE TABLE compra_detalle (
  id_detalle INT AUTO_INCREMENT PRIMARY KEY,
  id_compra INT NOT NULL,
  id_producto INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (id_compra) REFERENCES compras(id_compra),
  FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 8. Pedidos
CREATE TABLE pedidos (
  id_pedido INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL,
  fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('Pendiente','En proceso','Completado','Cancelado') DEFAULT 'Pendiente',
  total_pedido DECIMAL(12,2),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- 9. Detalle de pedidos
CREATE TABLE pedido_detalle (
  id_item INT AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT NOT NULL,
  id_producto INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
  FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 10. Movimientos de inventario (ingresos y salidas)
CREATE TABLE mov_inventario (
  id_mov INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  tipo_mov ENUM('Ingreso','Salida') NOT NULL,
  cantidad INT NOT NULL,
  fecha_mov DATETIME DEFAULT CURRENT_TIMESTAMP,
  descripcion VARCHAR(255),
  FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 11. Auditoría de acciones
CREATE TABLE auditoria (
  id_aud INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT,
  accion VARCHAR(100) NOT NULL,
  tabla_afectada VARCHAR(50),
  fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);


CREATE TABLE IF NOT EXISTS password_resets (
  id_reset INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token_hash VARCHAR(64) NOT NULL,
  expires_at DATETIME NOT NULL,
  used_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_token_hash (token_hash),
  INDEX idx_user_id (user_id),
  CONSTRAINT fk_password_resets_user
    FOREIGN KEY (user_id) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE pedido_online_db.pedidos ADD COLUMN fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;


-- 1. Roles
INSERT INTO roles (nombre_rol)
VALUES ('admin');

-- 2. Usuarios
INSERT INTO usuarios (nombre, email, password, id_rol)
VALUES ('Jose Perez', 'jperez@ecorreo.com', '123465', 1);

-- 3. Proveedores
INSERT INTO proveedores (nombre_proveedor, contacto, telefono, email, direccion)
VALUES ('prov1', 'maria', '15858568', 'contacto@correo.com', 'Zona 1, Ciudad de Guatemala');

-- 4. Productos
INSERT INTO productos (nombre, descripcion, precio_unitario)
VALUES ('Pulsera de plata', 'Pulsera artesanal de plata .925', 25.50);

-- 5. Inventario
INSERT INTO inventario (id_producto, cantidad_actual, cantidad_minima, ubicacion)
VALUES (1, 50, 5, 'Estantería');

-- 6. Compras
INSERT INTO compras (id_proveedor, fecha_compra, total_compra)
VALUES (1, '2025-04-01', 1275.00);

-- 7. Detalle de compras
INSERT INTO compra_detalle (id_compra, id_producto, cantidad, precio_unitario)
VALUES (1, 1, 50, 25.50);

-- 8. Pedidos
INSERT INTO pedidos (id_usuario, estado, total_pedido)
VALUES (1, 'Pendiente', 51.00);

-- 9. Detalle de pedidos
INSERT INTO pedido_detalle (id_pedido, id_producto, cantidad, precio_unitario)
VALUES (1, 1, 2, 25.50);

-- 10. Movimientos de inventario
INSERT INTO mov_inventario (id_producto, tipo_mov, cantidad, descripcion)
VALUES (1, 'Salida', 2, 'Pedido #1');

-- 11. Auditoría
INSERT INTO auditoria (id_usuario, accion, tabla_afectada)
VALUES (1, 'Creación de pedido', 'pedidos');
