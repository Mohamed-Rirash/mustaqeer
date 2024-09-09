from datetime import datetime
from pydantic import BaseModel, Field



class MyProgressResponse(BaseModel):
    juz: int
    chapter: int
    verse: int
    page: int
    submission_time: datetime
    content: str
    progress_count: int = Field(default=0)
    no_of_khatmis: int = Field(default=0)
    xp: int = Field(default=0)
    remained: int = Field(default=0)
    state: str = Field(default="not_started")

    class Config:
        from_attributes = True
