from pydantic import BaseModel
from typing import Optional, List

class ProductSchema(BaseModel):
    id_product: Optional[int] = None
    name: str
    submission: str
    stock: int
    codesku: str
    id_category: int
    id_subcategory: int
    id_typeproduct: int
    id_user: int
    

class ProductData(BaseModel):
    id_product: Optional[int] = None
    nombre: str
    codesku: str
    stock: int
    activo: bool
    

class ListProductSchema(BaseModel):
    id_product: int
    name: str
    codesku: str
    stock: Optional[int] = None
    price: float
    id_category: int
    name_category: str
    id_provider: int
    name_provider: str
    
class ParamVistaProduct(BaseModel):
    name: str = ""
    id_category: Optional[int] = 0
    page: int = 1
    
    

