from typing import ClassVar

from .base import BaseRepo
from ..models import VocabTagAssociation


__all__ = ['VocabTagAssociationsRepo']


class VocabTagAssociationsRepo(BaseRepo[VocabTagAssociation]):
    model: ClassVar = VocabTagAssociation

    async def create_associations(
        self,
        vocab_id: int,
        tag_ids: list[int]
    ) -> None:
        associations = [
            {
                'vocab_id': vocab_id,
                'tag_id': tag_id
            } for tag_id in tag_ids
        ]
        if associations:
            await self.bulk_create(*associations)
