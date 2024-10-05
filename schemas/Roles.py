from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class RoleSchema(BaseModel):
    id: Optional[int]
    name: str
    activo: bool
    fecha_creacion: str
    
class RoleCreate(BaseModel):
    id: Optional[int] = None
    name: str
    descripcion: str
    ls_permisos: List[int]

class RoleUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
    descripcion: Optional[str]
    ls_permisos: List[int]
    
class RolePhysicalDelete(BaseModel):
    id: Optional[int]
    name: str
    
class RoleSoftDelete(BaseModel):
    idRol: Optional[int]
    name: str
    
class RoleResponse(BaseModel):
    id: Optional[int]
    name: str
    activo: bool
    fecha_creacion: str