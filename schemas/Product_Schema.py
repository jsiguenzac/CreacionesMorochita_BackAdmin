from pydantic import BaseModel
from typing import Optional

class ListProductSchema(BaseModel):
    id_product: int
    name: str
    codesku: str
    stock: Optional[int] = 0
    price: float
    id_category: int
    name_category: str
    id_provider: int
    name_provider: str
    sales_percentage: Optional[float] = None
    
class ParamVistaProduct(BaseModel):
    name: str = ""
    id_category: Optional[int] = 0
    page: int = 1
    
class ParamAddUpdateProduct(BaseModel):
    id_product: Optional[int] = None
    name: str
    codesku: str
    stock: int
    price: float
    id_category: int
    id_provider: int
