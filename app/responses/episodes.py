from pydantic import BaseModel
from typing import Optional
from app.utils.enum import Juz

class AddEpisodeResponse(BaseModel):
    juz: int
    description: str
    no_of_khatmis: int
    progress: int
    
