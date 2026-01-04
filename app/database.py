from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models import Base

engine = create_async_engine(
    DATABASE_URL, 
    echo=True, 
    future=True,
    connect_args={"check_same_thread": False}
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    """Получение сессии базы данных"""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)