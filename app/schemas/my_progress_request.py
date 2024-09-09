from datetime import datetime
from pydantic import BaseModel, Field

class MyProgress(BaseModel):
    readed_juz: int
