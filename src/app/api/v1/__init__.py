from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.stores import router as stores_router
from app.api.v1.products import router as products_router
from app.api.v1.orders import router as orders_router
from app.api.v1.users import router as users_router
from app.api.v1.vendors import router as vendors_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(stores_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(users_router)
api_router.include_router(vendors_router)
