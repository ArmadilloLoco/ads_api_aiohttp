from aiohttp import web
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import UserRegister
from database import get_db
from auth import create_jwt_token
from database import AsyncSessionLocal
from sqlalchemy import text

async def register(request):
    """Регистрация пользователя"""
    try:
        data = await request.json()
        user_data = UserRegister(**data)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

    async with AsyncSessionLocal() as session:
        # Проверка email
        result = await session.execute(
            text("SELECT 1 FROM users WHERE email = :email"),
            {"email": user_data.email}
        )
        if result.fetchone():
            return web.json_response({"error": "Email already registered"}, status=409)

        # Вставка
        await session.execute(
            text("INSERT INTO users (email, password_hash) VALUES (:email, :password_hash)"),
            {
                "email": user_data.email,
                "password_hash": generate_password_hash(user_data.password)
            }
        )
        await session.commit()

        # Получение ID
        result = await session.execute(
            text("SELECT id, email FROM users WHERE email = :email"),
            {"email": user_data.email}
        )
        row = result.fetchone()
        return web.json_response({"id": row[0], "email": row[1]}, status=201)
    
async def login(request):
    """Вход пользователя: проверяет email и пароль, выдаёт JWT-токен"""
    
    # Получаем данные из запроса
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        # Проверяем, что оба поля переданы
        if not email or not password:
            return web.json_response(
                {"error": "Нужны email и пароль"}, 
                status=400
            )

    except Exception:
        return web.json_response(
            {"error": "Неверный формат данных"}, 
            status=400
        )

    # Ищем пользователя в базе по email
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT id, password_hash FROM users WHERE email = :email"),
            {"email": email}
        )
        user_row = result.fetchone()

        # Проверяем: существует ли пользователь и верный ли пароль
        if user_row is None:
            return web.json_response(
                {"error": "Неверный email или пароль"}, 
                status=401
            )

        user_id = user_row[0]
        stored_password_hash = user_row[1]

        if not check_password_hash(stored_password_hash, password):
            return web.json_response(
                {"error": "Неверный email или пароль"}, 
                status=401
            )

    token = create_jwt_token(user_id) # Создаём токен

    return web.json_response({"token": token}, status=200)