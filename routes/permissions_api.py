from fastapi import APIRouter, Depends
from repository.permissions_repo import *
from routes.auth_api import current_user

router = APIRouter(
    prefix="/Permissions",
    tags=["Permisos"],
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)

@router.get("/List")
async def get_permissions():
    try:
        return await get_list_permissions()
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
