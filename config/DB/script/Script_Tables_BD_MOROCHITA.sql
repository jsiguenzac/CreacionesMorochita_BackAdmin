-- Seteo de codificación

SET client_encoding = 'UTF8';

-- Creación de tablas
-- select * from tb_modulos
CREATE TABLE public.tb_modulos (
    "IdModulo" BIGSERIAL PRIMARY KEY,
    "Nombre" character varying(30) NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100)
);

CREATE TABLE public.tb_permisos (
    "IdPermiso" BIGSERIAL PRIMARY KEY,
    "IdModulo" BIGSERIAL NOT NULL,
    "Nombre" character varying(30) NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100),
    FOREIGN KEY ("IdModulo") REFERENCES public.tb_modulos("IdModulo")
);

CREATE TABLE public.tb_roles (
    "IdRol" BIGSERIAL PRIMARY KEY,
    "Nombre" character varying(30) NOT NULL,
    "Activo" boolean NOT NULL,
    "Descripcion" text NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100)
);

CREATE TABLE public.tb_rolpermisos (
    "IdRolPermiso" BIGSERIAL PRIMARY KEY,
    "IdPermiso" BIGSERIAL NOT NULL,
    "IdRol" BIGSERIAL NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100),   
    FOREIGN KEY ("IdPermiso") REFERENCES public.tb_permisos("IdPermiso"),
    FOREIGN KEY ("IdRol") REFERENCES public.tb_roles("IdRol")
);

CREATE TABLE public.tb_usuarios (
    "IdUsuario" BIGSERIAL PRIMARY KEY,
    "IdRol" BIGSERIAL NOT NULL,
    "Nombre" character varying(50) NOT NULL,
    "Apellidos" character varying(80) NOT NULL,
	"DNI" integer NULL,
    "Correo" character varying(100) NOT NULL,
    "Clave" character varying(300) NOT NULL,
    "Telefono" integer NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100),
    FOREIGN KEY ("IdRol") REFERENCES public.tb_roles("IdRol")
);

/** SPRINT 2 **/

-- Categoria Producto
CREATE TABLE public.tb_categoria_producto (
    "IdCategoria" BIGSERIAL PRIMARY KEY,
    "Nombre" character varying(50) NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100)
);

-- Productos
CREATE TABLE public.tb_productos (
    "IdProducto" BIGSERIAL PRIMARY KEY,
    "CodigoSKU" character varying(50) NOT NULL,
    "Stock" integer NULL,
    "Nombre" character varying(100) NOT NULL,
    "Precio" DECIMAL(10, 2) NOT NULL,
    "IdCategoria" BIGINT NOT NULL,
	"IdUsuario" BIGINT NOT NULL,
	"IdUsuarioProveedor" BIGINT NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100),
    FOREIGN KEY ("IdCategoria") REFERENCES public.tb_categoria_producto("IdCategoria"),
    FOREIGN KEY ("IdUsuario") REFERENCES public.tb_usuarios("IdUsuario"),
	FOREIGN KEY ("IdUsuarioProveedor") REFERENCES public.tb_usuarios("IdUsuario")
);

---- 3

-- Metodo Pago
CREATE TABLE public.tb_metodo_pago (
    "IdMetodoPago" BIGSERIAL PRIMARY KEY,
    "Nombre" character varying(50) NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100)
);

-- EstadoVenta - PAGADO - ANULADO - DEVOLUCION - PENDIENTE
CREATE TABLE public.tb_estado_venta (
    "IdEstadoVenta" BIGSERIAL PRIMARY KEY,
    "Nombre" character varying(50) NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100)
);

-- Venta
CREATE TABLE public.tb_venta (
    "IdVenta" BIGSERIAL PRIMARY KEY,
	"IdUsuarioVenta" BIGINT NOT NULL,
	"IdUsuarioCliente" BIGINT NOT NULL,
	"FechaHoraVenta" BIGINT NOT NULL,
	"IdEstadoVenta" BIGINT NOT NULL,
	"IdMetodoPago" BIGINT NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100),
    FOREIGN KEY ("IdUsuarioVenta") REFERENCES public.tb_usuarios("IdUsuario"),
	FOREIGN KEY ("IdUsuarioCliente") REFERENCES public.tb_usuarios("IdUsuario"),
	FOREIGN KEY ("IdEstadoVenta") REFERENCES public.tb_estado_venta("IdEstadoVenta"),
	FOREIGN KEY ("IdMetodoPago") REFERENCES public.tb_metodo_pago("IdMetodoPago")
);

-- DetalleVenta
CREATE TABLE public.tb_detalle_venta (
    "IdDetalleVenta" BIGSERIAL PRIMARY KEY,
	"IdVenta" BIGINT NOT NULL,
	"IdProducto" BIGINT NOT NULL,
    "Activo" boolean NOT NULL,
    "FechaHoraCreacion" TIMESTAMP,
    "UsuarioCreacion" character varying(100),
    "FechaHoraModificacion" TIMESTAMP,
    "UsuarioModificacion" character varying(100),
    FOREIGN KEY ("IdVenta") REFERENCES public.tb_venta("IdVenta"),
	FOREIGN KEY ("IdProducto") REFERENCES public.tb_productos("IdProducto")
);







