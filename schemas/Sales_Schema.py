from pydantic import BaseModel
from typing import Optional

class ParamListSalesSchema(BaseModel):
    page: int = 1
    id_seller: int = 0
    id_status: int = 0
    date_sale: int = -1
    
class ListSalesSchema(BaseModel):
    id_sale: int
    id_seller: int
    name_seller: str
    name_client: str
    dni_client: Optional[int] = None
    date_sale: str
    id_payment: int
    name_payment: str
    id_status: int
    name_status: str
    total: Optional[float] = None