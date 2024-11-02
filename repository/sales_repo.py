from models import model_user as ModelUser
from models import model_method_payment as ModelPayment
from models import model_status_sale as ModelStatusSale
from models import model_sale as ModelSales
from models import model_detail_sale as ModelDetailSales
from models import model_roles_permissions as ModelRolPermiso
from config.DB.database import get_db
from sqlalchemy.orm import Session
from schemas.User_Schema import UserSchema
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


async def add_sale(body: ParamAddUpdateSale, user_creation: UserSchema, db: Session):
    try:
        # Validación de productos
        if not body.products:
            return exit_json(0, {"exito": False, "mensaje": "NO_HAY_PRODUCTOS"})
        
        # Registro de venta
        date_sale_created = datetime.now()
        u_creation = user_creation["email"]
        new_sale = ModelSales.Venta(
            IdUsuarioVenta=user_creation["id_user"],
            NombreCliente=body.name_client,
            DNICliente=body.dni_client,
            IdMetodoPago=body.id_payment,
            IdEstadoVenta=body.id_status,
            Total=body.total,
            Activo=True,
            FechaHoraVenta=date_sale_created,
            UsuarioCreacion=u_creation
        )
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)

        # Registro de detalles de la venta
        for product in body.products:
            detail_sale = ModelDetailSales.DetalleVenta(
                IdVenta=new_sale.IdVenta,
                IdProducto=product.id_product,
                Cantidad=product.quantity,
                Precio=product.price,
                SubTotal=product.subtotal,
                Activo=True,
                FechaHoraCreacion=date_sale_created,
                UsuarioCreacion=u_creation
            )
            db.add(detail_sale)
        
        db.commit()        
        return exit_json(1, {"exito": True, "mensaje": "VENTA_REGISTRADA", "id_sale": new_sale.IdVenta})    
    except Exception as ex:
        db.rollback()
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def update_sale(body: ParamAddUpdateSale, user_update: UserSchema, db: Session):
    try:
        # Validación de productos
        if not body.products:
            return exit_json(0, {"exito": False, "mensaje": "NO_HAY_PRODUCTOS"})
        
        # Obtener venta existente
        date_sale_updated = datetime.now()
        u_update = user_update["email"]
        
        find_sale = db.query(ModelSales.Venta).filter(
            ModelSales.Venta.IdVenta == body.id_sale
        ).first()
        
        if not find_sale:
            return exit_json(0, {"exito": False, "mensaje": "VENTA_NO_ENCONTRADA"})
        
        # Actualizar venta
        find_sale.IdUsuarioVenta = body.id_seller
        find_sale.NombreCliente = body.name_client
        find_sale.DNICliente = body.dni_client
        find_sale.IdMetodoPago = body.id_payment
        find_sale.IdEstadoVenta = body.id_status
        find_sale.Total = body.total
        find_sale.FechaHoraModificacion = date_sale_updated
        find_sale.UsuarioModificacion = u_update
        db.commit()

        # Obtener productos actuales en la base de datos
        existing_details = db.query(ModelDetailSales.DetalleVenta).filter(
            and_(
                ModelDetailSales.DetalleVenta.Activo,
                ModelDetailSales.DetalleVenta.IdVenta == body.id_sale
            )
        ).all()
        
        # Crear un diccionario de productos actuales para optimizar la búsqueda
        existing_details_dict = {detail.IdProducto: detail for detail in existing_details}
        
        # Actualizar o agregar nuevos productos
        for product in body.products:
            detail = existing_details_dict.get(product.id_product)
            
            if detail:
                # Actualizar detalles existentes
                detail.Cantidad = product.quantity
                detail.Precio = product.price
                detail.SubTotal = product.subtotal
                detail.FechaHoraModificacion = date_sale_updated
                detail.UsuarioModificacion = u_update
            else:
                # Agregar nuevo detalle de venta
                new_detail = ModelDetailSales.DetalleVenta(
                    IdVenta=body.id_sale,
                    IdProducto=product.id_product,
                    Cantidad=product.quantity,
                    Precio=product.price,
                    SubTotal=product.subtotal,
                    Activo=True,
                    FechaHoraCreacion=date_sale_updated,
                    UsuarioCreacion=u_update
                )
                db.add(new_detail)
        
        # Inactivar productos que ya no están en la lista
        incoming_product_ids = {product.id_product for product in body.products}
        for detail in existing_details:
            if detail.IdProducto not in incoming_product_ids:
                detail.Activo = False
                detail.FechaHoraModificacion = date_sale_updated
                detail.UsuarioModificacion = u_update

        db.commit()
        return exit_json(1, {"exito": True, "mensaje": "VENTA_ACTUALIZADA"})    
    except Exception as ex:
        db.rollback()
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
