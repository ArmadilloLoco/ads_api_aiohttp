import asyncio
from aiohttp import web
# custom
from routes.users import register, login
from routes.ads import create_ad, get_ads, get_ad, update_ad, delete_ad
from database import init_db, db_session_middleware 


def create_app():
    """Создание приложения"""
    app = web.Application(middlewares=[db_session_middleware])
    app.add_routes([
        web.post('/register', register),
        web.post('/login', login),
        web.post('/ads', create_ad),
        web.get('/ads', get_ads),
        web.get('/ads/{ad_id}', get_ad),
        web.put('/ads/{ad_id}', update_ad),
        web.delete('/ads/{ad_id}', delete_ad),
    ])
    return app


async def main():
    await init_db()
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Server started at http://0.0.0.0:8080")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())