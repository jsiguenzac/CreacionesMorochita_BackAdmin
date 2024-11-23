from fastapi import Depends
from config.DB.database import get_db
from sqlalchemy.orm import Session
from schemas.User_Schema import UserSchema
from utils.methods import exit_json
#from datetime import datetime
from utils.methods import get_peru_date, get_peru_datetime
from sqlalchemy import func, or_, and_, Date
from models import (
    model_products as ModelProduct,
    model_sale as ModelSales,
    model_detail_sale as ModelDetailSale,
    model_user as ModelUser,
    model_category_product as ModelCategory,
)
from schemas.Product_Schema import *

# db: Session = Depends(get_db)

async def get_list_products(body: ParamVistaProduct, db: Session):
    try:
        idcateg = body.id_category
        name = body.name.strip()
        page_size = 10
        offset = (body.page - 1) * page_size
        
        total_products = db.query(ModelProduct.Productos).filter(
            and_(
                ModelProduct.Productos.Activo,
                or_(
                    len(name) == 0,
                    ModelProduct.Productos.Nombre.ilike(f"%{name}%")
                ),
                or_(
                    idcateg == 0,
                    ModelProduct.Productos.IdCategoria == idcateg
                )
            )
        ).count()

        products = db.query(ModelProduct.Productos).filter(
            and_(
                ModelProduct.Productos.Activo,
                or_(
                    len(name) == 0,
                    ModelProduct.Productos.Nombre.ilike(f"%{name}%")
                ),
                or_(
                    idcateg == 0,
                    ModelProduct.Productos.IdCategoria == idcateg
                )
            )
        ).order_by(
            ModelProduct.Productos.IdProducto.desc()
        ).offset(offset).limit(page_size).all()
        
        current_month = get_peru_date().month
        current_year = get_peru_date().year
        lstProducts = []
        
        for prod in products:
            # Calcular ventas del mes actual para el producto desde la tabla de detalle de venta
            monthly_sales = db.query(func.sum(ModelDetailSale.DetalleVenta.Cantidad)).join(
                ModelSales.Venta,
                ModelDetailSale.DetalleVenta.IdVenta == ModelSales.Venta.IdVenta
            ).filter(
                ModelDetailSale.DetalleVenta.IdProducto == prod.IdProducto,
                ModelSales.Venta.IdEstadoVenta != 3,  # No contar ventas anuladas
                func.extract('month', ModelSales.Venta.FechaHoraVenta.cast(Date)) == current_month,
                func.extract('year', ModelSales.Venta.FechaHoraVenta.cast(Date)) == current_year
            ).scalar() or 0  # Si no hay ventas, asigna 0
            
            sales_percentage = (monthly_sales / prod.Stock) * 100 if prod.Stock > 0 else 0
            lstProducts.append(
                ListProductSchema(
                    id_product = prod.IdProducto,
                    name = prod.Nombre,
                    codesku = prod.CodigoSKU,
                    stock = prod.Stock,
                    price = prod.Precio,
                    id_category = prod.IdCategoria,
                    name_category = prod.Categoria.Nombre,
                    id_provider = prod.IdUsuarioProveedor,
                    name_provider = prod.UsuarioProveedor.Nombre,
                    sales_percentage=round(sales_percentage, 2) if sales_percentage > 0 else 0
                )
            )
        return exit_json(1, 
            {
                "total": total_products,
                "page_size": page_size,
                "products": lstProducts
            }
        )
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def add_product(body: ParamAddUpdateProduct, user_creation: UserSchema, db: Session):
    try:
        find_product = db.query(ModelProduct.Productos).filter(
                ModelProduct.Productos.Nombre == body.name
        ).first()
        
        if find_product:
            return exit_json(0, {"exito": False, "mensaje": "PRODUCTO_EXISTENTE"})
        
        new_product = ModelProduct.Productos(
            Nombre = body.name,
            CodigoSKU = body.codesku,
            Stock = body.stock if body.stock > 0 else 0,
            Precio = body.price if body.price > 0 else 0,
            IdCategoria = body.id_category,
            IdUsuario= user_creation["id_user"],
            IdUsuarioProveedor = body.id_provider,
            Activo = True,
            FechaHoraCreacion = get_peru_datetime(),
            UsuarioCreacion= user_creation["email"],
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return exit_json(1, {"exito": True, "mensaje": "PRODUCTO_REGISTRADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def update_product(body: ParamAddUpdateProduct, user_creation: UserSchema, db: Session):
    try:
        find_product = db.query(ModelProduct.Productos).filter(
            ModelProduct.Productos.IdProducto == body.id_product
        ).first()
        
        if not find_product:
            return exit_json(0, {"exito": False, "mensaje": "PRODUCTO_NO_ENCONTRADO"})
        
        find_product.Nombre = body.name
        find_product.CodigoSKU = body.codesku
        find_product.Stock = body.stock if body.stock > 0 else 0
        find_product.Precio = body.price if body.price > 0 else 0
        find_product.IdCategoria = body.id_category
        find_product.IdUsuarioProveedor = body.id_provider
        find_product.FechaHoraModificacion = get_peru_datetime()
        find_product.UsuarioModificacion = user_creation["email"]        
        db.commit()
        db.refresh(find_product)
        
        return exit_json(1, {"exito": True, "mensaje": "PRODUCTO_ACTUALIZADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def find_product_by_name(name: str, db: Session):
    try:
        find_products = db.query(ModelProduct.Productos).filter(
            and_(
                ModelProduct.Productos.Activo,
                ModelProduct.Productos.Nombre.ilike(f"%{name}%")
            )
        ).all()
        result = [
            {
                "id_product": find_product.IdProducto,
                "name": find_product.Nombre,
                "price": find_product.Precio,
                "stock": find_product.Stock
            } for find_product in find_products
        ] if len(find_products) > 0 else []
        return exit_json(1, {"products": result})      
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
