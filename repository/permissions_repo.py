from fastapi import Depends
from config.DB.database import get_db
from sqlalchemy.orm import Session
from models import model_permissions as ModelPermiso
from models import model_modules as ModelModulo
from utils.methods import exit_json

# db: Session = Depends(get_db)

async def get_list_permissions(db: Session):
    try:
        permissions = db.query(
            ModelPermiso.Permisos
        ).filter(
            ModelPermiso.Permisos.Activo
        ).all()
        
        lstPermissions = [
            {
                'id': permiso.IdPermiso,
                'name_module': permiso.Modulo.Nombre
            }
            for permiso in permissions
        ]
        
        return exit_json(1, {
            "permissions": lstPermissions
        })
    except Exception as e:
        return exit_json(0, {
            "mensaje": str(e)
        })