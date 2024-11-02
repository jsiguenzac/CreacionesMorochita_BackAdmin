from pydantic import BaseModel
from typing import Optional

class CategorySchema(BaseModel):
    id: Optional[int]
    name: str