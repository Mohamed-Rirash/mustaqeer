from pydantic import BaseModel, Field
from app.utils.enum import Juz
from typing import Optional

class AddEpisodeRequest(BaseModel):
    juz: Optional[Juz] = Juz.ONE
    description: str = Field(..., min_length=20 , max_length=150)


