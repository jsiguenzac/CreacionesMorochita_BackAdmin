from config.security.security import crypt
from models import model_user as ModelUser
from models import model_roles_permissions as ModelRolPermiso
from config.DB.database import get_db
from utils.methods import EmailServiceEnv, exit_json, generate_random_password
from datetime import datetime
from sqlalchemy import and_, or_
from collections import defaultdict
from schemas.User_Schema import (
    ListUserSchema,
    ParamListUserSchema,
    UserPasswordUpdate,
    UserSchema,
    UserUpdate,
)

db = next(get_db())

def find_user_by_id(id: int):
    try:
        user = db.query(ModelUser.Usuario).filter(
            ModelUser.Usuario.IdUsuario == id
        ).first()
        if user is None:
            return exit_json(0, {"mensaje": "USUARIO_NO_ENCONTRADO"})
        if not user.Activo:
            return exit_json(0, {"mensaje": "USUARIO_INACTIVO"})
        
        user_schema = ListUserSchema(
            id_user=user.IdUsuario,
            name=user.Nombre,
            last_name=user.Apellidos,
            dni=user.DNI,
            email=user.Correo,
            phone=user.Telefono,
            active=user.Activo,
            name_rol=user.Rol.Nombre,
            id_rol=user.IdRol
        )
        return exit_json(1, user_schema)
    except Exception as e:
        return exit_json(0, str(e))


