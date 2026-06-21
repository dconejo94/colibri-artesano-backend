"""Unit tests for StoreOrderService — the order layer that owns a store order's
product lines (variant resolution, stock, pricing, add/update/remove)."""

import uuid
from decimal import Decimal

import pytest

from app.domain.models.product import Product
from app.domain.models.product_variant import ProductVariant
from app.domain.models.store_order import StoreOrder
from app.domain.models.order_item import OrderItem
from app.services.store_order_service import StoreOrderService
from app.core.exceptions import NotFoundException, ConflictException


class _FakeVariantRepo:
    def __init__(self, variants):
        self._by_id = {v.id: v for v in variants}

    async def get_by_id(self, variant_id):
        return self._by_id.get(variant_id)

    async def list_by_product(self, product_id):
        return [v for v in self._by_id.values() if v.product_id == product_id]


class _FakeCartRepo:
    def __init__(self):
        self.items: dict[tuple, OrderItem] = {}
        self.removed: list = []

    async def get_order_item(self, store_order_id, product_id, variant_id):
        return self.items.get((store_order_id, product_id, variant_id))

    async def create_order_item(self, item):
        self.items[(item.store_order_id, item.product_id, item.variant_id)] = item
        return item

    async def remove_order_item(self, product_id, variant_id, store_order_id):
        removed = self.items.pop((store_order_id, product_id, variant_id), None)
        self.removed.append(removed)
        return removed


def _product(base="10.00"):
    return Product(
        id=uuid.uuid4(),
        store_id=uuid.uuid4(),
        name="Product",
        base_price=Decimal(base),
    )


def _variant(product_id, modifier="0.00", stock=50):
    return ProductVariant(
        id=uuid.uuid4(),
        product_id=product_id,
        name="Size",
        value="M",
        price_modifier=Decimal(modifier),
        stock_quantity=stock,
    )


def _store_order():
    return StoreOrder(
        id=uuid.uuid4(),
        main_order_id=uuid.uuid4(),
        store_id=uuid.uuid4(),
        seller_status="pending",
        subtotal_amount=Decimal("0.00"),
    )


def _service(variants, cart_repo=None):
    return StoreOrderService(
        cart_repository=cart_repo or _FakeCartRepo(),
        variant_repository=_FakeVariantRepo(variants),
    )


# ── resolve_variant ───────────────────────────────────────────────


async def test_resolve_named_variant():
    product = _product()
    variant = _variant(product.id)
    svc = _service([variant])

    resolved = await svc.resolve_variant(product.id, variant.id)

    assert resolved is variant


async def test_resolve_single_variant_without_id():
    product = _product()
    variant = _variant(product.id)
    svc = _service([variant])

    resolved = await svc.resolve_variant(product.id, None)

    assert resolved is variant


async def test_resolve_multiple_variants_without_id_raises():
    product = _product()
    svc = _service([_variant(product.id), _variant(product.id)])

    with pytest.raises(ConflictException):
        await svc.resolve_variant(product.id, None)


async def test_resolve_no_variants_raises():
    product = _product()
    svc = _service([])

    with pytest.raises(ConflictException):
        await svc.resolve_variant(product.id, None)


async def test_resolve_variant_of_wrong_product_raises():
    product = _product()
    other = _product()
    variant = _variant(other.id)
    svc = _service([variant])

    with pytest.raises(NotFoundException):
        await svc.resolve_variant(product.id, variant.id)


# ── add_product ───────────────────────────────────────────────────


async def test_add_product_creates_line_and_returns_amount():
    product = _product("10.00")
    variant = _variant(product.id, modifier="5.00", stock=50)
    repo = _FakeCartRepo()
    svc = _service([variant], repo)
    store_order = _store_order()

    amount = await svc.add_product(store_order, product, variant, 2)

    # (10 + 5) * 2
    assert amount == Decimal("30.00")
    assert store_order.subtotal_amount == Decimal("30.00")
    assert len(repo.items) == 1


async def test_add_product_accumulates_quantity():
    product = _product()
    variant = _variant(product.id, stock=50)
    repo = _FakeCartRepo()
    svc = _service([variant], repo)
    store_order = _store_order()

    await svc.add_product(store_order, product, variant, 2)
    await svc.add_product(store_order, product, variant, 3)

    line = repo.items[(store_order.id, product.id, variant.id)]
    assert line.quantity == 5


async def test_add_product_over_stock_raises():
    product = _product()
    variant = _variant(product.id, stock=3)
    svc = _service([variant])
    store_order = _store_order()

    with pytest.raises(ConflictException):
        await svc.add_product(store_order, product, variant, 4)


# ── update_quantity ───────────────────────────────────────────────


async def test_update_quantity_missing_line_raises():
    product = _product()
    variant = _variant(product.id)
    svc = _service([variant])
    store_order = _store_order()

    with pytest.raises(NotFoundException):
        await svc.update_quantity(store_order, product.id, variant, 5)


async def test_update_quantity_over_stock_raises():
    product = _product()
    variant = _variant(product.id, stock=10)
    repo = _FakeCartRepo()
    svc = _service([variant], repo)
    store_order = _store_order()
    await svc.add_product(store_order, product, variant, 2)

    with pytest.raises(ConflictException):
        await svc.update_quantity(store_order, product.id, variant, 11)


async def test_update_quantity_returns_signed_diff():
    product = _product("10.00")
    variant = _variant(product.id, stock=50)
    repo = _FakeCartRepo()
    svc = _service([variant], repo)
    store_order = _store_order()
    await svc.add_product(store_order, product, variant, 2)

    diff = await svc.update_quantity(store_order, product.id, variant, 5)

    # from 2 to 5 units at 10.00 -> +30.00
    assert diff == Decimal("30.00")
    assert store_order.subtotal_amount == Decimal("50.00")


# ── remove_line ───────────────────────────────────────────────────


async def test_remove_line_returns_amount_and_updates_subtotal():
    product = _product("10.00")
    variant = _variant(product.id, stock=50)
    repo = _FakeCartRepo()
    svc = _service([variant], repo)
    store_order = _store_order()
    await svc.add_product(store_order, product, variant, 3)
    line = repo.items[(store_order.id, product.id, variant.id)]

    amount = await svc.remove_line(store_order, line)

    assert amount == Decimal("30.00")
    assert store_order.subtotal_amount == Decimal("0.00")
    assert repo.items == {}
