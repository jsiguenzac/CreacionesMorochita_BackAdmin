from config.DB.database import Base
from sqlalchemy.orm import relationship, backref
from models.model_permissions import Permisos
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

class Rolpermisos(Base):
    __tablename__ = 'tb_rolpermisos'

    IdRolPermiso = Column(Integer, primary_key=True, index=True)
    IdPermiso = Column(Integer, ForeignKey('tb_permisos.IdPermiso'), nullable=False)
    IdRol = Column(Integer, ForeignKey('tb_roles.IdRol'), nullable=False) 
    Activo = Column(Boolean, default=True)
    FechaHoraCreacion = Column(DateTime, nullable=True)
    UsuarioCreacion = Column(String(100), nullable=True)
    FechaHoraModificacion = Column(DateTime, nullable=True)
    UsuarioModificacion = Column(String(100), nullable=True)
    
    Rol = relationship("Roles", backref=backref("tb_rolpermisos", lazy=True))
    Permiso = relationship("Permisos", backref=backref("tb_rolpermisos", lazy=True))
    
    def __repr__(self):
        return f"<RolPermiso(idRolPermiso={self.IdRolPermiso}, idPermiso={self.IdPermiso}, idRol={self.IdRol}, Activo={self.Activo})>"