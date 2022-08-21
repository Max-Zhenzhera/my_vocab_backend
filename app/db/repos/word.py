from typing import ClassVar

from .base import BaseRepo
from ..models import Word


__all__ = ['WordsRepo']


class WordsRepo(BaseRepo[Word]):
    model: ClassVar = Word
