from fastapi import APIRouter
from app.api.v1.products import router as products_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(products_router)
