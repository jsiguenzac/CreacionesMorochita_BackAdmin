from fastapi import Depends
from config.DB.database import get_db
from sqlalchemy.orm import Session
from utils.methods import exit_json
from datetime import datetime
from sqlalchemy import or_, and_
from models import (
    model_products as ModelProduct,
    model_user as ModelUser,
    model_category_product as ModelCategory,
)
from schemas.Product_Schema import *

# db: Session = Depends(get_db)

async def get_list_products(body: ParamVistaProduct, db: Session):
    try:
        idcateg = body.id_category
        name = body.name.strip()
        page_size = 20
        offset = (body.page - 1) * page_size
        
        total_products = db.query(ModelProduct.Productos).filter(
            and_(
                ModelProduct.Productos.Activo,
                or_(
                    len(name) == 0,
                    ModelProduct.Productos.Nombre.ilike(f"%{name}")
                ),
                or_(
                    idcateg == 0,
                    ModelProduct.Productos.IdCategoria == idcateg
                )
            ),
        ).count()
            
        products = db.query(ModelProduct.Productos).filter(
            and_(
                ModelProduct.Productos.Activo,
                or_(
                    len(name) == 0,
                    ModelProduct.Productos.Nombre.ilike(f"%{name}")
                ),
                or_(
                    idcateg == 0,
                    ModelProduct.Productos.IdCategoria == idcateg
                )
            ),
        ).order_by(
            ModelProduct.Productos.IdProducto.desc()
        ).offset(offset).limit(page_size).all()
        
        lstProducts= [
            ListProductSchema(
                id_product = prod.IdProducto,
                name = prod.Nombre,
                codesku = prod.CodigoSKU,
                stock = prod.Stock,
                price = prod.Precio,
                id_category = prod.IdCategoria,
                name_category = prod.Categoria.Nombre,
                id_provider = prod.IdUsuarioProveedor,
                name_provider = prod.UsuarioProveedor.Nombre
            )
            for prod in products
        ]
        return exit_json(
            1, {"total": total_products, "page_size": page_size, "products": lstProducts}
        )
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})