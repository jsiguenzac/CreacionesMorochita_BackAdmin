from models import model_user as ModelUser
from models import model_method_payment as ModelPayment
from models import model_status_sale as ModelStatusSale
from models import model_products as ModelProducts
from models import model_sale as ModelSales
from models import model_detail_sale as ModelDetailSales
from models import model_roles_permissions as ModelRolPermiso
from config.DB.database import get_db
from sqlalchemy.orm import Session, joinedload
from schemas.User_Schema import UserSchema
from utils.methods import EmailServiceEnv, exit_json, long_to_date
from datetime import datetime
from sqlalchemy import Date, and_, or_
from schemas.Sales_Schema import *
from collections import defaultdict
from utils.methods import export_sales_report_to_excel


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
                name_seller=sale.UsuarioVenta.Nombre,
                name_client=sale.NombreCliente,
                dni_client=sale.DNICliente,
                # convertir fecha a string
                date_sale=sale.FechaHoraVenta.strftime("%d-%m-%Y"),
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


async def validate_stock(products: list, db: Session):
    try:
        # Agrupar productos por `id` y sumar cantidades ignorando `talla`
        product_quantities = defaultdict(int)
        for product in products:
            product_quantities[product.id] += product.quantity
        # Obtener el stock actual de los productos en la base de datos
        product_ids = list(product_quantities.keys())
        products_in_db = db.query(ModelProducts.Productos).filter(
            and_(
                ModelProducts.Productos.Activo,
                ModelProducts.Productos.IdProducto.in_(product_ids)
            )
        ).all()
        # Crear un mapa de stock para cada `IdProducto`
        stock_map = {p.IdProducto: (p.Stock, p.Nombre) for p in products_in_db}
        # Validación de stock
        for product_id, total_quantity in product_quantities.items():
            # Verificar que el producto exista en el stock
            if product_id not in stock_map:
                return False, f"PRODUCTO_NO_ENCONTRADO", product_id

            # Validar que el stock sea suficiente
            if stock_map[product_id][0] < total_quantity:
                return False, f"STOCK_INSUFICIENTE", stock_map[product_id][1]
        return True, "STOCK_VALIDADO", None
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def add_sale(body: ParamAddUpdateSale, user_creation: UserSchema, db: Session):
    try:
        # Validación de productos
        if not body.products:
            return exit_json(0, {"exito": False, "mensaje": "NO_HAY_PRODUCTOS"})
        # validar stock de productos
        stock_valid, msg, id_product = await validate_stock(body.products, db)
        if not stock_valid:
            return exit_json(0, {"exito": False, "mensaje": msg, "product": id_product})
        
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
                Talla=product.talla,
                Cantidad=product.quantity,
                PrecioVenta=product.price,
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

        date_sale_updated = datetime.now()
        u_update = user_update["email"]
        
        find_sale = db.query(ModelSales.Venta).filter(
            ModelSales.Venta.IdVenta == body.id_sale
        ).first()
        
        if not find_sale:
            return exit_json(0, {"exito": False, "mensaje": "VENTA_NO_ENCONTRADA"})

        # Actualizar venta
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
            ModelDetailSales.DetalleVenta.IdVenta == body.id_sale
        ).all()
        
        # Crear un diccionario de productos actuales para optimizar la búsqueda
        existing_details_dict = {detail.IdProducto: detail for detail in existing_details}
        
        # Actualizar o agregar nuevos productos
        for product in body.products:
            detail = existing_details_dict.get(product.id_product)
            
            # Validar stock solo si es un producto nuevo o si la cantidad es diferente
            if detail is None or detail.Cantidad != product.quantity:
                stock_valid, msg, id_product = await validate_stock([product], db)
                if not stock_valid:
                    return exit_json(0, {"exito": False, "mensaje": msg, "product": id_product})
            if detail:
                # Actualizar detalles existentes
                detail.Cantidad = product.quantity
                detail.PrecioVenta = product.price
                detail.Talla = product.talla
                detail.SubTotal = product.subtotal
                detail.FechaHoraModificacion = date_sale_updated
                detail.UsuarioModificacion = u_update
            else:
                # Agregar nuevo detalle de venta
                new_detail = ModelDetailSales.DetalleVenta(
                    IdVenta=body.id_sale,
                    IdProducto=product.id_product,
                    Cantidad=product.quantity,
                    PrecioVenta=product.price,
                    Talla=product.talla,
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


async def details_sale(id_sale: int, db: Session):
    try:
        details = db.query(ModelDetailSales.DetalleVenta).filter(
            and_(
                ModelDetailSales.DetalleVenta.Activo,
                ModelDetailSales.DetalleVenta.IdVenta == id_sale
            )
        ).all()
        
        details_map = [
            ProductSaleSchema(
                id_product=detail.IdProducto,
                name_product=detail.Producto.Nombre,
                talla=detail.Talla,
                quantity=detail.Cantidad,
                price=detail.PrecioVenta,
                subtotal=detail.SubTotal
            ) for detail in details
        ]
        return exit_json(1, {"details": details_map})
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def get_report_sales(body: ParamReportSalesSchema, db: Session):
    try:
        date_start = long_to_date(body.date_start)
        date_end = long_to_date(body.date_end)
        id_seller = body.id_seller
        page = body.page
        page_size = 20
        offset = (page - 1) * page_size
        
        # Validaciones
        current_date = datetime.now().date()
        
        if date_start == -1:
            date_start = current_date
        if date_end == -1:
            date_end = current_date

        if date_end < date_start:
            return exit_json(0, {"exito": False, "mensaje": "FECHA_FIN_MENOR"})
                
        sales_list = db.query(ModelSales.Venta).filter(
            and_(
                ModelSales.Venta.Activo,
                or_(
                    id_seller == 0,
                    ModelSales.Venta.IdUsuarioVenta == id_seller
                ),
                or_(
                    date_start == -1,
                    ModelSales.Venta.FechaHoraVenta.cast(Date) >= date_start
                ),
                or_(
                    date_end == -1,
                    ModelSales.Venta.FechaHoraVenta.cast(Date) <= date_end
                )
            )
        ).order_by(
            ModelSales.Venta.IdVenta.desc()
        ).offset(offset).limit(page_size).all()
        
        sales_map = [
            ListSalesSchema(
                id_sale=sale.IdVenta,
                id_seller=sale.IdUsuarioVenta,
                name_seller=(f'{sale.UsuarioVenta.Nombre} {sale.UsuarioVenta.Apellidos}'),
                name_client=sale.NombreCliente,
                dni_client=sale.DNICliente,
                date_sale=sale.FechaHoraVenta.strftime("%d-%m-%Y %H:%M"),
                id_payment=sale.IdMetodoPago,
                name_payment=sale.MetodoPago.Nombre,
                id_status=sale.IdEstadoVenta,
                name_status=sale.EstadoVenta.Nombre,
                total=sale.Total
            ) for sale in sales_list
        ]
        return exit_json(1, {"sales": sales_map})
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def export_report_sales(body: ParamReportSalesSchema, db: Session):
    try:
        date_start = long_to_date(body.date_start)
        date_end = long_to_date(body.date_end)
        id_seller = body.id_seller
        # Validaciones
        current_date = datetime.now().date()
        
        if date_start == -1:
            date_start = current_date
        if date_end == -1:
            date_end = current_date
        
        isDateEndLower = date_end < date_start
        if isDateEndLower:
            return exit_json(0, {"exito": False, "mensaje": "FECHA_FIN_MENOR"})
                
        sales_list = db.query(ModelSales.Venta).options(
            joinedload(ModelSales.Venta.DetalleVenta).joinedload(ModelDetailSales.DetalleVenta.Producto)
        ).filter(
            and_(
                ModelSales.Venta.Activo,
                or_(
                    id_seller == 0,
                    ModelSales.Venta.IdUsuarioVenta == id_seller
                ),
                or_(
                    date_start == -1,
                    ModelSales.Venta.FechaHoraVenta.cast(Date) >= date_start
                ),
                or_(
                    date_end == -1,
                    ModelSales.Venta.FechaHoraVenta.cast(Date) <= date_end
                )
            )
        ).order_by(
            ModelSales.Venta.IdVenta.desc()
        ).all()
        
        if len(sales_list) <= 0:
            return exit_json(0, {"exito": False, "mensaje": "NO_HAY_VENTAS"})
        
        sales_map = [
            ExportReportSalesSchema(
                name_seller=(f'{sale.UsuarioVenta.Nombre} {sale.UsuarioVenta.Apellidos}'),
                name_client=sale.NombreCliente,
                dni_client=sale.DNICliente,
                date_sale=sale.FechaHoraVenta.strftime("%d-%m-%Y"),
                hour_sale=sale.FechaHoraVenta.strftime("%H:%M"),
                name_payment=sale.MetodoPago.Nombre,
                name_status=sale.EstadoVenta.Nombre,
                total=sale.Total,
                products=[
                    ProductSaleSchema(
                        id_product=detail.IdProducto,
                        name_product=detail.Producto.Nombre,
                        talla=detail.Talla,
                        price=detail.PrecioVenta,
                        quantity=detail.Cantidad,
                        subtotal=detail.SubTotal
                    ) for detail in sale.DetalleVenta
                ]
            ).dict()
            for sale in sales_list
        ]
        
        print("data_sales_map", sales_map)
        # Exportar reporte a Excel
        data_exported, name_file = export_sales_report_to_excel(sales_map)
        if not data_exported:
            return exit_json(0, {"exito": False, "mensaje": "ERROR_EXPORTAR_EXCEL"})
        
        return exit_json(1, {
            "exito": True,
            "mensaje": "REPORTE_EXPORTADO",
            "data_export": data_exported,
            "name_file": name_file
        })
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
