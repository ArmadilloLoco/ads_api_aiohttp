from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class AdCreate(BaseModel):
    title: str
    description: str

    @field_validator("title")
    def validate_title(cls, v):
        """Проверка длины заголовка"""
        if len(v) < 3 or len(v) > 100:
            raise ValueError("Длина заголовка должна быть от 3 до 100 символов")