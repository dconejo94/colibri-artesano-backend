import uuid

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_PRODUCT_ID,
)


async def test_remove_nonexistent_product_returns_404(client):
    fake_product = uuid.uuid4()

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{fake_product}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={uuid.uuid4()}"
    )

    assert resp.status_code == 404


async def test_remove_product_from_nonexistent_cart_returns_404(client):
    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={uuid.uuid4()}"
    )

    assert resp.status_code == 404
