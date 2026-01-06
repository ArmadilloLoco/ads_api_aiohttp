from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiohttp import web
# custom
from models import Base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@web.middleware
async def db_session_middleware(request, handler):
    """Middleware для работы с сессиями"""
    async with AsyncSessionLocal() as session:
        request["db_session"] = session
        return await handler(request)