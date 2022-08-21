import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine
)
from sqlalchemy.orm import sessionmaker


__all__ = ['DBState']

logger = logging.getLogger(__name__)


@dataclass
class DBState:
    sqlalchemy_url: str

    def __post_init__(self) -> None:
        self.engine = create_async_engine(self.sqlalchemy_url)
        self.sessionmaker = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info('Database state has been set.')

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self.sessionmaker()
        try:
            yield session
        except HTTPException:
            await session.commit()
        except Exception:
            await session.rollback()
        else:
            await session.commit()
        finally:
            await session.close()

    async def shutdown(self) -> None:
        await self.engine.dispose()
        logger.info('Database state has been shutdown.')
