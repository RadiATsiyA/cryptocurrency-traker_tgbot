from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


DATABASE_URL = "sqlite+aiosqlite:///./crypto_tracking.db"

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

