from fastapi import Depends
from config.DB.database import get_db
from sqlalchemy.orm import Session
from models import model_method_payment as ModelMethodPayment
from utils.methods import exit_json


async def get_list_payments(db: Session):
    try:
        payments = db.query(
            ModelMethodPayment.MetodoPago
        ).filter(
            ModelMethodPayment.MetodoPago.Activo
        ).all()
        
        lstPayments = [
            {
                'id': payment.IdMetodoPago,
                'name': payment.Nombre
            }
            for payment in payments
        ]
        
        return exit_json(1, {
            "payments": lstPayments
        })
    except Exception as e:
        return exit_json(0, {
            "mensaje": str(e)
        })
