from aiohttp import web
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
# custom
from models import User
from schemas import UserRegister 
from auth import create_jwt_token


async def register(request):
    """Регистрация нового пользователя"""
    try:  # валидация данных
        user_data = UserRegister(**await request.json())
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

    session = request["db_session"]  # сессия из middleware

    # проверка уникальности
    existing = await session.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        return web.json_response({"error": "The user already exists"}, status=409)

    # ORM: создание объекта
    new_user = User(
        email=user_data.email,
        password_hash=generate_password_hash(user_data.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return web.json_response({"id": new_user.id, "email": new_user.email}, status=201)

async def login(request):
    """Авторизация пользователя"""
    try:
        user_data = UserRegister(**await request.json())
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

    session = request["db_session"]

    result = await session.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not check_password_hash(user.password_hash, user_data.password):
        return web.json_response({"error": "Invalid credentials"}, status=401)

    token = create_jwt_token(user.id)
    return web.json_response({"token": token}, status=200)