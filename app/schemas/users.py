from pydantic import BaseModel, EmailStr
from typing import Optional
class RegisterUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class VerifyUserRequest(BaseModel):
    token: str
    email: EmailStr

class EmailRequest(BaseModel):
    email: EmailStr

class ResetRequest(BaseModel):
    token: str
    email: EmailStr
    password: str
