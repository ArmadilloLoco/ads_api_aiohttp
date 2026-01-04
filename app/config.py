import os

JWT_KEY = os.getenv("JWT_KEY", "jwt-key")
JWT_ALGORITHM = "HS256"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/ads.db")