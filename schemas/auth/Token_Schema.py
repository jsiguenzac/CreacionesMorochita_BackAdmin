from typing import Optional
from pydantic import BaseModel

class Token_Data(BaseModel):
    id_user: int
    name: str
    last_name: str
    dni: Optional[int]=None
    email: str
    phone: Optional[int]=None
    id_rol: int
    name_rol: str

class TokenResponse(BaseModel):
    token: str
    user: Token_Data