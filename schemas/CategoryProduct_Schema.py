from pydantic import BaseModel
from typing import Optional

class CategorySchema(BaseModel):
    idCategory: Optional[int]
    name: str