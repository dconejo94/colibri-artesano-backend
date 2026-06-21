from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.stores import router as stores_router

# search_router MUST come before products_router so that the literal paths
# /products/search and /products/autocomplete are registered before the
# /{product_id} wildcard route.
from app.api.v1.search import router as search_router
from app.api.v1.products import router as products_router
from app.api.v1.orders import router as orders_router
from app.api.v1.users import router as users_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.events import router as events_router
from app.api.v1.carts import router as cart_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(stores_router)
api_router.include_router(search_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(users_router)
api_router.include_router(vendors_router)
api_router.include_router(events_router)
api_router.include_router(cart_router)
