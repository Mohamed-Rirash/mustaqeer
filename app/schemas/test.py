
from app.config.dependencies import db_dependency
from pydantic import BaseModel

class BookCreate(BaseModel):

    name: str
    author: str
    publisher: str
