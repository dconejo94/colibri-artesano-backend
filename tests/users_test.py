import pytest
from httpx import AsyncClient

from tests.factories.user_factory import TEST_USER_ID


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
async def test_delete_me(client: AsyncClient):
    response = await client.delete("/api/v1/users/me")
    assert response.status_code == 204

    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
