from pydantic import BaseModel
from typing import Optional

class TypeProductSchema(BaseModel):
    id_typeproduct: Optional[int] = None
    name: str


class TypeProductData(BaseModel):
    id_product: Optional[int] = None
    nombre: str
    activo: bool

    
class ListTypeProductSchema(BaseModel):
    id_typeproduct: int
    name: Optional[str] = None
    