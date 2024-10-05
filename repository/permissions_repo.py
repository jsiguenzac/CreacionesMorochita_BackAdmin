from config.DB.database import SessionLocal
from models import model_permissions as ModelPermiso
from models import model_modules as ModelModulo
from utils.methods import exit_json

db = SessionLocal()

async def get_list_permissions():
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