from pydantic import BaseModel
from typing import List, Optional

class ParamListSalesSchema(BaseModel):
    page: int = 1
    id_seller: int = 0 # vendendor
    id_status: int = 0 # estado de la venta
    date_sale: int = -1 # fecha de la venta
    
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
    
class ProductSaleSchema(BaseModel):
    id_product: int
    price: float
    quantity: int
    subtotal: float

class ParamAddUpdateSale(BaseModel):
    id_sale: Optional[int] = None
    id_seller: int
    name_client: str
    dni_client: int
    id_payment: int
    id_status: int
    total: float
    products: List[ProductSaleSchema]
