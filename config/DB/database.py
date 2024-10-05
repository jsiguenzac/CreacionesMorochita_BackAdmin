from sqlalchemy.orm import declarative_base
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)