from fastapi import Depends
from config.security.security import crypt
from models import model_user as ModelUser
from models import model_roles_permissions as ModelRolPermiso
from models import model_sale as ModelSale
from models import model_products as ModelProduct
from config.DB.database import get_db
from sqlalchemy.orm import Session
from utils.methods import EmailServiceEnv, exit_json, generate_random_password, long_to_date
from datetime import datetime, timedelta
from sqlalchemy import Date, and_, or_, func
from collections import defaultdict
from schemas.User_Schema import (
    ListUserSchema,
    ParamListUserSchema,
    UserPasswordUpdate,
    UserSchema,
    UserUpdate,
)
import locale

# db: Session = Depends(get_db)

def find_user_by_id(id: int, db: Session):
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


def validate_dni_exist(dni: int, email_user_current: str, db: Session):
    try:
        find_dni = db.query(ModelUser.Usuario).filter(
            and_(
                len(str(dni)) == 8,
                ModelUser.Usuario.DNI == dni,
                ModelUser.Usuario.Correo != email_user_current                
            )
        ).first()
        if find_dni is not None:
            return exit_json(1, {"exito": False, "mensaje": "DNI_EXISTENTE"})
        return exit_json(1, {"exito": True, "mensaje": "DNI_NO_EXISTENTE"})
    except Exception as ex:
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def add_user(user: UserSchema, user_creation: UserSchema, db: Session):
    try:
        find_user = db.query(ModelUser.Usuario).filter(
            ModelUser.Usuario.Correo == user.email
        ).first()
        
        # validar si el dni ya existe
        dni_exist = validate_dni_exist(user.dni, user_creation["email"], db).dict()
        if dni_exist["state"] == 1 and dni_exist["data"]["exito"] == False:
            return dni_exist
        
        user_creat_mod = user_creation["email"]
        new_password = generate_random_password(10)
        new_pass_encrypt = crypt.hash(new_password)
        print("Nueva contraseña aleatoria: ", new_password)
        
        if find_user is not None:
            if find_user.Activo:
                return exit_json(0, {"exito": False, "mensaje": "USUARIO_YA_EXISTE"})
            else:
                find_user.Nombre = user.name.strip()
                find_user.Apellidos = user.last_name.strip()
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
                Nombre=user.name.strip(),
                Apellidos=user.last_name.strip(),
                Correo=user.email.strip(),
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
        emailOrDni = f"<strong>{user.email}</strong> ó </strong>{user.dni}<strong>" if len(str(user.dni)) == 8 else f"<strong>{user.email}</strong>"
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


