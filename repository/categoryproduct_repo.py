from fastapi import Depends
from config.DB.database import get_db
from sqlalchemy.orm import Session
from schemas.CategoryProduct_Schema import CategorySchema
from models import model_category_product as ModelCateg
from utils.methods import exit_json

# db: Session = Depends(get_db)

async def get_list_category(db: Session):
    try:
        category = db.query(ModelCateg.CategoriaProducto).filter(
            ModelCateg.CategoriaProducto.Activo
        ).all()
        print("category: ", category)
        lstCategory = [
            CategorySchema(
                idCategory = categoria.IdCategoria,
                name = categoria.Nombre
            )
            for categoria in category
        ]
        return exit_json(1, {
            "category": lstCategory
        })
    except Exception as ex:
        return exit_json(0, {"mensaje": str(ex)})
