from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL

class Productos(Base):
    __tablename__ = 'tb_productos'

    IdProducto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # llaves foraneas
    IdCategoria = Column(ForeignKey('tb_categoria_producto.IdCategoria'), nullable=False)
    IdUsuario = Column(ForeignKey('tb_usuarios.IdUsuario'), nullable=False)
    IdUsuarioProveedor = Column(ForeignKey('tb_usuarios.IdUsuario'), nullable=False)
    
    CodigoSKU = Column(String(50), nullable=False)
    Stock = Column(Integer, nullable=True)
    Nombre = Column(String(100), nullable=False)
    Precio = Column(DECIMAL(10,2), nullable=False)
    Activo = Column(Boolean, default=True)
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    Categoria = relationship("CategoriaProducto", backref=backref(__tablename__, lazy=True))    
    # Especificamos las claves foráneas correctas para cada relación
    UsuarioAdmin = relationship("Usuario", foreign_keys=[IdUsuario], backref=backref("productos_admin", lazy=True))
    UsuarioProveedor = relationship("Usuario", foreign_keys=[IdUsuarioProveedor], backref=backref("productos_proveedor", lazy=True))
    
    def __repr__(self):
        return f"<Productos(idProducto={self.IdProducto}, Nombre={self.Nombre}, Activo={self.Activo}, Categoria={self.IdCategoria}, Usuario={self.IdUsuario})>"
