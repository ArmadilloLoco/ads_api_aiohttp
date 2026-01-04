from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class AdCreate(BaseModel):
    title: str
    description: str