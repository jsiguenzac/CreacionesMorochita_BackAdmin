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
async def get_products(body: ParamVistaProduct, db: Session = Depends(get_db)):
    try:
        if body.page <=0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Página no válida")
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_list_products(body, db)
    except Exception as ex:
        return exit_json(0, str(ex))


@router.post("/Add", status_code=status.HTTP_200_OK)
async def add_new_product(body: ParamAddUpdateProduct, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await add_product(body, current_user, db)
    except Exception as ex:
        return exit_json(0, str(ex))


@router.post("/Update", status_code=status.HTTP_200_OK)
async def update_data_product(body: ParamAddUpdateProduct, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await update_product(body, current_user, db)
    except Exception as ex:
        return exit_json(0, str(ex))
