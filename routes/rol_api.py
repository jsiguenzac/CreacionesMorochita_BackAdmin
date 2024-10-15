from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from repository.rol_repo import *
from routes.auth_api import current_user
from schemas.User_Schema import UserSchema
from schemas.Roles import RoleCreate, RoleUpdate

router = APIRouter(
    prefix="/Rol", 
    tags=["Roles"], 
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)


@router.get("/List", status_code=status.HTTP_200_OK)
async def get_roles_active(db: Session = Depends(get_db)):
    try:
        return await get_list_roles(db)
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})


@router.get("/List/{idRol}")
async def get_roles_active_by_id(idRol: int, all_permissions: bool = Query(False), only_permissions: bool = Query(False), db: Session = Depends(get_db)):
    try:
        return await get_list_roles_by_id(idRol, all_permissions, only_permissions, db)

    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})

""" 
@router.post("/Create", status_code=status.HTTP_200_OK)
async def post_create_new_rol(
    createRol: RoleCreate,
    current_user: UserSchema = Depends(current_user),
    db: Session = Depends(get_db),
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado"
            )
        return await create_new_roles(createRol, current_user, db)
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})


@router.put("/Update", status_code=status.HTTP_200_OK)
async def put_update_active_role(
    updateRol: RoleUpdate,
    current_user: UserSchema = Depends(current_user),
    db: Session = Depends(get_db),
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado"
            )
        return await put_update_role(updateRol, current_user, db)
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})
 """