async def add_user(user: UserSchema, user_creation: UserSchema):
    try:
        find_user = db.query(ModelUser.Usuario).filter(
            ModelUser.Usuario.Correo == user.email
        ).first()
        print("UserEncontrado", find_user)

        user_creat_mod = user_creation["email"]
        new_password = generate_random_password(10)
        new_pass_encrypt = crypt.hash(new_password)
        print("Nueva contraseña aleatoria: ", new_password)
        
        if find_user is not None:
            if find_user.Activo:
                return exit_json(0, {"exito": False, "mensaje": "USUARIO_YA_EXISTE"})
            else:
                find_user.Nombre = user.name
                find_user.Apellidos = user.last_name
                find_user.DNI = user.dni
                find_user.Clave = new_pass_encrypt                
                find_user.IdRol = user.id_rol
                find_user.Telefono = user.phone
                find_user.Activo = True
                find_user.FechaHoraModificacion = datetime.now()
                find_user.UsuarioModificacion = user_creat_mod
                db.commit()
                db.refresh(user)
        else:
            new_user = ModelUser.Usuario(
                Nombre=user.name,
                Apellidos=user.last_name,
                Correo=user.email,
                DNI=user.dni,
                Clave=new_pass_encrypt,
                IdRol=user.id_rol,
                Telefono=user.phone,
                Activo=True,
                FechaHoraCreacion=datetime.now(),
                UsuarioCreacion=user_creat_mod,
            )            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        
        subject = f"Plataforma Morochita - Bienvenid@"
        emailOrDni = f"<strong>{user.email}</strong> ó </strong>{user.dni}<strong>" if len(user.dni)==8 else f"<strong>{user.email}</strong>"
        body = f"""
        <html>
        <body>
            <h2>¡BIENVENID@!</h2>
            <hr>
            <p>Hola, {user.name.capitalize()} {user.last_name.capitalize()}</p>
            <p>Se ha creado tu usuario exitosamente.</p>
            <p>Podrás iniciar sesión con las siguientes credenciales:</p>
            <p>Correo ó DNI: {emailOrDni}</p>
            <p>Contraseña temporal: <strong>{new_password}</strong></p>
            <br>
            <p>Por favor, inicia sesión en la plataforma y cambia tu contraseña.</p>
            <p>Podrás cambiar tu contraseña desde tu perfil.</p>
            <br>
            <p>El Equipo de Soporte.</p>
        </body>
        </html>
        """
        EmailServiceEnv().send_email(
            recipient_email=user.email,
            subject=subject,
            body=body
        )
        return exit_json(1, {"exito": True, "mensaje": "USUARIO_CREADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def update_user_by_id_(user: UserUpdate, user_modification: UserSchema):
    try:
        find_user = db.query(ModelUser.Usuario).filter(
            and_(
                ModelUser.Usuario.IdUsuario == user.id_user,
                ModelUser.Usuario.Activo
            )
        ).first()

        if find_user is None:
            return exit_json(0, {"exito": False, "mensaje": "USUARIO_NO_ENCONTRADO"})

        find_user.Nombre = user.name
        find_user.Apellidos = user.last_name
        find_user.DNI = user.dni if user.dni else find_user.DNI
        find_user.IdRol = user.id_rol if user.id_rol else find_user.IdRol
        find_user.Telefono = user.phone if user.phone else find_user.Telefono
        find_user.FechaHoraModificacion = datetime.now()
        find_user.UsuarioModificacion = user_modification.get("email")

        db.commit()
        db.refresh(find_user)

        return exit_json(1, {"exito": True, "mensaje": "USUARIO_ACTUALIZADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def get_list_users(body: ParamListUserSchema):
    try:
        page_size = 10
        page = body.page
        name = body.name.strip()
        id_rol = body.id_rol
        offset = (page - 1) * page_size

        # Consulta para contar el número total de usuarios activos
        total_users = db.query(ModelUser.Usuario).filter(
            and_(
                ModelUser.Usuario.Activo,
                or_(
                    ModelUser.Usuario.IdRol == id_rol,
                    id_rol == 0
                ),
                or_(
                    name == "",
                    ModelUser.Usuario.Nombre.ilike(f"%{name}%"),
                    ModelUser.Usuario.Apellidos.ilike(f"%{name}%"),
                )
            )
        ).count()
        
        users = db.query(ModelUser.Usuario).filter(
            and_(
                ModelUser.Usuario.Activo,
                or_(
                    id_rol == 0,
                    ModelUser.Usuario.IdRol == id_rol
                ),
                or_(
                    name == "",
                    ModelUser.Usuario.Nombre.ilike(f"%{name}%"),
                    ModelUser.Usuario.Apellidos.ilike(f"%{name}%")
                )
            )
        ).offset(offset).limit(page_size).all()

        lstUsers = [
            ListUserSchema(
                id_user=user.IdUsuario,
                name=user.Nombre,
                last_name=user.Apellidos,
                dni=user.DNI,
                email=user.Correo,
                phone=user.Telefono,
                active=user.Activo,
                name_rol=user.Rol.Nombre,
                id_rol=user.IdRol,
            )
            for user in users
        ]
        return exit_json(
            1, {"total": total_users, "page_size": page_size, "users": lstUsers}
        )
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def delete_user_by_id(id_user: int, user_delete: UserSchema):
    try:
        if user_delete["id_rol"] != 1:  # 1: Administrador
            return exit_json(0, {"exito": False, "mensaje": "NO_TIENE_PERMISOS"})

        user = db.query(ModelUser.Usuario).filter(
            and_(
                ModelUser.Usuario.IdUsuario == id_user,
                ModelUser.Usuario.Activo
            )
        ).first()

        if user is None:
            return exit_json(0, {"exito": False, "mensaje": "USUARIO_NO_ENCONTRADO"})

        user.Activo = False
        user.FechaHoraModificacion = datetime.now()
        user.UsuarioModificacion = user_delete["email"]
        db.commit()
        db.refresh(user)
        return exit_json(1, {"exito": True, "mensaje": "USUARIO_ELIMINADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def get_list_permissions_by_user(user: UserSchema):
    try:
        print("Usuario", user)
        permissionsUser = db.query(ModelRolPermiso.Rolpermisos).filter(
            and_(
                ModelRolPermiso.Rolpermisos.Activo,
                ModelRolPermiso.Rolpermisos.IdRol == user["id_rol"]
            )
        ).all()
        print("Permisos", permissionsUser)
        # Diccionario para agrupar permisos por módulo
        modulos_permisos = defaultdict(lambda: {"name_module": "", "permissions": []})
        
        # Agrupar permisos por IdModulo y añadir los detalles
        for perm in permissionsUser:
            id_modulo = perm.Permiso.Modulo.IdModulo
            modulos_permisos[id_modulo]["name_module"] = perm.Permiso.Modulo.Nombre
            modulos_permisos[id_modulo]["permissions"].append(perm.IdPermiso)
        
        lstPermisos = [
            {
                "id_module": id_modulo,
                "name_module": data["name_module"],
                "permissions": data["permissions"]
            }
            for id_modulo, data in modulos_permisos.items()
        ]
        return exit_json(1, {"permissions": lstPermisos})
    except Exception as ex:
        return exit_json(0, {"mensaje": str(ex)})


async def update_password_user_with_hash(
    userPass: UserPasswordUpdate, user: UserSchema
):
    try:
        find_user = db.query(ModelUser.Usuario).filter(
            and_(
                ModelUser.Usuario.Activo,
                ModelUser.Usuario.IdUsuario == user["id_user"]
            )
        ).first()

        if find_user is None:
            return exit_json(0, {"exito": False, "mensaje": "USUARIO_NO_ENCONTRADO"})

        if not crypt.verify(userPass.current_pass, find_user.Clave):
            return exit_json(0, {"exito": False, "mensaje": "CLAVE_ACTUAL_INCORRECTA"})

        find_user.Clave = crypt.hash(userPass.new_pass)
        find_user.FechaHoraModificacion = datetime.now()
        find_user.UsuarioModificacion = user["email"]

        db.commit()
        db.refresh(find_user)

        return exit_json(1, {"exito": True, "message": "PASSWORD_USUARIO_ACTUALIZADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})
