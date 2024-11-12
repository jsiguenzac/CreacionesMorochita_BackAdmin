from fastapi import APIRouter, Depends
from repository.method_payments_repo import *
from routes.auth_api import current_user

router = APIRouter(
    prefix="/Payments",
    tags=["Métodos de Pago"],
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)

@router.get("/List")
async def get_permissions(db: Session = Depends(get_db)):
    try:
        return await get_list_payments(db)
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
