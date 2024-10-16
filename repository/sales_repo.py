from models import model_user as ModelUser
from models import model_sale as ModelSales
from models import model_detail_sale as ModelDetailSales
from models import model_roles_permissions as ModelRolPermiso
from sqlalchemy.orm import Session
from utils.methods import EmailServiceEnv, exit_json, generate_random_password, long_to_date
from datetime import datetime
from sqlalchemy import Date, and_, or_
from collections import defaultdict

""" 
def get_total_sales_by_user(id_user: int, db: Session):
    try:
        today = datetime.now()
        init_date_month = datetime(today.year, today.month, 1)
        # Si estamos en diciembre, el siguiente mes es enero del próximo año
        if today.month == 12:
            finish_date_month = datetime(today.year + 1, 1, 1)
        else:
            # Si no es diciembre, simplemente avanzamos un mes
            finish_date_month = datetime(today.year, today.month + 1, 1)
        
        total_sales = db.query(ModelSales.Venta).filter(
            and_(
                ModelSales.Venta.IdUsuarioCliente == id_user,
                ModelSales.Venta.Activo,
                ModelSales.Venta.FechaHoraVenta >= init_date_month,
                ModelSales.Venta.FechaHoraVenta <= finish_date_month
            )
        ).select_from(
            ModelSales.Venta.
        ).all()
        
        details = db.query(ModelDetailSales.DetalleVenta).filter(
            and_(
                ModelDetailSales.DetalleVenta.IdVenta.in_([sale.IdVenta for sale in total_sales]),
                ModelDetailSales.DetalleVenta.Activo
            )
        ).all()
        
        sum_total_month = sum([detail.Total for detail in details if init_date_month <= detail.FechaCreacion <= finish_date_month])
        
        if total_sales is None:
            return exit_json(0, {"mensaje": "USUARIO_NO_ENCONTRADO"})
        return exit_json(1, {"total_sales": total_sales})
    except Exception as e:
        return exit_json(0, str(e))
 """