from typing import ClassVar

from .base import BaseRepo
from ..models import Vocab


__all__ = ['VocabsRepo']


class VocabsRepo(BaseRepo[Vocab]):
    model: ClassVar = Vocab

    async def check_owner_has(self, vocab_id: int, owner_id: int) -> bool:
        return await self.exists([Vocab.id == vocab_id, Vocab.is_owner(owner_id)])

    async def check_title_is_taken(self, title: str, owner_id: int) -> bool:
        return await self.exists([Vocab.title == title, Vocab.is_owner(owner_id)])

    async def get_one_if_permitted_to_read(self, id_: int, reader_id: int) -> Vocab:
        return await self.get_one(
            [
                Vocab.id == id_,
                Vocab.is_public | Vocab.is_owner(reader_id)
            ]
        )
