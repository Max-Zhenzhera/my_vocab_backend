from abc import (
    ABC,
    abstractmethod
)
from collections.abc import Iterable
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Type,
    TypeAlias,
    TypeVar,
    cast
)

from fastapi import Depends
from sqlalchemy import (
    Column,
    delete as sa_delete,
    insert as sa_insert,
    update as sa_update
)
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select as sa_select
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.dml import UpdateBase

from ..errors import EntityDoesNotExistError
from ..models import Base
from ...api.dependencies.markers import DBSessionInTransactionMarker


__all__ = ['BaseRepo']

SQLAlchemyModelT = TypeVar('SQLAlchemyModelT', bound=Base)

PrimaryKey: TypeAlias = tuple[Column[Any], ...]


@dataclass  # type: ignore[misc]
class BaseRepo(Generic[SQLAlchemyModelT], ABC):
    session: AsyncSession = Depends(DBSessionInTransactionMarker)

    @property
    def primary_key(self) -> PrimaryKey:
        return cast(PrimaryKey, sa_inspect(self.model).primary_key)

    @property
    @abstractmethod
    def model(self) -> Type[SQLAlchemyModelT]:
        """ Repo's model. """

    async def create_one(
        self,
        **insert_data: Any
    ) -> SQLAlchemyModelT:
        stmt = (
            sa_insert(self.model)
            .values(insert_data)
        )
        result = await self._return_from_statement(stmt)
        return cast(SQLAlchemyModelT, result.scalar())

    async def create_many(
        self,
        *insert_data: dict[str, Any]
    ) -> list[SQLAlchemyModelT]:
        stmt = (
            sa_insert(self.model)
            .values(insert_data)
        )
        result = await self._return_from_statement(stmt)
        return result.scalars().all()

    async def bulk_create(
        self,
        *insert_data: dict[str, Any]
    ) -> None:
        stmt = sa_insert(self.model)
        async with self.session.begin_nested():
            await self.session.execute(stmt, insert_data)

    async def get_one_by_pk(
        self,
        pk: Any,
        joins: Iterable[Any] | None = None
    ) -> SQLAlchemyModelT:
        return await self.get_one(self._build_pk_clauses(pk), joins)

    async def get_one(
        self,
        clauses: Iterable[Any],
        joins: Iterable[Any] | None = None
    ) -> SQLAlchemyModelT:
        stmt = sa_select(self.model)
        if joins:
            for join in joins:
                stmt = stmt.options(joinedload(join))
        stmt = stmt.where(*clauses)
        result = await self.session.execute(stmt)
        return self._fetch_one_or_raise(result)

    async def update_one_by_pk(
        self,
        pk: Any,
        **update_data: Any
    ) -> SQLAlchemyModelT:
        return await self.update_one(self._build_pk_clauses(pk), **update_data)

    async def update_one(
        self,
        clauses: Iterable[Any],
        **update_data: Any
    ) -> SQLAlchemyModelT:
        stmt = (
            sa_update(self.model)
            .values(update_data)
            .where(*clauses)
        )
        return await self._return_one(stmt)

    async def delete_one_by_pk(
        self,
        pk: Any
    ) -> SQLAlchemyModelT:
        return await self.delete_one(self._build_pk_clauses(pk))

    async def delete_one(
        self,
        clauses: Iterable[Any]
    ) -> SQLAlchemyModelT:
        stmt = (
            sa_delete(self.model)
            .where(*clauses)
        )
        return await self._return_one(stmt)

    async def delete_all(self) -> None:
        stmt = sa_delete(self.model)
        async with self.session.begin_nested():
            await self.session.execute(stmt)

    async def _return_one(
        self,
        stmt: UpdateBase
    ) -> SQLAlchemyModelT:
        result = await self._return_from_statement(stmt)
        return self._fetch_one_or_raise(result)

    async def _return_from_statement(
        self,
        stmt: UpdateBase
    ) -> Result:
        async with self.session.begin_nested():
            stmt = stmt.returning(self.model)
            orm_stmt = (
                sa_select(self.model)
                .from_statement(stmt)
                .execution_options(populate_existing=True)
            )
            result = await self.session.execute(orm_stmt)
        return result

    @staticmethod
    def _fetch_one_or_raise(result: Result) -> SQLAlchemyModelT:
        try:
            entity = result.scalar_one()
        except NoResultFound as error:
            raise EntityDoesNotExistError from error
        else:
            return cast(SQLAlchemyModelT, entity)

    async def exists_by_pk(
        self,
        pk: Any,
    ) -> bool:
        return await self.exists(self._build_pk_clauses(pk))

    async def exists(
        self,
        clauses: Iterable[Any]
    ) -> bool:
        stmt = (
            sa_select(self.model)
            .where(*clauses)
            .exists().select()
        )
        result = await self.session.execute(stmt)
        return cast(bool, result.scalar())

    def _build_pk_clauses(self, pk: Any) -> Iterable[Any]:
        pk = pk if isinstance(pk, (tuple, list)) else (pk,)
        return [
            pk_column == pk_value
            for pk_column, pk_value in zip(self.primary_key, pk)
        ]
