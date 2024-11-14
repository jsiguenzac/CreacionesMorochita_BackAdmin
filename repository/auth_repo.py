from fastapi import Depends
from config.security.security import crypt
from config.DB.database import get_db
from sqlalchemy.orm import Session
from schemas.User_Schema import ListUserSchema
from utils.methods import exit_json
from models import model_roles as ModelRol
from models import model_user as ModelUser
from utils.methods import generate_random_password, EmailServiceEnv
from sqlalchemy import or_, and_

#db: Session = Depends(get_db())

async def generate_token(emailOrDNI: str, password: str, db: Session):
    try:
        user = db.query(ModelUser.Usuario).filter(
            and_(
                ModelUser.Usuario.Activo,
                or_(
                    ModelUser.Usuario.Correo == str(emailOrDNI),
                    and_(
                        ModelUser.Usuario.DNI == int(emailOrDNI) if emailOrDNI.isdigit() else None,
                        ModelUser.Usuario.DNI.isnot(None)
                    )
                )
            )
        ).first()
        
        if user is None:
            return exit_json(0, {
                "mensaje": "USUARIO_NO_ENCONTRADO"
            })

        if not crypt.verify(password, user.Clave):
            return exit_json(0, {
                "mensaje": "CLAVE_INCORRECTA"
            })
        rol_find = db.query(
            ModelRol.Roles
        ).filter(
            ModelRol.Roles.IdRol == user.IdRol
        ).first()
        
        user_data = ListUserSchema(
            id_user=user.IdUsuario,
            name=user.Nombre,
            last_name=user.Apellidos,
            dni=user.DNI,
            email=user.Correo,
            phone=user.Telefono,
            active=user.Activo,
            id_rol=user.IdRol,
            name_rol=rol_find.Nombre if rol_find.Nombre is not None else "Sin rol asignado"
        )
        return exit_json(1, user_data)
    except Exception as e:
        print("ERR", str(e))
        db.rollback()
        return exit_json(0,
        {
            "mensaje": "Error de conexión con la base de datos"            
        })

async def recover_password(email: str, db: Session):
    try:
        if email is None or len(email.strip()) <= 0:
            return exit_json(0, {
                "exito": False,
                "mensaje": "CORREO_INVALIDO"
            })
        user = db.query(
            ModelUser.Usuario
        ).filter(
            and_(
                ModelUser.Usuario.Activo,
                ModelUser.Usuario.Correo == email
            )
        ).first()
        
        if user is None:
            return exit_json(0, {
                "exito": False,
                "mensaje": "USUARIO_NO_ENCONTRADO"
            })        
        new_password = generate_random_password(10)
        print("Nueva contraseña aleatoria: ", new_password)
        subject = "Plataforma Morochita - Recuperación de contraseña"
        body = f"""
        <html>
        <body>
            <h2>Recuperación de Contraseña</h2>
            <hr>
            <p>Hola,</p>
            <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
            <p>Tu nueva contraseña temporal es: <strong>{new_password}</strong></p>
            <p>Por favor, utiliza esta contraseña para iniciar sesión. 
            <br>
            Te recomendamos cambiar esta contraseña desde tu perfil una vez hayas iniciado sesión.</p>
            <p>Gracias,</p>
            <p>El Equipo de Soporte.</p>
        </body>
        </html>
        """
        EmailServiceEnv().send_email(
            recipient_email=email,
            subject=subject,
            body=body
        )
        user.Clave = crypt.hash(new_password)
        db.commit()
        return exit_json(1, {
            "exito": True,
            "mensaje": "CORREO_ENVIADO"
        })
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {
            "exito": False,
            "mensaje": str(ex)
        })
