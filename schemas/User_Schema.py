from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    #id_user: Optional[int] = None
    name: str
    last_name: str
    dni: Optional[int] = None
    id_rol: int
    email: str
    #password: str
    phone: Optional[int] = None
    
class UserUpdate(BaseModel):
    id_user: int
    name: str
    last_name: str
    dni: Optional[int] = None
    id_rol: Optional[int] = None
    phone: Optional[int] = None
    isProfile: bool = False
    #email: str
    #password: Optional[str] = None
    
class UserData(BaseModel):
    id_user: Optional[int] = None
    nombre: str
    id_rol: int
    correo: str
    activo: bool
    
class ListUserSchema(BaseModel):
    id_user: int
    name: str
    last_name: str
    dni: Optional[int] = None
    email: str
    phone: Optional[int] = None
    active: bool
    name_rol: str
    id_rol: int
    date_creation: Optional[str] = None
    total: Optional[int] = None

class ParamListUserSchema(BaseModel):
    page: int = 1
    name: str = ""
    id_rol: int = 0
    date_creation: int = -1

class UserPasswordUpdate(BaseModel):
    current_pass: str
    new_pass: str