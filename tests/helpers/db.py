from fastapi import FastAPI

from app.db.models import Base


__all__ = ['create_clear_db']


async def create_clear_db(app: FastAPI) -> None:
    async with app.state.db_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
