""" from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.db import DatabaseConfig
from dotenv import load_dotenv
import os

load_dotenv()

#BD xata
db_config = DatabaseConfig(
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    host = os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT'),
    database = os.getenv('DB_NAME')
)

db_url = db_config.get_url()

engine = create_engine(db_url, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) """

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from schemas.db import DatabaseConfig
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = DatabaseConfig(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME')
)

# Asegurarse de que los valores están presentes
if not all([db_config.user, db_config.password, db_config.host, db_config.port, db_config.database]):
    raise ValueError("Faltan variables de entorno para la conexión a la base de datos")

# Construir la URL de conexión
db_url = db_config.get_url()

# Crear el motor de la base de datos
try:
    engine = create_engine(db_url, echo=True, pool_pre_ping=True)  # pool_pre_ping para verificar conexiones
except SQLAlchemyError as e:
    raise RuntimeError(f"Error al conectar con la base de datos: {e}")

# Crear la base declarativa
Base = declarative_base()

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener una sesión de base de datos
def get_db():
    """Obtiene una sesión de base de datos para usar en el contexto de las peticiones"""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Confirmar transacción
    except SQLAlchemyError as e:
        db.rollback()  # Revertir si hay errores
        print(f"Error en la transacción: {e}")
        raise
    finally:
        db.close()  # Cerrar la sesión

# Inicializar las tablas en la base de datos (si es necesario)
""" def init_db():
    #Inicializa las tablas en la base de datos si no existen
    Base.metadata.create_all(bind=engine)
 """