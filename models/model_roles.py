from config.DB.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text

class Roles(Base):
    __tablename__ = "tb_roles"

    IdRol = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(30), unique=True, nullable=False)  # Cambiado a nullable=False
    Descripcion = Column(Text, nullable=False)
    Activo = Column(Boolean, default=True)  # Cambiado a Boolean y quitada la coma extra
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(50), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(50), nullable=True)

    def __repr__(self):
        return (
            f"<Roles(idRol={self.IdRol}, Nombre={self.Nombre}, Activo={self.Activo})>"
        )
