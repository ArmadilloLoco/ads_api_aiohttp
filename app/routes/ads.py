from aiohttp import web
from sqlalchemy import select
from database import AsyncSessionLocal
from models import Ad
from auth import require_auth


@require_auth
async def create_ad(request):
    """Создание объявления"""
    data = await request.json()
    title = data.get('title')
    description = data.get('description')
    
    if not title or not description:
        return web.json_response({'error': 'title and description required'}, status=400)
    
    async with AsyncSessionLocal() as session:
        new_ad = Ad(
            title=title,
            description=description,
            owner_id=request['current_user_id']
        )
        session.add(new_ad)
        await session.commit()
        await session.refresh(new_ad)
        
        return web.json_response({
            'id': new_ad.id,
            'title': new_ad.title,
            'description': new_ad.description,
            'created_at': new_ad.created_at.isoformat().replace('+00:00', 'Z'),
            'owner_id': new_ad.owner_id
        }, status=201)

async def get_ads(request):
    """Получение всех объявлений"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad))
        ads = result.scalars().all()
        return web.json_response([
            {
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'created_at': ad.created_at.isoformat().replace('+00:00', 'Z'),
                'owner_id': ad.owner_id
            }
            for ad in ads
        ], status=200)

async def get_ad(request):
    """Получение одного объявления"""
    try:
        ad_id = int(request.match_info['ad_id'])

    except ValueError:
        return web.json_response({'error': 'Invalid ad ID'}, status=400)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        
        if ad is None:
            return web.json_response({'error': 'Ad not found'}, status=404)
        
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'created_at': ad.created_at.isoformat().replace('+00:00', 'Z'),
            'owner_id': ad.owner_id
        }, status=200)

@require_auth
async def update_ad(request):
    """Обновление объявления"""
    try:
        ad_id = int(request.match_info['ad_id'])

    except ValueError:
        return web.json_response({'error': 'Invalid ad ID'}, status=400)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        
        if ad is None:
            return web.json_response({'error': 'Ad not found'}, status=404)
        
        if ad.owner_id != request['current_user_id']:
            return web.json_response({'error': 'You are not the owner'}, status=403)
        
        data = await request.json()
        ad.title = data.get('title', ad.title)
        ad.description = data.get('description', ad.description)
        await session.commit()
        
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'created_at': ad.created_at.isoformat().replace('+00:00', 'Z'),
            'owner_id': ad.owner_id
        }, status=200)

@require_auth
async def delete_ad(request):
    """Удаление объявления"""
    try:
        ad_id = int(request.match_info['ad_id'])

    except ValueError:
        return web.json_response({'error': 'Invalid ad ID'}, status=400)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        
        if ad is None:
            return web.json_response({'error': 'Ad not found'}, status=404)
        
        if ad.owner_id != request['current_user_id']:
            return web.json_response({'error': 'You are not the owner'}, status=403)
        
        await session.delete(ad)
        await session.commit()
        return web.Response(status=204)