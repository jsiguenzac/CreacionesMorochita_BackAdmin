from config.DB.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class Modulos(Base):
    __tablename__ = 'tb_modulos'

    IdModulo = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(30), unique=True, nullable=False)
    Activo = Column(Boolean, default=True)
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Modulos(idModulo={self.IdModulo}, Nombre={self.Nombre}, Activo={self.Activo})>"