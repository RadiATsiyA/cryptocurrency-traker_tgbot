from sqlalchemy import Column, Integer, String, Float, Boolean, select, insert, update, or_

from database import Base, async_session_maker


class CryptoTrackInfo(Base):
    __tablename__ = "track_info"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    crypto_name = Column(String, nullable=False)
    min_threshold = Column(Float, nullable=False)
    max_threshold = Column(Float, nullable=False)
    min_notified = Column(Boolean, default=False)
    max_notified = Column(Boolean, default=False)

    @classmethod
    async def find_all_unchecked(cls):
        async with async_session_maker() as session:
            query = select(CryptoTrackInfo).where(
                or_(CryptoTrackInfo.min_notified == False, CryptoTrackInfo.max_notified == False)
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update_crypto_thresholds_by_id(cls, id: int, **data):
        async with async_session_maker() as session:
            query = update(cls).where(cls.id == id).values(**data)
            result = await session.execute(query)
            if result.rowcount == 0:
                raise ValueError(f"No record found with id: {id}")
            await session.commit()

    @classmethod
    async def get_crypto_thresholds_by_chat_id(cls, chat_id: int):
        async with async_session_maker() as session:
            query = select(cls).filter_by(chat_id=chat_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add_crypto_threshold(cls, crypto_name: str, min_threshold: float, max_threshold: float, chat_id: int):
        async with async_session_maker() as session:
            query = insert(cls).values(
                crypto_name=crypto_name,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
                chat_id=chat_id
            )
            await session.execute(query)
            await session.commit()
