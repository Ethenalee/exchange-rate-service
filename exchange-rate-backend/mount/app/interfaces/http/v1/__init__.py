from fastapi import APIRouter
from . import currencies, rates


router = APIRouter()
router.include_router(currencies.router)
router.include_router(rates.router)
