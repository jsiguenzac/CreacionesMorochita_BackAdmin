from pydantic import BaseModel
from typing import Any

class Salida():
    def __init__(self, state, msg):
        self.state = state
        self.msg = msg
        self.data = {}  # Inicializamos "data" como objeto vacío

class BaseM(BaseModel):
    state: int
    msg: str
    data: Any