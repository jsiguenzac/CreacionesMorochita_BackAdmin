from datetime import datetime
from typing import List

from sqlalchemy import true
from config.DB.database import SessionLocal
from repository.rol_permisos_repo import create_rol_permisos
from schemas.RolPermisos import RolPermisoCreate
from schemas.User_Schema import UserSchema
from schemas.Roles import RoleCreate, RolePhysicalDelete, RoleSoftDelete, RoleUpdate
from utils.methods import exit_json
from models import model_roles_permissions as ModelRolPermiso
from models import model_roles as Model_R
from models import model_permissions as ModelPermisos


db = SessionLocal()


async def get_list_roles():
    try:
        roles = db.query(Model_R.Roles).filter(Model_R.Roles.Activo).all()

        lstRoles = [
            {
                "id": rol.IdRol,
                "name": rol.Nombre,
                "descripcion": rol.Descripcion,
            }
            for rol in roles
        ]
        print(lstRoles)
        return exit_json(1, {"roles": lstRoles})
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})


async def get_list_roles_by_id(
    RolById: int, all_permissions: bool = False, only_permissions: bool = False
):
    try:
        roles = (
            db.query(Model_R.Roles)
            .filter(Model_R.Roles.Activo and Model_R.Roles.IdRol == RolById)
            .all()
        )

        if all_permissions:
            rol_permisos = (
                db.query(ModelRolPermiso.Rolpermisos)
                .filter(ModelRolPermiso.Rolpermisos.IdRol == RolById)
                .all()
            )

        else:
            rol_permisos = (
                db.query(ModelRolPermiso.Rolpermisos)
                .filter(ModelRolPermiso.Rolpermisos.Activo)
                .filter(ModelRolPermiso.Rolpermisos.IdRol == RolById)
                .all()
            )

        lstRoles = [
            {
                "id": rol.IdRol,
                "name": rol.Nombre,
                "descripcion": rol.Descripcion,
                "permissions": [
                    {
                        "id": rp.IdPermiso,
                        "name": rp.Permisos.Nombre,
                        "activo": rp.Activo,
                    }
                    for rp in rol_permisos
                ],
            }
            for rol in roles
        ]

        if only_permissions:
            lstOnlyPermisions = [
                {
                    "id": rp.IdPermiso,
                    "name": rp.Permisos.Nombre,
                    "activo": rp.Activo,
                }
                for rp in rol_permisos
            ]

            return exit_json(1, {"permissions": lstOnlyPermisions})
        else:
            return exit_json(1, {"roles": lstRoles})
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})


