from config.DB.database import get_db
from sqlalchemy.orm import Session
from models.model_status_sale import EstadoVenta as ModelStatus
from utils.methods import exit_json


async def get_list_status_sales(db: Session):
    try:
        status_sales = db.query(ModelStatus).filter(
            ModelStatus.Activo
        ).order_by(
            ModelStatus.IdEstadoVenta
        ).all()
        
        status_map = [
            {
                "id": status.IdEstadoVenta,
                "name": status.Nombre,
            }
            for status in status_sales
        ]
        
        return exit_json(1, { "status_sales": status_map })
    except Exception as e:
        db.rollback()
        return exit_json(0, str(e))