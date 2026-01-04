from aiohttp import web
from sqlalchemy import select
from schemas import AdCreate
from database import get_db
from auth import require_auth
from database import AsyncSessionLocal
from models import Ad

@require_auth
async def create_ad(request):
    """Создать новое объявление (только для авторизованных)"""
    
    # Получаем данные из запроса
    try:
        data = await request.json()
        title = data.get("title")
        description = data.get("description")

        if not title or not description:
            return web.json_response(
                {"error": "Нужны заголовок и описание"}, 
                status=400
            )

    except Exception:
        return web.json_response(
            {"error": "Неверный формат данных"}, 
            status=400
        )

    # Сохраняем объявление в базу
    async with AsyncSessionLocal() as session:
        new_ad = Ad(
            title=title,
            description=description,
            owner_id=request["current_user_id"]
        )
        session.add(new_ad)
        await session.commit()
        await session.refresh(new_ad)  # Получаем id и дату из базы

    # Возвращаем созданное объявление
    return web.json_response({
        "id": new_ad.id,
        "title": new_ad.title,
        "description": new_ad.description,
        "created_at": new_ad.created_at.isoformat().replace("+00:00", "Z"),
        "owner_id": new_ad.owner_id
    }, status=201)

async def get_ads(request):
    """Получить список всех объявлений (публичный доступ)"""
    
    async with AsyncSessionLocal() as session:
        # Получаем все объявления из базы
        result = await session.execute(select(Ad))
        all_ads = result.scalars().all()

        # Преобразуем каждое объявление в словарь
        ads_list = []
        for ad in all_ads:
            ads_list.append({
                "id": ad.id,
                "title": ad.title,
                "description": ad.description,
                "created_at": ad.created_at.isoformat().replace("+00:00", "Z"),
                "owner_id": ad.owner_id
            })

        return web.json_response(ads_list, status=200)
    
async def get_ad(request):
    """Получить объявление по номеру (публичный доступ)"""
    
    # Получаем ID из URL
    try:
        ad_id = int(request.match_info["ad_id"])
    except (ValueError, KeyError):
        return web.json_response({"error": "Неверный номер объявления"}, status=400)

    # Ищем объявление в базе
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()

        if ad is None:
            return web.json_response({"error": "Объявление не найдено"}, status=404)

    # Возвращаем данные
    return web.json_response({
        "id": ad.id,
        "title": ad.title,
        "description": ad.description,
        "created_at": ad.created_at.isoformat().replace("+00:00", "Z"),
        "owner_id": ad.owner_id
    }, status=200)

@require_auth
async def update_ad(request):
    """Изменить своё объявление (только владелец)"""
    
    # Получаем ID из URL
    try:
        ad_id = int(request.match_info["ad_id"])
    except (ValueError, KeyError):
        return web.json_response({"error": "Неверный номер объявления"}, status=400)

    # Ищем объявление и проверяем права
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()

        if ad is None:
            return web.json_response({"error": "Объявление не найдено"}, status=404)

        if ad.owner_id != request["current_user_id"]:
            return web.json_response({"error": "Можно изменять только свои объявления"}, status=403)

        # Получаем новые данные
        try:
            data = await request.json()
            title = data.get("title", ad.title)
            description = data.get("description", ad.description)

            if len(title) < 3 or len(title) > 100:
                return web.json_response(
                    {"error": "Заголовок должен быть от 3 до 100 символов"}, 
                    status=400
                )

        except Exception:
            return web.json_response(
                {"error": "Неверный формат данных"}, 
                status=400
            )

        # Обновляем данные
        ad.title = title
        ad.description = description
        await session.commit()

    # Возвращаем обновлённое объявление
    return web.json_response({
        "id": ad.id,
        "title": ad.title,
        "description": ad.description,
        "created_at": ad.created_at.isoformat().replace("+00:00", "Z"),
        "owner_id": ad.owner_id
    }, status=200)

@require_auth
async def delete_ad(request):
    """Удалить своё объявление (только владелец)"""
    
    # Получаем ID из URL
    try:
        ad_id = int(request.match_info["ad_id"])

    except (ValueError, KeyError):
        return web.json_response({"error": "Неверный номер объявления"}, status=400)

    # Ищем объявление и проверяем права
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()

        if ad is None:
            return web.json_response({"error": "Объявление не найдено"}, status=404)

        if ad.owner_id != request["current_user_id"]:
            return web.json_response({"error": "Можно удалять только свои объявления"}, status=403)

        await session.delete(ad)
        await session.commit()

    return web.Response(status=204)