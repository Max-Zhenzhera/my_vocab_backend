from fastapi import APIRouter

from .auth import router as auth_router
from .oauth import router as oauth_router
from .verification import router as verification_router


__all__ = ['router']


router = APIRouter()

router.include_router(
    router=verification_router,
    tags=['Verification'],
    prefix='/verification'
)
router.include_router(
    router=auth_router,
    tags=['Authentication'],
    prefix='/auth'
)
router.include_router(
    router=oauth_router,
    tags=['OAuth'],
    prefix='/oauth'
)
