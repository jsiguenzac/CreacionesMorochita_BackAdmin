from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth_api import current_user
from repository.categoryproduct_repo import *

router = APIRouter(
    prefix="/Category",
    tags=["Categoria Producto"],
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)]
)

@router.get("/List")
async def get_categories(db: Session = Depends(get_db)):
    try:
        return await get_list_category(db)
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})