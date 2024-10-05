from datetime import datetime
from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

class Venta(Base):
    __tablename__ = 'tb_venta'

    IdVenta = Column(Integer, primary_key=True, index=True)
    
    IdUsuarioVenta = Column(Integer, ForeignKey('tb_usuarios.IdUsuario'), nullable=False)
    IdUsuarioCliente = Column(Integer, ForeignKey('tb_usuarios.IdUsuario'), nullable=True)
    IdEstadoVenta = Column(Integer, ForeignKey('tb_estado_venta.IdEstadoVenta'), nullable=False)
    IdMetodoPago = Column(Integer, ForeignKey('tb_metodo_pago.IdMetodoPago'), nullable=False)
    
    FechaHoraVenta = Column(DateTime, nullable=False, default=datetime.now())
    Activo = Column(Boolean, default=True)
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    UsuarioVenta = relationship("Usuario", backref=backref("tb_venta", lazy=True))
    UsuarioCliente = relationship("Usuario", backref=backref("tb_venta", lazy=True))
    EstadoVenta = relationship("EstadoVenta", backref=backref("tb_venta", lazy=True))
    MetodoPago = relationship("MetodoPago", backref=backref("tb_venta", lazy=True))
    
    def __repr__(self):
        return f"<Venta(IdVenta={self.IdVenta}, IdEstadoVenta={self.IdEstadoVenta}, IdMetodoPago={self.IdMetodoPago}, Activo={self.Activo})>"