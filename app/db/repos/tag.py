from typing import ClassVar

from .base import BaseRepo
from ..models import Tag


__all__ = ['TagsRepo']


class TagsRepo(BaseRepo[Tag]):
    model: ClassVar = Tag

    async def check_owner_has(self, tag_id: int, owner_id: int) -> bool:
        return await self.exists([Tag.id == tag_id, Tag.is_owner(owner_id)])

    async def check_title_is_taken(self, title: str, owner_id: int) -> bool:
        return await self.exists([Tag.title == title, Tag.is_owner(owner_id)])

    async def get_one_if_owner(self, tag_id: int, reader_id: int) -> Tag:
        return await self.get_one([Tag.id == tag_id, Tag.is_owner(reader_id)])

    # async def get_ids_owner_does_not_have(
    #     self,
    #     models_ids: list[int],
    #     user_id: int
    # ) -> list[int]:
    #     ids_as_array = sa_cast(models_ids, ARRAY(BigInteger))
    #     ids_as_table = (
    #         func.unnest(ids_as_array)
    #         .alias('model_id')
    #     )
    #     stmt = (
    #         sa_select(ids_as_table.column)
    #         .select_from(ids_as_table)
    #         .join(
    #             self.model,
    #             onclause=self.model.id == ids_as_table.table_valued(),
    #             isouter=True
    #         )
    #         .where(
    #             (self.model.id.is_(null())) |
    #             (self.model.user_id != user_id)
    #         )
    #     )
    #     result = await self.session.execute(stmt)
    #     return result.scalars().all()
