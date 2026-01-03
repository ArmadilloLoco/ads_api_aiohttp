import asyncio
from aiohttp import web
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash


users = {}          # {user_id: {id, email, password_hash}}
ads = {}            # {ad_id: {id, title, description, created_at, owner_id}}
tokens = {}         # {token: user_id}
next_user_id = 1
next_ad_id = 1


# --- Вспомогательные функции ---
def require_auth(handler):
    """Декоратор для проверки авторизации по токену"""
    async def wrapper(request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return web.json_response({'error': 'Missing or invalid Authorization header'}, status=401)
        token = auth_header.split(' ', 1)[1]
        user_id = tokens.get(token)
        if user_id is None:
            return web.json_response({'error': 'Invalid or expired token'}, status=401)
        request['current_user_id'] = user_id
        return await handler(request)
    return wrapper


# --- Эндпоинты пользователей ---
async def register(request):
    """Регистрация нового пользователя"""
    global next_user_id
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'error': 'Email and password are required'}, status=400)

    if any(u['email'] == email for u in users.values()):
        return web.json_response({'error': 'User with this email already exists'}, status=409)

    user = {
        'id': next_user_id,
        'email': email,
        'password_hash': generate_password_hash(password)
    }
    users[next_user_id] = user
    next_user_id += 1
    return web.json_response({'id': user['id'], 'email': user['email']}, status=201)


async def login(request):
    """Авторизация пользователя"""
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'error': 'Email and password are required'}, status=400)

    user = next((u for u in users.values() if u['email'] == email), None)
    if not user or not check_password_hash(user['password_hash'], password):
        return web.json_response({'error': 'Invalid credentials'}, status=401)
    
    # Генерируем уникальный токен
    token = secrets.token_urlsafe(32)
    tokens[token] = user['id']
    return web.json_response({'token': token}, status=200)


# --- Эндпоинты объявлений ---
@require_auth
async def create_ad(request):
    """Создание нового объявления"""
    global next_ad_id
    data = await request.json()

    if not data or 'title' not in data or 'description' not in data:
        return web.json_response({'error': 'title and description are required'}, status=400)

    ad = {
        'id': next_ad_id,
        'title': data['title'],
        'description': data['description'],
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'owner_id': request['current_user_id']
    }

    ads[next_ad_id] = ad
    next_ad_id += 1
    return web.json_response(ad, status=201)


async def get_ads(request):
    """Получение списка всех объявлений"""
    return web.json_response(list(ads.values()), status=200)


async def get_ad(request):
    """Получение конкретного объявления"""
    ad_id = int(request.match_info['ad_id'])
    ad = ads.get(ad_id)
    if not ad:
        return web.json_response({'error': 'Ad not found'}, status=404)
    return web.json_response(ad, status=200)


@require_auth
async def update_ad(request):
    """Обновление объявления"""
    ad_id = int(request.match_info['ad_id'])
    ad = ads.get(ad_id) # Получаем объявление по ID
    if not ad:
        return web.json_response({'error': 'Ad not found'}, status=404)
    if ad['owner_id'] != request['current_user_id']:
        return web.json_response({'error': 'You are not the owner'}, status=403)

    data = await request.json()
    ad['title'] = data.get('title', ad['title'])
    ad['description'] = data.get('description', ad['description'])
    return web.json_response(ad, status=200)


@require_auth
async def delete_ad(request):
    """Удаление объявления"""
    ad_id = int(request.match_info['ad_id'])
    ad = ads.get(ad_id)
    if not ad:
        return web.json_response({'error': 'Ad not found'}, status=404)
    if ad['owner_id'] != request['current_user_id']:
        return web.json_response({'error': 'You are not the owner'}, status=403)

    del ads[ad_id]
    return web.json_response({'message': 'Ad deleted'}, status=200)


# --- Настройка приложеня ---
def create_app():
    app = web.Application()
    app.router.add_post('/register', register)
    app.router.add_post('/login', login)
    app.router.add_post('/ads', create_ad)
    app.router.add_get('/ads', get_ads)
    app.router.add_get('/ads/{ad_id}', get_ad)
    app.router.add_put('/ads/{ad_id}', update_ad)
    app.router.add_delete('/ads/{ad_id}', delete_ad)
    return app


if __name__ == '__main__':
    web.run_app(create_app(), host='0.0.0.0', port=8080)