import pytest
from httpx import AsyncClient
from tests.factories.product_factory import TEST_STORE_ID

pytestmark = pytest.mark.asyncio


async def test_follow_unfollow_store(client: AsyncClient):
    store_id = str(TEST_STORE_ID)

    # Follow store
    response = await client.post(f"/api/v1/stores/{store_id}/follow")
    assert response.status_code == 204

    # Try following again (conflict)
    response = await client.post(f"/api/v1/stores/{store_id}/follow")
    assert response.status_code == 409

    # Unfollow store
    response = await client.delete(f"/api/v1/stores/{store_id}/follow")
    assert response.status_code == 204

    # Unfollow again
    response = await client.delete(f"/api/v1/stores/{store_id}/follow")
    assert response.status_code == 204


async def test_follow_store_not_found(client: AsyncClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(f"/api/v1/stores/{fake_id}/follow")
    assert response.status_code == 404


async def test_unfollow_store_not_found(client: AsyncClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/api/v1/stores/{fake_id}/follow")
    assert response.status_code == 404


async def test_get_store_profile_followers(client: AsyncClient):
    store_id = str(TEST_STORE_ID)

    # Initially not following
    response = await client.get(f"/api/v1/stores/{store_id}/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["follower_count"] == 0
    assert data["is_following"] is False

    # Follow store
    await client.post(f"/api/v1/stores/{store_id}/follow")

    # Check profile again
    response = await client.get(f"/api/v1/stores/{store_id}/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["follower_count"] == 1
    assert data["is_following"] is True


async def test_get_store_profile_unauthenticated(auth_client: AsyncClient):
    store_id = str(TEST_STORE_ID)

    # Check profile unauthenticated using auth_client
    response = await auth_client.get(f"/api/v1/stores/{store_id}/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["follower_count"] == 0
    assert data["is_following"] is False
