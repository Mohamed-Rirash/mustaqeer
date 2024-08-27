from typing import Union
from datetime import datetime
from pydantic import EmailStr, BaseModel
from app.responses.base import BaseResponse


class UserResponse(BaseResponse):
    id: int
    first_name: str
    email: EmailStr
    profile_image: str
    points: int
    no_of_khatmis: int
    is_active: bool
    created_at: Union[str, None, datetime] = None


class LoginResponse(BaseModel):
    access_token: str
    # refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
