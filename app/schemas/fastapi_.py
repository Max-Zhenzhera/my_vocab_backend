"""
Supposed to be used in routes' `responses`.

Class name is verbose and contains `Schema` ending
for some purposes:
    - make reference to the real `HTTPException`;
    - `Schema` as serialazable pydantic model.

Example:
    .. code-block:: python
        >>> from starlette.status import HTTP_400_BAD_REQUEST
        >>>
        >>> # `responses` as an argument to:
        >>> # router.get(..., responses={...})
        >>>
        >>> responses = {
        >>>     HTTP_400_BAD_REQUEST: {
        >>>         'model': HTTPExceptionSchema
        >>>     },
        >>>     ...
        >>> }


Docs about this schema has been written on module level.
Not a schema (class) level beacuse this way
docs will be copied to the swagger.
"""


from pydantic import BaseModel


__all__ = ['HTTPExceptionSchema']


class HTTPExceptionSchema(BaseModel):
    detail: str
