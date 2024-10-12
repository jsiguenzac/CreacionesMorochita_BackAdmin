from fastapi import APIRouter, Depends, HTTPException, status
from config.security.security import *
from schemas.auth.RecoverPass_Schema import RecoverPassSchema
from schemas.auth.Token_Schema import TokenResponse
from schemas.auth.Login_Schema import LoginSchema
from repository.auth_repo import *
from repository.user_repo import *
from datetime import datetime, timedelta
from schemas.User_Schema import UserSchema
from jose import jwt, JWTError

router = APIRouter(
    prefix="/Login", 
    tags=["Autenticación"], 
    responses={404: {"message": "No encontrado"}}
)

@router.post("/Authenticate", response_model=TokenResponse, status_code=status.HTTP_200_OK, name="Login", description="Autenticación de usuario")
async def login(form_data: LoginSchema, db: Session = Depends(get_db)):
        try:
                val = await generate_token(form_data.email, form_data.password, db)
                x = val.dict()
                if x.get("state") == 0:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=x.get("data"))
                else:
                        current_time = int(datetime.now().timestamp())
                        ACCESS_TOKEN_EXPIRE = ACCESS_TOKEN_EXPIRE_WITH_REMIND if form_data.remind else ACCESS_TOKEN_EXPIRE_DEFAULT
                        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE)
                        acces_token = {
                                "sub": str(x.get("data").get("id_user")),
                                "exp": expire,  
                                "iat": current_time,
                                "nbf": current_time,
                                "aud": AUDIENCE,
                                "iss": ISSUER,
                                "scopes": "access_token",
                                "key_global": SECRET_KEY,
                        }
                        return TokenResponse(
                                token=jwt.encode(acces_token, SECRET_KEY, algorithm=ALGORITHM),
                                user=x.get("data")
                        )
        except JWTError as e:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/RecoverPassword", status_code=status.HTTP_200_OK, description="Se envía un correo con una nueva contraseña aleatoria")
async def Recover_Password(body: RecoverPassSchema, db: Session = Depends(get_db)):
        try:
                val = await recover_password(body.email, db)
                return val
        except Exception as e:
                return exit_json(0, {
                        "exito": False,
                        "mensaje": str(e)
                })

# Region METODOS
async def auth_user(token: str = Depends(oauth2)):
    try:
        excep = HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Token inválido",
                headers = {"WWW-Authenticate": "Bearer"})
        
        user = int(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER).get("sub"))
        if user is None:
            raise excep
        return int(user)
    except JWTError as ex:
        print("Error", str(ex))
        raise excep

async def current_user(user: UserSchema = Depends(auth_user), db: Session = Depends(get_db)):
        u = find_user_by_id(user,db)
        x = u.dict()
        if x.get("state") == 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=x.get("data"))                
        return x.get("data")

# EndRegion METODOS