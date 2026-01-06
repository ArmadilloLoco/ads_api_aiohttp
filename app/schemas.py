from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class AdCreate(BaseModel):
    title: str
    description: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 100:
            raise ValueError("Title must be between 3 and 100 characters")
        return v