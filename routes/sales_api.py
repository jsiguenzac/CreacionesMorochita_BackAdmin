from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from repository.rol_repo import *
from routes.auth_api import current_user

from schemas.User_Schema import UserSchema
from schemas.Roles import RoleCreate, RoleUpdate

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

