# Домашнее задание к лекции «Aiohttp»

## Ads API

REST API для управления объявлениями.

## Эндпоинты

### Регистрация
```http
POST /register
Content-Type: application/json
```
```json
{"email": "user@test.com", "password": "pass123"}
```

Ответ:
201 Created
```json
{"id": 1, "email": "..."}
```

### Вход
```http
POST /login
Content-Type: application/json
```
```json
{"email": "user@test.com", "password": "pass123"}
```
ответ:
200 OK
```json
{"token": "JWT..."}
```

### Создать объявление
```http
POST /ads
Authorization: Bearer <token>
Content-Type: application/json
```
```json
{"title": "Bike", "description": "Cool bike"}
```

### Получить все объявления
```http
GET /ads
```
Ответ, если есть объявления:
201 Created
```json
{"title": "Bike", "description": "Cool bike"}
```
Ответ, если нет объявления:
204 No Content

### Получить/обновить/удалить
- GET /ads/{id} 
ответ: 200 OK (объявление) или 404 Not Found
- PUT /ads/{id}
ответ: 200 OK (обновлённое объявление, только для владельца)
- DELETE /ads/{id}
ответ: 204 No Content (только для владельца)

### Запуск
```bash
docker-compose up --build
```

### Проверка полного цикла
0. Зарегистрироваться
```bash
curl.exe -X POST http://localhost:8080/register \
-H "Content-Type: application/json" \
-d '{"email": "user@test.com", "password": "pass123"}'
```
1. Войти и получить токен
```bash
curl.exe -X POST http://localhost:8080/login \
-H "Content-Type: application/json" \
-d '{"email": "user@test.com", "password": "pass123"}'
```
2. Создать объявление
```bash
curl.exe -X POST http://localhost:8080/ads \
-H "Authorization: Bearer <ваш_токен>" \
-H "Content-Type: application/json" \
-d '{"title": "Bike", "description": "Cool bike"}'
```
3. Посмотреть все объявления
```bash
curl.exe http://localhost:8080/ads
```

### Удаление
```bash
docker-compose down
```