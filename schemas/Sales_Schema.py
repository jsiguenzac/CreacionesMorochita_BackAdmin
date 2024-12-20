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
    name_product: Optional[str] = None
    talla: Optional[str] = None
    price: float
    quantity: int
    subtotal: float

class ParamAddUpdateSale(BaseModel):
    id_sale: Optional[int] = None
    name_client: str
    dni_client: Optional[int] = None
    id_payment: int
    id_status: int
    total: float
    products: List[ProductSaleSchema]

class DetailSalesSchema(BaseModel):
    """ id_sale: int
    id_seller: int
    name_seller: str
    name_client: str
    dni_client: Optional[int] = None
    date_sale: str
    id_payment: int
    name_payment: str
    id_status: int
    name_status: str
    total: float """
    products: List[ProductSaleSchema]

class ParamReportSalesSchema(BaseModel):
    page: int = 1
    date_start: int = -1
    date_end: int = -1
    id_seller: int = 0
    
class ExportReportSalesSchema(BaseModel):
    name_seller: str
    name_client: str
    dni_client: Optional[int] = None
    date_sale: str
    hour_sale: str
    name_payment: str
    name_status: str
    total: float
    products: List[ProductSaleSchema]