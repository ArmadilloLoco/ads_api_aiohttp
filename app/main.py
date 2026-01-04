from aiohttp import web
import asyncio
from routes.users import register, login
from routes.ads import create_ad, get_ads, get_ad, update_ad, delete_ad
from database import init_db

def create_app():
    """Создание приложения"""
    app = web.Application()
    
    app.router.add_post("/register", register)
    app.router.add_post("/login", login)
    app.router.add_post("/ads", create_ad)
    app.router.add_get("/ads", get_ads)
    app.router.add_get("/ads/{ad_id}", get_ad)
    app.router.add_put("/ads/{ad_id}", update_ad)
    app.router.add_delete("/ads/{ad_id}", delete_ad)

    return app

if __name__ == "__main__":
    asyncio.run(init_db())
    web.run_app(create_app(), host="0.0.0.0", port=8080)