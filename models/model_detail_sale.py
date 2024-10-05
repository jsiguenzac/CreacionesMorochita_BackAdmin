from datetime import datetime
from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

class DetalleVenta(Base):
    __tablename__ = 'tb_detalle_venta'

    IdDetalleVenta = Column(Integer, primary_key=True, index=True)
    
    IdVenta = Column(Integer, ForeignKey('tb_venta.IdVenta'), nullable=False)
    IdProducto = Column(Integer, ForeignKey('tb_productos.IdProducto'), nullable=False)
    
    Cantidad = Column(Integer, nullable=False)
    Activo = Column(Boolean, default=True)
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    Venta = relationship("EstadoVenta", backref=backref("tb_detalle_venta", lazy=True))
    Producto = relationship("MetodoPago", backref=backref("tb_detalle_venta", lazy=True))
    
    def __repr__(self):
        return f"<DetalleVenta(IdDetalleVenta={self.IdDetalleVenta}, IdVenta={self.IdVenta}, IdProducto={self.IdProducto}, Activo={self.Activo})>"