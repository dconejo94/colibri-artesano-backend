"""Unit tests for ProductImageService blob-host validation and cleanup."""

import uuid

import pytest

from app.domain.models.product_image import ProductImage
from app.domain.schemas.product_image import ProductImageCreateDTO
from app.services.product_image_service import ProductImageService
from app.core.exceptions import InvalidImageUrlError

_BLOB_PREFIX = "https://acct.blob.core.windows.net/product-images/"


class _FakeRepo:
    def __init__(self):
        self.store: dict[uuid.UUID, ProductImage] = {}
        self.deleted: list[ProductImage] = []

    async def create(self, image):
        if image.id is None:
            image.id = uuid.uuid4()
        self.store[image.id] = image
        return image

    async def get_by_id(self, image_id):
        return self.store.get(image_id)

    async def delete(self, image):
        self.deleted.append(image)
        self.store.pop(image.id, None)

    async def clear_primary(self, product_id):
        pass


class _FakeStorage:
    def __init__(self):
        self.deleted: list[str] = []

    def is_own_blob_url(self, url):
        return url.startswith(_BLOB_PREFIX)

    def delete_blob(self, url):
        self.deleted.append(url)


async def test_add_image_rejects_foreign_url_when_validation_on():
    svc = ProductImageService(
        _FakeRepo(), blob_storage=_FakeStorage(), validate_image_url=True
    )
    with pytest.raises(InvalidImageUrlError):
        await svc.add_image(
            uuid.uuid4(),
            ProductImageCreateDTO(image_url="https://evil.example.com/x.jpg"),
        )


async def test_add_image_accepts_own_blob_url_when_validation_on():
    svc = ProductImageService(
        _FakeRepo(), blob_storage=_FakeStorage(), validate_image_url=True
    )
    image = await svc.add_image(
        uuid.uuid4(),
        ProductImageCreateDTO(image_url=f"{_BLOB_PREFIX}p/a.jpg"),
    )
    assert image.image_url == f"{_BLOB_PREFIX}p/a.jpg"


async def test_add_image_skips_validation_when_flag_off():
    svc = ProductImageService(
        _FakeRepo(), blob_storage=_FakeStorage(), validate_image_url=False
    )
    image = await svc.add_image(
        uuid.uuid4(),
        ProductImageCreateDTO(image_url="https://picsum.photos/200"),
    )
    assert image.image_url == "https://picsum.photos/200"


async def test_delete_image_cleans_up_blob():
    repo = _FakeRepo()
    storage = _FakeStorage()
    variant_id = uuid.uuid4()
    image = ProductImage(
        id=uuid.uuid4(),
        variant_id=variant_id,
        image_url=f"{_BLOB_PREFIX}p/gone.jpg",
    )
    repo.store[image.id] = image

    svc = ProductImageService(repo, blob_storage=storage)
    await svc.delete_image(variant_id, image.id)

    assert storage.deleted == [f"{_BLOB_PREFIX}p/gone.jpg"]
