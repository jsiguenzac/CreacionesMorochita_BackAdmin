from fastapi import APIRouter, Depends, HTTPException, status
from repository.user_repo import *
from schemas.User_Schema import ParamListUserSchema, UserPasswordUpdate, UserSchema, UserUpdate
from routes.auth_api import current_user

router = APIRouter(
    prefix="/User", 
    tags=["Usuario"], 
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)

@router.post("/List", status_code=status.HTTP_200_OK)
async def get_users(body: ParamListUserSchema, db: Session = Depends(get_db)):
    try:
        if body.page <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Página no válida")
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_list_users(body, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.post("/Create", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserSchema, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await add_user(user, current_user, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.put("/Update", status_code=status.HTTP_200_OK)
async def update_user(updated_user: UserUpdate, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await update_user_by_id_(updated_user, current_user, db)
    except Exception as e:
        return exit_json(0, str(e))
    
@router.put("/Update/Password", status_code=status.HTTP_200_OK)
async def update_user_password(pass_update: UserPasswordUpdate, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await update_password_user_with_hash(pass_update, current_user, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.get("/Detail/{id_user}", status_code=status.HTTP_200_OK)
async def detail_user(id_user: int, db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return find_user_by_id(id_user, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.put("/Update/Status", status_code=status.HTTP_200_OK)
async def update_status_user(id_user: int, is_active: bool, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await update_status_user_by_id(id_user, is_active, current_user, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.get("/Permissions", status_code=status.HTTP_200_OK)
async def get_permissions_by_user(current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_list_permissions_by_user(current_user, db)
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})

@router.get("/Dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard(current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await details_dashboard_by_user(current_user, db)
    except Exception as ex:
        return exit_json(0, {"success": False, "mensaje": str(ex)})