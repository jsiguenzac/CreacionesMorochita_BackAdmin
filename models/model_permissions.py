from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

class Permisos(Base):
    __tablename__ = 'tb_permisos'

    IdPermiso = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # llave foranea
    IdModulo = Column(ForeignKey('tb_modulos.IdModulo'), nullable=False)
    Nombre = Column(String(30), nullable=False)
    Activo = Column(Boolean, default=True)    
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    Modulo = relationship("Modulos", backref=backref("tb_permisos", lazy=True))
    
    def __repr__(self):
        return f"<Permisos(idPermiso={self.IdPermiso}, Nombre={self.Nombre}, Activo={self.Activo}, Modulo={self.IdModulo})>"