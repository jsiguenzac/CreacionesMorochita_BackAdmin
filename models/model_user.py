from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

class Usuario(Base):
    __tablename__ = 'tb_usuarios'

    IdUsuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # llave foranea
    IdRol = Column(Integer, ForeignKey('tb_roles.IdRol'), nullable=False)
    Nombre = Column(String(50), nullable=False)
    Apellidos = Column(String(80), nullable=False)
    DNI = Column(Integer(), nullable=True)
    Correo = Column(String(100), nullable=False)
    Clave = Column(String(300), nullable=False)
    Telefono = Column(Integer(), nullable=True)
    Activo = Column(Boolean, default=True)    
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(50), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(50), nullable=True)
    
    Rol = relationship("Roles", backref=backref("tb_usuarios", lazy=True))
    
    def __repr__(self):
        return f"<Usuarios(idUsuario={self.IdUsuario}, Nombre={self.Nombre}, Activo={self.Activo}, Rol={self.IdRol})>"