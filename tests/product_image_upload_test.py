"""Tests for the SAS image upload-url endpoint."""

import uuid
from datetime import datetime, timezone

from app.main import app
from app.api.deps import get_blob_storage_service

from tests.factories.product_factory import TEST_PRODUCT_ID


class _FakeStorage:
    """Stand-in for BlobStorageService so tests never touch Azure."""

    def generate_upload_sas(self, product_id, filename, content_type):
        blob_url = (
            f"https://fake.blob.core.windows.net/product-images/{product_id}/img.jpg"
        )
        upload_url = f"{blob_url}?sv=2024-01-01&sig=fakesignature&se=2030-01-01"
        return upload_url, blob_url, datetime(2030, 1, 1, tzinfo=timezone.utc)


def _use_fake_storage():
    app.dependency_overrides[get_blob_storage_service] = lambda: _FakeStorage()


async def test_upload_url_returns_sas_and_clean_blob_url(client):
    _use_fake_storage()

    resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images/upload-url",
        json={"filename": "photo.jpg", "content_type": "image/jpeg"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "sig=" in body["upload_url"]
    assert "?" not in body["blob_url"]
    assert body["blob_url"] in body["upload_url"]


async def test_upload_url_wrong_product_returns_404(client):
    """Requesting an upload URL for a product the user doesn't own must 404."""
    _use_fake_storage()
    fake_product = uuid.uuid4()

    resp = await client.post(
        f"/api/v1/products/{fake_product}/images/upload-url",
        json={"filename": "photo.jpg", "content_type": "image/jpeg"},
    )

    assert resp.status_code == 404


async def test_blob_url_round_trips_through_add_image(client):
    _use_fake_storage()

    up = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images/upload-url",
        json={"filename": "photo.jpg", "content_type": "image/jpeg"},
    )
    blob_url = up.json()["blob_url"]

    resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images",
        json={"image_url": blob_url, "is_primary": True},
    )

    assert resp.status_code == 201
    assert resp.json()["image_url"] == blob_url


async def test_upload_url_returns_503_when_unconfigured(client):
    """With no Azure settings the real provider yields a 503, not a 500."""
    resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images/upload-url",
        json={"filename": "photo.jpg", "content_type": "image/jpeg"},
    )

    assert resp.status_code == 503
