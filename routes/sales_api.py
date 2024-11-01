from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth_api import current_user
from repository.sales_repo import *

router = APIRouter(
    prefix="/Sales", 
    tags=["Ventas"], 
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)

@router.post("/List", status_code=status.HTTP_200_OK)
async def get_sales(body: ParamListSalesSchema, db: Session = Depends(get_db)):
    try:
        if body.page <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Página no válida")
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_list_sales(body, db)
    except Exception as e:
        return exit_json(0, str(e))