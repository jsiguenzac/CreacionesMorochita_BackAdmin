from datetime import datetime
from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL

class Venta(Base):
    __tablename__ = 'tb_venta'

    IdVenta = Column(Integer, primary_key=True, index=True)
    
    IdUsuarioVenta = Column(Integer, ForeignKey('tb_usuarios.IdUsuario'), nullable=False)
    IdEstadoVenta = Column(Integer, ForeignKey('tb_estado_venta.IdEstadoVenta'), nullable=False)
    IdMetodoPago = Column(Integer, ForeignKey('tb_metodo_pago.IdMetodoPago'), nullable=False)
    
    NombreCliente = Column(String(100), nullable=False)
    DNICliente = Column(Integer(), nullable=True)
    FechaHoraVenta = Column(DateTime, nullable=False, default=datetime.now())
    Activo = Column(Boolean, default=True)
    Total = Column(DECIMAL(10,2), nullable=True)
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    UsuarioVenta = relationship("Usuario", backref=backref(__tablename__, lazy=True))
    EstadoVenta = relationship("EstadoVenta", backref=backref(__tablename__, lazy=True))
    MetodoPago = relationship("MetodoPago", backref=backref(__tablename__, lazy=True))
    DetalleVenta = relationship("DetalleVenta", backref=backref(__tablename__, lazy=True))
    
    def __repr__(self):
        return f"<Venta(IdVenta={self.IdVenta}, IdEstadoVenta={self.IdEstadoVenta}, IdMetodoPago={self.IdMetodoPago}, Activo={self.Activo})>"