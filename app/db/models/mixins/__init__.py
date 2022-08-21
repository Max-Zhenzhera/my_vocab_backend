"""
https://docs.sqlalchemy.org/en/14/orm/declarative_mixins.html#mixing-in-columns
https://docs.sqlalchemy.org/en/14/orm/declarative_mixins.html#mixing-in-relationships
https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html#using-declared-attr-and-declarative-mixins

https://stackoverflow.com/a/4013184/17221540
"""

from .expirable import ExpirableMixin
from .id_ import IDMixin
from .timestamp import (
    CreatedAtMixin,
    TimestampMixin,
    UpdatedAtMixin
)


###########################################################
# from .has_user import HasUserMixin
#
# If indicate return annotation for the 'user' relationship
# in 'HasUserMixin' by:
#
# 1. Forward ref
#   + have to import under 'TYPE_CHECKING'
#   + 'User' model for each inheritor.
# 2. Real 'User' model
#   + have to indicate full path ['.mixins.user']
#   + on import to avoid circular imports.
###########################################################

__all__ = [
    'ExpirableMixin',
    'IDMixin',
    'CreatedAtMixin',
    'TimestampMixin',
    'UpdatedAtMixin'
]