async def create_new_roles(createRol: RoleCreate, user: UserSchema):
    try:

        find_role = (
            db.query(Model_R.Roles)
            .filter(Model_R.Roles.Nombre == createRol.name)
            .first()
        )
        print("RoleEncontrado", find_role)

        if find_role is not None:
            if find_role.Activo:
                return exit_json(0, {"exito": False, "mensaje": "ROL_YA_EXISTE"})
            else:
                find_role.Nombre = createRol.name
                find_role.Descripcion=createRol.descripcion
                find_role.Activo=True
                find_role.FechaHoraModificacion=datetime.now()
                find_role.UsuarioModificacion=user["email"]
                
                db.commit()
                db.refresh(find_role)

                createRol.id = find_role.idRol

                ls_permissions: List[int] = createRol.ls_permisos

                rol_permisos_list = (
                    db.query(ModelRolPermiso.Rolpermisos)
                    .filter(ModelRolPermiso.Rolpermisos.idRol == find_role.idRol)
                    .all()
                )
                for permisos in rol_permisos_list:
                    permisos.Activo = True
                    permisos.FechaHoraModificacion = datetime.now()
                    permisos.UsuarioModificacion = user["email"]
                    db.commit()
                    db.refresh(permisos)

                lstPermisos = [
                    {
                        "permissions": [
                            {
                                "id": rp.IdPermiso,
                                "name": rp.Permisos.Nombre,
                                "activo": rp.Activo,
                            }
                            for rp in rol_permisos_list
                        ],
                    }
                ]

                createRol.id = find_role.IdRol
                createRol.ls_permisos = lstPermisos
                print(createRol)
                return exit_json(1, {"roles": createRol})
        else:
            db_roles = Model_R.Roles(
                Nombre=createRol.name,
                Descripcion=createRol.descripcion,
                Activo=True,
                FechaHoraCreacion=datetime.now(),
                UsuarioCreacion=user["email"],
            )
            db.add(db_roles)
            db.commit()
            db.refresh(db_roles)

            createRol.id = db_roles.idRol

            ls_permissions: List[int] = createRol.ls_permisos

            for permission in ls_permissions:
                db_permissionRol = ModelRolPermiso.Rolpermisos(
                    idPermiso=permission,
                    idRol=db_roles.idRol,
                    Activo=True,
                    FechaHoraCreacion=datetime.now(),
                    UsuarioCreacion=user["email"],
                )
                db.add(db_permissionRol)
                db.commit()
                db.refresh(db_permissionRol)

                
            ls_permissions: List[int] = createRol.ls_permisos

            rol_permisos_list = (
                    db.query(ModelRolPermiso.Rolpermisos)
                    .filter(ModelRolPermiso.Rolpermisos.IdRol == db_roles.idRol)
                    .all()
                )

            lstPermisos = [
                    {
                        "permissions": [
                            {
                                "id": rp.IdPermiso,
                                "name": rp.Permisos.Nombre,
                                "activo": rp.Activo,
                            }
                            for rp in rol_permisos_list
                        ],
                    }
                ]
                
            createRol.ls_permisos = lstPermisos
            print(createRol)
            return exit_json(1, {"roles": createRol})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def put_update_role(updateRol: RoleUpdate, user: UserSchema):
    try:
        if updateRol.id is None or updateRol.id < 1:
            return exit_json(0, {"exito": False, "mensaje": "ID_ROL_INVALIDO"})

        db_role_list = (
            db.query(Model_R.Roles).filter(Model_R.Roles.idRol == updateRol.id).all()
        )
        if db_role_list[0] is None:
            return exit_json(0, {"exito": False, "mensaje": "ROL_NO_ENCONTRADO"})
        else:
            db_role_list[0].Nombre = updateRol.name
            db_role_list[0].Descripcion = updateRol.descripcion
            db_role_list[0].FechaHoraModificacion = datetime.now()
            db_role_list[0].UsuarioModificacion = user["email"]
            db.commit()
            db.refresh(db_role_list[0])

            ls_permission = list(dict.fromkeys(updateRol.ls_permisos))

            rol_permisos_list = (
                db.query(ModelRolPermiso.Rolpermisos)
                .filter(ModelRolPermiso.Rolpermisos.IdRol == updateRol.id)
                .all()
            )

            id_permisos_list = await get_id_permisos_list()

            unregistered_list: List[int] = await get_unregistered_ids_permisos(
                updateRol.id, ls_permission
            )
            val = True
            for per in unregistered_list:
                if per not in id_permisos_list:
                    val = False

            if val:
                ls_permission = [
                    permiso
                    for permiso in ls_permission
                    if permiso not in unregistered_list
                ]

                for per in unregistered_list:
                    rol_permiso_create: RolPermisoCreate = RolPermisoCreate(
                        idRol=updateRol.id,
                        idPermiso=per,
                        activo=True,
                        fecha_creacion=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        usuario_creacion=user["email"],
                    )
                    await create_rol_permisos(rol_permiso_create, user)

                for rolpermiso in rol_permisos_list:
                    if rolpermiso.IdPermiso in ls_permission:
                        rolpermiso.Activo = True
                        rolpermiso.UsuarioModificacion = user["email"]
                        rolpermiso.FechaHoraModificacion = datetime.now()
                        db.commit()
                        db.refresh(rolpermiso)
                    else:
                        rolpermiso.Activo = False
                        rolpermiso.UsuarioModificacion = user["email"]
                        rolpermiso.FechaHoraModificacion = datetime.now()
                        db.commit()
                        db.refresh(rolpermiso)

                rol_permisos_list = (
                    db.query(ModelRolPermiso.Rolpermisos)
                    .filter(ModelRolPermiso.Rolpermisos.IdRol == updateRol.id)
                    .all()
                )

                lstRoles = [
                    {
                        "id": rol.IdRol,
                        "name": rol.Nombre,
                        "descripcion": rol.Descripcion,
                        "activo": rol.Activo,
                        "permissions": [
                            {
                                "id": rp.IdPermiso,
                                "name": rp.Permisos.Nombre,
                                "activo": rp.Activo,
                            }
                            for rp in rol_permisos_list
                        ],
                    }
                    for rol in db_role_list
                ]
                print(lstRoles)
                return exit_json(1, {"roles": lstRoles})
            else:
                raise Exception("ROL_PERMISO_NO_EXISTE")
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def get_id_permisos_list():
    permisos_id_list: List[int] = []
    permisos_list = db.query(ModelPermisos.Permisos).all()
    for permisos in permisos_list:
        permisos_id_list.append(permisos.IdPermiso)
    return permisos_id_list