async def update_user_by_id_(user: UserUpdate, user_modification: UserSchema, db: Session):
    try:
        find_user = db.query(ModelUser.Usuario).filter(
            ModelUser.Usuario.IdUsuario == user.id_user
        ).first()

        if find_user is None:
            return exit_json(0, {"exito": False, "mensaje": "USUARIO_NO_ENCONTRADO"})

        # validar si el dni ya existe
        email_user_current = user_modification["email"] if user.isProfile else find_user.Correo
        dni_exist = validate_dni_exist(user.dni, email_user_current, db).dict()
        if dni_exist["state"] == 1 and dni_exist["data"]["exito"] == False:
            return dni_exist

        find_user.Nombre = user.name
        find_user.Apellidos = user.last_name
        find_user.DNI = user.dni if user.dni else None
        find_user.IdRol = user.id_rol if user.id_rol else find_user.IdRol
        find_user.Telefono = user.phone if user.phone else None
        find_user.FechaHoraModificacion = datetime.now()
        find_user.UsuarioModificacion = user_modification["email"]

        db.commit()
        db.refresh(find_user)

        return exit_json(1, {"exito": True, "mensaje": "USUARIO_ACTUALIZADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def get_list_users(body: ParamListUserSchema, db: Session):
    try:
        page_size = 5
        page = body.page
        name = body.name.strip()
        id_rol = body.id_rol
        date_creation = long_to_date(body.date_creation)
        offset = (page - 1) * page_size
        
        # Consulta para contar el número total de usuarios activos
        total_users = db.query(ModelUser.Usuario).filter(
            and_(
                #ModelUser.Usuario.Activo,
                or_(
                    and_(
                        id_rol == 0,
                        ModelUser.Usuario.IdRol != 5
                    ),
                    ModelUser.Usuario.IdRol == id_rol
                ),
                or_(
                    name == "",
                    ModelUser.Usuario.Nombre.ilike(f"%{name}%"),
                    ModelUser.Usuario.Apellidos.ilike(f"%{name}%"),
                ),
                or_(
                    date_creation == -1,
                    ModelUser.Usuario.FechaHoraCreacion.cast(Date) == date_creation
                )
            )
        ).count()
        
        users = db.query(ModelUser.Usuario).filter(
            and_(
                #ModelUser.Usuario.Activo,
                or_(
                    and_(
                        id_rol == 0,
                        ModelUser.Usuario.IdRol != 5
                    ),
                    ModelUser.Usuario.IdRol == id_rol
                ),
                or_(
                    name == "",
                    ModelUser.Usuario.Nombre.ilike(f"%{name}%"),
                    ModelUser.Usuario.Apellidos.ilike(f"%{name}%")
                ),
                or_(
                    date_creation == -1,
                    ModelUser.Usuario.FechaHoraCreacion.cast(Date) == date_creation
                )
            )
        ).order_by(
            ModelUser.Usuario.IdUsuario.desc()
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
                date_creation=user.FechaHoraCreacion.date().strftime("%d-%m-%Y"),
                total=total_users
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


async def update_status_user_by_id(id_user: int, is_active, user_delete: UserSchema, db: Session):
    try:
        if user_delete["id_rol"] != 1:  # 1: Administrador
            return exit_json(0, {"exito": False, "mensaje": "NO_TIENE_PERMISOS"})

        user = db.query(ModelUser.Usuario).filter(
            ModelUser.Usuario.IdUsuario == id_user
        ).first()

        if user is None:
            return exit_json(0, {"exito": False, "mensaje": "USUARIO_NO_ENCONTRADO"})

        user.Activo = is_active
        user.FechaHoraModificacion = datetime.now()
        user.UsuarioModificacion = user_delete["email"]
        db.commit()
        db.refresh(user)
        return exit_json(1, {"exito": True, "mensaje": "ESTADO_USUARIO_ACTUALIZADO"})
    except Exception as ex:
        try:
            db.rollback()
        except Exception as e:
            print("ERR", str(e))
        return exit_json(0, {"exito": False, "mensaje": str(ex)})


async def get_list_permissions_by_user(user: UserSchema, db: Session):
    try:
        print("Usuario", user)
        permissionsUser = db.query(ModelRolPermiso.Rolpermisos).filter(
            and_(
                ModelRolPermiso.Rolpermisos.Activo,
                ModelRolPermiso.Rolpermisos.IdRol == user["id_rol"]
            )
        ).all()
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
    userPass: UserPasswordUpdate, user: UserSchema, db: Session
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


async def details_dashboard_by_user(user: UserSchema, db: Session):
    try:
        # Obtener permisos del usuario de una vez
        """ permissions = await get_list_permissions_by_user(user, db)        
        if permissions.state == 0:
            return exit_json(0, { "mensaje": "Usuario sin permisos" }) """

        # Fecha de inicio del mes actual y seis meses atrás
        start_of_month = datetime.now().replace(day=1)
        six_months_ago = datetime.now() - timedelta(days=180)
        previous_six_months = six_months_ago - timedelta(days=180)

        # Total de usuarios activos y nuevos usuarios en el mes actual
        total_users, new_users_month = db.query(
            func.count(ModelUser.Usuario.IdUsuario).filter(ModelUser.Usuario.Activo, ModelUser.Usuario.IdRol != 5),
            func.count(ModelUser.Usuario.IdUsuario).filter(
                ModelUser.Usuario.Activo,
                ModelUser.Usuario.FechaHoraCreacion >= start_of_month
            )
        ).first()

        # Porcentaje de nuevos usuarios
        porcent_users_news_month = round((new_users_month / total_users) * 100, 2) if total_users else 0
        flag_users_news_month = porcent_users_news_month < 0

        # Ventas del día actual, últimos 6 meses y período anterior
        ventas_hoy, ventas_ultimos_6_meses, ventas_periodo_anterior = db.query(
            func.sum(ModelSale.Venta.Total).filter(
                ModelSale.Venta.Activo,
                ModelSale.Venta.FechaHoraVenta.cast(Date) == datetime.now().date()
            ),
            func.sum(ModelSale.Venta.Total).filter(
                ModelSale.Venta.Activo,
                ModelSale.Venta.FechaHoraVenta >= six_months_ago
            ),
            func.sum(ModelSale.Venta.Total).filter(
                ModelSale.Venta.Activo,
                ModelSale.Venta.FechaHoraVenta.between(previous_six_months, six_months_ago)
            )
        ).first()

        # Asegurar valores no nulos para evitar errores de tipo
        ventas_hoy = ventas_hoy or 0
        ventas_ultimos_6_meses = round(ventas_ultimos_6_meses or 0, 2)
        ventas_periodo_anterior = ventas_periodo_anterior or 0

        # Porcentaje de cambio en ventas de los últimos 6 meses
        porcentaje_ventas = (
            round(((ventas_ultimos_6_meses - ventas_periodo_anterior) / ventas_periodo_anterior) * 100, 2)
            if ventas_periodo_anterior else 0
        )
        flag_porcent_ventas = porcentaje_ventas < 0

        # Total de inventario activo y nuevos productos del mes
        total_inventory, new_stock_month = db.query(
            func.count(ModelProduct.Productos.IdProducto).filter(ModelProduct.Productos.Activo),
            func.count(ModelProduct.Productos.IdProducto).filter(
                ModelProduct.Productos.Activo,
                ModelProduct.Productos.FechaHoraCreacion >= start_of_month
            )
        ).first()

        # Porcentaje de nuevos productos en el mes
        porcent_inventory_news_month = round((new_stock_month / total_inventory) * 100, 2) if total_inventory else 0
        flag_inventory_news_month = porcent_inventory_news_month < 0

        # Ventas del mes actual según estado (1: pendiente, 2: completada, 3: anulada)
        ventas_estado = db.query(
            ModelSale.Venta.IdEstadoVenta,
            func.sum(ModelSale.Venta.Total)
        ).filter(
            ModelSale.Venta.Activo,
            ModelSale.Venta.FechaHoraVenta >= start_of_month
        ).group_by(ModelSale.Venta.IdEstadoVenta).all()

        # Procesar resultados para obtener total y porcentajes de ventas por estado
        total_ventas_mes_actual = sum(v[1] or 0 for v in ventas_estado)
        ventas_por_estado = {
            "pending": 0,
            "complete": 0,
            "annul": 0,
            "porcent_pending": 0,
            "porcent_complete": 0,
            "porcent_annul": 0
        }

        for estado, total in ventas_estado:
            if estado == 1:
                ventas_por_estado["pending"] = total or 0
                ventas_por_estado["porcent_pending"] = round((total / total_ventas_mes_actual) * 100, 2) if total_ventas_mes_actual else 0
            elif estado == 2:
                ventas_por_estado["complete"] = total or 0
                ventas_por_estado["porcent_complete"] = round((total / total_ventas_mes_actual) * 100, 2) if total_ventas_mes_actual else 0
            elif estado == 3:
                ventas_por_estado["annul"] = total or 0
                ventas_por_estado["porcent_annul"] = round((total / total_ventas_mes_actual) * 100, 2) if total_ventas_mes_actual else 0

        return exit_json(1, {
            "users": {
                "total_users": total_users,
                "porcent_users_news_month": porcent_users_news_month,
                "flag_users_news_month": flag_users_news_month
            },
            "sales": {
                "sales_today": ventas_hoy,
                "sales_last_6_month": ventas_ultimos_6_meses,
                "porcent_sales": porcentaje_ventas,
                "flag_porcent_sales": flag_porcent_ventas,
                "sales_status": ventas_por_estado
            },
            "inventory": {
                "total_inventory": total_inventory,
                "porcent_inventory_news_month": porcent_inventory_news_month,
                "flag_inventory_news_month": flag_inventory_news_month
            }
        })
    except Exception as ex:
        return exit_json(0, {"mensaje": str(ex)})


async def profile_user(user: UserSchema, db: Session):
    try:
        id_user_current = user["id_user"]        
        # Fecha de inicio del mes actual
        start_of_month = datetime.now().replace(day=1)
        # Cantidad de ventas del mes actual
        ventas_month_current = db.query(
            func.count(ModelSale.Venta.IdVenta)
        ).filter(
            ModelSale.Venta.Activo,
            ModelSale.Venta.IdUsuarioVenta == id_user_current,
            ModelSale.Venta.FechaHoraVenta >= start_of_month
        ).scalar() or 0  # .scalar() para obtener directamente el valor, y default a 0
        # Ventas por estado en el mes actual
        ventas_estado = db.query(
            ModelSale.Venta.IdEstadoVenta,
            func.count(ModelSale.Venta.IdVenta)
        ).filter(
            ModelSale.Venta.Activo,
            ModelSale.Venta.IdUsuarioVenta == id_user_current,
            ModelSale.Venta.FechaHoraVenta >= start_of_month
        ).group_by(ModelSale.Venta.IdEstadoVenta).all()
        # Inicializar contadores de ventas por estado
        ventas_por_estado = {
            "pending": 0,
            "complete": 0,
            "annul": 0
        }
        # Procesar resultados para asignar cantidades por estado
        for estado, cantidad in ventas_estado:
            if estado == 1:
                ventas_por_estado["pending"] = cantidad or 0
            elif estado == 2:
                ventas_por_estado["complete"] = cantidad or 0
            elif estado == 3:
                ventas_por_estado["annul"] = cantidad or 0
        # Configurar el idioma para obtener el nombre del mes en español
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Español (España)
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'es_PE.UTF-8')  # Español (Perú, como alternativa)        
        # Obtener el nombre del mes en español y capitalizarlo
        name_month_current = start_of_month.strftime("%B").capitalize()
        # Construir respuesta
        return exit_json(1, {
            "sales_by_user": {
                "sales_month_current": ventas_month_current,
                "name_month_current": name_month_current,
                "sales_status": ventas_por_estado
            }
        })
    except Exception as e:
        return exit_json(0, f"Error en profile_user: {str(e)}")

