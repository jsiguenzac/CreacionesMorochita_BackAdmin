from datetime import datetime
from typing import List
from fastapi import Depends
from config.DB.database import SessionLocal
from schemas.RolPermisos import RolPermisoCreate, RolPermisoSchema
from schemas.User_Schema import UserSchema
from utils.methods import exit_json
from models import model_roles_permissions as Model

db = SessionLocal()


async def get_list_roles_permissions(user: UserSchema):
    try:
        rolPermisos = (
            db.query(Model.Rolpermisos)
            .filter(Model.Rolpermisos.Activo)
            .filter(Model.Rolpermisos.IdRol == user["id_rol"])
            .all()
        )

        lstRolPermisos = [
            {
                "id": rol.IdRolPermiso,
                "activo": rol.Activo,
                "permiso": rol.IdPermiso,
                "rol": rol.IdRol,
            }
            for rol in rolPermisos
        ]
        print(lstRolPermisos)
        return exit_json(1, {"rol_permisos": lstRolPermisos})
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})


async def get_list_rol_permisos_by_id(idRolPermiso: int, user: UserSchema):
    try:
        rolPermisos = (
            db.query(Model.Rolpermisos)
            .filter(Model.Rolpermisos.Activo)
            .filter(Model.Rolpermisos.IdRol == user["id_rol"])
            .filter(Model.Rolpermisos.IdRolPermiso == idRolPermiso)
            .all()
        )
        lstRolPermisos = [
            {
                "id": rol.IdRolPermiso,
                "activo": rol.Activo,
                "permiso": rol.IdPermiso,
                "rol": rol.IdRol,
            }
            for rol in rolPermisos
        ]
        print(lstRolPermisos)
        return exit_json(1, {"roles": lstRolPermisos})
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})


async def create_rol_permisos(rolPermiso: RolPermisoCreate, user: UserSchema):
    try:
        db_rol_permiso = Model.Rolpermisos(
            IdPermiso=rolPermiso.idPermiso,
            IdRol=rolPermiso.idRol,
            Activo=rolPermiso.activo,
            FechaHoraCreacion=datetime.now(),
            UsuarioCreacion=user["email"],
        )
        db.add(db_rol_permiso)
        db.commit()
        db.refresh(db_rol_permiso)

        print(rolPermiso)
        return exit_json(1, {"roles": rolPermiso})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {
            "exito": False,
            "mensaje": str(ex)
        })