# Obtiene una lista de enteros con los idPermisos de los rolPermisos Registrados
async def get_id_registered_rol_permisos_list(idRol: int):
    rol_permisos_id_list: List[int] = []
    rol_permisos_list = (
        db.query(ModelRolPermiso.Rolpermisos)
        .filter(ModelRolPermiso.Rolpermisos.IdRol == idRol)
        .all()
    )
    for rolpermisos in rol_permisos_list:
        rol_permisos_id_list.append(rolpermisos.IdPermiso)
    return rol_permisos_id_list


# Aisla los idPermisos que no están registrados en rolesPermisos
async def get_unregistered_ids_permisos(idRol: int, lista_de_ids_a_activar: list[int]):
    registered_ids = await get_id_registered_rol_permisos_list(idRol)
    unregistered_ids = [id for id in lista_de_ids_a_activar if id not in registered_ids]
    return unregistered_ids


async def physical_delete_role(role_id: int):
    try:
        db_role = db.query(Model_R.Roles).filter(Model_R.Roles.IdRol == role_id).first()
        db_role_aux = RolePhysicalDelete(id=db_role.IdRol, name=db_role.Nombre)
        if db_role:
            db.delete(db_role)
            db.commit()
            return exit_json(1, {"roles": db_role_aux})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def soft_delete_role(role_id: int, user: UserSchema):
    try:
        db_role = db.query(Model_R.Roles).filter(Model_R.Roles.IdRol == role_id).first()
        db_role_aux = RoleSoftDelete(idRol=db_role.IdRol, name=db_role.Nombre)

        db_role_permissions = (
            db.query(ModelRolPermiso.Rolpermisos)
            .filter(ModelRolPermiso.Rolpermisos.IdRol == role_id)
            .all()
        )

        if db_role:
            db_role.Activo = False
            db_role.FechaHoraModificacion = datetime.now()
            db_role.UsuarioModificacion = user["email"]
            db.commit()
            db.refresh(db_role)
            print(db_role)

            for permission in db_role_permissions:
                permission.Activo = False
                db.commit()
                db.refresh(permission)
            return exit_json(1, {"roles": db_role_aux})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def reverse_soft_delete_role(role_id: int, user: UserSchema):
    try:
        db_role = db.query(Model_R.Roles).filter(Model_R.Roles.IdRol == role_id).first()
        db_role_aux = RoleSoftDelete(idRol=db_role.IdRol, name=db_role.Nombre)

        db_role_permissions = (
            db.query(ModelRolPermiso.Rolpermisos)
            .filter(ModelRolPermiso.Rolpermisos.IdRol == role_id)
            .all()
        )

        if db_role:
            db_role.Activo = True
            db_role.FechaHoraModificacion = datetime.now()
            db_role.UsuarioModificacion = user["email"]
            db.commit()
            db.refresh(db_role)
            print(db_role)

            for permission in db_role_permissions:
                permission.Activo = True
                db.commit()
                db.refresh(permission)
            return exit_json(1, {"roles": db_role_aux})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
