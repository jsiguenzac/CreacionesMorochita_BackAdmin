from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RolPermisoSchema(BaseModel):
    id: Optional[int]
    idRol: int
    idPermiso: int
    activo: bool
    
class RolPermisoCreate(BaseModel):
    idRol: int
    idPermiso: int
    activo: bool
    fecha_creacion: str
    usuario_creacion:str