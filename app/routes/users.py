from aiohttp import web
from werkzeug.security import generate_password_hash, check_password_hash
from database import AsyncSessionLocal
from auth import create_jwt_token
from sqlalchemy import text

async def register(request):
    """Регистрация нового пользователя"""
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return web.json_response({'error': 'email and password required'}, status=400)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT 1 FROM users WHERE email = :email"),
            {'email': email}
        )
        if result.fetchone():
            return web.json_response({'error': 'User already exists'}, status=409)
        
        await session.execute(
            text("INSERT INTO users (email, password_hash) VALUES (:email, :password_hash)"),
            {'email': email, 'password_hash': generate_password_hash(password)}
        )
        await session.commit()
        
        result = await session.execute(
            text("SELECT id, email FROM users WHERE email = :email"),
            {'email': email}
        )
        row = result.fetchone()
        return web.json_response({'id': row[0], 'email': row[1]}, status=201)

async def login(request):
    """Авторизация пользователя"""
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return web.json_response({'error': 'email and password required'}, status=400)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT id, password_hash FROM users WHERE email = :email"),
            {'email': email}
        )
        row = result.fetchone()
        
        if not row or not check_password_hash(row[1], password):
            return web.json_response({'error': 'Invalid credentials'}, status=401)
        
        token = create_jwt_token(row[0])
        return web.json_response({'token': token}, status=200)