import jwt
from jwt.exceptions import InvalidTokenError
from aiohttp import web
from config import JWT_KEY, JWT_ALGORITHM

def create_jwt_token(user_id: int) -> str:
    """Создает JWT токен для пользователя"""
    return jwt.encode({"user_id": user_id}, JWT_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> int | None:
    """Декодирует JWT токен"""
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    
    except InvalidTokenError:
        return None

def require_auth(handler):
    """Обертка для проверки авторизации"""
    async def wrapper(request):
        # Получаем заголовок Authorization
        auth_header = request.headers.get("Authorization")
        
        # Проверяем, что заголовок начинается с "Bearer "
        if not auth_header or not auth_header.startswith("Bearer "):
            return web.json_response(
                {"error": "Требуется заголовок: Authorization: Bearer <токен>"}, 
                status=401
            )
        
        token = auth_header[7:]  # Извлекаем токен 
        
        user_id = decode_jwt_token(token) # Проверяем токен
        if user_id is None:
            return web.json_response({"error": "Неверный токен"}, status=401)
        
        request["current_user_id"] = user_id # Передаём user_id в запрос
        
        return await handler(request) # Выполняем основную функцию
    
    return wrapper