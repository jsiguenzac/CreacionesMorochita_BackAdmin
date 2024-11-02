from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth_api import current_user
from repository.status_sale_repo import *

router = APIRouter(
    prefix="/StatusSale", 
    tags=["Estado de Venta"], 
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)

@router.get("/List", status_code=status.HTTP_200_OK)
async def get_status_sales(db: Session = Depends(get_db)):
    try:
        return await get_list_status_sales(db)
    except Exception as e:
        return exit_json(0, str(e))
