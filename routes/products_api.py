from fastapi import APIRouter, Depends, HTTPException, status
from repository.products_repo import *
from routes.auth_api import current_user

router = APIRouter(
    prefix="/Products", 
    tags=["Productos"], 
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)


@router.post("/List", status_code=status.HTTP_200_OK)
async def get_products(request: ParamVistaProduct, db: Session = Depends(get_db)):
    try:
        if request.page <=0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Página no válida")
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_list_products(request, db)
    except Exception as ex:
        return exit_json(0, str(ex))
