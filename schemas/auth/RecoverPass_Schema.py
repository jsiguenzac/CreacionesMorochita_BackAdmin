from pydantic import BaseModel
    
class RecoverPassSchema(BaseModel):
    email: str