from models import model_user as ModelUser
from models import model_method_payment as ModelPayment
from models import model_status_sale as ModelStatusSale
from models import model_sale as ModelSales
from models import model_detail_sale as ModelDetailSales
from models import model_roles_permissions as ModelRolPermiso
from config.DB.database import get_db
from sqlalchemy.orm import Session
from utils.methods import EmailServiceEnv, exit_json, long_to_date
from datetime import datetime
from sqlalchemy import Date, and_, or_
from schemas.Sales_Schema import *


async def get_list_sales(body: ParamListSalesSchema, db: Session):
    try:
        page_size = 20
        id_seller = body.id_seller
        id_status = body.id_status
        date_sale = long_to_date(body.date_sale)
        offset = (body.page - 1) * page_size
        
        sales_total = db.query(ModelSales.Venta).filter(
            and_(
                ModelSales.Venta.Activo,
                or_(
                    id_seller == 0,
                    ModelSales.Venta.IdUsuarioVenta == id_seller
                ),
                or_(
                    id_status == 0,
                    ModelSales.Venta.IdEstadoVenta == id_status
                ),
                or_(
                    date_sale == -1,
                    ModelSales.Venta.FechaHoraVenta.cast(Date) == date_sale
                )
            )
        ).count()
        
        sales_list = db.query(ModelSales.Venta).filter(
            and_(
                ModelSales.Venta.Activo,
                or_(
                    id_seller == 0,
                    ModelSales.Venta.IdUsuarioVenta == id_seller
                ),
                or_(
                    id_status == 0,
                    ModelSales.Venta.IdEstadoVenta == id_status
                ),
                or_(
                    date_sale == -1,
                    ModelSales.Venta.FechaHoraVenta.cast(Date) == date_sale
                )
            )
        ).order_by(
            ModelSales.Venta.IdVenta.desc()
        ).offset(offset).limit(page_size).all()
        
        sales_map = [
            ListSalesSchema(
                id_sale=sale.IdVenta,
                id_seller=sale.IdUsuarioVenta,
                name_seller=sale.Usuario.Nombre,
                name_client=sale.NombreCliente,
                dni_client=sale.DNICliente,
                date_sale=sale.FechaHoraVenta,
                id_payment=sale.IdMetodoPago,
                name_payment=sale.MetodoPago.Nombre,
                id_status=sale.IdEstadoVenta,
                name_status=sale.EstadoVenta.Nombre,
                total=sale.Total
            ) for sale in sales_list
        ]
        return exit_json(1, {
                "total": sales_total,
                "page_size": page_size,
                "sales": sales_map
            }
        )
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})

