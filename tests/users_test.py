import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.models.user import User
from tests.conftest import TestingSessionLocal
from tests.factories.product_factory import TEST_STORE_ID, TEST_USER_ID

_BUYER_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")
_MAIN_ORDER_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
_STORE_ORDER_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")


async def _seed_main_order():
    async with TestingSessionLocal() as db:
        order = MainOrder(
            id=_MAIN_ORDER_ID,
            buyer_id=TEST_USER_ID,
            total_amount=Decimal("10.00"),
        )
        db.add(order)
        await db.commit()


async def _seed_store_order():
    async with TestingSessionLocal() as db:
        buyer = User(
            id=_BUYER_ID,
            email="buyer@test.com",
            password_hash="hash",
        )
        main_order = MainOrder(
            id=_MAIN_ORDER_ID,
            buyer_id=_BUYER_ID,
            total_amount=Decimal("10.00"),
        )
        store_order = StoreOrder(
            id=_STORE_ORDER_ID,
            main_order_id=_MAIN_ORDER_ID,
            store_id=TEST_STORE_ID,
            subtotal_amount=Decimal("10.00"),
        )
        db.add_all([buyer, main_order, store_order])
        await db.commit()


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["id"] == str(TEST_USER_ID)


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient):
    payload = {"name": "Nombre Actualizado", "bio": "Bio actualizada"}
    response = await client.put("/api/v1/users/me", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nombre Actualizado"
    assert data["bio"] == "Bio actualizada"


@pytest.mark.asyncio
async def test_update_me_partial(client: AsyncClient):
    response = await client.put("/api/v1/users/me", json={"phone": "1234-5678"})
    assert response.status_code == 200
    assert response.json()["phone"] == "1234-5678"


@pytest.mark.asyncio
async def test_update_me_clear_field(client: AsyncClient):
    await client.put("/api/v1/users/me", json={"bio": "texto inicial"})
    response = await client.put("/api/v1/users/me", json={"bio": None})
    assert response.status_code == 200
    assert response.json()["bio"] is None


@pytest.mark.asyncio
async def test_delete_me(client: AsyncClient):
    response = await client.delete("/api/v1/users/me")
    assert response.status_code == 204

    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_me_with_orders(client: AsyncClient):
    await _seed_main_order()
    response = await client.delete("/api/v1/users/me")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_me_seller_with_sales(client: AsyncClient):
    await _seed_store_order()
    response = await client.delete("/api/v1/users/me")
    assert response.status_code == 204
